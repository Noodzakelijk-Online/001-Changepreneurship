import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Slider } from '@/components/ui/slider.jsx';
import { 
  User, 
  Target, 
  TrendingUp, 
  Users, 
  Lightbulb, 
  Shield, 
  Zap,
  Heart,
  Brain,
  DollarSign,
  Clock,
  Globe
} from 'lucide-react';

const EntrepreneurProfileSliders = ({ profileData = null }) => {
  // Default profile data if none provided
  const defaultProfile = {
    risk_tolerance: 25,           // -100 (Risk Averse) to +100 (Risk Seeking)
    innovation_focus: 40,         // -100 (Incremental) to +100 (Disruptive)
    leadership_style: -20,        // -100 (Collaborative) to +100 (Directive)
    market_approach: 15,          // -100 (Niche Focus) to +100 (Mass Market)
    decision_making: -10,         // -100 (Data-Driven) to +100 (Intuitive)
    growth_orientation: 60,       // -100 (Sustainable) to +100 (Aggressive)
    customer_focus: 30,           // -100 (Product-Led) to +100 (Customer-Led)
    financial_approach: -35,      // -100 (Conservative) to +100 (Aggressive)
    time_horizon: 45,             // -100 (Short-term) to +100 (Long-term)
    social_impact: 20,            // -100 (Profit-First) to +100 (Impact-First)
    team_building: -15,           // -100 (Solo/Small) to +100 (Large Teams)
    market_timing: 10             // -100 (Early Adopter) to +100 (Mass Market)
  };

  const profile = profileData || defaultProfile;

  const dimensions = [
    {
      key: 'risk_tolerance',
      title: 'Risk Tolerance',
      icon: Shield,
      leftLabel: 'Risk Averse',
      rightLabel: 'Risk Seeking',
      leftDesc: 'Prefers proven strategies and calculated moves',
      rightDesc: 'Comfortable with uncertainty and bold ventures',
      color: 'from-red-500 to-orange-500'
    },
    {
      key: 'innovation_focus',
      title: 'Innovation Approach',
      icon: Lightbulb,
      leftLabel: 'Incremental',
      rightLabel: 'Disruptive',
      leftDesc: 'Focuses on improving existing solutions',
      rightDesc: 'Creates entirely new markets and paradigms',
      color: 'from-blue-500 to-purple-500'
    },
    {
      key: 'leadership_style',
      title: 'Leadership Style',
      icon: Users,
      leftLabel: 'Collaborative',
      rightLabel: 'Directive',
      leftDesc: 'Builds consensus and shared decision-making',
      rightDesc: 'Makes decisive calls and leads from the front',
      color: 'from-green-500 to-teal-500'
    },
    {
      key: 'market_approach',
      title: 'Market Strategy',
      icon: Target,
      leftLabel: 'Niche Focus',
      rightLabel: 'Mass Market',
      leftDesc: 'Targets specific segments with tailored solutions',
      rightDesc: 'Aims for broad appeal and market penetration',
      color: 'from-indigo-500 to-blue-500'
    },
    {
      key: 'decision_making',
      title: 'Decision Making',
      icon: Brain,
      leftLabel: 'Data-Driven',
      rightLabel: 'Intuitive',
      leftDesc: 'Relies on analytics and systematic analysis',
      rightDesc: 'Trusts instincts and pattern recognition',
      color: 'from-purple-500 to-pink-500'
    },
    {
      key: 'growth_orientation',
      title: 'Growth Philosophy',
      icon: TrendingUp,
      leftLabel: 'Sustainable',
      rightLabel: 'Aggressive',
      leftDesc: 'Prioritizes steady, controlled expansion',
      rightDesc: 'Pursues rapid scaling and market dominance',
      color: 'from-emerald-500 to-green-500'
    },
    {
      key: 'customer_focus',
      title: 'Business Orientation',
      icon: Heart,
      leftLabel: 'Product-Led',
      rightLabel: 'Customer-Led',
      leftDesc: 'Builds great products and finds customers',
      rightDesc: 'Starts with customer needs and builds solutions',
      color: 'from-rose-500 to-red-500'
    },
    {
      key: 'financial_approach',
      title: 'Financial Strategy',
      icon: DollarSign,
      leftLabel: 'Conservative',
      rightLabel: 'Aggressive',
      leftDesc: 'Maintains strong cash flow and low debt',
      rightDesc: 'Leverages capital for rapid growth',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      key: 'time_horizon',
      title: 'Time Perspective',
      icon: Clock,
      leftLabel: 'Short-term',
      rightLabel: 'Long-term',
      leftDesc: 'Focuses on immediate results and quick wins',
      rightDesc: 'Invests in long-term vision and patient capital',
      color: 'from-cyan-500 to-blue-500'
    },
    {
      key: 'social_impact',
      title: 'Purpose Orientation',
      icon: Globe,
      leftLabel: 'Profit-First',
      rightLabel: 'Impact-First',
      leftDesc: 'Maximizes financial returns for stakeholders',
      rightDesc: 'Prioritizes social and environmental impact',
      color: 'from-teal-500 to-emerald-500'
    },
    {
      key: 'team_building',
      title: 'Team Preference',
      icon: Users,
      leftLabel: 'Solo/Small',
      rightLabel: 'Large Teams',
      leftDesc: 'Prefers working alone or with small teams',
      rightDesc: 'Builds and manages large organizations',
      color: 'from-violet-500 to-purple-500'
    },
    {
      key: 'market_timing',
      title: 'Market Entry',
      icon: Zap,
      leftLabel: 'Early Adopter',
      rightLabel: 'Mass Market',
      leftDesc: 'Enters emerging markets with early adopters',
      rightDesc: 'Waits for proven demand and enters mainstream',
      color: 'from-amber-500 to-yellow-500'
    }
  ];

  const getSliderPosition = (value) => {
    // Convert from -100 to +100 scale to 0 to 100 scale for slider
    return ((value + 100) / 2);
  };

  const getValueColor = (value) => {
    if (value < -30) return 'text-blue-600';
    if (value > 30) return 'text-orange-600';
    return 'text-gray-600';
  };

  const getInterpretation = (dimension, value) => {
    const isLeft = value < -20;
    const isRight = value > 20;
    const isCenter = !isLeft && !isRight;
    
    if (isCenter) {
      return `Balanced approach between ${dimension.leftLabel.toLowerCase()} and ${dimension.rightLabel.toLowerCase()}`;
    }
    
    return isLeft ? dimension.leftDesc : dimension.rightDesc;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5 text-primary" />
          Your Entrepreneur Profile
        </CardTitle>
        <CardDescription>
          A multi-dimensional view of your entrepreneurial characteristics and preferences
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {dimensions.map((dimension) => {
          const value = profile[dimension.key] || 0;
          const Icon = dimension.icon;
          
          return (
            <div key={dimension.key} className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-gray-600" />
                  <span className="font-medium text-sm">{dimension.title}</span>
                </div>
                <Badge variant="outline" className={getValueColor(value)}>
                  {value > 0 ? '+' : ''}{value}
                </Badge>
              </div>
              
              {/* Slider */}
              <div className="relative">
                <div className="flex justify-between text-xs text-gray-500 mb-2">
                  <span>{dimension.leftLabel}</span>
                  <span className="text-gray-400">Neutral</span>
                  <span>{dimension.rightLabel}</span>
                </div>
                
                <div className="relative h-2 bg-gray-200 rounded-full">
                  {/* Background gradient */}
                  <div className={`absolute inset-0 bg-gradient-to-r ${dimension.color} rounded-full opacity-20`} />
                  
                  {/* Center line */}
                  <div className="absolute left-1/2 top-0 w-0.5 h-full bg-gray-400 transform -translate-x-0.5" />
                  
                  {/* Value indicator */}
                  <div 
                    className={`absolute top-0 w-3 h-2 bg-gradient-to-r ${dimension.color} rounded-full transform -translate-x-1.5 transition-all duration-300`}
                    style={{ left: `${getSliderPosition(value)}%` }}
                  />
                </div>
                
                {/* Scale markers */}
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>-100</span>
                  <span>-50</span>
                  <span>0</span>
                  <span>+50</span>
                  <span>+100</span>
                </div>
              </div>
              
              {/* Interpretation */}
              <p className="text-xs text-gray-600 italic">
                {getInterpretation(dimension, value)}
              </p>
            </div>
          );
        })}
        
        {/* Profile Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-sm mb-2">Profile Insights</h4>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="font-medium">Strongest Tendencies:</span>
              <ul className="mt-1 space-y-1">
                {dimensions
                  .filter(d => Math.abs(profile[d.key] || 0) > 40)
                  .slice(0, 3)
                  .map(d => {
                    const value = profile[d.key] || 0;
                    const label = value > 0 ? d.rightLabel : d.leftLabel;
                    return (
                      <li key={d.key} className="text-gray-600">
                        • {label} ({d.title})
                      </li>
                    );
                  })}
              </ul>
            </div>
            <div>
              <span className="font-medium">Balanced Areas:</span>
              <ul className="mt-1 space-y-1">
                {dimensions
                  .filter(d => Math.abs(profile[d.key] || 0) <= 20)
                  .slice(0, 3)
                  .map(d => (
                    <li key={d.key} className="text-gray-600">
                      • {d.title}
                    </li>
                  ))}
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default EntrepreneurProfileSliders;

