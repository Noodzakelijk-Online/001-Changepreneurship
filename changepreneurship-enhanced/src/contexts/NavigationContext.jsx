import React, { createContext, useContext, useEffect, useState } from 'react';
import { fromCode, toCode, normalizePath } from '../lib/navigation.js';
import { getNavigationStructure } from '../lib/navigation-structure.js';

const NavigationContext = createContext();

export const NavigationProvider = ({ children }) => {
  const [structure, setStructure] = useState([]);
  const [path, setPath] = useState(null);
  const [progress, setProgress] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('questionProgress')) || {};
    } catch {
      return {};
    }
  });

  useEffect(() => {
    getNavigationStructure().then(setStructure);
  }, []);

  useEffect(() => {
    if (!structure.length) return;
    const raw = localStorage.getItem('lastLocation');
    let target = {};
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') {
          target = parsed;
        } else {
          target = fromCode(raw);
        }
      } catch {
        target = fromCode(raw);
      }
    }
    const normalized = normalizePath(target, structure);
    setPath(normalized);
  }, [structure]);

  useEffect(() => {
    if (!structure.length || !path) return;
    const payload = {
      phaseId: path.phaseId,
      tabId: path.tabId,
      sectionId: path.sectionId,
      questionId: path.questionId,
      phase: path.phase,
      tab: path.tab,
      section: path.section,
      question: path.question,
      code: toCode(path),
    };
    localStorage.setItem('lastLocation', JSON.stringify(payload));
  }, [path, structure]);

  useEffect(() => {
    localStorage.setItem('questionProgress', JSON.stringify(progress));
  }, [progress]);

  const navigateTo = (next) => {
    if (!structure.length) return;
    setPath(normalizePath(next, structure));
  };

  const markVisited = (id) => {
    setProgress((prev) => (prev[id] ? prev : { ...prev, [id]: true }));
  };

  return (
    <NavigationContext.Provider value={{ structure, path, navigateTo, progress, markVisited }}>
      {children}
    </NavigationContext.Provider>
  );
};

export const useNavigation = () => useContext(NavigationContext);
