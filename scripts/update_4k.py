"""Daily 4K maintenance: re-probe the known 4K URLs, and if one dies,
try to replace it from fresh upstream lists. Keeps only 3840-wide streams.
Run from the repo root: python3 scripts/update_4k.py
"""
import subprocess, re, json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM = [
    "https://raw.githubusercontent.com/zilong7728/Collect-IPTV/main/best_sorted.m3u8",
    "https://raw.githubusercontent.com/suxuang/myIPTV/main/ipv4.m3u",
    "https://raw.githubusercontent.com/xiaomayi0804/ding/main/MTV.m3u8",
    "https://iptv-org.github.io/iptv/index.m3u",
]
def ffprobe_width(url):
    try:
        p = subprocess.run(["timeout", "20", "ffprobe", "-v", "error",
            "-show_entries", "stream=width", "-of", "default=noprint_wrappers=1", url],
            capture_output=True, text=True, timeout=25)
        w = [int(x) for x in re.findall(r'width=(\d+)', p.stdout)]
        return max(w) if w else 0
    except Exception:
        return 0
def parse_m3u(path):
    out = []; ext = None
    for line in open(path, encoding='utf-8', errors='ignore'):
        line = line.strip()
        if line.startswith('#EXTINF'): ext = line
        elif line.startswith('http') and ext:
            out.append((ext.rsplit(',', 1)[-1].strip(), line)); ext = None
    return out
def main():
    cur = parse_m3u(os.path.join(REPO, "4k.m3u"))
    kept = []
    for name, url in cur:
        w = ffprobe_width(url)
        print(name, w, url[:100], flush=True)
        if w >= 3840:
            kept.append((name, url))
    print(f"kept {len(kept)}/{len(cur)}")
    if len(kept) == len(cur):
        return 0
    # try replacements from upstream for dropped channels
    for name, url in cur:
        if any(n == name for n, _ in kept):
            continue
        print(f"trying replacement for {name}", flush=True)
        for i, src in enumerate(UPSTREAM):
            tmp = f"/tmp/upstream-{i}.m3u"
            subprocess.run(["curl", "-L", "-s", "--max-time", "60", "-o", tmp, src])
            for n2, u2 in parse_m3u(tmp):
                if n2 == name or (name in n2 and '4K' in n2):
                    if ffprobe_width(u2) >= 3840:
                        kept.append((name, u2)); print(f"replaced {name} -> {u2[:100]}", flush=True); break
            else:
                continue
            break
    # rebuild preserving original order, with kept entries only
    order = [n for n, _ in cur]
    kept_map = dict(kept)
    out = ["#EXTM3U x-tvg-url=\"https://iptv-org.github.io/epg.xml\""]
    # reuse original EXTINF lines where possible
    ext_map = {}
    for line in open(os.path.join(REPO, "4k.m3u"), encoding='utf-8'):
        if line.startswith('#EXTINF'):
            ext_map[line.rsplit(',', 1)[-1].strip()] = line.strip()
    for name in order:
        if name in kept_map:
            out.append(ext_map.get(name, f'#EXTINF:-1 tvg-name="{name}",{name}'))
            out.append(kept_map[name])
    open(os.path.join(REPO, "4k.m3u"), "w", encoding='utf-8').write("\n".join(out) + "\n")
    return 0
if __name__ == "__main__":
    sys.exit(main())
