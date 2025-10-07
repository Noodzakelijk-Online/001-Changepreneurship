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
 *      * ["v1","v2"...] or
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
  // Quick map of value -> option
  const optionMap = useMemo(() => {
    const m = new Map();
    options.forEach((o) => m.set(o.value, o));
    return m;
  }, [options]);

  // Normalize value from props into an ordered array of values ["v1","v2"...]
  const normalizedIncoming = useMemo(() => {
    if (!Array.isArray(value)) return [];
    // if incoming objects have {value, rank}, sort them first
    if (value.length && typeof value[0] === "object") {
      const sorted = [...value].sort((a, b) => (a.rank || 0) - (b.rank || 0));
      return sorted.map((x) => x.value).filter((v) => optionMap.has(v));
    }
    // if already an array of strings
    return value.filter((v) => optionMap.has(v));
  }, [value, optionMap]);

  // Local state
  const [rankings, setRankings] = useState([]); // array of { value, label }
  const [unrankedItems, setUnrankedItems] = useState([]); // array of { value, label }
  const [dragged, setDragged] = useState(null); // { value, source: 'ranked'|'unranked' }
  const [dragOverIndex, setDragOverIndex] = useState(null);
  const [isKeyboardMode, setIsKeyboardMode] = useState(false);

  // Initial sync/when props change, but only if different
  useEffect(() => {
    // current order in state
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
      // still ensure unranked items are preserved when options change
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

    // Utility to emit to parent once per actual change
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
  // Original gap logic kept for empty list drop, but we prefer swap-on-hover.
  const onDragOverRankedGap = (e, index) => {
    e.preventDefault();
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
      // Add from unranked to ranked at the targetIndex
      const newRankings = [...rankings];
      newRankings.splice(targetIndex, 0, {
        value: dragged.value,
        label: dragged.label,
      });
      setRankings(newRankings);
      setUnrankedItems((prev) => prev.filter((u) => u.value !== dragged.value));
      emit(newRankings);
    } else {
      // Reorder within ranked items
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
      // avoid duplicates
      if (prev.some((u) => u.value === removed.value)) return prev;
      // ensure it exists in options
      const opt = optionMap.get(removed.value);
      return opt ? [...prev, { value: opt.value, label: opt.label }] : prev;
    });
    emit(newRankings);
    setDragged(null);
  };

  // Button click
  const moveItem = (fromIndex, dir) => {
    const to = fromIndex + (dir === "up" ? -1 : 1);
    if (to < 0 || to >= rankings.length) return;
    const next = [...rankings];
    const [m] = next.splice(fromIndex, 1);
    next.splice(to, 0, m);
    setRankings(next);
    emit(next);
  };

  // Swap-on-hover while dragging ranked item over another ranked item
  const onDragOverRankedItem = (e, overItemValue) => {
    e.preventDefault();
    if (!dragged) return;
    const toIdx = rankings.findIndex(r => r.value === overItemValue);
    if (toIdx === -1) return;
    // If dragging from unranked: insert if not already ranked
    if (dragged.source === 'unranked') {
      if (rankings.some(r => r.value === dragged.value)) return; // already inserted
      if (maxRankings && rankings.length >= maxRankings) return;
      const next = [...rankings];
      next.splice(toIdx, 0, { value: dragged.value, label: dragged.label });
      setRankings(next);
      setUnrankedItems(prev => prev.filter(u => u.value !== dragged.value));
      emit(next);
      // Convert dragged marker to ranked so subsequent hover swaps work
      setDragged({ ...dragged, source: 'ranked' });
      return;
    }
    // If dragging within ranked: perform swap (as before)
    if (dragged.source === 'ranked') {
      const fromIdx = rankings.findIndex(r => r.value === dragged.value);
      if (fromIdx === -1 || fromIdx === toIdx) return;
      const next = [...rankings];
      const temp = next[fromIdx];
      next[fromIdx] = next[toIdx];
      next[toIdx] = temp;
      setRankings(next);
      emit(next);
    }
  };

  // Keyboard accessible reorder (focus item then arrow up/down)
  const onKeyDownRankedItem = (e, index) => {
    if (e.key === 'ArrowUp') { e.preventDefault(); moveItem(index, 'up'); }
    if (e.key === 'ArrowDown') { e.preventDefault(); moveItem(index, 'down'); }
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
    // return to unranked if it's part of options
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
      {/* Instructions */}
      <div className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">
        <div className="font-medium mb-1">How to rank:</div>
        <ul className="space-y-1">
          <li>• Drag directly from Available Options into the list above</li>
          <li>• While dragging over a ranked item it will auto-place / swap</li>
          <li>• Drag a ranked item back down to remove it</li>
          <li>• Arrow keys move focused ranked item up/down</li>
          {maxRankings && <li>• Maximum {maxRankings} items</li>}
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
                <Card
                  className={`group relative cursor-move transition-all border border-border/60 hover:border-primary/50 hover:bg-muted/30 focus-within:ring-2 focus-within:ring-primary/40 rounded-lg ${dragged?.value === item.value ? "opacity-50 scale-95" : ""}`}
                  draggable
                  onDragStart={(e) => onDragStart(e, item, "ranked")}
                  onDragOver={(e) => onDragOverRankedItem(e, item.value)}
                  tabIndex={0}
                  onFocus={() => setIsKeyboardMode(true)}
                  onBlur={() => setIsKeyboardMode(false)}
                  onKeyDown={(e) => onKeyDownRankedItem(e, index)}
                >
                  <CardContent className="p-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2 select-none">
                        <Badge className="w-7 h-7 rounded-full flex items-center justify-center p-0 text-xs font-semibold bg-primary/15 text-primary border border-primary/30">
                          {index + 1}
                        </Badge>
                        <GripVertical className="h-4 w-4 text-muted-foreground group-hover:text-primary/80 transition-colors" />
                      </div>
                      <div className="flex-1 font-medium tracking-tight text-sm">
                        {item.label}
                      </div>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity">
                        <button
                          type="button"
                          onClick={() => moveItem(index, "up")}
                          disabled={index === 0}
                          className="p-1 hover:bg-muted rounded disabled:opacity-40 disabled:cursor-not-allowed"
                          aria-label="Move up"
                        >
                          <ArrowUp className="h-3 w-3" />
                        </button>
                        <button
                          type="button"
                          onClick={() => moveItem(index, "down")}
                          disabled={index === rankings.length - 1}
                          className="p-1 hover:bg-muted rounded disabled:opacity-40 disabled:cursor-not-allowed"
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
                className="cursor-move hover:border-primary/40 hover:bg-muted/40 transition-all border border-border/60 rounded-lg group"
                draggable
                onDragStart={(e) => onDragStart(e, option, "unranked")}
              >
                <CardContent className="p-3">
                  <div className="flex items-center gap-2">
                    <GripVertical className="h-4 w-4 text-muted-foreground group-hover:text-primary/80 transition-colors" />
                    <span className="font-medium text-sm tracking-tight select-none">{option.label}</span>
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
