#!/usr/bin/env python3
"""Build frequencies.json (the offline PiFlip frequency catalog).

Tier 1 = standardized US channel plans, generated here from the published
plans (formula or table) so every value is auditable.
Tier 2 = local Cincinnati / Hamilton County OH data from data/local_cincinnati.json,
each entry carrying the public `source` URL it was taken from (see SOURCES.md).

Run:  python3 tools/build_frequencies.py   (rewrites ../frequencies.json)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / 'data' / 'local_cincinnati.json'
OUT = ROOT / 'frequencies.json'


def E(name, f, mode, notes='', source=None, **kw):
    e = {'name': name, 'freqMHz': None if f is None else round(float(f), 5), 'mode': mode, 'notes': notes}
    if source:
        e['source'] = source
    e.update(kw)
    return e


# ------------------------------------------------------------------ Tier 1
def noaa():
    # NWR channel numbering: WX1..WX7
    src = 'https://www.weather.gov/nwr/'
    plan = [(1, 162.550), (2, 162.400), (3, 162.475), (4, 162.425), (5, 162.450), (6, 162.500), (7, 162.525)]
    return [E('NOAA WX%d' % n, f, 'nfm', 'NOAA Weather Radio / SAME alerts', src, channel='WX%d' % n)
            for n, f in sorted(plan, key=lambda x: x[1])]


MARINE = [
    # ch, ship MHz, coast MHz (duplex) or None, use
    ('01A', 156.050, None, 'Port operations/commercial, VTS (selected areas)'),
    ('03A', 156.150, None, 'US Government / Coast Guard'),
    ('05A', 156.250, None, 'Port operations, VTS (selected areas)'),
    ('06', 156.300, None, 'Intership safety'),
    ('07A', 156.350, None, 'Commercial'),
    ('08', 156.400, None, 'Commercial (intership)'),
    ('09', 156.450, None, 'Boater calling; commercial & non-commercial'),
    ('10', 156.500, None, 'Commercial'),
    ('11', 156.550, None, 'Commercial; VTS (selected areas)'),
    ('12', 156.600, None, 'Port operations; VTS (selected areas)'),
    ('13', 156.650, None, 'Bridge-to-bridge navigation safety (1 W); locks & bridges'),
    ('14', 156.700, None, 'Port operations; VTS (selected areas)'),
    ('15', 156.750, None, 'Environmental (receive only)'),
    ('16', 156.800, None, 'International distress, safety and calling'),
    ('17', 156.850, None, 'State & local government maritime control'),
    ('18A', 156.900, None, 'Commercial'),
    ('19A', 156.950, None, 'Commercial'),
    ('20', 157.000, 161.600, 'Port operations (duplex)'),
    ('20A', 157.000, None, 'Port operations'),
    ('21A', 157.050, None, 'US Coast Guard only'),
    ('22A', 157.100, None, 'Coast Guard liaison & maritime safety info broadcasts'),
    ('23A', 157.150, None, 'US Coast Guard only'),
    ('24', 157.200, 161.800, 'Public correspondence (marine operator)'),
    ('25', 157.250, 161.850, 'Public correspondence (marine operator)'),
    ('26', 157.300, 161.900, 'Public correspondence (marine operator)'),
    ('27', 157.350, 161.950, 'Public correspondence (marine operator)'),
    ('28', 157.400, 162.000, 'Public correspondence (marine operator)'),
    ('63A', 156.175, None, 'Port operations, VTS (selected areas)'),
    ('65A', 156.275, None, 'Port operations'),
    ('66A', 156.325, None, 'Port operations'),
    ('67', 156.375, None, 'Commercial; bridge-to-bridge (Lower Mississippi)'),
    ('68', 156.425, None, 'Non-commercial (recreational)'),
    ('69', 156.475, None, 'Non-commercial (recreational)'),
    ('70', 156.525, None, 'Digital Selective Calling (DSC data - no voice)'),
    ('71', 156.575, None, 'Non-commercial (recreational)'),
    ('72', 156.625, None, 'Non-commercial (intership)'),
    ('73', 156.675, None, 'Port operations'),
    ('74', 156.725, None, 'Port operations'),
    ('77', 156.875, None, 'Port operations (intership)'),
    ('78A', 156.925, None, 'Non-commercial (recreational)'),
    ('79A', 156.975, None, 'Commercial (non-commercial Great Lakes only)'),
    ('80A', 157.025, None, 'Commercial (non-commercial Great Lakes only)'),
    ('81A', 157.075, None, 'US Government only (environmental protection)'),
    ('82A', 157.125, None, 'US Government only'),
    ('83A', 157.175, None, 'US Coast Guard only'),
    ('84', 157.225, 161.825, 'Public correspondence (marine operator)'),
    ('85', 157.275, 161.875, 'Public correspondence (marine operator)'),
    ('86', 157.325, 161.925, 'Public correspondence (marine operator)'),
    ('87A', 157.375, None, 'Commercial (intership)'),
    ('88A', 157.425, None, 'Commercial (intership)'),
    ('AIS1', 161.975, None, 'AIS ship tracking (ch 87B, data - no voice)'),
    ('AIS2', 162.025, None, 'AIS ship tracking (ch 88B, data - no voice)'),
]


def marine():
    src = 'https://www.navcen.uscg.gov/us-vhf-channel-information'
    out = []
    for ch, ship, coast, use in MARINE:
        notes = use
        if coast:
            notes += '; duplex - ship %.3f / coast %.3f (tuned: coast side)' % (ship, coast)
        data = 'data - no voice' in use
        out.append(E('Marine Ch %s' % ch, coast or ship, 'nfm', notes, src, channel=ch,
                     **({'digital': True} if data else {})))
    return out


GMRS_FREQS = ([462.5625 + 0.025 * i for i in range(7)] +      # ch 1-7
              [467.5625 + 0.025 * i for i in range(7)] +      # ch 8-14
              [462.550 + 0.025 * i for i in range(8)])        # ch 15-22


def gmrs():
    src = 'https://www.ecfr.gov/current/title-47/part-95/section-95.1763'
    out = []
    for n, f in enumerate(GMRS_FREQS, 1):
        if n <= 7:
            note = 'Shared with FRS 1-7; GMRS up to 5 W'
        elif n <= 14:
            note = 'Interstitial, 0.5 W max (shared with FRS 8-14)'
        else:
            note = 'GMRS main/repeater output; repeater input %.4f (+5 MHz)' % (f + 5.0)
        out.append(E('GMRS %d' % n, f, 'nfm', note, src, channel=str(n)))
    return out


def frs():
    src = 'https://www.ecfr.gov/current/title-47/part-95/section-95.563'
    out = []
    for n, f in enumerate(GMRS_FREQS, 1):
        note = '0.5 W max' if 8 <= n <= 14 else 'up to 2 W'
        out.append(E('FRS %d' % n, f, 'nfm', note + '; shared with GMRS %d' % n, src, channel=str(n)))
    return out


def murs():
    src = 'https://www.ecfr.gov/current/title-47/part-95/section-95.2763'
    plan = [(1, 151.820, '11.25 kHz narrowband'), (2, 151.880, '11.25 kHz narrowband'),
            (3, 151.940, '11.25 kHz narrowband'), (4, 154.570, '"Blue Dot" - 20 kHz allowed'),
            (5, 154.600, '"Green Dot" - 20 kHz allowed')]
    return [E('MURS %d' % n, f, 'nfm', note, src, channel=str(n)) for n, f, note in plan]


def railroad():
    # AAR channel plan, 15 kHz steps: AAR ch N = 160.110 + 0.015*N  (07 = 160.215 ... 97 = 161.565)
    src = 'https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-90 (AAR railroad channel plan)'
    out = []
    for n in range(7, 98):
        f = 160.110 + 0.015 * n
        out.append(E('AAR %02d' % n, f, 'nfm', 'Railroad road/yard channel', src, channel='%02d' % n))
    return out


CB = [26.965, 26.975, 26.985, 27.005, 27.015, 27.025, 27.035, 27.055, 27.065, 27.075,
      27.085, 27.105, 27.115, 27.125, 27.135, 27.155, 27.165, 27.175, 27.185, 27.205,
      27.215, 27.225, 27.255, 27.235, 27.245, 27.265, 27.275, 27.285, 27.295, 27.305,
      27.315, 27.325, 27.335, 27.345, 27.355, 27.365, 27.375, 27.385, 27.395, 27.405]


def cb():
    src = 'https://www.ecfr.gov/current/title-47/part-95/section-95.963'
    special = {9: 'Emergency & traveler assistance', 19: 'Highway / truckers',
               36: 'SSB common (radio decodes AM only)', 38: 'LSB calling (AM only here)'}
    return [E('CB %d' % n, f, 'am', special.get(n, 'Citizens Band AM') +
              '; HF - V4 uses its built-in upconverter below 28.8 MHz', src, channel=str(n))
            for n, f in enumerate(CB, 1)]


def ham():
    src = 'https://www.arrl.org/band-plan'
    rows = [
        ('2m National Simplex Calling', 146.520, 'nfm', 'National FM simplex calling frequency'),
        ('2m Simplex 146.550', 146.550, 'nfm', 'Common FM simplex'),
        ('2m Simplex 146.580', 146.580, 'nfm', 'Common FM simplex'),
        ('2m Simplex 146.460', 146.460, 'nfm', 'FM simplex (regional plans vary)'),
        ('2m Simplex 146.490', 146.490, 'nfm', 'FM simplex (regional plans vary)'),
        ('2m Simplex 147.420', 147.420, 'nfm', 'FM simplex (regional plans vary)'),
        ('2m Simplex 147.450', 147.450, 'nfm', 'FM simplex (regional plans vary)'),
        ('2m Simplex 147.480', 147.480, 'nfm', 'FM simplex (regional plans vary)'),
        ('2m Simplex 147.510', 147.510, 'nfm', 'FM simplex (regional plans vary)'),
        ('2m Simplex 147.540', 147.540, 'nfm', 'FM simplex (regional plans vary)'),
        ('2m APRS', 144.390, 'nfm', 'North American APRS packet (data bursts)'),
        ('ISS Voice Downlink', 145.800, 'nfm', 'International Space Station FM voice (passes only)'),
        ('70cm National Simplex Calling', 446.000, 'nfm', 'National FM simplex calling frequency'),
        ('70cm Simplex 446.500', 446.500, 'nfm', 'FM simplex (regional plans vary)'),
        ('6m FM Simplex Calling', 52.525, 'nfm', 'National 6m FM simplex calling'),
        ('1.25m FM Simplex Calling', 223.500, 'nfm', 'National 1.25m FM simplex calling'),
        ('10m FM Simplex Calling', 29.600, 'nfm', '10m FM calling (HF, via V4 upconverter)'),
    ]
    return [E(n, f, m, notes, src) for n, f, m, notes in rows]


def ism():
    src = 'https://github.com/merbanan/rtl_433'
    rows = [('315 MHz ISM', 315.000, '315M', 'US car key fobs, TPMS, garage remotes'),
            ('345 MHz', 345.000, None, 'Honeywell/2GIG security sensors (not a PiFlip rtl_433 band preset)'),
            ('433.92 MHz ISM', 433.920, '433.92M', 'Weather stations, remotes, sensors'),
            ('915 MHz ISM', 915.000, '915M', 'US ISM sensors, meters')]
    return [E(n, f, 'nfm', notes, src, route='rtl433', **({'band': b} if b else {}))
            for n, f, b, notes in rows]


def adsb():
    src = 'https://www.faa.gov/air_traffic/technology/adsb'
    return [E('ADS-B 1090ES', 1090.0, 'am', 'Aircraft transponders (Mode S/ADS-B). Decoding needs dump1090; '
              'opens the waterfall on the ADS-B band', src, route='waterfall', band='adsb', digital=True),
            E('UAT 978', 978.0, 'am', 'US general-aviation ADS-B (UAT). Decoding needs dump978; '
              'opens the waterfall', src, route='waterfall', band='adsb', digital=True)]


def wwv():
    src = 'https://www.nist.gov/pml/time-and-frequency-division/time-distribution/radio-station-wwv'
    rows = [(2.5, 'WWV (Fort Collins) + WWVH (Kauai)'), (5.0, 'WWV + WWVH'), (10.0, 'WWV + WWVH'),
            (15.0, 'WWV + WWVH'), (20.0, 'WWV only')]
    return [E('WWV %g MHz' % f, f, 'am', who + ' time signal; HF via V4 upconverter', src)
            for f, who in rows]


# ------------------------------------------------------------------ Tier 2
DIGITAL_NOTE = 'needs trunk-tracking (not tunable with rtl_fm)'


def local():
    d = json.loads(LOCAL.read_text())
    reps = []
    for r in sorted(d['ham_repeaters'], key=lambda x: x['freqMHz']):
        off = r.get('offsetMHz')
        extra = 'Output %.4f' % r['freqMHz']
        if off is not None:
            extra += ', offset %+g MHz (input %.4f)' % (off, r['freqMHz'] + off)
        if r.get('pl'):
            extra += ', tone %s' % r['pl']
        reps.append(E(r['name'], r['freqMHz'], 'nfm', extra + '. ' + r.get('notes', ''), r['source'],
                      callsign=r.get('callsign'), location=r.get('location'),
                      offsetMHz=off, pl=r.get('pl')))
    fm = [E(x['name'], x['freqMHz'], 'wfm', x.get('notes', ''), x['source'], callsign=x.get('callsign'))
          for x in sorted(d['fm_broadcast'], key=lambda x: x['freqMHz'])]
    air = [E(x['name'], x['freqMHz'], 'am', x.get('notes', ''), x['source'], airport=x.get('airport'))
           for x in d['airband']]
    ps = []
    for x in d['public_safety']:
        dig = bool(x.get('digital')) or x.get('freqMHz') is None or x.get('mode') not in ('nfm', 'am', 'wfm')
        notes = x.get('notes', '')
        if dig and DIGITAL_NOTE not in notes:
            notes = (notes + '; ' + DIGITAL_NOTE).strip('; ')
        e = E(x['name'], x.get('freqMHz'), x.get('mode') if not dig else 'nfm', notes, x['source'])
        if dig:
            e['digital'] = True
            e['mode_raw'] = x.get('mode')
        ps.append(e)
    ps.sort(key=lambda e: (e.get('digital', False), e['freqMHz'] or 0))
    return reps, fm, air, ps, d.get('sources', []), d.get('gaps', '')


def main():
    reps, fm, air, ps, sources, gaps = local()
    types = [
        ('noaa', 'NOAA Weather', '🌦️', 1, noaa()),
        ('marine', 'Marine VHF', '⚓', 1, marine()),
        ('gmrs', 'GMRS', '📟', 1, gmrs()),
        ('frs', 'FRS', '🎙️', 1, frs()),
        ('murs', 'MURS', '📻', 1, murs()),
        ('railroad', 'Railroad (AAR)', '🚂', 1, railroad()),
        ('cb', 'CB Radio', '🚚', 1, cb()),
        ('ham', 'Ham Calling / Simplex', '📡', 1, ham()),
        ('ism', 'rtl_433 ISM Sensors', '🌡️', 1, ism()),
        ('adsb', 'ADS-B / UAT', '✈️', 1, adsb()),
        ('wwv', 'WWV / WWVH Time', '⏱️', 1, wwv()),
        ('local_repeaters', 'Cincinnati Ham Repeaters', '🗼', 2, reps),
        ('local_fm', 'Cincinnati FM Stations', '🎵', 2, fm),
        ('local_air', 'CVG + Lunken Airband', '🛫', 2, air),
        ('local_ps', 'Hamilton Co. Public Safety', '🚓', 2, ps),
    ]
    out = {'version': 1,
           'description': 'PiFlip offline frequency catalog. Tier 1 = standardized US channel plans; '
                          'Tier 2 = Cincinnati/Hamilton County OH from cited public sources (see SOURCES.md).',
           'local_sources': sources, 'local_gaps': gaps,
           'types': [{'id': i, 'name': n, 'icon': ic, 'tier': t, 'count': len(es), 'entries': es}
                     for i, n, ic, t, es in types]}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    for t in out['types']:
        print('%-16s %3d' % (t['id'], t['count']))


if __name__ == '__main__':
    main()
