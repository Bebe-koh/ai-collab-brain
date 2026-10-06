#!/usr/bin/env python3
"""Parse Dong et al. 2026 (arXiv:2511.15134) LaTeX tables + psrcat F0,
compute effective mutual-friction parameters B_eff = 1/(2*Omega*tau)."""
import re, math, csv, os

Q2 = os.path.expanduser("~/workspace/superfluid-vacuum/q2_work")
EP = os.path.join(Q2, "eprint")

def clean_psr(s):
    s = s.replace("$-$", "-").replace("$+$", "+")
    s = re.sub(r"\^\{\\rm [^}]*\}", "", s)   # ^{\rm g}
    s = re.sub(r"\^\*", "", s)               # ^*
    s = re.sub(r"\\dagger", "", s)
    s = s.replace("$", "").replace("*", "").strip()
    return s

# ---------- 1. psrcat.db -> F0 ----------
f0 = {}
cur = None
with open(os.path.join(Q2, "psrcat_tar", "psrcat.db")) as fh:
    for line in fh:
        if line.startswith("PSRJ"):
            cur = line[6:20].strip()
        elif line.startswith("F0") and cur and cur not in f0:
            try:
                f0[cur] = float(line[6:30].split()[0])
            except Exception:
                pass
        elif line.startswith("P0") and cur and cur not in f0:
            try:
                f0[cur] = 1.0 / float(line[6:30].split()[0])
            except Exception:
                pass
        elif line.startswith("@---"):
            cur = None

# ---------- 2. Tables B1-B3 ----------
def parse_val(s):
    s = s.strip().strip("$")
    m = re.match(r"([+-]?[\d.]+)\^\{\+([\d.]+)\}_\{-(.*?)\}$", s)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3).rstrip("}"))
    m2 = re.match(r"([+-]?[\d.]+)$", s)
    if m2:
        return float(m2.group(1)), 0.0, 0.0
    return None

rows = []
for fn in ["model_comparison_canonical.tex", "model_comparison_msp.tex",
           "model_comparison_magnetar.tex"]:
    with open(os.path.join(EP, "papertabs", fn)) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(("\\", "%")) or "&" not in line:
                continue
            parts = [p.strip() for p in line.split("&")]
            if len(parts) < 9:
                continue
            name = clean_psr(parts[0])
            if not re.match(r"^J?\d{4}[-+]\d{3,4}", name):
                continue
            if not name.startswith("J"):
                name = "J" + name
            try:
                lnbf = float(parts[2])
            except Exception:
                continue
            v = parse_val(parts[3])
            if v is None:
                continue
            rows.append(dict(psr=name, model=parts[1], lnbf=lnbf,
                             logtau=v[0], logtau_up=v[1], logtau_lo=v[2],
                             peaky=parts[4].strip(), table=fn))

sel = [r for r in rows if r["model"] == "2C" and r["lnbf"] >= 5.0]
print(f"total rows: {len(rows)}, lnBF>=5: {len(sel)}")
from collections import Counter
print("models:", Counter(r["model"] for r in sel))
print("peaky:", Counter(r["peaky"] for r in sel))
missing = sorted(set(r["psr"] for r in sel if r["psr"] not in f0))
print(f"missing F0: {len(missing)} {missing}")

def beff_from_logtau(logtau, nu):
    return -math.log10(2 * math.pi * nu) - logtau

with open(os.path.join(Q2, "dong105_tau.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["psr", "F0_Hz", "model", "lnBF", "peaky",
                "log10_tau_s", "log10_tau_up", "log10_tau_lo",
                "log10_Beff_upperbound", "note"])
    for r in sel:
        nu = f0.get(r["psr"])
        logB = round(beff_from_logtau(r["logtau"], nu), 3) if nu else ""
        w.writerow([r["psr"], round(nu, 6) if nu else "", r["model"], r["lnbf"],
                    r["peaky"], r["logtau"], r["logtau_up"], r["logtau_lo"],
                    logB,
                    "B_eff=1/(2 pi nu tau): UPPER BOUND on B_mf (tau>=tau_s; pinning ignored)"])

# ---------- 3. glitched_pulsars.tex ----------
def parse_vg(s):
    s = s.strip()
    s = re.sub(r"^\\multirow\{\d+\}\{\*\}\{", "", s)
    if s.endswith("}"):
        # remove the multirow closing brace only if it wraps the value
        inner = s[:-1]
        if inner.startswith("$") and inner.endswith("$"):
            s = inner
    m = re.match(r"\$([+-]?[\d.]+)\^\{\+([\d.]+)\}_\{-(.*?)\}\$", s)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3))
    return None

