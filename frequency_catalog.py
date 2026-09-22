#!/usr/bin/env python3
"""Loader for the offline frequency catalog (frequencies.json, built by tools/build_frequencies.py)."""
import json
from pathlib import Path

CATALOG_FILE = Path(__file__).resolve().parent / 'frequencies.json'
_cache = {'mtime': None, 'data': None}


def load():
    m = CATALOG_FILE.stat().st_mtime
    if _cache['mtime'] != m:
        _cache['data'] = json.loads(CATALOG_FILE.read_text())
        _cache['mtime'] = m
    return _cache['data']


def summary():
    d = load()
    return {'version': d.get('version'), 'description': d.get('description'),
            'types': [{k: t[k] for k in ('id', 'name', 'icon', 'tier', 'count')} for t in d['types']]}


def get_type(type_id):
    for t in load()['types']:
        if t['id'] == type_id:
            return t
    return None


def is_tunable(e):
    return (not e.get('digital') and e.get('freqMHz') is not None and not e.get('route')
            and e.get('mode') in ('wfm', 'nfm', 'am'))


def tunable_entries(t):
    """Entries the radio/scanner can actually play (analog, rtl_fm-demodulable)."""
    return [{'name': e['name'], 'freq': e['freqMHz'], 'mode': e['mode']}
            for e in t['entries'] if is_tunable(e)]
