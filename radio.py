#!/usr/bin/env python3
"""PiFlip Radio: RTL-SDR -> rtl_fm -> ffmpeg -> MP3 over HTTP.

One managed background pipeline (rtl_fm | python pump | ffmpeg) feeds any number
of <audio> listeners.  The single RTL-SDR dongle is arbitrated here: starting the
radio evicts other rtl_* jobs, and other RTL routes call radio.stop() first
(see the before_request hook in web_interface.py).
"""
import atexit
import collections
import json
import math
import os
import queue
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path

from flask import Blueprint, Response, jsonify, render_template, request

import dongle

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

bp = Blueprint('radio', __name__)

BASE = Path(__file__).resolve().parent
PRESET_FILE = BASE / 'config' / 'radio_presets.json'

MIN_MHZ, MAX_MHZ = 0.5, 1766.0
IDLE_STOP_SECONDS = 600          # auto-free the dongle if nobody is listening
COMPETING = ['rtl_433', 'rtl_power', 'rtl_sdr', 'rtl_test', 'rtl_tcp', 'rtl_adsb']

MODES = {
    'wfm': {'label': 'WFM', 'rtl': ['-M', 'wbfm', '-s', '200k', '-r', '44100', '-E', 'deemp'],
            'rate': 44100, 'kbps': 128, 'noise_d': -14.0},
    'nfm': {'label': 'NFM', 'rtl': ['-M', 'fm', '-s', '24k', '-r', '24k'],
            'rate': 24000, 'kbps': 112, 'noise_d': 2.3},
    'am':  {'label': 'AM',  'rtl': ['-M', 'am', '-s', '24k', '-r', '24k', '-E', 'dc'],
            'rate': 24000, 'kbps': 112, 'noise_d': 0.0},
}

DEFAULT_PRESETS = [
    {'id': 'noaa1', 'name': 'NOAA WX 1', 'freq': 162.400, 'mode': 'nfm', 'group': 'Weather', 'squelch': 0},
    {'id': 'noaa2', 'name': 'NOAA WX 2', 'freq': 162.425, 'mode': 'nfm', 'group': 'Weather', 'squelch': 0},
    {'id': 'noaa3', 'name': 'NOAA WX 3', 'freq': 162.450, 'mode': 'nfm', 'group': 'Weather', 'squelch': 0},
    {'id': 'noaa4', 'name': 'NOAA WX 4', 'freq': 162.475, 'mode': 'nfm', 'group': 'Weather', 'squelch': 0},
    {'id': 'noaa5', 'name': 'NOAA WX 5', 'freq': 162.500, 'mode': 'nfm', 'group': 'Weather', 'squelch': 0},
    {'id': 'noaa6', 'name': 'NOAA WX 6', 'freq': 162.525, 'mode': 'nfm', 'group': 'Weather', 'squelch': 0},
    {'id': 'noaa7', 'name': 'NOAA WX 7', 'freq': 162.550, 'mode': 'nfm', 'group': 'Weather', 'squelch': 0},
    {'id': 'fm1', 'name': 'FM 91.7 (example)', 'freq': 91.7, 'mode': 'wfm', 'group': 'FM', 'squelch': 0},
    {'id': 'fm2', 'name': 'FM 101.1 (example)', 'freq': 101.1, 'mode': 'wfm', 'group': 'FM', 'squelch': 0},
    {'id': 'air1', 'name': 'Local Tower (set freq)', 'freq': None, 'mode': 'am', 'group': 'Airband', 'squelch': 0},
]


# --------------------------------------------------------------------------- presets
_preset_lock = threading.Lock()


def _clean_preset(p):
    if not isinstance(p, dict):
        raise ValueError('preset must be an object')
    mode = str(p.get('mode', 'wfm')).lower()
    if mode not in MODES:
        raise ValueError('bad mode')
    freq = p.get('freq')
    if freq in (None, ''):
        freq = None
    else:
        freq = round(float(freq), 4)
        if not (MIN_MHZ <= freq <= MAX_MHZ):
            raise ValueError('frequency out of range')
    name = str(p.get('name', '')).strip()[:40] or ('%.3f MHz' % freq if freq else 'Untitled')
    squelch = int(p.get('squelch') or 0)
    if not 0 <= squelch <= 500:
        raise ValueError('bad squelch')
    return {
        'id': str(p.get('id') or uuid.uuid4().hex[:8])[:16],
        'name': name,
        'freq': freq,
        'mode': mode,
        'group': str(p.get('group', 'Other')).strip()[:20] or 'Other',
        'squelch': squelch,
    }


