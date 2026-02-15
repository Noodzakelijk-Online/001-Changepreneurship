import React, { useEffect, useState } from "react";
import { useParams, Navigate } from "react-router-dom";
import { fetchPhase, fetchTab } from "../api.js";
import SectionView from "../components/SectionView.jsx";

export default function PhasePage() {
  const { phaseId, tabId, sectionId } = useParams();
  const [phase, setPhase] = useState(null);
  const [tab, setTab] = useState(null);

  useEffect(() => {
    fetchPhase(phaseId).then(setPhase);
  }, [phaseId]);

  useEffect(() => {
    fetchTab(phaseId, tabId).then(setTab);
  }, [phaseId, tabId]);

  if (!phase || !tab) return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <p className="text-gray-400">Loading...</p>
    </div>
  );
  if (!phase.tabs) return <Navigate to="/" replace />;

  return (
    <div className="min-h-screen bg-black text-white p-4 space-y-4">
      <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
        {phase.title} / {tab.title}
      </h1>
      <SectionView phaseId={phaseId} tabId={tabId} sectionId={sectionId} />
    </div>
  );
}
