import os

import robin_stocks.robinhood as r


def login_to_robinhood():
    # try:
    # Fetch credentials from environment variables
    username = os.getenv("ROBINHOOD_USERNAME")
    password = os.getenv("ROBINHOOD_PASSWORD")

    if not username or not password:
        raise ValueError("Environment variables for username or password are not set.")

    # Prompt for MFA code if needed
    # mfa_code = input("Enter your 2FA code (if enabled): ")

    # Login to Robinhood
    login = r.authentication.login(
        username=username,
        password=password,
        expiresIn=86400,  # Session duration in seconds
        store_session=True,
        # mfa_code=mfa_code
    )
    print("Login successful!")
    return login
    # except Exception as e:
    #     print(f"Login failed: {e} - {login}")
    #     return None


# Step 2: Get Account Details
def get_account_data():
    try:
        profile = r.profiles.load_account_profile()
        positions = r.account.build_holdings()
        buying_power = r.profiles.load_portfolio_profile()["buying_power"]

        print("Account Profile:", profile)
        print("Portfolio Holdings:", positions)
        print("Buying Power:", buying_power)
    except Exception as e:
        print(f"Error fetching account data: {e}")


# Step 3: Get All Transactions
def get_transactions():
    try:
        orders = r.orders.get_all_stock_orders()
        crypto_orders = r.crypto.get_crypto_orders()

        print("Stock Orders:", orders)
        print("Crypto Orders:", crypto_orders)
    except Exception as e:
        print(f"Error fetching transactions: {e}")


# Main Function
if __name__ == "__main__":
    # Login and fetch data
    if login_to_robinhood():
        get_account_data()
        get_transactions()
