import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';
import AIRecommendations from './AIRecommendations';
import './PrinciplesSearch.css';

const PrinciplesSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedStage, setSelectedStage] = useState('');
  const [categories, setCategories] = useState([]);
  const [stages, setStages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCategoriesAndStages();
  }, []);

  const fetchCategoriesAndStages = async () => {
    try {
      const [categoriesResponse, stagesResponse] = await Promise.all([
        ApiService.getCategories(),
        ApiService.getStages()
      ]);

      if (categoriesResponse.success) {
        setCategories(categoriesResponse.data);
      }

      if (stagesResponse.success) {
        setStages(stagesResponse.data);
      }
    } catch (error) {
      console.error('Error fetching categories and stages:', error);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('');
    setSelectedStage('');
  };

  const formatOption = (option) => {
    return option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const hasActiveFilters = searchQuery || selectedCategory || selectedStage;

  const getRecommendationProps = () => {
    if (searchQuery) {
      return {
        title: `Search Results for "${searchQuery}"`,
        category: null,
        stage: null,
        userStage: null,
        focusAreas: [],
        limit: 10
      };
    }

    if (selectedCategory || selectedStage) {
      return {
        title: `Filtered Principles`,
        category: selectedCategory || null,
        stage: selectedStage || null,
        userStage: null,
        focusAreas: [],
        limit: 10
      };
    }

    return {
      title: "All Entrepreneurship Principles",
      category: null,
      stage: null,
      userStage: null,
      focusAreas: [],
      limit: 10
    };
  };

  return (
    <div className="principles-search">
      <div className="search-header">
        <h2>🔍 Explore Entrepreneurship Principles</h2>
        <p>Search and filter through our comprehensive database of entrepreneurship wisdom</p>
      </div>

      <div className="search-controls">
        <div className="search-input-group">
          <input
            type="text"
            placeholder="Search principles by title or summary..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button 
              className="clear-search"
              onClick={() => setSearchQuery('')}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        <div className="filter-controls">
          <div className="filter-group">
            <label htmlFor="category-select">Category:</label>
            <select
              id="category-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="filter-select"
            >
              <option value="">All Categories</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {formatOption(category)}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="stage-select">Business Stage:</label>
            <select
              id="stage-select"
              value={selectedStage}
              onChange={(e) => setSelectedStage(e.target.value)}
              className="filter-select"
            >
              <option value="">All Stages</option>
              {stages.map((stage) => (
                <option key={stage} value={stage}>
                  {formatOption(stage)}
                </option>
              ))}
            </select>
          </div>

          {hasActiveFilters && (
            <button 
              className="clear-filters"
              onClick={handleClearFilters}
              title="Clear all filters"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      <div className="search-results">
        {searchQuery ? (
          <AIRecommendations
            key={`search-${searchQuery}`}
            title={`Search Results for "${searchQuery}"`}
            category={null}
            stage={null}
            userStage={null}
            focusAreas={[]}
            limit={20}
            searchQuery={searchQuery}
          />
        ) : (
          <AIRecommendations
            key={`filter-${selectedCategory}-${selectedStage}`}
            {...getRecommendationProps()}
          />
        )}
      </div>

      <div className="search-tips">
        <h4>💡 Search Tips:</h4>
        <ul>
          <li>Use keywords like "lean startup", "marketing", "leadership" to find relevant principles</li>
          <li>Filter by business stage to see principles most relevant to your current phase</li>
          <li>Combine category and stage filters for more targeted results</li>
          <li>Click "Show More" on any principle card to see detailed action steps and risks</li>
        </ul>
      </div>
    </div>
  );
};

export default PrinciplesSearch;
