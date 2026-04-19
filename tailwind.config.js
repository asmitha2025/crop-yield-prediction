/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        "surface": "#0b1326",
        "surface-container-low": "#131b2e",
        "surface-container": "#171f33",
        "surface-container-high": "#222a3d",
        "surface-container-highest": "#2d3449",
        "primary": "#4edea3",
        "primary-container": "#10b981",
        "on-surface": "#dae2fd",
        "surface-variant": "#2d3449",
        "outline-variant": "rgba(60, 74, 66, 0.15)",
        "secondary-container": "#0566d9",
        "on-secondary-container": "#e6ecff",
        "tertiary": "#ffb95f",
      },
      fontFamily: {
        "headline": ["Plus Jakarta Sans", "sans-serif"],
        "body": ["Inter", "sans-serif"],
      }
    },
  },
  plugins: [],
}
