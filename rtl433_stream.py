#!/usr/bin/env python3
"""Live rtl_433 decoder for PiFlip.

One managed `rtl_433 -F json` process; each JSON line becomes an event
{model, id, channel, readings, rssi, snr, time}.  A last-seen rollup keyed by
(model, id) feeds the live table, and every decode is logged to SQLite
(~/piflip/rtl433_decodes.db, table `decodes`) for /api/rtl433/history.
The dongle is taken through dongle.claim('rtl433') so the radio, scanner and
waterfall are stopped first.
"""
import atexit
import collections
import json
import sqlite3
import subprocess
import threading
import time
from pathlib import Path

import dongle

BANDS = {'315M': '315 MHz (US cars/remotes)', '433.92M': '433.92 MHz (ISM)', '915M': '915 MHz (US ISM)'}
DEFAULT_BAND = '433.92M'
DB_PATH = Path('~/piflip').expanduser() / 'rtl433_decodes.db'

# rtl_433 JSON keys that describe the packet rather than the sensor reading
META_KEYS = {'time', 'model', 'id', 'channel', 'rssi', 'snr', 'noise', 'freq', 'freq1', 'freq2',
             'mic', 'mod', 'protocol', 'subtype'}


def parse_event(obj, now=None):
    """Normalise one rtl_433 JSON object. Returns None for non-decode lines."""
    if not isinstance(obj, dict) or 'model' not in obj:
        return None
    readings = {k: v for k, v in obj.items() if k not in META_KEYS}
    return {
        'model': str(obj.get('model')),
        'id': obj.get('id'),
        'channel': obj.get('channel'),
        'readings': readings,
        'rssi': obj.get('rssi'),
        'snr': obj.get('snr'),
        'freq': obj.get('freq'),
        'time': obj.get('time'),
        'ts': now if now is not None else time.time(),
    }


class DecodeLog:
    def __init__(self, path=DB_PATH):
        self.path = Path(path)
        self.lock = threading.Lock()
        self._conn = None

    def _db(self):
        if self._conn is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.path), check_same_thread=False, timeout=5)
            self._conn.execute('CREATE TABLE IF NOT EXISTS decodes '
                               '(ts REAL, model TEXT, dev_id TEXT, json TEXT, rssi REAL)')
            self._conn.execute('CREATE INDEX IF NOT EXISTS decodes_model_ts ON decodes(model, ts)')
            self._conn.execute('CREATE INDEX IF NOT EXISTS decodes_ts ON decodes(ts)')
            self._conn.commit()
        return self._conn

    def add(self, ev, raw):
        with self.lock:
            try:
                db = self._db()
                rssi = ev.get('rssi')
                db.execute('INSERT INTO decodes (ts, model, dev_id, json, rssi) VALUES (?,?,?,?,?)',
                           (ev['ts'], ev['model'], None if ev['id'] is None else str(ev['id']),
                            json.dumps(raw), float(rssi) if isinstance(rssi, (int, float)) else None))
                db.commit()
            except Exception:
                pass

    def query(self, model=None, since=None, limit=200):
        sql, args = 'SELECT ts, model, dev_id, json, rssi FROM decodes WHERE 1=1', []
        if model:
            sql += ' AND model = ?'
            args.append(model)
        if since is not None:
            sql += ' AND ts >= ?'
            args.append(float(since))
        sql += ' ORDER BY ts DESC LIMIT ?'
        args.append(max(1, min(int(limit), 5000)))
        with self.lock:
            rows = self._db().execute(sql, args).fetchall()
        out = []
        for ts, m, dev, js, rssi in rows:
            try:
                data = json.loads(js)
            except Exception:
                data = {}
            out.append({'ts': ts, 'model': m, 'dev_id': dev, 'rssi': rssi, 'data': data})
        return out

    def models(self):
        with self.lock:
            return [r[0] for r in self._db().execute(
                'SELECT model, COUNT(*) c FROM decodes GROUP BY model ORDER BY c DESC').fetchall()]


