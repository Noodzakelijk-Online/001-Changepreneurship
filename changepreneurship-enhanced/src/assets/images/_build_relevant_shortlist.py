import json
from pathlib import Path

base = Path(r"E:/GIT/001-Changepreneurship/changepreneurship-enhanced/src/assets/images/recording_2026_02_24_225733_keyframes")
manifest = json.loads((base / "keyframes_manifest.json").read_text(encoding="utf-8"))
frames = manifest["frames"]

# top by visual change
by_change = sorted(frames[1:], key=lambda x: x["mad_from_prev"], reverse=True)
top_change = by_change[:20]

# evenly sampled coverage
n = len(frames)
idxs = sorted(set(int(i * (n - 1) / 19) for i in range(20)))
coverage = [frames[i] for i in idxs]

# merged shortlist
merged = {}
for item in coverage + top_change:
    merged[item["order"]] = item
shortlist = [merged[k] for k in sorted(merged.keys())]

out = {
    "total_selected_frames": len(frames),
    "shortlist_count": len(shortlist),
    "shortlist": shortlist
}

(base / "relevant_frames_shortlist.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"shortlist_count={len(shortlist)}")
print(base / "relevant_frames_shortlist.json")
