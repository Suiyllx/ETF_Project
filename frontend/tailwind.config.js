/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  // 主题切换不走 Tailwind 的 dark: 前缀，而是用 CSS 变量 + html.light
  // 覆盖（默认深色，见 src/style.css）。darkMode:'class' 仅为未来需要
  // dark: 工具类时预留。
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg:      'var(--bg)',
        surface: { 1: 'var(--surface-1)', 2: 'var(--surface-2)', 3: 'var(--surface-3)' },
        label:   { 1: 'var(--label-1)', 2: 'var(--label-2)', 3: 'var(--label-3)' },
        hairline: 'var(--hairline)',
        glass:   { bg: 'var(--glass-bg)', border: 'var(--glass-border)' },
        sys: {
          blue:      'var(--sys-blue)',
          green:     'var(--sys-green)',
          red:       'var(--sys-red)',
          orange:    'var(--sys-orange)',
          blueDim:   'var(--sys-blue-dim)',
          greenDim:  'var(--sys-green-dim)',
          redDim:    'var(--sys-red-dim)',
          orangeDim: 'var(--sys-orange-dim)',
        },
      },
      boxShadow: {
        glass: 'var(--glass-shadow)',
      },
    },
  },
  plugins: [],
}
