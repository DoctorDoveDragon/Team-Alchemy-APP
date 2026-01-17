import { useState } from 'react';
import MBTISelector from '../MBTISelector/MBTISelector';
import JungianProfile from '../JungianProfile/JungianProfile';

function TeamAnalysisDashboard() {
  const [selectedMBTI, setSelectedMBTI] = useState('');

  return (
    <div className="team-analysis-dashboard space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
          Team Alchemy Analysis
        </h2>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Explore psychological profiles, archetypes, and team dynamics using Jungian and Freudian frameworks.
        </p>

        <MBTISelector onSelect={setSelectedMBTI} selectedType={selectedMBTI} />
      </div>

      {selectedMBTI && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <JungianProfile mbtiType={selectedMBTI} />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-mustard-50 to-mustard-100 dark:from-mustard-900 dark:to-mustard-800 p-6 rounded-lg">
          <h3 className="font-semibold text-mustard-900 dark:text-mustard-100 mb-2">
            Psychological Profiles
          </h3>
          <p className="text-sm text-mustard-700 dark:text-mustard-200">
            Comprehensive Jungian function stacks and archetype mappings for all 16 MBTI types
          </p>
        </div>

        <div className="bg-gradient-to-br from-crimson-50 to-crimson-100 dark:from-crimson-900 dark:to-crimson-800 p-6 rounded-lg">
          <h3 className="font-semibold text-crimson-900 dark:text-crimson-100 mb-2">
            Case Studies
          </h3>
          <p className="text-sm text-crimson-700 dark:text-crimson-200">
            Historical case studies with proven interventions and measurable outcomes
          </p>
        </div>

        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900 dark:to-emerald-800 p-6 rounded-lg">
          <h3 className="font-semibold text-emerald-900 dark:text-emerald-100 mb-2">
            Defense Mechanisms
          </h3>
          <p className="text-sm text-emerald-700 dark:text-emerald-200">
            Freudian analysis of defense mechanisms with adaptiveness scoring
          </p>
        </div>
      </div>
    </div>
  );
}

export default TeamAnalysisDashboard;
