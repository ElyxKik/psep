/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      './templates/*.html',
      './node_modules/flowbite/**/*.js'
  ],
  theme: {
    screens: {
      'md': '640px',
      // => @media (min-width: 640px) { ... }

      'lg': '1024px',
      // => @media (min-width: 1024px) { ... }

      'xl': '1280px',
      // => @media (min-width: 1280px) { ... }
    },
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')({
      charts: true,
  }),
  ],
}

