/**
 * Design System Theme Configuration
 * 
 * Defines the color palette and theme constants for the Team Alchemy APP
 */

export const colors = {
  primary: 'mustard',
  secondary: 'crimson',
  success: 'emerald',
  neutral: 'gray',
};

export const colorValues = {
  primary: '#D4AF37',
  secondary: '#DC2626',
  success: '#10B981',
};

export const semanticColors = {
  // Action colors
  action: {
    primary: 'mustard-600',
    hover: 'mustard-700',
    disabled: 'gray-400',
  },
  
  // State colors
  state: {
    success: 'emerald-500',
    warning: 'mustard-500',
    error: 'crimson-500',
    info: 'gray-500',
  },
  
  // Function stack colors (for Jungian profiles)
  functions: {
    dominant: 'mustard-500',
    auxiliary: 'emerald-500',
    tertiary: 'gray-400',
    inferior: 'crimson-500',
  },
};

export const gradients = {
  primary: 'from-mustard-50 to-white',
  secondary: 'from-crimson-50 to-white',
  success: 'from-emerald-50 to-white',
  mixed: 'from-mustard-50 via-white to-emerald-50',
};

export default {
  colors,
  colorValues,
  semanticColors,
  gradients,
};