class Rtl433Streamer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.lock = threading.RLock()
        self.proc = None
        self.band = DEFAULT_BAND
        self.gain = 40
        self.started = 0.0
        self.error = None
        self.stopped_reason = None
        self.devices = {}
        self.recent = collections.deque(maxlen=50)
        self.stderr_tail = collections.deque(maxlen=8)
        self.total = 0
        self.version = 0
        self.log = DecodeLog()

    def is_running(self):
        with self.lock:
            return self.proc is not None and self.proc.poll() is None

    def start(self, band=DEFAULT_BAND, gain=40):
        band = band if band in BANDS else DEFAULT_BAND
        gain = int(gain) if gain not in (None, '') else 40
        self.stop('restart')
        dongle.claim('rtl433')              # before self.lock (dongle lock first)
        with self.lock:
            self.band, self.gain = band, gain
            self.error = self.stopped_reason = None
            self.devices.clear()
            self.recent.clear()
            self.stderr_tail.clear()
            self.total = 0
            # -M level adds rssi/snr/noise to every decode
            cmd = ['rtl_433', '-F', 'json', '-f', band, '-g', str(gain), '-M', 'level']
            try:
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             text=True, bufsize=1)
            except Exception as e:
                self.proc = None
                self.error = 'could not start rtl_433: %s' % e
                self.version += 1
                raise
            self.started = time.time()
            proc = self.proc
            self.version += 1
        threading.Thread(target=self._read, args=(proc,), daemon=True).start()
        threading.Thread(target=self._drain, args=(proc,), daemon=True).start()
        return self.status()

    def stop(self, reason='stopped'):
        with self.lock:
            proc, self.proc = self.proc, None
            if proc is None:
                return self.status()
            self.stopped_reason = reason
            self.version += 1
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
                proc.wait(timeout=2)
            except Exception:
                pass
        dongle.release('rtl433')
        return self.status()

    def _read(self, proc):
        try:
            for line in proc.stdout:
                line = line.strip()
                if not line.startswith('{'):
                    continue
                try:
                    raw = json.loads(line)
                except ValueError:
                    continue
                ev = parse_event(raw)
                if ev is None:
                    continue
                self.log.add(ev, raw)
                with self.lock:
                    if self.proc is not proc:
                        break
                    key = '%s|%s' % (ev['model'], ev['id'])
                    d = self.devices.get(key)
                    if d is None:
                        d = self.devices[key] = {'key': key, 'model': ev['model'], 'id': ev['id'],
                                                 'first_seen': ev['ts'], 'count': 0}
                    d.update(channel=ev['channel'], readings=ev['readings'], rssi=ev['rssi'],
                             snr=ev['snr'], time=ev['time'], last_seen=ev['ts'])
                    d['count'] += 1
                    self.recent.appendleft(ev)
                    self.total += 1
                    self.version += 1
        except Exception:
            pass
        finally:
            with self.lock:
                if self.proc is proc:
                    rc = proc.poll()
                    self.proc = None
                    self.error = ('rtl_433 exited (%s). %s' % (rc, ' | '.join(self.stderr_tail))).strip()
                    self.version += 1

    def _drain(self, proc):
        try:
            for line in proc.stderr:
                t = line.strip()
                if t:
                    self.stderr_tail.append(t[:160])
        except Exception:
            pass

    def status(self):
        with self.lock:
            running = self.proc is not None and self.proc.poll() is None
            return {'running': running, 'band': self.band, 'gain': self.gain,
                    'uptime': round(time.time() - self.started, 1) if running else 0,
                    'total': self.total, 'device_count': len(self.devices),
                    'error': self.error, 'stopped_reason': None if running else self.stopped_reason}

    def snapshot(self):
        with self.lock:
            devs = sorted(self.devices.values(), key=lambda d: d['last_seen'], reverse=True)
            return self.version, {'status': self.status(), 'devices': [dict(d) for d in devs],
                                  'recent': list(self.recent)[:20], 'now': time.time()}


streamer = Rtl433Streamer()
dongle.register('rtl433', lambda reason: streamer.stop(reason))
atexit.register(lambda: streamer.stop('shutdown'))
