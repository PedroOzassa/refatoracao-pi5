// Frontend configuration
const CONFIG = {
  // Backend API base URL
  API_BASE_URL: 'http://localhost:8000',
  
  // Health check interval (milliseconds)
  HEALTH_CHECK_INTERVAL: 10000,
  
  // Request timeout (milliseconds)
  REQUEST_TIMEOUT: 30000,
  
  // UI Settings
  UI: {
    maxMessages: 100,
    autoScroll: true,
    typingIndicatorDuration: 500,
  }
};

// Export for use in index.html
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}