gevents = []
cur = {}
with open(os.path.join(EP, "papertabs", "glitched_pulsars.tex")) as fh:
    for raw in fh:
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        if "multirow" in line and line.lstrip().startswith("\\hline"):
            m = re.search(r"\\multirow\{\d+\}\{\*\}\{(.+?)\}", line)
            if m:
                cur = {"psr": clean_psr(m.group(1))}
                if not cur["psr"].startswith("J"):
                    cur["psr"] = "J" + cur["psr"]
            parts = [p.strip() for p in line.split("&")]
            vals = [v for v in (parse_vg(p) for p in parts) if v]
            if len(vals) >= 2:
                cur["logtau_tn"] = vals[0][0]
                cur["logx_tn"] = vals[1][0]
            # the header line ALSO carries the first glitch event
            ep = next((p for p in parts if re.match(r"^\d{5}(\.\d+)?\(\d+\)$", p)), None)
            refs = re.findall(r"\\citet\{([^}]+)\}", line)
            if ep and len(vals) >= 4:
                gevents.append(dict(psr=cur["psr"], epoch=ep,
                                    logtau_tn=cur["logtau_tn"],
                                    logx_tn=cur["logx_tn"],
                                    logtau_g=vals[-2][0], logtau_g_up=vals[-2][1],
                                    logtau_g_lo=vals[-2][2],
                                    logq=vals[-1][0], logq_up=vals[-1][1],
                                    logq_lo=vals[-1][2],
                                    ref=";".join(refs)))
            continue
        elif "&" in line and cur.get("psr"):
            parts = [p.strip() for p in line.split("&")]
            ep = next((p for p in parts if re.match(r"^\d{5}(\.\d+)?\(\d+\)$", p)), None)
            vals = [parse_vg(p) for p in parts]
            vals = [v for v in vals if v]
            refs = re.findall(r"\\citet\{([^}]+)\}", line)
            if ep and len(vals) >= 2:
                gevents.append(dict(psr=cur["psr"], epoch=ep,
                                    logtau_tn=cur.get("logtau_tn"),
                                    logx_tn=cur.get("logx_tn"),
                                    logtau_g=vals[-2][0], logtau_g_up=vals[-2][1],
                                    logtau_g_lo=vals[-2][2],
                                    logq=vals[-1][0], logq_up=vals[-1][1],
                                    logq_lo=vals[-1][2],
                                    ref=";".join(refs)))

print(f"glitch events: {len(gevents)}")
for e in gevents:
    print(e["psr"], e["epoch"], "logtau_g=", e["logtau_g"], "logq=", e["logq"],
          "F0=", round(f0.get(e["psr"], -1), 4), e["ref"][:45])

with open(os.path.join(Q2, "dong5_glitch.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["psr", "F0_Hz", "epoch_mjd", "log10_tau_g_s", "tau_g_days",
                "log10_q_heal", "log10_tau_TN_s", "log10_x_TN",
                "log10_B_mf", "B_note", "ref"])
    for e in gevents:
        nu = f0.get(e["psr"])
        tau_g = 10 ** e["logtau_g"]
        q = 10 ** e["logq"]
        if nu:
            # tau_g^-1 = (1+Is/Ic) tau_s^-1 ; q_heal = Is/(Is+Ic)  ->  tau_s = tau_g/(1-q_heal)
            # B_mf = 1/(2 pi nu tau_s) = (1-q_heal)/(2 pi nu tau_g)
            logB = round(math.log10((1 - q) / (2 * math.pi * nu * tau_g)), 3)
            note = "B_mf=(1-q_heal)/(2 pi nu tau_g); 2-fluid (Baym+1969/Alpar+1993); q_heal=Is/(Is+Ic) assumed"
        else:
            logB, note = "", "no F0"
        w.writerow([e["psr"], round(nu, 6) if nu else "", e["epoch"],
                    e["logtau_g"], round(tau_g / 86400, 1), e["logq"],
                    round(e["logtau_tn"], 2) if e["logtau_tn"] else "",
                    round(e["logx_tn"], 3) if e["logx_tn"] is not None else "",
                    logB, note, e["ref"]])
print("done")
