import { useState } from 'react'

const METHODOLOGY_STEPS = [
  {
    id: 'approach',
    title: 'Research Approach',
    options: ['Quantitative', 'Qualitative', 'Mixed Methods']
  },
  {
    id: 'design',
    title: 'Research Design',
    options: ['Experimental', 'Survey', 'Case Study', 'Ethnographic', 'Action Research']
  },
  {
    id: 'data',
    title: 'Data Collection',
    options: ['Interviews', 'Questionnaires', 'Observations', 'Documents', 'Experiments']
  },
  {
    id: 'analysis',
    title: 'Data Analysis',
    options: ['Statistical', 'Thematic', 'Content Analysis', 'Discourse Analysis', 'Grounded Theory']
  }
]

const MethodologyWizard = () => {
  const [currentStep, setCurrentStep] = useState(0)
  const [selections, setSelections] = useState({})
  const [isComplete, setIsComplete] = useState(false)

  const handleSelect = (option) => {
    const stepId = METHODOLOGY_STEPS[currentStep].id
    setSelections(prev => ({ ...prev, [stepId]: option }))
  }

  const handleNext = () => {
    if (currentStep < METHODOLOGY_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      setIsComplete(true)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
      setIsComplete(false)
    }
  }

  const handleReset = () => {
    setCurrentStep(0)
    setSelections({})
    setIsComplete(false)
  }

  const currentStepData = METHODOLOGY_STEPS[currentStep]
  const currentSelection = selections[currentStepData?.id]
  const canProceed = currentSelection !== undefined

  if (isComplete) {
    return (
      <div className="space-y-6">
        <div className="bg-emerald-50 dark:bg-emerald-900 border border-emerald-200 dark:border-emerald-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-emerald-800 dark:text-emerald-200 mb-4">
            ✓ Methodology Defined
          </h3>
          <div className="space-y-2 text-emerald-700 dark:text-emerald-300">
            {METHODOLOGY_STEPS.map(step => (
              <div key={step.id} className="flex items-center">
                <span className="font-medium w-40">{step.title}:</span>
                <span className="text-emerald-900 dark:text-emerald-100 font-semibold">
                  {selections[step.id]}
                </span>
              </div>
            ))}
          </div>
        </div>
        <button
          onClick={handleReset}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
        >
          Start Over
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Step {currentStep + 1} of {METHODOLOGY_STEPS.length}
          </span>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {Math.round(((currentStep + 1) / METHODOLOGY_STEPS.length) * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
          <div
            className="bg-mustard-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentStep + 1) / METHODOLOGY_STEPS.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Current Step */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-white">
          {currentStepData.title}
        </h3>
        
        <div className="grid grid-cols-1 gap-3">
          {currentStepData.options.map((option) => (
            <button
              key={option}
              onClick={() => handleSelect(option)}
              className={`
                p-4 rounded-lg border-2 text-left transition-all
                ${currentSelection === option
                  ? 'border-mustard-500 bg-mustard-50 dark:bg-mustard-900/20'
                  : 'border-gray-200 dark:border-gray-600 hover:border-mustard-300 dark:hover:border-mustard-700'
                }
              `}
            >
              <span className={`font-medium ${
                currentSelection === option
                  ? 'text-mustard-700 dark:text-mustard-300'
                  : 'text-gray-700 dark:text-gray-300'
              }`}>
                {option}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between pt-4">
        <button
          onClick={handlePrevious}
          disabled={currentStep === 0}
          className="px-4 py-2 bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-800 dark:text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>
        <button
          onClick={handleNext}
          disabled={!canProceed}
          className="px-6 py-2 bg-mustard-600 hover:bg-mustard-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {currentStep === METHODOLOGY_STEPS.length - 1 ? 'Complete' : 'Next'}
        </button>
      </div>
    </div>
  )
}

export default MethodologyWizard
