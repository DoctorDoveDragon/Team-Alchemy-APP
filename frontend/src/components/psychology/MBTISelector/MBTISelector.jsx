import { useState } from 'react';
import PropTypes from 'prop-types';

const MBTI_TYPES = [
  'INTJ', 'INTP', 'ENTJ', 'ENTP',
  'INFJ', 'INFP', 'ENFJ', 'ENFP',
  'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
  'ISTP', 'ISFP', 'ESTP', 'ESFP'
];

function MBTISelector({ onSelect, selectedType }) {
  const [localType, setLocalType] = useState(selectedType || '');

  const handleSelect = (type) => {
    setLocalType(type);
    if (onSelect) {
      onSelect(type);
    }
  };

  return (
    <div className="mbti-selector">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Select MBTI Type
      </label>
      <div className="grid grid-cols-4 gap-2">
        {MBTI_TYPES.map((type) => (
          <button
            key={type}
            onClick={() => handleSelect(type)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              localType === type
                ? 'bg-mustard-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            {type}
          </button>
        ))}
      </div>
    </div>
  );
}

MBTISelector.propTypes = {
  onSelect: PropTypes.func.isRequired,
  selectedType: PropTypes.string,
};

export default MBTISelector;
