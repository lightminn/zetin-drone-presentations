#!/usr/bin/env python3
"""오늘(2026-10-30) 테더 비행 로그에서 비행별 위치 유지 지표를 뽑아 poshold_stats.json 으로 저장한다.
사용: make_poshold_stats.py <logs 폴더> <출력 json>"""
import csv, glob, json, math, sys
f = lambda x: float(x) if x not in ('', None) else None
out = []
for fn in sorted(glob.glob(sys.argv[1] + '/flight_log_2026-10-30_*.csv')):
    r = list(csv.DictReader(open(fn)))
    air = [x for x in r if x['Armed'] == '1' and f(x['Range_MM']) and f(x['Range_MM']) > 400 and f(x['Flow_Vel_R']) is not None]
    if len(air) < 400:
        continue
    sp = lambda x: math.hypot(f(x['Flow_Vel_R']), f(x['Flow_Vel_P']))
    rms = lambda xs: math.sqrt(sum(sp(x) ** 2 for x in xs) / len(xs)) if xs else None
    act = [x for x in air if x['PosHold_State'] == '1']
    non = [x for x in air if x['PosHold_State'] != '1']
    runs, cur = [], 0
    for x in r:
        if x['PosHold_State'] == '1' and x['Armed'] == '1':
            cur += 1
        else:
            runs.append(cur); cur = 0
    runs.append(cur)
    t = fn.split('_')[-1][:4]
    out.append({'time': t[:2] + ':' + t[2:], 'air_s': round(len(air) / 20), 'longest_active_s': round(max(runs) / 20, 1),
                'rms_active': None if not act else round(rms(act), 3), 'rms_other': round(rms(non), 3), 'rms_all': round(rms(air), 3)})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
for o in out: print(o)
