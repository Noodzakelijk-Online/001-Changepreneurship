# Ranking Component UX Notes

## Current Interaction Model
1. Drag from Available Options directly into the ranked list area.
2. While hovering a ranked card, the system computes midpoint and:
   - Inserts BEFORE if cursor is in top half.
   - Inserts AFTER if cursor is in bottom half.
3. Visual insertion indicator (animated bar) shows the exact drop position.
4. New unranked item auto-inserts immediately on hover (no separate drop required) making the action instantaneous.
5. Reordering an existing ranked item uses the same midpoint logic; card animates to new spot.
6. Keyboard: Focus a ranked item and use Arrow Up / Arrow Down to move it.
7. Remove: Drag item back to Available Options or click the × button.

## Rationale
- Eliminates cognitive load of temporary swap model (predictable insert location).
- Reduces motor effort: user does not need to drag precisely between narrow gaps.
- Instant insertion creates faster feedback loop and encourages exploration.

## Accessibility Considerations
- Badge numbers reflect rank order and update live.
- Arrow key support provides non-pointer reordering.
- Future enhancement: announce reordering via ARIA live region for screen readers.

## Constraints
- Optional `maxRankings` enforced; additional insertions ignored gracefully.
- Duplicate prevention: unranked item becomes ranked only once per drag session.

## Potential Future Enhancements
| Idea | Benefit | Effort |
|------|---------|--------|
| ARIA live region updates ("Moved X to position Y") | Screen reader clarity | Medium |
| Smooth height/position transitions (auto-animate) | Visual polish | Low/Medium |
| Long-press to drag on touch devices | Mobile usability | Medium |
| Type-ahead filter for Available Options | Scales with large lists | Low |
| Undo last change (Ctrl+Z) | Error recovery | Medium |

## Implementation Highlights
- Midpoint calculation: `clientY < rect.top + rect.height / 2` determines before/after.
- Insertion ghost driven by `dragOverIndex` showing animated bar.
- State thrash protection: last insertion key cached to avoid redundant re-renders.
- Emits normalized array of `{ value, label, rank }` to parent via `onChange`.

## Edge Cases Handled
- Dragging item rapidly across multiple cards inserts/reorders only when index changes.
- Removing ranked item restores it to Available Options if still in master option list.
- Max capacity halts additional inserts without breaking existing ordering.

## Testing Checklist
- [ ] Drag first available item to create list (indicator appears at top).
- [ ] Insert between two existing items (indicator between them, order updates).
- [ ] Drag last item upward and verify order adjusts correctly.
- [ ] Hit max capacity and confirm further drags are ignored.
- [ ] Keyboard reorder reflects in visual numbering.
- [ ] Remove item and ensure it reappears exactly once in Available Options.

