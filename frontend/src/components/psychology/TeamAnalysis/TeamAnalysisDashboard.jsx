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
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800 p-6 rounded-lg">
          <h3 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">
            Psychological Profiles
          </h3>
          <p className="text-sm text-purple-700 dark:text-purple-200">
            Comprehensive Jungian function stacks and archetype mappings for all 16 MBTI types
          </p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-6 rounded-lg">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
            Case Studies
          </h3>
          <p className="text-sm text-blue-700 dark:text-blue-200">
            Historical case studies with proven interventions and measurable outcomes
          </p>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 p-6 rounded-lg">
          <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2">
            Defense Mechanisms
          </h3>
          <p className="text-sm text-green-700 dark:text-green-200">
            Freudian analysis of defense mechanisms with adaptiveness scoring
          </p>
        </div>
      </div>
    </div>
  );
}

export default TeamAnalysisDashboard;
