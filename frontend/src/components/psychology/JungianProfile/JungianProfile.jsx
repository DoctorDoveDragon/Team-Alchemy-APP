import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

function JungianProfile({ mbtiType }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!mbtiType) {
      setProfile(null);
      return;
    }

    const fetchProfile = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/v1/psychology/jungian/profile/${mbtiType}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch profile: ${response.status}`);
        }
        const data = await response.json();
        setProfile(data);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching Jungian profile:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [mbtiType]);

  if (!mbtiType) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-8">
        Select an MBTI type to view the Jungian profile
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-mustard-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-crimson-50 dark:bg-crimson-900 border border-crimson-200 dark:border-crimson-700 rounded-md p-4">
        <p className="text-crimson-800 dark:text-crimson-200">Error: {error}</p>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <div className="jungian-profile space-y-6">
      {/* Header */}
      <div className="bg-mustard-50 dark:bg-mustard-900 rounded-lg p-4">
        <h3 className="text-xl font-bold text-mustard-900 dark:text-mustard-100">
          {profile.mbti_type} - Jungian Profile
        </h3>
      </div>

      {/* Function Stack */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
          Cognitive Function Stack
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="bg-blue-50 dark:bg-blue-900 p-3 rounded-md">
            <p className="text-sm font-medium text-blue-900 dark:text-blue-100">Dominant</p>
            <p className="text-lg text-blue-800 dark:text-blue-200">{profile.dominant_function}</p>
          </div>
          <div className="bg-emerald-50 dark:bg-emerald-900 p-3 rounded-md">
            <p className="text-sm font-medium text-emerald-900 dark:text-emerald-100">Auxiliary</p>
            <p className="text-lg text-emerald-800 dark:text-emerald-200">{profile.auxiliary_function}</p>
          </div>
          <div className="bg-yellow-50 dark:bg-yellow-900 p-3 rounded-md">
            <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">Tertiary</p>
            <p className="text-lg text-yellow-800 dark:text-yellow-200">{profile.tertiary_function}</p>
          </div>
          <div className="bg-crimson-50 dark:bg-crimson-900 p-3 rounded-md">
            <p className="text-sm font-medium text-crimson-900 dark:text-crimson-100">Inferior</p>
            <p className="text-lg text-crimson-800 dark:text-crimson-200">{profile.inferior_function}</p>
          </div>
        </div>
      </div>

      {/* Archetype Affinities */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
          Archetype Affinities
        </h4>
        <div className="flex flex-wrap gap-2">
          {profile.archetype_affinity.map((archetype) => (
            <span
              key={archetype}
              className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full text-sm font-medium"
            >
              {archetype}
            </span>
          ))}
        </div>
      </div>

      {/* Strengths */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
          Strengths
        </h4>
        <ul className="space-y-2">
          {profile.strengths.map((strength, index) => (
            <li key={index} className="flex items-start">
              <span className="text-emerald-600 dark:text-emerald-400 mr-2">✓</span>
              <span className="text-gray-700 dark:text-gray-300">{strength}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Shadow */}
      <div>
        <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
          Shadow Aspects
        </h4>
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-md">
          <p className="text-gray-700 dark:text-gray-300">{profile.shadow}</p>
        </div>
      </div>
    </div>
  );
}

JungianProfile.propTypes = {
  mbtiType: PropTypes.string,
};

export default JungianProfile;
