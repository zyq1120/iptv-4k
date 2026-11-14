# iptv-4k

Verified high-resolution IPTV channels only: 3840×2160 true 4K, plus 2560×1440
(1440p, approved by the user 2026-11-14). A channel is listed here only if
ffprobe actually reads a >=2560-wide video stream from it. Channels whose name
says 4K but whose stream is 1080p/720p are NOT listed (e.g. the CCTV-4K official
feed currently resolves to 1080p, and the CCTV-4K auth_key feeds expire).

## Aptv usage (aggregated config)

Add this file as a separate ordinary config in Aptv, then include it in an
Aggregated config together with your main playlist. Put the 4K config FIRST
in the aggregated order, so the 4K line becomes the default line for that
channel. Channel names match the main playlist (湖南卫视, 河北卫视), so Aptv
merges them by name; 苏州4K and Eleven Sports 1 4K PL appear as new channels.

Subscription URL (raw, always latest):

```
https://raw.githubusercontent.com/zyq1120/iptv-4k/main/4k.m3u
```

## Channels

- 湖南卫视 — 3840×2160, mgtv signed URL (may expire; maintenance re-sources it from upstream lists)
- 河北卫视 — 3840×2160, hebtv live101 (unsigned http, most stable)
- 苏州4K — 3840×2160, tylive kan0512 (intermittent in earlier tests)
- Eurosport 4K Czechia — 2560×1440, verified 2026-11-14
- Travelxp 4K Czechia — 2560×1440, verified 2026-11-14

Removed: Eleven Sports 1 4K PL (source 404, no upstream replacement, 2026-11-02).

## Maintenance

`scripts/update_4k.py` re-downloads the upstream lists (Collect-IPTV,
suxuang, ding, iptv-org index), re-runs ffprobe on all 4K-named candidates,
and rebuilds `4k.m3u` with only true 3840-wide streams. It is run daily by
a scheduled job; if a signed URL dies, the script tries to replace it from
a fresh upstream copy before dropping the channel. The job does not
regenerate broadcaster signatures from scratch — no public API for that
exists — it re-sources them from upstream lists that refresh them.
