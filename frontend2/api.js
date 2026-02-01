const API_BASE =
  window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "https://microyield.onrender.com"; // change this



/**
 * Make API request with proper error handling
 * @param {string} endpoint - API endpoint (e.g., "/auth/login")
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {object} body - Request body (optional)
 * @returns {Promise<object>} Response data
 */
async function apiRequest(endpoint, method = "GET", body = null) {
  try {
    const token = localStorage.getItem("token");
    
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
      }
    };

    // Add Authorization header if token exists
    if (token) {
      options.headers["Authorization"] = `Bearer ${token}`;
    }

    // Add body if provided
    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);
    
    // Check if response is ok
    if (!response.ok) {
      // Try to get error message from response
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    // Parse JSON response
    const data = await response.json();
    return data;

  } catch (error) {
    console.error("API Request Error:", error);
    throw error;
  }
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
function isAuthenticated() {
  return localStorage.getItem("token") !== null;
}

/**
 * Redirect to login if not authenticated
 */
function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = "login.html";
  }
}

/**
 * Logout user
 */
function logout() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}
