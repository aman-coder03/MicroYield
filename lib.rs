#![no_std]

use soroban_sdk::{
    contract, contractimpl, contracttype, token,
    Address, Env, Map, Symbol
};

/// -------------------------------
/// DATA TYPES
/// -------------------------------

#[contracttype]
#[derive(Clone)]
pub struct UserBalance {
    pub amount: i128,
}

/// Storage keys
#[contracttype]
pub enum DataKey {
    Admin,
    Token,
    Balances,
}

/// -------------------------------
/// CONTRACT
/// -------------------------------

#[contract]
pub struct MicroYieldVault;

/// -------------------------------
/// IMPLEMENTATION
/// -------------------------------

#[contractimpl]
impl MicroYieldVault {

    /// Initialize the vault
    /// admin -> contract owner
    /// token -> stablecoin or XLM wrapped token address
    pub fn initialize(env: Env, admin: Address, token: Address) {
        if env.storage().instance().has(&DataKey::Admin) {
            panic!("Already initialized");
        }

        admin.require_auth();

        env.storage().instance().set(&DataKey::Admin, &admin);
        env.storage().instance().set(&DataKey::Token, &token);
        env.storage().instance().set(
            &DataKey::Balances,
            &Map::<Address, UserBalance>::new(&env),
        );
    }

    /// Deposit tokens into vault
    pub fn deposit(env: Env, user: Address, amount: i128) {
        user.require_auth();

        if amount <= 0 {
            panic!("Amount must be positive");
        }

        let token_address: Address = env
            .storage()
            .instance()
            .get(&DataKey::Token)
            .unwrap();

        let token_client = token::Client::new(&env, &token_address);

        // Transfer token from user to vault
        token_client.transfer(&user, &env.current_contract_address(), &amount);

        // Update internal vault balance
        let mut balances: Map<Address, UserBalance> = env
            .storage()
            .instance()
            .get(&DataKey::Balances)
            .unwrap();

        let mut user_balance = balances
            .get(user.clone())
            .unwrap_or(UserBalance { amount: 0 });

        user_balance.amount += amount;
        balances.set(user.clone(), user_balance);

        env.storage().instance().set(&DataKey::Balances, &balances);
    }

    /// Withdraw tokens from vault
    pub fn withdraw(env: Env, user: Address, amount: i128) {
        user.require_auth();

        if amount <= 0 {
            panic!("Invalid withdrawal amount");
        }

        let token_address: Address = env
            .storage()
            .instance()
            .get(&DataKey::Token)
            .unwrap();

        let token_client = token::Client::new(&env, &token_address);

        let mut balances: Map<Address, UserBalance> = env
            .storage()
            .instance()
            .get(&DataKey::Balances)
            .unwrap();

        let mut user_balance = balances
            .get(user.clone())
            .unwrap_or(UserBalance { amount: 0 });

        if user_balance.amount < amount {
            panic!("Insufficient vault balance");
        }

        user_balance.amount -= amount;
        balances.set(user.clone(), user_balance);

        env.storage().instance().set(&DataKey::Balances, &balances);

        // Transfer tokens back to user
        token_client.transfer(
            &env.current_contract_address(),
            &user,
            &amount,
        );
    }

    /// Get user vault balance
    pub fn balance(env: Env, user: Address) -> i128 {
        let balances: Map<Address, UserBalance> = env
            .storage()
            .instance()
            .get(&DataKey::Balances)
            .unwrap();

        balances
            .get(user)
            .unwrap_or(UserBalance { amount: 0 })
            .amount
    }

    /// Get vault total TVL
    pub fn total_value_locked(env: Env) -> i128 {
        let balances: Map<Address, UserBalance> = env
            .storage()
            .instance()
            .get(&DataKey::Balances)
            .unwrap();

        let mut total: i128 = 0;

        for (_, balance) in balances.iter() {
            total += balance.amount;
        }

        total
    }

    /// Admin only emergency withdrawal
    pub fn emergency_withdraw(env: Env, to: Address, amount: i128) {
        let admin: Address = env
            .storage()
            .instance()
            .get(&DataKey::Admin)
            .unwrap();

        admin.require_auth();

        let token_address: Address = env
            .storage()
            .instance()
            .get(&DataKey::Token)
            .unwrap();

        let token_client = token::Client::new(&env, &token_address);

        token_client.transfer(
            &env.current_contract_address(),
            &to,
            &amount,
        );
    }
}
