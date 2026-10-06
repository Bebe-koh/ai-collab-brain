"""Parse Greiner's GRB table (grbgen.html) into a catalog CSV.

Columns: name, ra_deg, dec_deg, z_raw, z (float or NaN), z_flag
Provenance: https://www.mpe.mpg.de/~jcg/grbgen.html downloaded 2026-09-24.
"""
import re, math, csv, html as htmlmod

html = open('/home/hatch/workspace/grb/grbgen.html', encoding='utf-8', errors='replace').read()
rows = re.findall(r'<TR VALIGN="TOP">(.*?)(?=<TR VALIGN="TOP">|$)', html, re.S | re.I)
print('candidate rows:', len(rows))

def strip_tags(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = htmlmod.unescape(s)
    return s.strip()

out = []
skipped = 0
for r in rows:
    tds = re.findall(r'<TD[^>]*>(.*?)</TD>', r, re.S | re.I)
    if len(tds) < 10:
        continue
    name_m = re.search(r'>([^<>]+)</a>', tds[0])
    name = name_m.group(1).strip() if name_m else strip_tags(tds[0])
    if not re.match(r'^[0-9]{6}[A-Za-z]*$', name):
        skipped += 1
        continue
    pos = strip_tags(tds[1])
    # expect like: 21 h 53 m 03 s +12 deg 49'
    m = re.search(r'(\d+)\s*h\s*(\d+)\s*m\s*([\d.]+)\s*s\s*([+-])\s*(\d+)\s*[°\u00b0]\s*([\d.]+)', pos)
    if not m:
        skipped += 1
        continue
    rah, ram, ras = int(m.group(1)), int(m.group(2)), float(m.group(3))
    dsign = -1 if m.group(4) == '-' else 1
    dd, dm = int(m.group(5)), float(m.group(6))
    if ram >= 60 or ras >= 60 or dm >= 60:
        skipped += 1
        continue
    ra = (rah + ram/60 + ras/3600) * 15.0
    dec = dsign * (dd + dm/60)
    z_raw = strip_tags(tds[9])
    zm = re.search(r'([\d.]+)', z_raw)
    z = float(zm.group(1)) if zm else float('nan')
    flag = 'clean' if re.fullmatch(r'[\d.]+', z_raw) else ('none' if not z_raw else 'qualified:' + z_raw)
    out.append((name, ra, dec, z_raw, z, flag))

print('parsed:', len(out), 'skipped:', skipped)
with open('/home/hatch/workspace/grb/grb_catalog_greiner.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['name', 'ra_deg', 'dec_deg', 'z_raw', 'z', 'z_flag'])
    w.writerows(out)

nz = sum(1 for r in out if not math.isnan(r[4]))
nbin = sum(1 for r in out if not math.isnan(r[4]) and 1.6 <= r[4] <= 2.1)
print('total rows:', len(out), '| with z:', nz, '| z in [1.6,2.1]:', nbin)
