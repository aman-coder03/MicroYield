// Require authentication
requireAuth();

/**
 * Load dashboard data
 */
async function loadDashboard() {
  try {
    // Fetch vault summary data
    const data = await apiRequest("/vault/my-balance");

    // Update dashboard elements
    document.getElementById("totalVault").textContent =
      `${data.on_chain_vault_balance || 0} USDC`;

    document.getElementById("principal").textContent =
      `${data.on_chain_vault_balance || 0} USDC`;

    document.getElementById("yield").textContent =
      `On-chain`;

  } catch (error) {
    console.error("Error loading dashboard:", error);
    
    // Show error in UI
    const dashboardContent = document.getElementById("dashboardContent");
    dashboardContent.innerHTML = `
      <div class="place-card">
        <div style="padding: 40px; text-align: center;">
          <p style="color: #ff6b6b; font-size: 16px;">
            ⚠️ Error loading dashboard data
          </p>
          <p style="font-size: 14px; opacity: 0.7; margin-top: 10px;">
            ${error.message}
          </p>
          <button 
            onclick="location.reload()"
            style="margin-top: 20px; padding: 12px 24px; background: var(--primary-cyan); color: #0a1219; border: none; border-radius: 30px; cursor: pointer; font-weight: bold;"
          >
            Retry
          </button>
        </div>
      </div>
    `;

    // Set default values
    document.getElementById("totalVault").textContent = "-- USDC";
    document.getElementById("principal").textContent = "-- USDC";
    document.getElementById("yield").textContent = "-- USDC";
  }
}

// Load data when page loads
document.addEventListener("DOMContentLoaded", loadDashboard);
