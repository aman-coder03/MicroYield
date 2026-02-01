// Require authentication
requireAuth();

/**
 * Handle payment submission
 */

async function makePayment() {
  const investToggle = document.getElementById("investToggle");
  const statusElement = document.getElementById("paymentStatus");

  statusElement.style.display = "block";
  statusElement.style.color = "var(--primary-cyan)";
  statusElement.textContent = "Processing payment...";

  try {
    const shouldInvest = investToggle.checked;

    const response = await apiRequest("/wallet/pay", "POST", {
      destination: "GAHR3XVY4E7IASHKMCF2IZF5X7JJ42J2QHX7HQ55A74V2KIE7SCX7HFK",
      amount: 7,
      invest: shouldInvest
    });

    statusElement.style.color = "var(--primary-teal)";
    statusElement.textContent = "✅ Payment successful!";

    setTimeout(() => {
      window.location.href = shouldInvest ? "vault.html" : "dashboard.html";
    }, 2000);

  } catch (error) {
    statusElement.style.color = "#ff6b6b";
    statusElement.textContent = `❌ Payment failed: ${error.message}`;
  }
}
