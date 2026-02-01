// Require authentication
requireAuth();

/**
 * Load yield data
 */
async function loadYield() {
  const apyElement = document.getElementById("apy");
  const distributedElement = document.getElementById("distributed");
  const yieldContent = document.getElementById("yieldContent");

  try {
    // Try to fetch from backend
    const data = await apiRequest("/vault/apy");

    // If backend returns valid data
    apyElement.textContent = `${data.apy ?? 8.0}%`;
    distributedElement.textContent =
      `${data.total_distributed ?? 0} USDC`;

  } catch (error) {
    console.warn("APY endpoint not available, using fallback values.");

    // Fallback values (safe mode)
    apyElement.textContent = "8.0%";
    distributedElement.textContent = "On-chain";

    // Optional: Show subtle warning (without breaking UI)
    const cards = yieldContent.querySelectorAll(".place-card");
    if (cards.length >= 2) {
      const warning = document.createElement("p");
      warning.textContent = "⚠ Live APY unavailable (backend endpoint missing)";
      warning.style.color = "#ff6b6b";
      warning.style.fontSize = "12px";
      warning.style.marginTop = "10px";
      warning.style.opacity = "0.8";

      cards[1].querySelector("div").appendChild(warning);
    }
  }
}

// Load data when page loads
document.addEventListener("DOMContentLoaded", loadYield);
