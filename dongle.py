#!/usr/bin/env python3
"""Single RTL-SDR dongle arbiter shared by every RF consumer.

Only one process can hold the RTL-SDR at a time.  Each consumer (radio, radio
scanner, rtl_433 streamer, spectrum/waterfall, one-shot rtl_433 jobs) calls
claim(owner) before touching the dongle.  claim():
  1. calls the stop callback of every *other* registered owner,
  2. kills stray rtl_* contender processes,
  3. bumps a generation counter and returns it as a token.

Long-running loops keep the token and poll is_current(token); once another
owner claims the dongle the token goes stale and the loop must exit.

Lock order: dongle._lock is always taken BEFORE any consumer's own lock.
Stop callbacks therefore must not call back into claim().
"""
import subprocess
import threading
import time

ALL_CONTENDERS = ['rtl_433', 'rtl_power', 'rtl_fm', 'rtl_sdr', 'rtl_test',
                  'rtl_tcp', 'rtl_adsb', 'dump1090', 'dump1090-mutability', 'dump1090-fa']

_lock = threading.RLock()
_active = None
_gen = 0
_releasers = {}


def pkill(names):
    for n in names:
        try:
            subprocess.run(['pkill', '-x', n], timeout=3,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


def wait_dead(names, secs=3.0):
    """Wait for the named processes to exit; SIGKILL whatever is left."""
    end = time.time() + secs
    while time.time() < end:
        alive = False
        for n in names:
            try:
                r = subprocess.run(['pgrep', '-x', n], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
            except Exception:
                continue
            if r.returncode == 0:
                alive = True
        if not alive:
            return True
        time.sleep(0.1)
    for n in names:
        try:
            subprocess.run(['pkill', '-9', '-x', n], timeout=3,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    time.sleep(0.3)
    return False


def register(owner, stop_cb):
    """stop_cb(reason) is called when a different owner claims the dongle."""
    with _lock:
        _releasers[owner] = stop_cb


def claim(owner, kill=None, wait=2.0):
    """Take the dongle for `owner`. Returns a token for is_current()."""
    global _active, _gen
    kill = ALL_CONTENDERS if kill is None else kill
    with _lock:
        _gen += 1
        token = _gen
        reason = 'dongle claimed by ' + owner
        for other, cb in list(_releasers.items()):
            if other == owner:
                continue
            try:
                cb(reason)
            except Exception:
                pass
        if kill:
            pkill(kill)
            wait_dead(kill, wait)
        _active = owner
        return token


def is_current(token):
    return token is not None and token == _gen


def release(owner):
    global _active
    with _lock:
        if _active == owner:
            _active = None


def active():
    return _active


def status():
    return {'active': _active, 'generation': _gen}
