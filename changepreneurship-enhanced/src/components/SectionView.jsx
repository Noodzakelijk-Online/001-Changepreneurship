import React, { useEffect, useState } from "react";
import QuestionView from "./QuestionView.jsx";
import { fetchSection } from "../api.js";

const ITEM_HEIGHT = 80;

export default function SectionView({ phaseId, tabId, sectionId }) {
  const [section, setSection] = useState(null);
  const [scrollTop, setScrollTop] = useState(0);

  useEffect(() => {
    fetchSection(phaseId, tabId, sectionId).then(setSection);
  }, [phaseId, tabId, sectionId]);

  if (!section) return <p>Loading section...</p>;

  const { questions } = section;
  const onScroll = (e) => setScrollTop(e.currentTarget.scrollTop);
  const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - 5);
  const endIndex = Math.min(
    questions.length,
    Math.ceil((scrollTop + 400) / ITEM_HEIGHT) + 5
  );
  const offsetY = startIndex * ITEM_HEIGHT;
  const visible = questions.slice(startIndex, endIndex);

  return (
    <div
      style={{ height: 400, overflow: "auto" }}
      onScroll={onScroll}
      className="border"
    >
      <div style={{ height: questions.length * ITEM_HEIGHT, position: "relative" }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visible.map((q) => (
            <div key={q.id} style={{ height: ITEM_HEIGHT }} className="p-4 border-b">
              <QuestionView question={q} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
