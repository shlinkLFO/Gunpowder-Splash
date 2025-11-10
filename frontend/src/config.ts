/**
 * Frontend configuration
 * Uses environment variables for flexibility across environments
 */

export const config = {
  // API base URL - defaults to relative path for dev proxy, absolute for production
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
  
  // WebSocket URL
  wsBaseUrl: import.meta.env.VITE_WS_BASE_URL || '/ws',
  
  // Environment
  environment: import.meta.env.MODE || 'development',
  
  // Feature flags
  enableNotebooks: true,
  enableDataExplorer: true,
  enableRainbowCSV: true,
}

export default config

