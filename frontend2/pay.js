// Require authentication
requireAuth();

/**
 * Handle payment submission
 */
async function makePayment() {
  const investToggle = document.getElementById("investToggle");
  const statusElement = document.getElementById("paymentStatus");
  
  // Show processing status
  statusElement.style.display = "block";
  statusElement.style.color = "var(--primary-cyan)";
  statusElement.textContent = "Processing payment...";

  try {
    // Determine if user wants to invest
    const shouldInvest = investToggle.checked;

    // Make payment request
    // Backend expects query params, not JSON
    const roundoff_option = shouldInvest ? "invest" : "none";

    // Replace with real Stellar public key of merchant
    const merchantPublicKey = "GXXXXXXXXXXXXXXXXXXXXXXXXXXXX";

    const response = await apiRequest(
      `/wallet/pay?destination=${merchantPublicKey}&amount=7&roundoff_option=${roundoff_option}`,
      "POST"
    );

    // Show success message
    statusElement.style.color = "var(--primary-teal)";
    
    if (shouldInvest) {
      statusElement.textContent = `✅ Payment successful! 7 XLM paid, 3 XLM invested into vault.`;
    } else {
      statusElement.textContent = `✅ Payment successful! 7 XLM paid to Cafe Stellar.`;
    }

    // Optional: Redirect after successful payment
    setTimeout(() => {
      if (confirm("Payment complete! View your vault?")) {
        window.location.href = "vault.html";
      } else {
        window.location.href = "dashboard.html";
      }
    }, 2000);

  } catch (error) {
    console.error("Payment error:", error);
    statusElement.style.color = "#ff6b6b";
    statusElement.textContent = `❌ Payment failed: ${error.message}`;
  }
}
