import subprocess, pathlib, sys

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = pathlib.Path(sys.argv[1])
BASE = "http://localhost:4310/"
OUT.mkdir(parents=True, exist_ok=True)

# desktop: real 1440 window, one section per shot via ?only=
D = {"top": 900, "before-after": 1050, "scan": 1000, "tour": 1500, "lane": 710, "docs": 890,
     "who": 840, "price": 690, "faq": 640, "cta": 680}
# mobile: headless Chrome can't lay out narrower than ~500px, so the page is
# rendered inside a 390px iframe zoomed 2x (_frame.html) -> 780px-wide, retina-sharp image
M = {"top": 1180, "before-after": 860, "scan": 1270, "tour": 3290, "lane": 990, "docs": 760,
     "who": 820, "price": 1840, "faq": 970, "cta": 760}

jobs = [("desktop-00-full-page", "1440,10200", BASE + "showroom-v2.html")]
for i, sec in enumerate(D, 1):
    jobs.append((f"desktop-{i:02d}-{sec}", f"1440,{D[sec]}", BASE + "showroom-v2.html?only=" + sec))
jobs.append(("mobile-00-full-page", "780,26240", BASE + "_frame.html?h=13120"))
for i, sec in enumerate(M, 1):
    jobs.append((f"mobile-{i:02d}-{sec}", f"780,{M[sec]*2}", BASE + f"_frame.html?only={sec}&h={M[sec]}"))

only = set(sys.argv[2:])
for name, size, url in jobs:
    if only and not any(o in name for o in only):
        continue
    target = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={size}", "--virtual-time-budget=7000",
                    f"--screenshot={target}", url], capture_output=True, timeout=180)
    print(name, target.stat().st_size if target.exists() else "MISSING")
