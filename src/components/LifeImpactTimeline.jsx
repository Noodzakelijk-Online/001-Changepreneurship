import React, { useState, useRef, useEffect } from 'react';
import { Plus, Edit3, Trash2, Calendar, MapPin, Heart, Zap, TrendingUp, TrendingDown, Info, Save, X } from 'lucide-react';
import './LifeImpactTimeline.css';

const LifeImpactTimeline = ({ 
  events = [], 
  onEventsChange,
  timelineStart = new Date().getFullYear() - 30,
  timelineEnd = new Date().getFullYear() + 5
}) => {
  const [lifeEvents, setLifeEvents] = useState(events);
  const [isAddingEvent, setIsAddingEvent] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [newEvent, setNewEvent] = useState({
    title: '',
    description: '',
    date: '',
    impact: 0, // -100 to +100
    category: 'personal',
    x: 0,
    y: 0
  });
  const [showEventForm, setShowEventForm] = useState(false);
  const timelineRef = useRef(null);
  const [timelineRect, setTimelineRect] = useState(null);

  useEffect(() => {
    if (timelineRef.current) {
      setTimelineRect(timelineRef.current.getBoundingClientRect());
    }
  }, []);

  useEffect(() => {
    const handleResize = () => {
      if (timelineRef.current) {
        setTimelineRect(timelineRef.current.getBoundingClientRect());
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const eventCategories = [
    { id: 'personal', name: 'Personal', color: '#ff6b35', icon: <Heart className="w-4 h-4" /> },
    { id: 'education', name: 'Education', color: '#3b82f6', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'career', name: 'Career', color: '#10b981', icon: <Zap className="w-4 h-4" /> },
    { id: 'family', name: 'Family', color: '#f59e0b', icon: <Heart className="w-4 h-4" /> },
    { id: 'health', name: 'Health', color: '#ef4444', icon: <Heart className="w-4 h-4" /> },
    { id: 'achievement', name: 'Achievement', color: '#8b5cf6', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'challenge', name: 'Challenge', color: '#6b7280', icon: <TrendingDown className="w-4 h-4" /> },
    { id: 'other', name: 'Other', color: '#64748b', icon: <MapPin className="w-4 h-4" /> }
  ];

  const handleTimelineClick = (e) => {
    if (!timelineRect || isAddingEvent || editingEvent) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Calculate position relative to timeline
    const timelineWidth = rect.width - 80; // Account for padding
    const timelineHeight = rect.height - 80;
    const centerY = rect.height / 2;
    
    // Calculate year based on x position
    const yearProgress = (x - 40) / timelineWidth;
    const year = Math.round(timelineStart + (timelineEnd - timelineStart) * yearProgress);
    
    // Calculate impact based on y position (-100 to +100)
    const impactProgress = (centerY - y) / (timelineHeight / 2);
    const impact = Math.max(-100, Math.min(100, Math.round(impactProgress * 100)));

    // Check if clicking near an existing event
    const clickedEvent = findEventAtPosition(x, y, rect);
    if (clickedEvent) {
      setEditingEvent(clickedEvent);
      setNewEvent({ ...clickedEvent });
      setShowEventForm(true);
      return;
    }

    // Create new event
    setNewEvent({
      title: '',
      description: '',
      date: year.toString(),
      impact: impact,
      category: impact > 0 ? 'achievement' : 'challenge',
      x: x,
      y: y,
      id: Date.now()
    });
    setIsAddingEvent(true);
    setShowEventForm(true);
  };

  const findEventAtPosition = (x, y, rect) => {
    const threshold = 30; // Click threshold in pixels
    return lifeEvents.find(event => {
      const eventX = getEventXPosition(event, rect);
      const eventY = getEventYPosition(event, rect);
      const distance = Math.sqrt(Math.pow(x - eventX, 2) + Math.pow(y - eventY, 2));
      return distance <= threshold;
    });
  };

  const getEventXPosition = (event, rect = timelineRect) => {
    if (!rect) return 0;
    const timelineWidth = rect.width - 80;
    const year = parseInt(event.date) || new Date().getFullYear();
    const yearProgress = (year - timelineStart) / (timelineEnd - timelineStart);
    return 40 + (yearProgress * timelineWidth);
  };

  const getEventYPosition = (event, rect = timelineRect) => {
    if (!rect) return 0;
    const timelineHeight = rect.height - 80;
    const centerY = rect.height / 2;
    const impactProgress = event.impact / 100;
    return centerY - (impactProgress * (timelineHeight / 2));
  };

  const handleSaveEvent = () => {
    if (!newEvent.title.trim()) return;

    let updatedEvents;
    if (editingEvent) {
      updatedEvents = lifeEvents.map(event => 
        event.id === editingEvent.id ? { ...newEvent, id: editingEvent.id } : event
      );
    } else {
      updatedEvents = [...lifeEvents, { ...newEvent, id: Date.now() }];
    }

    setLifeEvents(updatedEvents);
    onEventsChange && onEventsChange(updatedEvents);
    resetForm();
  };

  const handleDeleteEvent = (eventId) => {
    const updatedEvents = lifeEvents.filter(event => event.id !== eventId);
    setLifeEvents(updatedEvents);
    onEventsChange && onEventsChange(updatedEvents);
    resetForm();
  };

  const resetForm = () => {
    setNewEvent({
      title: '',
      description: '',
      date: '',
      impact: 0,
      category: 'personal',
      x: 0,
      y: 0
    });
    setIsAddingEvent(false);
    setEditingEvent(null);
    setShowEventForm(false);
  };

  const getImpactLabel = (impact) => {
    if (impact > 75) return 'Extremely Positive';
    if (impact > 50) return 'Very Positive';
    if (impact > 25) return 'Positive';
    if (impact > 0) return 'Slightly Positive';
    if (impact === 0) return 'Neutral';
    if (impact > -25) return 'Slightly Negative';
    if (impact > -50) return 'Negative';
    if (impact > -75) return 'Very Negative';
    return 'Extremely Negative';
  };

  const getCategoryInfo = (categoryId) => {
    return eventCategories.find(cat => cat.id === categoryId) || eventCategories[0];
  };

  const renderYearMarkers = () => {
    const years = [];
    const yearInterval = Math.max(1, Math.floor((timelineEnd - timelineStart) / 10));
    
    for (let year = timelineStart; year <= timelineEnd; year += yearInterval) {
      years.push(year);
    }

    return years.map(year => {
      const progress = (year - timelineStart) / (timelineEnd - timelineStart);
      return (
        <div
          key={year}
          className="year-marker"
          style={{ left: `${40 + progress * (100 - 8)}%` }}
        >
          <div className="year-line" />
          <div className="year-label">{year}</div>
        </div>
      );
    });
  };

  const renderImpactScale = () => {
    const levels = [
      { value: 100, label: 'Extremely Positive', color: '#10b981' },
      { value: 50, label: 'Positive', color: '#22c55e' },
      { value: 0, label: 'Neutral', color: '#6b7280' },
      { value: -50, label: 'Negative', color: '#f59e0b' },
      { value: -100, label: 'Extremely Negative', color: '#ef4444' }
    ];

    return levels.map(level => {
      const progress = (100 - level.value) / 200; // Convert -100/+100 to 0-1
      return (
        <div
          key={level.value}
          className="impact-marker"
          style={{ top: `${40 + progress * 60}%` }}
        >
          <div className="impact-line" style={{ backgroundColor: level.color }} />
          <div className="impact-label" style={{ color: level.color }}>
            {level.label}
          </div>
        </div>
      );
    });
  };

  const renderEvents = () => {
    if (!timelineRect) return null;

    return lifeEvents.map(event => {
      const x = getEventXPosition(event);
      const y = getEventYPosition(event);
      const category = getCategoryInfo(event.category);
      
      return (
        <div
          key={event.id}
          className={`timeline-event ${event.impact > 0 ? 'positive' : 'negative'}`}
          style={{
            left: `${x}px`,
            top: `${y}px`,
            backgroundColor: category.color,
            transform: 'translate(-50%, -50%)'
          }}
          onClick={(e) => {
            e.stopPropagation();
            setEditingEvent(event);
            setNewEvent({ ...event });
            setShowEventForm(true);
          }}
        >
          <div className="event-icon">
            {category.icon}
          </div>
          <div className="event-tooltip">
            <div className="tooltip-title">{event.title}</div>
            <div className="tooltip-date">{event.date}</div>
            <div className="tooltip-impact">{getImpactLabel(event.impact)}</div>
            {event.description && (
              <div className="tooltip-description">{event.description}</div>
            )}
          </div>
        </div>
      );
    });
  };

  const renderEventForm = () => {
    if (!showEventForm) return null;

    return (
      <div className="event-form-overlay">
        <div className="event-form">
          <div className="form-header">
            <h3>{editingEvent ? 'Edit Life Event' : 'Add Life Event'}</h3>
            <button onClick={resetForm} className="close-button">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="form-content">
            <div className="form-group">
              <label>Event Title *</label>
              <input
                type="text"
                value={newEvent.title}
                onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                placeholder="e.g., Started university, Got married, Lost job..."
                maxLength={100}
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={newEvent.description}
                onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                placeholder="Describe the event and its significance..."
                rows={3}
                maxLength={500}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Year *</label>
                <input
                  type="number"
                  value={newEvent.date}
                  onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                  min={timelineStart}
                  max={timelineEnd}
                />
              </div>

              <div className="form-group">
                <label>Category</label>
                <select
                  value={newEvent.category}
                  onChange={(e) => setNewEvent({ ...newEvent, category: e.target.value })}
                >
                  {eventCategories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Life Impact: {getImpactLabel(newEvent.impact)} ({newEvent.impact})</label>
              <div className="impact-slider-container">
                <div className="impact-labels">
                  <span className="negative-label">Very Negative</span>
                  <span className="neutral-label">Neutral</span>
                  <span className="positive-label">Very Positive</span>
                </div>
                <input
                  type="range"
                  min="-100"
                  max="100"
                  value={newEvent.impact}
                  onChange={(e) => setNewEvent({ ...newEvent, impact: parseInt(e.target.value) })}
                  className="impact-slider"
                />
                <div className="impact-value" style={{
                  color: newEvent.impact > 0 ? '#10b981' : newEvent.impact < 0 ? '#ef4444' : '#6b7280'
                }}>
                  {newEvent.impact}
                </div>
              </div>
            </div>
          </div>

          <div className="form-actions">
            {editingEvent && (
              <button
                onClick={() => handleDeleteEvent(editingEvent.id)}
                className="delete-button"
              >
                <Trash2 className="w-4 h-4" />
                Delete Event
              </button>
            )}
            <div className="action-buttons">
              <button onClick={resetForm} className="cancel-button">
                Cancel
              </button>
              <button
                onClick={handleSaveEvent}
                className="save-button"
                disabled={!newEvent.title.trim() || !newEvent.date}
              >
                <Save className="w-4 h-4" />
                {editingEvent ? 'Update' : 'Add'} Event
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const getEventsSummary = () => {
    const positiveEvents = lifeEvents.filter(e => e.impact > 0);
    const negativeEvents = lifeEvents.filter(e => e.impact < 0);
    const neutralEvents = lifeEvents.filter(e => e.impact === 0);
    
    const avgPositiveImpact = positiveEvents.length > 0 
      ? positiveEvents.reduce((sum, e) => sum + e.impact, 0) / positiveEvents.length 
      : 0;
    
    const avgNegativeImpact = negativeEvents.length > 0 
      ? negativeEvents.reduce((sum, e) => sum + e.impact, 0) / negativeEvents.length 
      : 0;

    return {
      total: lifeEvents.length,
      positive: positiveEvents.length,
      negative: negativeEvents.length,
      neutral: neutralEvents.length,
      avgPositiveImpact: Math.round(avgPositiveImpact),
      avgNegativeImpact: Math.round(avgNegativeImpact),
      overallTrend: lifeEvents.length > 0 
        ? lifeEvents.reduce((sum, e) => sum + e.impact, 0) / lifeEvents.length 
        : 0
    };
  };

  const summary = getEventsSummary();

  return (
    <div className="life-impact-timeline">
      <div className="timeline-header">
        <h2>Life Impact Timeline</h2>
        <p>
          Map the significant events in your life that have shaped who you are today. 
          Click above the center line for positive experiences and below for negative ones. 
          Understanding your life journey helps identify patterns of resilience and growth that will serve you as an entrepreneur.
        </p>
      </div>

      <div className="timeline-instructions">
        <div className="instruction-item">
          <div className="instruction-icon positive">
            <TrendingUp className="w-4 h-4" />
          </div>
          <span>Click above the line for positive experiences</span>
        </div>
        <div className="instruction-item">
          <div className="instruction-icon negative">
            <TrendingDown className="w-4 h-4" />
          </div>
          <span>Click below the line for negative experiences</span>
        </div>
        <div className="instruction-item">
          <div className="instruction-icon">
            <Calendar className="w-4 h-4" />
          </div>
          <span>Events are positioned chronologically from left to right</span>
        </div>
      </div>

      <div 
        ref={timelineRef}
        className="timeline-container"
        onClick={handleTimelineClick}
      >
        <div className="timeline-background">
          <div className="center-line" />
          <div className="positive-area">
            <span className="area-label">Positive Impact</span>
          </div>
          <div className="negative-area">
            <span className="area-label">Negative Impact</span>
          </div>
        </div>

        {renderYearMarkers()}
        {renderImpactScale()}
        {renderEvents()}

        {lifeEvents.length === 0 && (
          <div className="empty-state">
            <Info className="w-8 h-8" />
            <h3>Start Mapping Your Life Journey</h3>
            <p>Click anywhere on the timeline to add your first significant life event</p>
          </div>
        )}
      </div>

      {lifeEvents.length > 0 && (
        <div className="timeline-summary">
          <h3>Life Journey Summary</h3>
          <div className="summary-stats">
            <div className="stat-item">
              <div className="stat-value">{summary.total}</div>
              <div className="stat-label">Total Events</div>
            </div>
            <div className="stat-item positive">
              <div className="stat-value">{summary.positive}</div>
              <div className="stat-label">Positive Events</div>
            </div>
            <div className="stat-item negative">
              <div className="stat-value">{summary.negative}</div>
              <div className="stat-label">Challenging Events</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{Math.round(summary.overallTrend)}</div>
              <div className="stat-label">Overall Life Trend</div>
            </div>
          </div>
          
          <div className="entrepreneurial-insights">
            <h4>Entrepreneurial Insights</h4>
            <div className="insights-grid">
              {summary.positive > summary.negative && (
                <div className="insight-item">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                  <span>Your predominantly positive life experiences suggest strong optimism and resilience - key entrepreneurial traits.</span>
                </div>
              )}
              {summary.negative > 0 && (
                <div className="insight-item">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  <span>Overcoming {summary.negative} challenging events has likely built the resilience needed for entrepreneurial challenges.</span>
                </div>
              )}
              {summary.avgPositiveImpact > 70 && (
                <div className="insight-item">
                  <Heart className="w-5 h-5 text-red-400" />
                  <span>High-impact positive experiences indicate you recognize and create significant value - essential for business success.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {renderEventForm()}
    </div>
  );
};

export default LifeImpactTimeline;

