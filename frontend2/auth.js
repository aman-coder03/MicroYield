/**
 * Handle login form submission
 * @param {Event} event - Form submit event
 */
async function login(event) {
  event.preventDefault(); // Prevent form from refreshing page

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const errorMessage = document.getElementById("errorMessage");
  const loadingMessage = document.getElementById("loadingMessage");

  // Hide previous messages
  errorMessage.style.display = "none";
  loadingMessage.style.display = "block";

  // Basic validation
  if (!email || !password) {
    errorMessage.textContent = "Please enter both email and password";
    errorMessage.style.display = "block";
    loadingMessage.style.display = "none";
    return;
  }

  try {
    const response = await apiRequest("/auth/login", "POST", { 
      email, 
      password 
    });

    if (response.access_token) {
      // Store token
      localStorage.setItem("token", response.access_token);
      
      // Store user info if available
      if (response.user) {
        localStorage.setItem("user", JSON.stringify(response.user));
      }

      // Redirect to dashboard
      loadingMessage.textContent = "Login successful! Redirecting...";
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 500);
    } else {
      throw new Error("No access token received");
    }

  } catch (error) {
    console.error("Login error:", error);
    errorMessage.textContent = error.message || "Login failed. Please check your credentials.";
    errorMessage.style.display = "block";
    loadingMessage.style.display = "none";
  }
}

// Check if already logged in
if (isAuthenticated()) {
  window.location.href = "dashboard.html";
}
