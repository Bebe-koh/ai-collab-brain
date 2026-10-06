"""Parallel retry for NICER downloads. Prioritizes .orb files (small, fast,
critical for PINT) then missing/corrupt .evt files. Uses threads.
"""
import os, sys, csv, gzip, time, urllib.request, datetime
from concurrent.futures import ThreadPoolExecutor

OUT = "/home/hatch/workspace/prtp/hidden_files/nicer_pilot/data"
PILOT = "/home/hatch/workspace/prtp/hidden_files/nicer_pilot"
NTHREADS = 8


def mjd_to_datedir(mjd):
    d = datetime.date(1858, 11, 17) + datetime.timedelta(days=float(mjd))
    return f"{d.year:04d}_{d.month:02d}"


def valid_orb(path):
    return os.path.exists(path) and os.path.getsize(path) > 50000


def valid_evt(path):
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        return False
    try:
        with gzip.open(path, "rb") as f:
            f.read(1 << 20)
        return True
    except Exception:
        return False


def fetch(url, dest):
    for attempt in range(4):
        try:
            tmp = dest + '.tmp'
            req = urllib.request.Request(
                url, headers={"User-Agent": "PRTP-pilot/1.0-pretry"})
            with urllib.request.urlopen(req, timeout=120) as r, \
                    open(tmp, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            os.rename(tmp, dest)
            return True
        except Exception:
            time.sleep(3 * (attempt + 1))
    return False


def job_orb(args):
    obsid, mjd, base = args
    dest = os.path.join(OUT, obsid, f"ni{obsid}.orb.gz")
    if valid_orb(dest) or valid_orb(dest[:-3]):
        return (obsid, 'ok')
    ok = fetch(f"{base}/auxil/ni{obsid}.orb.gz", dest)
    if ok and not valid_orb(dest):
        ok = False
    return (obsid, 'ok' if ok else 'fail')


def job_evt(args):
    obsid, mjd, base = args
    dest = os.path.join(OUT, obsid, f"ni{obsid}_0mpu7_cl.evt.gz")
    if valid_evt(dest) or valid_evt(dest[:-3]):
        return (obsid, 'ok')
    ok = fetch(f"{base}/xti/event_cl/ni{obsid}_0mpu7_cl.evt.gz", dest)
    if ok and not valid_evt(dest):
        ok = False
    return (obsid, 'ok' if ok else 'fail')


def main():
    jobs = []
    with open(PILOT + "/obsids.csv") as f:
        for r in csv.DictReader(f):
            obsid, mjd = r['obsid'], float(r['mjd'])
            dd = mjd_to_datedir(mjd)
            base = f"https://heasarc.gsfc.nasa.gov/FTP/nicer/data/obs/{dd}/{obsid}"
            ddir = os.path.join(OUT, obsid)
            os.makedirs(ddir, exist_ok=True)
            jobs.append((obsid, mjd, base))
    print(f"{len(jobs)} obsids; phase 1: orb files", flush=True)
    with ThreadPoolExecutor(max_workers=NTHREADS) as ex:
        res = list(ex.map(job_orb, jobs))
    n_ok = sum(1 for _, s in res if s == 'ok')
    print(f"orb phase: {n_ok}/{len(jobs)} ok", flush=True)
    print("phase 2: evt files", flush=True)
    with ThreadPoolExecutor(max_workers=NTHREADS) as ex:
        res = list(ex.map(job_evt, jobs))
    n_ok = sum(1 for _, s in res if s == 'ok')
    print(f"evt phase: {n_ok}/{len(jobs)} ok", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
