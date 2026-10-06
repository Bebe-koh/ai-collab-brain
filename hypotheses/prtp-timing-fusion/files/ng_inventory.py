"""Step 1: inventory the extracted NANOGrav 15yr files for the 4 anchor pulsars."""
import os, glob, sys

base = os.path.expanduser("~/workspace/prtp/hidden_files/nanograv15yr")
# find extracted top dir
tops = [d for d in glob.glob(os.path.join(base, "*")) if os.path.isdir(d)]
print("top-level dirs:", tops)

anchors = {
    "J0437-4715": ["J0437-4715", "J0437+4715"],
    "J1909-3744": ["J1909-3744"],
    "B1937+21": ["B1937+21", "J1939+2134"],
    "B1855+09": ["B1855+09", "J1857+0943"],
}

for canon, aliases in anchors.items():
    found = []
    for alias in aliases:
        for ext in ("par", "tim"):
            hits = glob.glob(os.path.join(base, "**", f"*{alias}*.{ext}"), recursive=True)
            found.extend(hits)
    print(f"\n{canon}: {len(found)} files")
    for f in sorted(set(found))[:8]:
        print("   ", os.path.relpath(f, base), f"{os.path.getsize(f)/1e6:.1f} MB")