def load_presets():
    with _preset_lock:
        try:
            data = json.loads(PRESET_FILE.read_text())
            return [_clean_preset(p) for p in data.get('presets', [])]
        except FileNotFoundError:
            pass
        except Exception:
            pass
    save_presets(DEFAULT_PRESETS)
    return [dict(p) for p in DEFAULT_PRESETS]


def save_presets(presets):
    cleaned = [_clean_preset(p) for p in presets][:200]
    with _preset_lock:
        PRESET_FILE.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(PRESET_FILE.parent), prefix='.radio_presets_')
        with os.fdopen(fd, 'w') as f:
            json.dump({'presets': cleaned}, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, PRESET_FILE)
    return cleaned


# --------------------------------------------------------------------------- pipeline
_pkill = dongle.pkill
_wait_dead = dongle.wait_dead


class DongleLost(RuntimeError):
    pass


def measure(s, rate, noise_d=0.0):
    """Return (level_dBFS, clarity 0..1) for a block of mono int16-as-float samples.
    Clarity compares high-band vs speech-band spectral density: real audio rolls
    off (strongly negative dB), demodulated noise stays flat or rises."""
    rms = float(np.sqrt(np.mean(s * s)))
    db = 20.0 * math.log10(max(rms, 1.0) / 32768.0)
    if db < -62:
        return db, 0.0
    F = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2
    fr = np.fft.rfftfreq(len(s), 1.0 / rate)
    nyq = rate / 2.0
    lo = F[(fr >= 250) & (fr <= 2500)].mean() + 1e-9
    hi = F[(fr >= 0.4 * nyq) & (fr <= 0.65 * nyq)].mean() + 1e-9
    d = 10.0 * math.log10(hi / lo)
    # noise_d = measured hi/low dB of an empty channel in this mode (calibrated on the Pi)
    return db, max(0.0, min(1.0, (noise_d - d - 4.0) / 22.0))


