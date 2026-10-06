"""Retry failed NICER downloads and repair partial/corrupt files.

The main download script counts a partial file (>100 kB) as 'skip' forever,
and logs failures to data/download.log. This script:
  1. reads obsids.csv (full pilot list),
  2. for each obsid checks the .evt.gz and .orb.gz exist AND are valid gzip,
  3. re-downloads missing/corrupt files with backoff.
Run after the main download finishes.
"""
import os, sys, time, csv, gzip, urllib.request, datetime

OUT = "/home/hatch/workspace/prtp/hidden_files/nicer_pilot/data"
PILOT = "/home/hatch/workspace/prtp/hidden_files/nicer_pilot"


def mjd_to_datedir(mjd):
    d = datetime.date(1858, 11, 17) + datetime.timedelta(days=float(mjd))
    return f"{d.year:04d}_{d.month:02d}"


def valid_gz(path, min_size=100000, check_events=False):
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        return False
    try:
        with gzip.open(path, "rb") as f:
            # read first and last chunks to catch truncation
            f.read(1 << 20)
            try:
                f.seek(-65536, 2)
                f.read()
            except OSError:
                pass  # file smaller than 64k; head read already validates
        if check_events:
            # must be a readable FITS with EVENTS/TIME/PI (not just valid gzip)
            from astropy.io import fits
            with fits.open(path) as h:
                d = h['EVENTS'].data
                _ = d['TIME'][:1], d['PI'][:1]
        elif os.path.getsize(path) < min_size:
            return False
        return True
    except Exception:
        return False


def fetch(url, dest):
    for attempt in range(5):
        try:
            if os.path.exists(dest):
                os.remove(dest)
            req = urllib.request.Request(
                url, headers={"User-Agent": "PRTP-pilot/1.0-retry"})
            with urllib.request.urlopen(req, timeout=180) as r, \
                    open(dest, "wb") as f:
                n = 0
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    n += len(chunk)
            is_evt = dest.endswith('.evt.gz')
            if (not is_evt and n < 50000) or \
               not valid_gz(dest, check_events=is_evt):
                continue
            return True
        except Exception as e:
            print(f"    attempt {attempt+1} failed: {str(e)[:100]}",
                  flush=True)
            time.sleep(5 * (attempt + 1))
    return False


def main():
    jobs = []
    with open(PILOT + "/obsids.csv") as f:
        for r in csv.DictReader(f):
            jobs.append((r["psr"], r["obsid"], float(r["mjd"])))
    n_fix = n_ok = 0
    for i, (psr, obsid, mjd) in enumerate(jobs):
        dd = mjd_to_datedir(mjd)
        base = f"https://heasarc.gsfc.nasa.gov/FTP/nicer/data/obs/{dd}/{obsid}"
        ddir = os.path.join(OUT, obsid)
        os.makedirs(ddir, exist_ok=True)
        need = []
        ev = os.path.join(ddir, f"ni{obsid}_0mpu7_cl.evt.gz")
        ob = os.path.join(ddir, f"ni{obsid}.orb.gz")
        if not valid_gz(ev, check_events=True):
            need.append((f"{base}/xti/event_cl/ni{obsid}_0mpu7_cl.evt.gz", ev))
        if not valid_gz(ob, min_size=50000):
            need.append((f"{base}/auxil/ni{obsid}.orb.gz", ob))
        if not need:
            n_ok += 1
            continue
        for url, dest in need:
            ok = fetch(url, dest)
            print(f"  {obsid} {os.path.basename(dest)}: {'OK' if ok else 'FAIL'}",
                  flush=True)
            n_fix += ok
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(jobs)} already-ok={n_ok} repaired={n_fix}",
                  flush=True)
    print(f"DONE already-ok={n_ok} repaired={n_fix}", flush=True)


if __name__ == "__main__":
    main()
