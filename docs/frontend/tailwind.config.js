/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        agri: {
          50: '#f4f8f5',
          100: '#e8f0ea',
          200: '#d3e1d6',
          300: '#b5c9ba',
          400: '#8fa996',
          500: '#647f6b',
          600: '#4f6956',
          700: '#3f5445',
          800: '#334438',
          900: '#29372d',
          950: '#1f2923',
        },

        darkbg: '#f6f8f7',
        cardbg: '#ffffff',
        bordergray: '#e2e7e3',

        textprimary: '#1f2933',
        textsecondary: '#667085',

        blueaccent: '#2563eb',
        bluebg: '#eff6ff',

        success: '#15803d',
        warning: '#d97706',
        danger: '#dc2626',
      }
    },
  },
  plugins: [],
}