import { useState, useEffect } from 'react'
import CitationStyleDropdown from './components/common/Dropdown/CitationStyleDropdown'
import VerificationButton from './components/common/Button/VerificationButton'
import MethodologyWizard from './components/academic/MethodologyWizard/MethodologyWizard'

function App() {
  const [selectedStyle, setSelectedStyle] = useState('APA')
  const [isVerified, setIsVerified] = useState(false)
  const [healthStatus, setHealthStatus] = useState(null)

  useEffect(() => {
    // Check backend health
    fetch('/healthz')
      .then(res => res.json())
      .then(data => setHealthStatus(data))
      .catch(err => console.error('Health check failed:', err))
  }, [])

  const handleVerification = async () => {
    // Simulate verification process
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsVerified(true)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Team Alchemy APP
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Academic Collaboration & Research Platform
          </p>
          {healthStatus && (
            <div className="mt-4 inline-flex items-center px-4 py-2 bg-green-100 dark:bg-green-900 rounded-full">
              <span className="text-green-800 dark:text-green-200">
                ✓ Backend: {healthStatus.status}
              </span>
            </div>
          )}
        </header>

        <div className="max-w-4xl mx-auto space-y-8">
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

        <footer className="text-center mt-12 text-gray-600 dark:text-gray-400">
          <p>Powered by React + Vite + Tailwind CSS</p>
        </footer>
      </div>
    </div>
  )
}

export default App
