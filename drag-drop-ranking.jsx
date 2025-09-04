// drag-drop-ranking.jsx
// "use client";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import { GripVertical, ArrowUp, ArrowDown, CheckCircle } from "lucide-react";

/**
 * DragDropRanking
 * props:
 *  - options: [{ value: string, label: string }]
 *  - value:   array of:
 *      * ["v1","v2"...] atau
 *      * [{ value, label?, rank? }, ...]
 *  - onChange: (formattedRankings) => void
 *      formattedRankings: [{ value, label, rank }, ...]
 *  - maxRankings?: number | null
 */
const DragDropRanking = ({
  options = [],
  value = [],
  onChange,
  maxRankings = null,
}) => {
  // Peta cepat value -> option
  const optionMap = useMemo(() => {
    const m = new Map();
    options.forEach((o) => m.set(o.value, o));
    return m;
  }, [options]);

  // Normalisasi value dari props jadi array nilai ["v1","v2"...] sesuai urutan
  const normalizedIncoming = useMemo(() => {
    if (!Array.isArray(value)) return [];
    // jika datangnya objek {value, rank}, urutkan dulu
    if (value.length && typeof value[0] === "object") {
      const sorted = [...value].sort((a, b) => (a.rank || 0) - (b.rank || 0));
      return sorted.map((x) => x.value).filter((v) => optionMap.has(v));
    }
    // jika sudah array of strings
    return value.filter((v) => optionMap.has(v));
  }, [value, optionMap]);

  // State lokal
  const [rankings, setRankings] = useState([]); // array of { value, label }
  const [unrankedItems, setUnrankedItems] = useState([]); // array of { value, label }
  const [dragged, setDragged] = useState(null); // { value, source: 'ranked'|'unranked' }
  const [dragOverIndex, setDragOverIndex] = useState(null);

  // Sinkronisasi awal/ketika props berubah, tapi hanya kalau beda
  useEffect(() => {
    // urutan saat ini di state
    const currentValues = rankings.map((r) => r.value);
    if (!arraysEqual(currentValues, normalizedIncoming)) {
      const nextRankings = normalizedIncoming.map((v) => ({
        value: v,
        label: optionMap.get(v)?.label ?? String(v),
      }));
      const rankedSet = new Set(nextRankings.map((x) => x.value));
      const nextUnranked = options
        .filter((o) => !rankedSet.has(o.value))
        .map((o) => ({ value: o.value, label: o.label }));
      setRankings(nextRankings);
      setUnrankedItems(nextUnranked);
    } else {
      // tetap pastikan unranked terjaga saat options berubah
      const rankedSet = new Set(currentValues);
      const nextUnranked = options
        .filter((o) => !rankedSet.has(o.value))
        .map((o) => ({ value: o.value, label: o.label }));
      if (
        !sameSet(
          unrankedItems.map((u) => u.value),
          nextUnranked.map((u) => u.value)
        )
      ) {
        setUnrankedItems(nextUnranked);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [normalizedIncoming, options, optionMap]);

  // Util untuk emit ke parent sekali tiap perubahan nyata
  const emit = (list) => {
    if (typeof onChange !== "function") return;
    const formatted = list.map((item, idx) => ({
      value: item.value,
      label: item.label,
      rank: idx + 1,
    }));
    onChange(formatted);
  };

  // Drag handlers
  const onDragStart = (e, item, source) => {
    setDragged({ value: item.value, label: item.label, source });
    try {
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", item.value);
    } catch {}
  };

  const lastOverRef = useRef(-1);
  const onDragOverRankedGap = (e, index) => {
    e.preventDefault();
    // hanya update highlight kalau index berubah (hemat render)
    if (lastOverRef.current !== index) {
      lastOverRef.current = index;
      setDragOverIndex(index);
    }
  };

  const onDragLeaveRankedGap = () => {
    setDragOverIndex(null);
    lastOverRef.current = -1;
  };

  const onDropToRanked = (e, targetIndex) => {
    e.preventDefault();
    setDragOverIndex(null);
    lastOverRef.current = -1;

    if (!dragged) return;

    if (dragged.source === "unranked") {
      if (maxRankings && rankings.length >= maxRankings) {
        setDragged(null);
        return;
      }
      // Tambah dari unranked ke ranked pada posisi targetIndex
      const newRankings = [...rankings];
      newRankings.splice(targetIndex, 0, {
        value: dragged.value,
        label: dragged.label,
      });
      setRankings(newRankings);
      setUnrankedItems((prev) => prev.filter((u) => u.value !== dragged.value));
      emit(newRankings);
    } else {
      // Reorder sesama ranked
      const from = rankings.findIndex((r) => r.value === dragged.value);
      if (from === -1 || from === targetIndex) {
        setDragged(null);
        return;
      }
      const newRankings = [...rankings];
      const [moved] = newRankings.splice(from, 1);
      newRankings.splice(targetIndex, 0, moved);
      setRankings(newRankings);
      emit(newRankings);
    }

    setDragged(null);
  };

  const onDropToUnranked = (e) => {
    e.preventDefault();
    setDragOverIndex(null);
    lastOverRef.current = -1;
    if (!dragged || dragged.source !== "ranked") {
      setDragged(null);
      return;
    }
    const idx = rankings.findIndex((r) => r.value === dragged.value);
    if (idx === -1) {
      setDragged(null);
      return;
    }
    const removed = rankings[idx];
    const newRankings = rankings.filter((_, i) => i !== idx);
    setRankings(newRankings);
    setUnrankedItems((prev) => {
      // hindari duplikat
      if (prev.some((u) => u.value === removed.value)) return prev;
      // pastikan ada di options
      const opt = optionMap.get(removed.value);
      return opt ? [...prev, { value: opt.value, label: opt.label }] : prev;
    });
    emit(newRankings);
    setDragged(null);
  };

  // Klik tombol
  const moveItem = (fromIndex, dir) => {
    const to = fromIndex + (dir === "up" ? -1 : 1);
    if (to < 0 || to >= rankings.length) return;
    const next = [...rankings];
    const [m] = next.splice(fromIndex, 1);
    next.splice(to, 0, m);
    setRankings(next);
    emit(next);
  };

  const addToRanking = (option) => {
    if (maxRankings && rankings.length >= maxRankings) return;
    if (rankings.some((r) => r.value === option.value)) return;
    const next = [...rankings, { value: option.value, label: option.label }];
    setRankings(next);
    setUnrankedItems((prev) => prev.filter((u) => u.value !== option.value));
    emit(next);
  };

  const removeFromRanking = (val) => {
    const idx = rankings.findIndex((r) => r.value === val);
    if (idx === -1) return;
    const next = rankings.filter((r) => r.value !== val);
    setRankings(next);
    // kembalikan ke unranked jika memang bagian dari options
    const opt = optionMap.get(val);
    if (opt) {
      setUnrankedItems((prev) =>
        prev.some((u) => u.value === val)
          ? prev
          : [...prev, { value: opt.value, label: opt.label }]
      );
    }
    emit(next);
  };

  return (
    <div className="space-y-6">
      {/* Petunjuk */}
      <div className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">
        <div className="font-medium mb-1">Cara mengurutkan:</div>
        <ul className="space-y-1">
          <li>• Drag item dari daftar “Available Options” ke “Your Ranking”</li>
          <li>• Gunakan tombol panah atau drag untuk mengubah urutan</li>
          <li>• Seret kembali ke bawah untuk menghapus dari ranking</li>
          {maxRankings && <li>• Maksimal {maxRankings} item</li>}
        </ul>
      </div>

      {/* Ranked */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="font-medium">Your Ranking</h4>
          <Badge variant="outline">
            {rankings.length}
            {maxRankings ? `/${maxRankings}` : ""} ranked
          </Badge>
        </div>

        {rankings.length === 0 ? (
          <div
            className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center text-muted-foreground"
            onDragOver={(e) => onDragOverRankedGap(e, 0)}
            onDragLeave={onDragLeaveRankedGap}
            onDrop={(e) => onDropToRanked(e, 0)}
          >
            Drag items here to start ranking
          </div>
        ) : (
          <div className="space-y-2">
            {rankings.map((item, index) => (
              <div key={item.value}>
                {/* Gap di atas item */}
                <div
                  className={`h-2 transition-all ${
                    dragOverIndex === index ? "bg-primary/20 rounded" : ""
                  }`}
                  onDragOver={(e) => onDragOverRankedGap(e, index)}
                  onDragLeave={onDragLeaveRankedGap}
                  onDrop={(e) => onDropToRanked(e, index)}
                />

                <Card
                  className={`cursor-move transition-all ${
                    dragged?.value === item.value ? "opacity-50 scale-95" : ""
                  }`}
                  draggable
                  onDragStart={(e) => onDragStart(e, item, "ranked")}
                >
                  <CardContent className="p-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <Badge
                          className="w-8 h-8 rounded-full flex items-center justify-center p-0"
                          variant="secondary"
                        >
                          {index + 1}
                        </Badge>
                        <GripVertical className="h-4 w-4 text-muted-foreground" />
                      </div>

                      <div className="flex-1 font-medium">{item.label}</div>

                      <div className="flex items-center gap-1">
                        <button
                          type="button"
                          onClick={() => moveItem(index, "up")}
                          disabled={index === 0}
                          className="p-1 hover:bg-muted rounded disabled:opacity-50 disabled:cursor-not-allowed"
                          aria-label="Move up"
                        >
                          <ArrowUp className="h-3 w-3" />
                        </button>
                        <button
                          type="button"
                          onClick={() => moveItem(index, "down")}
                          disabled={index === rankings.length - 1}
                          className="p-1 hover:bg-muted rounded disabled:opacity-50 disabled:cursor-not-allowed"
                          aria-label="Move down"
                        >
                          <ArrowDown className="h-3 w-3" />
                        </button>
                        <button
                          type="button"
                          onClick={() => removeFromRanking(item.value)}
                          className="p-1 hover:bg-destructive/10 hover:text-destructive rounded ml-1"
                          aria-label="Remove"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Gap setelah item terakhir */}
                {index === rankings.length - 1 && (
                  <div
                    className={`h-2 transition-all ${
                      dragOverIndex === index + 1 ? "bg-primary/20 rounded" : ""
                    }`}
                    onDragOver={(e) => onDragOverRankedGap(e, index + 1)}
                    onDragLeave={onDragLeaveRankedGap}
                    onDrop={(e) => onDropToRanked(e, index + 1)}
                  />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Unranked */}
      {unrankedItems.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium">Available Options</h4>
          <div
            className="grid grid-cols-1 gap-2"
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDropToUnranked}
          >
            {unrankedItems.map((option) => (
              <Card
                key={option.value}
                className="cursor-move hover:bg-muted/50 transition-colors"
                draggable
                onDragStart={(e) => onDragStart(e, option, "unranked")}
              >
                <CardContent className="p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <GripVertical className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{option.label}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => addToRanking(option)}
                      disabled={!!maxRankings && rankings.length >= maxRankings}
                      className="text-sm text-primary hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Add to ranking
                    </button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Status */}
      {rankings.length > 0 && (
        <div className="flex items-center gap-2 text-sm text-green-600">
          <CheckCircle className="h-4 w-4" />
          <span>
            {rankings.length} item{rankings.length !== 1 ? "s" : ""} ranked
            {maxRankings &&
              rankings.length >= maxRankings &&
              " (maximum reached)"}
          </span>
        </div>
      )}
    </div>
  );
};

export default DragDropRanking;

/* ===== helpers ===== */
function arraysEqual(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b)) return false;
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
  return true;
}

function sameSet(a, b) {
  if (a.length !== b.length) return false;
  const sa = new Set(a);
  for (const x of b) if (!sa.has(x)) return false;
  return true;
}
