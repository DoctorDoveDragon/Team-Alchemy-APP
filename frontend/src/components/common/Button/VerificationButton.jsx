import { useState } from 'react'

const VerificationButton = ({ onVerify, isVerified }) => {
  const [isLoading, setIsLoading] = useState(false)

  const handleClick = async () => {
    setIsLoading(true)
    try {
      await onVerify()
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={isLoading || isVerified}
      className={`
        relative inline-flex items-center px-6 py-3 rounded-lg font-medium text-white
        transition-all duration-200 transform
        ${isVerified 
          ? 'bg-emerald-500 hover:bg-emerald-600 cursor-default' 
          : 'bg-mustard-600 hover:bg-mustard-700 hover:scale-105 active:scale-95'
        }
        ${isLoading ? 'opacity-75 cursor-wait' : ''}
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-mustard-500
      `}
    >
      {isLoading && (
        <svg
          className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      
      {isVerified && (
        <svg
          className="mr-2 h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
      )}
      
      <span>
        {isLoading ? 'Verifying...' : isVerified ? 'Verified ✓' : 'Verify Document'}
      </span>
    </button>
  )
}

export default VerificationButton
