// Require authentication
requireAuth();

/**
 * Handle payment submission
 */

async function makePayment() {
  const destination = document.getElementById("destination").value.trim();
  const amount = parseFloat(document.getElementById("amount").value);
  const investToggle = document.getElementById("investToggle");
  const statusElement = document.getElementById("paymentStatus");

  if (!destination || !amount || amount <= 0) {
    alert("Enter valid destination and amount");
    return;
  }

  statusElement.style.display = "block";
  statusElement.style.color = "var(--primary-cyan)";
  statusElement.textContent = "Processing payment...";

  try {
    const response = await apiRequest("/wallet/pay", "POST", {
      destination: destination,
      amount: amount,
      roundoff_option: investToggle.checked ? "invest" : "none"
    });

    statusElement.style.color = "var(--primary-teal)";
    statusElement.textContent = "✅ Payment successful!";

  } catch (error) {
    statusElement.style.color = "#ff6b6b";
    statusElement.textContent = `❌ Payment failed: ${error.message}`;
  }
}

document.getElementById("amount").addEventListener("input", function() {
  const amount = parseFloat(this.value);
  if (!amount) return;

  let rounded;
  if (amount < 500) {
    rounded = Math.ceil(amount);
  } else if (amount <= 10000) {
    rounded = Math.ceil(amount / 10) * 10;
  } else {
    rounded = Math.ceil(amount / 100) * 100;
  }

  const roundoff = (rounded - amount).toFixed(7);

  document.querySelector("#investToggle + span").innerText =
    `Invest ${roundoff} XLM into USDC Vault`;
});
