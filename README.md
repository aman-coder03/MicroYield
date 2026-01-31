# 🚀 MicroYield

**Save spare change. Earn stable yield. Spend seamlessly — powered by Stellar.**

MicroYield is a Web3-powered savings and micropayment platform built on Stellar that enables users to save, invest, and transact seamlessly — without needing to understand blockchain.

---

## 🌍 Vision

MicroYield simplifies access to decentralized financial infrastructure for everyday users in APAC by:

- Automating micro-savings
- Converting deposits into stablecoin (USDC)
- Providing a vault-based savings model
- Enabling ultra-low-fee micropayments

All powered by the Stellar network.

---

## 🧠 What MicroYield Does

MicroYield allows users to:

- Sign up using email/password (Web2 UX)
- Automatically generate a custodial Stellar wallet
- Send and receive XLM payments
- Deposit funds into a centralized vault
- Convert vault holdings into stablecoin (USDC)
- Track vault balances separately from wallet balance
- Interact with real on-chain transactions (Testnet)

---

## 🏗 System Architecture

### Backend
- FastAPI
- SQLAlchemy (SQLite)
- JWT Authentication
- Encrypted custodial wallet storage
- Stellar SDK integration

### Blockchain Layer
- Stellar Testnet
- Real wallet creation
- XLM transfers
- Custom USDC asset issuance
- Trustline setup
- Stablecoin minting

---

## 🔐 Security Model

MicroYield currently uses a custodial model:

- User wallets generated server-side
- Secret keys encrypted using Fernet
- Secrets stored securely in database
- JWT-protected routes
- No private key exposure to client

Production roadmap includes:
- Secure key vault
- Role-based access
- Smart contract-based vault logic
- Audits

---

## 💼 Wallet Architecture

Each user has:

- 1 Stellar wallet
- Encrypted secret key
- Public key stored in DB

System-level wallets:

- Vault Wallet (holds pooled funds)
- Issuer Wallet (mints USDC stablecoin)

---

## 🪙 Stablecoin Architecture

MicroYield implements a proper Stellar asset structure:

1. Dedicated Issuer account
2. Vault trustline to USDC asset
3. Minting of USDC to vault
4. Future XLM → USDC conversion logic

This mirrors real-world stablecoin architecture.

---

## 🏦 Vault System

The Vault:

- Receives deposits from users (XLM)
- Records deposits in database
- Holds USDC stablecoin
- Tracks per-user vault balance
- Separates wallet balance from savings balance

Vault Endpoints:
- `POST /vault/deposit`
- `GET /vault/my-balance`
- `POST /vault/setup-trustline`
- `POST /vault/mint-usdc`

---

## 🔄 Current Features

### ✅ Authentication
- Email/password login
- JWT token system
- Protected routes

### ✅ Wallet Management
- Wallet creation
- Testnet funding
- Balance checking
- Peer-to-peer XLM transfers

### ✅ Vault
- Deposit to vault
- On-chain transfer tracking
- Stablecoin issuance setup
- User-level vault balance tracking

---

## 📡 API Overview

### Auth
POST /auth/login


### Wallet
POST /wallet/create
POST /wallet/fund
POST /wallet/send
GET /wallet/balance


### Vault
POST /vault/deposit
GET /vault/my-balance
POST /vault/setup-trustline
POST /vault/mint-usdc


---

## 💰 Business Model

MicroYield plans to generate revenue via:

- 0.5% performance fee on yield
- Vault management fee
- Marketplace transaction fees
- Premium analytics
- Merchant subscriptions

---

## 🎯 Target Audience

Primary:
- Young professionals in APAC
- New-to-crypto users
- Gig workers
- Cross-border earners

Secondary:
- Content creators
- Educators
- Small digital merchants

---

## 🌟 Why Stellar?

- Extremely low fees (0.00001 XLM)
- Fast settlement
- Asset issuance built-in
- Stablecoin friendly
- Ideal for micropayments
- Designed for cross-border use cases

---

## 🔮 Roadmap

### Phase 1 (Current)
- Custodial wallet system
- Vault deposit logic
- USDC asset issuance
- On-chain transactions

### Phase 2
- XLM → USDC automated conversion
- Yield simulation engine
- Vault withdrawal
- Frontend dashboard

### Phase 3
- Soroban smart contract vault
- Stablecoin DeFi integration
- APAC fiat on-ramp
- Mobile app

---

## 🛠 Installation

```
git clone <repo>
cd MicroYield
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
## Disclaimer
This is a prototype built on Stellar Testnet.

- Not production-ready

- No real assets involved

- For demonstration and grant purposes

## Built With
FastAPI
Stellar SDK
SQLAlchemy
Python
SQLite
JWT
Cryptography

## Status
Core blockchain infrastructure
Stablecoin issuance system
Vault logic
Next milestone: Yield engine & frontend dashboard


---

## 👥 Team

- **Aman Srivastava**  
  GitHub: https://github.com/aman-coder03  

- **Ipshit Singh**  
  GitHub: https://github.com/ipshitsingh27  

- **Aditya Mittal**
  Github: https://github.com/Aditya3960
---

## 🔮 Vision

MicroYield aims to become the default Web3 savings gateway for the next billion users embedding decentralized finance into familiar financial habits and making global yield accessible to everyone through Stellar-powered infrastructure.

---
