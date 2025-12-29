// src/api.js
import axios from 'axios';

// Backend API URL - configure via environment variable
// For local development: http://localhost:8000
// For production: Set REACT_APP_BACKEND_URL in Vercel environment variables
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL ||
  (process.env.NODE_ENV === 'production'
    ? 'https://your-backend-deployment.railway.app'  // Update this with your actual backend URL
    : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Send a message to the AI assistant
 * @param {string} message - User input message
 * @param {string|null} session_id - Optional session ID for chat persistence
 * @returns {Promise<{response: string, session_id: string}>}
 */
export const chatWithAI = async (message, session_id = null) => {
  try {
    const response = await api.post('/chat', {
      message,
      session_id,
    });

    // Support both standard Response and APIResponse formats
    if (response.data.status === 'success') {
      return response.data.data;
    }

    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error(error.response?.data?.message || 'Failed to connect to AI server');
  }
};

export default api;
