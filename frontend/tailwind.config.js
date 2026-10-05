/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        bridge: {
          deep:     "#0A121C",
          base:     "#0E1926",
          surface:  "#132233",
          border:   "#1F3047",
          muted:    "#2A3D52",
          
          text:     "#D8E1EC",
          dim:      "#7D8FA3",
          faint:    "#4A5C73",
          
          primary:  "#4A9EFF",
          ice:      "#6FB3E0",
          
          success:  "#4A8B5E",
          warning:  "#D49A3A",
          danger:   "#C1444A",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
