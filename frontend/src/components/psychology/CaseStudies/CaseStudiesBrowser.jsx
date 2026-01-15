import { useState, useEffect } from 'react';

function CaseStudiesBrowser() {
  const [studies, setStudies] = useState([]);
  const [selectedStudy, setSelectedStudy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStudies = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/api/v1/psychology/case-studies');
        if (!response.ok) {
          throw new Error(`Failed to fetch case studies: ${response.status}`);
        }
        const data = await response.json();
        setStudies(data);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching case studies:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStudies();
  }, []);

  const fetchStudyDetails = async (studyId) => {
    try {
      const response = await fetch(`/api/v1/psychology/case-studies/${studyId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch study details: ${response.status}`);
      }
      const data = await response.json();
      setSelectedStudy(data);
    } catch (err) {
      console.error('Error fetching study details:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md p-4">
        <p className="text-red-800 dark:text-red-200">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="case-studies-browser">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Studies List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Available Case Studies
          </h3>
          <div className="space-y-3">
            {studies.map((study) => (
              <div
                key={study.id}
                onClick={() => fetchStudyDetails(study.id)}
                className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow cursor-pointer hover:shadow-md transition-shadow border-2 border-transparent hover:border-indigo-500"
              >
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                  {study.title}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {study.summary}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-2 py-1 rounded">
                    {study.framework}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(study.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Study Details */}
        <div>
          {selectedStudy ? (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                {selectedStudy.title}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Framework
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400">{selectedStudy.framework}</p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Subject Profile
                  </h4>
                  <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                    <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {JSON.stringify(selectedStudy.profile, null, 2)}
                    </pre>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Interventions
                  </h4>
                  <ul className="space-y-1">
                    {selectedStudy.interventions.map((intervention, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-indigo-600 dark:text-indigo-400 mr-2">→</span>
                        <span className="text-gray-700 dark:text-gray-300">{intervention}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Outcomes
                  </h4>
                  <div className="space-y-2">
                    {Object.entries(selectedStudy.outcomes).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {typeof value === 'number' ? `${(value * 100).toFixed(0)}%` : value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg text-center">
              <p className="text-gray-500 dark:text-gray-400">
                Select a case study to view details
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CaseStudiesBrowser;
