import { useState } from 'react'
import citationStyles from '../../../data/citationStyles.sample.json'

const CitationStyleDropdown = ({ selectedStyle, onStyleChange }) => {
  const [isOpen, setIsOpen] = useState(false)

  const handleSelect = (styleId) => {
    onStyleChange(styleId)
    setIsOpen(false)
  }

  const selectedStyleData = citationStyles.find(s => s.id === selectedStyle.toLowerCase()) || citationStyles[0]

  return (
    <div className="relative inline-block text-left w-full max-w-md">
      <div>
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex justify-between w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white dark:bg-gray-700 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <span className="flex flex-col items-start">
            <span className="font-semibold">{selectedStyleData.name}</span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {selectedStyleData.fullName}
            </span>
          </span>
          <svg
            className={`-mr-1 ml-2 h-5 w-5 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>

      {isOpen && (
        <div className="origin-top-right absolute right-0 mt-2 w-full rounded-md shadow-lg bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 z-10">
          <div className="py-1" role="menu" aria-orientation="vertical">
            {citationStyles.map((style) => (
              <button
                key={style.id}
                onClick={() => handleSelect(style.id)}
                className={`${
                  selectedStyle.toLowerCase() === style.id
                    ? 'bg-gray-100 dark:bg-gray-600 text-gray-900 dark:text-white'
                    : 'text-gray-700 dark:text-gray-200'
                } group flex flex-col w-full px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-600 text-left`}
                role="menuitem"
              >
                <span className="font-semibold">{style.name}</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {style.description}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default CitationStyleDropdown
