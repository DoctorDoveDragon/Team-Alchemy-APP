import { useState, useEffect } from 'react'
import CitationStyleDropdown from './components/common/Dropdown/CitationStyleDropdown'
import VerificationButton from './components/common/Button/VerificationButton'
import MethodologyWizard from './components/academic/MethodologyWizard/MethodologyWizard'
import TeamAnalysisDashboard from './components/psychology/TeamAnalysis/TeamAnalysisDashboard'
import CaseStudiesBrowser from './components/psychology/CaseStudies/CaseStudiesBrowser'

function App() {
  const [selectedStyle, setSelectedStyle] = useState('APA')
  const [isVerified, setIsVerified] = useState(false)
  const [healthStatus, setHealthStatus] = useState(null)
  const [activeTab, setActiveTab] = useState('psychology')

  useEffect(() => {
    // Check backend health
    fetch('/healthz')
      .then(res => {
        if (!res.ok) {
          throw new Error(`Health check failed: ${res.status}`);
        }
        return res.json();
      })
      .then(data => setHealthStatus(data))
      .catch(err => {
        console.error('Health check failed:', err);
        setHealthStatus({
          status: 'unhealthy',
          error: err.message
        });
      });
  }, [])

  const handleVerification = async () => {
    // Simulate verification process
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsVerified(true)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-mustard-50 via-white to-emerald-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Team Alchemy APP
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Academic Collaboration & Research Platform
          </p>
          {healthStatus && (
            <div className={`mt-4 inline-flex items-center px-4 py-2 rounded-full ${
              healthStatus.status === 'unhealthy' 
                ? 'bg-crimson-100 dark:bg-crimson-900' 
                : 'bg-emerald-100 dark:bg-emerald-900'
            }`}>
              <span className={
                healthStatus.status === 'unhealthy'
                  ? 'text-crimson-800 dark:text-crimson-200'
                  : 'text-emerald-800 dark:text-emerald-200'
              }>
                {healthStatus.status === 'unhealthy' ? '✗' : '✓'} Backend: {healthStatus.status}
                {healthStatus.error && ` (${healthStatus.error})`}
              </span>
            </div>
          )}
        </header>

        {/* Tab Navigation */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex space-x-2 bg-white dark:bg-gray-800 rounded-lg shadow p-1">
            <button
              onClick={() => setActiveTab('psychology')}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'psychology'
                  ? 'bg-mustard-600 text-white'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Team Psychology
            </button>
            <button
              onClick={() => setActiveTab('cases')}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'cases'
                  ? 'bg-mustard-600 text-white'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Case Studies
            </button>
            <button
              onClick={() => setActiveTab('academic')}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'academic'
                  ? 'bg-mustard-600 text-white'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Academic Tools
            </button>
          </div>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Psychology Tab */}
          {activeTab === 'psychology' && (
            <TeamAnalysisDashboard />
          )}

          {/* Case Studies Tab */}
          {activeTab === 'cases' && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
                Psychological Case Studies
              </h2>
              <CaseStudiesBrowser />
            </div>
          )}

          {/* Academic Tools Tab */}
          {activeTab === 'academic' && (
            <div className="space-y-8">
              {/* Citation Style Selection */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
                  Citation Style
                </h2>
                <CitationStyleDropdown
                  selectedStyle={selectedStyle}
                  onStyleChange={setSelectedStyle}
                />
              </div>

              {/* Verification Section */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
                  Document Verification
                </h2>
                <VerificationButton
                  onVerify={handleVerification}
                  isVerified={isVerified}
                />
              </div>

              {/* Methodology Wizard */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
                  Research Methodology
                </h2>
                <MethodologyWizard />
              </div>
            </div>
          )}
        </div>

        <footer className="text-center mt-12 text-gray-600 dark:text-gray-400">
          <p>Powered by React + Vite + Tailwind CSS</p>
        </footer>
      </div>
    </div>
  )
}

export default App
