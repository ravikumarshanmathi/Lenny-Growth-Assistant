/**
 * API utility — fetch wrapper with base URL resolution and error handling.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Make a JSON API request to the backend.
 *
 * @param {string} path - API path (e.g., '/api/chat')
 * @param {object} options - Fetch options
 * @returns {Promise<object>} Parsed JSON response
 */
export async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(errorData.error?.message || `API error: ${response.status}`);
    error.status = response.status;
    error.code = errorData.error?.code;
    throw error;
  }

  return response.json();
}

/**
 * Health check — fetch backend status.
 */
export async function fetchHealth() {
  return apiFetch('/health');
}
