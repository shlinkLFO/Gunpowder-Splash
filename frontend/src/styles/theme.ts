import { createSystem, defaultConfig } from '@chakra-ui/react'

const customConfig = {
  ...defaultConfig,
  theme: {
    tokens: {
      colors: {
        midnight: {
          900: { value: '#1B102A' },
          800: { value: '#2D1B47' },
          700: { value: '#4E2A84' },
          600: { value: '#7F5AA2' },
          500: { value: '#B8A1D9' },
          400: { value: '#E8D9FF' },
          300: { value: '#9D7BC0' },
        },
      },
      fonts: {
        heading: { value: `'Crimson Text', 'Times New Roman', Times, serif` },
        body: { value: `'Crimson Text', 'Times New Roman', Times, serif` },
      },
    },
  },
}

export const system = createSystem(customConfig)
export default system
