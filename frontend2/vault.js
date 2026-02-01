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
      `-- USDC`;

    document.getElementById("yieldVault").textContent = 
      `-- USDC`;

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
  const amount = parseFloat(document.getElementById("withdrawAmount").value);
  const statusElement = document.getElementById("withdrawStatus");

  if (!amount || amount <= 0) {
    alert("Enter valid amount");
    return;
  }

  statusElement.style.display = "block";
  statusElement.style.color = "var(--primary-cyan)";
  statusElement.textContent = "Processing withdrawal...";

  try {
    await apiRequest("/vault/withdraw", "POST", {
      amount: amount
    });

    statusElement.style.color = "var(--primary-teal)";
    statusElement.textContent = "✅ Withdrawal successful!";

    setTimeout(() => {
      loadVault();
      document.getElementById("withdrawAmount").value = "";
    }, 1500);

  } catch (error) {
    statusElement.style.color = "#ff6b6b";
    statusElement.textContent = `❌ Withdrawal failed: ${error.message}`;
  }
}


// Load data when page loads
document.addEventListener("DOMContentLoaded", loadVault);
