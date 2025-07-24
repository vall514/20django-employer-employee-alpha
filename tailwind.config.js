/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './accounts/templates/**/*.html',
    './core/templates/**/*.html',
    './employees/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#003366', // Darker blue
          light: '#004E9A',
          dark: '#002347',
          hover: '#00407A',
        },
        secondary: {
          DEFAULT: '#0082B3', // Darker teal
          light: '#00A3D9',
          dark: '#006690',
        },
        background: {
          DEFAULT: '#E9ECEF', // Slightly darker background
          alt: '#D1D5DB',
          card: '#FFFFFF',
        },
        accent: {
          DEFAULT: '#FFA500',
          light: '#FFB52E',
          dark: '#E59400',
        },
        success: '#2E7D32',
        warning: '#F57C00',
        danger: '#D32F2F',
        disabled: '#B0BEC5',
        text: {
          primary: '#333333',
          secondary: '#757575',
          light: '#FFFFFF',
        }
      },
      fontFamily: {
        sans: ['Arial', 'Helvetica', 'sans-serif'],
        display: ['Roboto', 'Arial', 'sans-serif'],
      },
      borderRadius: {
        'sm': '0.25rem',
        'md': '0.375rem',
        'lg': '0.5rem',
        'xl': '1rem',
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'dropdown': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'button': '0 2px 4px rgba(0, 0, 0, 0.15)',
      },
      spacing: {
        'input-padding': '0.75rem',
        'button-padding-x': '1.25rem',
        'button-padding-y': '0.625rem',
        'layout-margin': '1.5rem',
        'layout-padding': '1rem',
        'section': '2rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