class Radio:
    def __init__(self):
        self.lock = threading.RLock()
        self.cond = threading.Condition(self.lock)
        self.gen = 0
        self.fm = None
        self.ff = None
        self.params = None
        self.nonce = None
        self.started = 0.0
        self.got_audio = False
        self.error = None
        self.stderr_tail = collections.deque(maxlen=12)
        self.listeners = set()
        self.last_listener = time.time()
        self.level_db = -90.0
        self.clarity = 0.0
        self.bytes_out = 0
        self.stopped_reason = None

    # -- state ---------------------------------------------------------------
    def is_running(self):
        with self.lock:
            return self.fm is not None and self.fm.poll() is None

    def status(self):
        with self.lock:
            running = self.is_running()
            if running:
                state = 'playing' if self.got_audio else 'starting'
            else:
                state = 'error' if self.error else 'stopped'
            p = self.params or {}
            level = max(0.0, min(1.0, (self.level_db + 60.0) / 50.0)) if running else 0.0
            bars = int(round(self.clarity * 5)) if running else 0
            return {
                'state': state, 'running': running,
                'freq': p.get('freq'), 'mode': p.get('mode'), 'name': p.get('name'),
                'squelch': p.get('squelch', 0), 'gain': p.get('gain', 0),
                'level': round(level, 3), 'level_db': round(self.level_db, 1),
                'signal': bars, 'clarity': round(self.clarity, 2),
                'listeners': len(self.listeners),
                'uptime': round(time.time() - self.started, 1) if running else 0,
                'error': self.error, 'nonce': self.nonce,
                'stopped_reason': None if running else self.stopped_reason,
            }

    # -- start / stop --------------------------------------------------------
    def start(self, freq, mode, name=None, squelch=0, nonce=None, gain=40, token=None):
        """token: a dongle.claim() token held by the caller (e.g. the scanner).
        Without one the radio claims the dongle itself."""
        mode = str(mode).lower()
        if mode not in MODES:
            raise ValueError('mode must be wfm, nfm or am')
        freq = float(freq)
        if not (MIN_MHZ <= freq <= MAX_MHZ):
            raise ValueError('frequency must be %.1f-%.0f MHz' % (MIN_MHZ, MAX_MHZ))
        squelch = int(squelch or 0)
        if not 0 <= squelch <= 500:
            raise ValueError('bad squelch')
        gain = float(gain or 0)
        if not 0 <= gain <= 50:
            raise ValueError('gain must be 0 (auto) to 50 dB')
        cfg = MODES[mode]
        if token is None:
            # single-dongle arbiter: stop other owners + evict other RTL jobs
            # (taken before self.lock: dongle lock always comes first)
            token = dongle.claim('radio', kill=COMPETING)
        with self.lock:
            if not dongle.is_current(token):
                raise DongleLost('dongle was claimed by ' + str(dongle.active()))
            self._stop_locked('retune')
            self.gen += 1
            gen = self.gen
            self.error = None
            self.stopped_reason = None
            self.got_audio = False
            self.level_db, self.clarity, self.bytes_out = -90.0, 0.0, 0
            self.stderr_tail.clear()
            self.nonce = nonce
            self.params = {'freq': freq, 'mode': mode, 'name': name or ('%.3f MHz' % freq),
                           'squelch': squelch, 'gain': gain}
            fm_cmd = ['rtl_fm', '-f', str(int(round(freq * 1e6))),
                      *cfg['rtl'], '-l', str(squelch), *(['-g', str(gain)] if gain else []), '-']
            ff_cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin',
                      '-fflags', 'nobuffer', '-probesize', '32', '-analyzeduration', '0',
                      '-f', 's16le', '-ar', str(cfg['rate']), '-ac', '1', '-i', 'pipe:0',
                      '-ar', '44100', '-ac', '1', '-codec:a', 'libmp3lame',
                      '-b:a', '%dk' % cfg['kbps'], '-flush_packets', '1', '-write_xing', '0', '-f', 'mp3', 'pipe:1']
            try:
                self.fm = subprocess.Popen(fm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
                self.ff = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, bufsize=0)
            except Exception as e:
                self.error = 'could not start pipeline: %s' % e
                self._stop_locked('error')
                raise
            self.started = time.time()
            self.last_listener = time.time()
            fm, ff = self.fm, self.ff
            for target, args in ((self._pump, (gen, fm, ff, cfg['rate'], cfg['noise_d'])), (self._out, (gen, ff)),
                                 (self._drain, (gen, fm, 'rtl_fm')), (self._drain, (gen, ff, 'ffmpeg'))):
                threading.Thread(target=target, args=args, daemon=True).start()
            self.cond.notify_all()
        return self.status()

    def stop(self, reason='stopped'):
        with self.lock:
            self._stop_locked(reason)
        return self.status()

    def _stop_locked(self, reason):
        fm, ff = self.fm, self.ff
        self.fm = self.ff = None
        self.gen += 1  # invalidate reader threads
        if fm is not None or ff is not None:
            self.stopped_reason = reason
        for proc in (fm, ff):
            if proc is None:
                continue
            try:
                proc.terminate()
            except Exception:
                pass
        for proc in (fm, ff):
            if proc is None:
                continue
            try:
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                except Exception:
                    pass
            for s in (proc.stdin, proc.stdout, proc.stderr):
                try:
                    if s:
                        s.close()
                except Exception:
                    pass
        for q in list(self.listeners):
            self._offer(q, None)
        self.listeners.clear()
        self.cond.notify_all()

    # -- worker threads -------------------------------------------------------
    def _alive(self, gen):
        return gen == self.gen

    def _pump(self, gen, fm, ff, rate, noise_d):
        """rtl_fm PCM -> ffmpeg stdin, measuring level/clarity on the way."""
        fd = fm.stdout.fileno() if fm.stdout else None
        ema_db, ema_c = -90.0, 0.0
        buf = bytearray()
        try:
            while self._alive(gen):
                data = os.read(fd, 8192)
                if not data:
                    break
                try:
                    ff.stdin.write(data)
                except Exception:
                    break
                if np is not None:
                    buf += data
                    if len(buf) >= 8192:
                        s = np.frombuffer(bytes(buf[:8192]), dtype='<i2').astype(np.float32)
                        buf = bytearray()
                        db, c = measure(s, rate, noise_d)
                        ema_db = 0.6 * ema_db + 0.4 * db
                        ema_c = 0.7 * ema_c + 0.3 * c
                        self.level_db, self.clarity = ema_db, ema_c
        except Exception:
            pass
        finally:
            with self.lock:
                if self._alive(gen) and self.fm is fm:
                    rc = fm.poll()
                    tail = ' | '.join(list(self.stderr_tail)[-3:])
                    self.error = ('rtl_fm exited (%s). %s' % (rc, tail)).strip()
                    self._stop_locked('error')

    def _out(self, gen, ff):
        try:
            while self._alive(gen):
                chunk = ff.stdout.read(4096)
                if not chunk:
                    break
                if not self.got_audio:
                    self.got_audio = True
                self.bytes_out += len(chunk)
                with self.lock:
                    if not self._alive(gen):
                        break
                    for q in list(self.listeners):
                        self._offer(q, chunk)
                    if not self.listeners and time.time() - self.last_listener > IDLE_STOP_SECONDS:
                        self._stop_locked('idle timeout (no listeners)')
                        break
        except Exception:
            pass

    def _drain(self, gen, proc, tag):
        try:
            for line in iter(proc.stderr.readline, b''):
                txt = line.decode('utf-8', 'replace').strip()
                if txt:
                    self.stderr_tail.append('%s: %s' % (tag, txt[:160]))
        except Exception:
            pass

    @staticmethod
    def _offer(q, item):
        try:
            q.put_nowait(item)
        except queue.Full:
            try:
                q.get_nowait()
            except queue.Empty:
                pass
            try:
                q.put_nowait(item)
            except queue.Full:
                pass

    # -- listeners ------------------------------------------------------------
    def subscribe(self, nonce=None, wait=10.0):
        end = time.time() + wait
        with self.lock:
            while True:
                ok = self.is_running() and (nonce is None or nonce == self.nonce)
                if ok:
                    q = queue.Queue(maxsize=256)
                    self.listeners.add(q)
                    self.last_listener = time.time()
                    return q
                left = end - time.time()
                if left <= 0:
                    return None
                self.cond.wait(timeout=min(left, 0.5))

    def unsubscribe(self, q):
        with self.lock:
            self.listeners.discard(q)
            self.last_listener = time.time()


