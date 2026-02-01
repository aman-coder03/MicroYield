// Require authentication
requireAuth();

/**
 * Load vault data
 */
async function loadVault() {
  try {
    // Fetch vault summary data
    const data = await apiRequest("/vault/my-balance");

    document.getElementById("xlmSaved").textContent =
      `${data.on_chain_vault_balance || 0} XLM`;
    
    document.getElementById("principalVault").textContent = 
      `${data.principal || 0} USDC`;
    
    document.getElementById("yieldVault").textContent = 
      `${data.yield || 0} USDC`;

  } catch (error) {
    console.error("Error loading vault:", error);
    
    // Show error in UI
    const vaultContent = document.getElementById("vaultContent");
    vaultContent.innerHTML = `
      <div class="place-card">
        <div style="padding: 40px; text-align: center;">
          <p style="color: #ff6b6b; font-size: 16px;">
            ⚠️ Error loading vault data
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
    document.getElementById("xlmSaved").textContent = "-- XLM";
    document.getElementById("principalVault").textContent = "-- USDC";
    document.getElementById("yieldVault").textContent = "-- USDC";
  }
}

/**
 * Handle withdrawal
 */
async function withdraw() {
  const statusElement = document.getElementById("withdrawStatus");
  
  // Confirm withdrawal
  if (!confirm("Are you sure you want to withdraw your funds?")) {
    return;
  }

  statusElement.style.display = "block";
  statusElement.style.color = "var(--primary-cyan)";
  statusElement.textContent = "Processing withdrawal...";

  try {
    // Make withdrawal request
    const response = await apiRequest("/vault/withdraw", "POST");

    statusElement.style.color = "var(--primary-teal)";
    statusElement.textContent = `✅ Withdrawal successful! Amount: ${response.amount || 0} USDC`;

    // Reload vault data after 2 seconds
    setTimeout(() => {
      location.reload();
    }, 2000);

  } catch (error) {
    console.error("Withdrawal error:", error);
    statusElement.style.color = "#ff6b6b";
    statusElement.textContent = `❌ Withdrawal failed: ${error.message}`;
  }
}

// Load data when page loads
document.addEventListener("DOMContentLoaded", loadVault);
