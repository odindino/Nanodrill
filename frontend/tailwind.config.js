/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          primary: {
            DEFAULT: '#1976D2',
            light: '#64B5F6',
            dark: '#0D47A1',
          },
          secondary: {
            DEFAULT: '#F57C00',
            light: '#FFB74D',
            dark: '#E65100',
          },
        },
      },
    },
    plugins: [],
  }