radio = Radio()
dongle.register('radio', lambda reason: radio.stop(reason))


def _cleanup_at_exit():
    try:
        radio.stop('shutdown')
    except Exception:
        pass


atexit.register(_cleanup_at_exit)
# nothing else legitimately runs rtl_fm; clear strays from a crashed earlier worker
_pkill(['rtl_fm'])


# --------------------------------------------------------------------------- routes
@bp.route('/radio')
def radio_page():
    return render_template('radio.html')


@bp.route('/api/radio/status')
def api_status():
    return jsonify(radio.status())


@bp.route('/api/radio/start', methods=['POST'])
def api_start():
    d = request.get_json(silent=True) or {}
    try:
        st = radio.start(d.get('freq'), d.get('mode', 'wfm'), d.get('name'),
                         d.get('squelch', 0), d.get('nonce'), d.get('gain', 40))
        return jsonify(st)
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/radio/stop', methods=['POST'])
def api_stop():
    return jsonify(radio.stop('stopped by user'))


@bp.route('/api/radio/presets', methods=['GET'])
def api_presets_get():
    return jsonify({'presets': load_presets(), 'modes': {k: v['label'] for k, v in MODES.items()}})


@bp.route('/api/radio/presets', methods=['POST'])
def api_presets_set():
    d = request.get_json(silent=True) or {}
    try:
        return jsonify({'presets': save_presets(d.get('presets', []))})
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/api/radio/presets/reset', methods=['POST'])
def api_presets_reset():
    return jsonify({'presets': save_presets(DEFAULT_PRESETS)})


@bp.route('/radio/stream.mp3')
def stream():
    q = radio.subscribe(request.args.get('g'))
    if q is None:
        return jsonify({'error': 'radio is not playing'}), 409

    def gen():
        try:
            while True:
                try:
                    chunk = q.get(timeout=15)
                except queue.Empty:
                    if not radio.is_running():
                        break
                    continue
                if chunk is None:
                    break
                yield chunk
        finally:
            radio.unsubscribe(q)

    return Response(gen(), mimetype='audio/mpeg', headers={
        'Cache-Control': 'no-cache, no-store', 'X-Accel-Buffering': 'no',
        'Connection': 'close', 'icy-name': 'PiFlip Radio'})

