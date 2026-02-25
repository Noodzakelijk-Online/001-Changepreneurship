import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageSequence

gif_path = Path(r"E:/GIT/001-Changepreneurship/changepreneurship-enhanced/src/assets/images/Recording 2026-02-24 225733.gif")
out_dir = gif_path.parent / "recording_2026_02_24_225733_keyframes"
out_dir.mkdir(parents=True, exist_ok=True)

img = Image.open(gif_path)
durations = []
mad = [0.0]

prev = None
total_frames = 0
for frame in ImageSequence.Iterator(img):
    curr = np.asarray(frame.convert("RGB"), dtype=np.uint8)
    durations.append(int(frame.info.get("duration", img.info.get("duration", 100))))
    if prev is not None:
        diff = np.abs(curr.astype(np.int16) - prev.astype(np.int16)).mean()
        mad.append(float(diff))
    prev = curr
    total_frames += 1

if total_frames == 0:
    raise RuntimeError("No frames found in GIF")

arr_mad = np.asarray(mad[1:] or [0.0], dtype=np.float32)
threshold = float(max(5.0, float(arr_mad.mean() + 1.25 * arr_mad.std())))

selected = [0]
last = 0
for i in range(1, total_frames):
    if i - last < 5:
        continue
    if mad[i] >= threshold:
        selected.append(i)
        last = i
if selected[-1] != total_frames - 1:
    selected.append(total_frames - 1)

if len(selected) < 30 and total_frames > 1:
    evenly = np.linspace(0, total_frames - 1, 30, dtype=int).tolist()
    selected = sorted(set(selected + evenly))

cum_ms = [0]
for d in durations[:-1]:
    cum_ms.append(cum_ms[-1] + d)

manifest = {
    "gif": str(gif_path),
    "total_frames": total_frames,
    "selected_count": len(selected),
    "threshold": threshold,
    "frames": []
}

# Save only selected frames via a second pass (memory-safe)
selected_lookup = {idx: pos + 1 for pos, idx in enumerate(selected)}
saved_paths = []
for idx, frame in enumerate(ImageSequence.Iterator(Image.open(gif_path))):
    if idx not in selected_lookup:
        continue
    order = selected_lookup[idx]
    filename = f"frame_{order:03d}_idx_{idx:04d}.png"
    out_file = out_dir / filename
    frame.convert("RGB").save(out_file)
    saved_paths.append(out_file)
    manifest["frames"].append({
        "order": order,
        "frame_index": int(idx),
        "timestamp_ms": int(cum_ms[idx]),
        "mad_from_prev": float(mad[idx]),
        "file": filename
    })

manifest["frames"].sort(key=lambda f: f["order"])

(out_dir / "keyframes_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

# quick contact sheet
thumb_w, thumb_h, cols = 320, 180, 5
rows = int(np.ceil(len(selected) / cols))
sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (18, 18, 18))
for i, frame_path in enumerate(sorted(saved_paths)):
    r, c = divmod(i, cols)
    thumb = Image.open(frame_path).convert("RGB").resize((thumb_w, thumb_h))
    sheet.paste(thumb, (c * thumb_w, r * thumb_h))
sheet.save(out_dir / "keyframes_contact_sheet.jpg", quality=90)

print(out_dir)
print(total_frames, len(selected), threshold)
