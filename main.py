from dotenv import load_dotenv
import os
import time
import subprocess
from web3 import Web3

# --- CONFIG ---
RPC_URL = "https://blockchain.googleapis.com/v1/projects/forward-garden-300612/locations/us-central1/endpoints/ethereum-sepolia/rpc?key=AIzaSyA1HjwEETcJWJAA1hR3QsnQ_CNa11BC61o"

load_dotenv('accounts.txt')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# Token addresses for balance display in the menu
TOKENS = {
    "ETH": None,
    "USDT": "0xee0418Bd560613fbcF924C36235AB1ec301D4933",
    "USDC": "0x77Ef087024f87976aaDA0aA7f73Bb8eAe6E9Dda1",
    "USDS": "0xF85938e2Bfc178026f60c5Ea50cC347D42C73b3D",
    "USDZ": "0x55Cc481D28Db3f1ffc9347745AA6fbB940505BdD"
}

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

ERC20_ABI = [{"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}]

def get_token_balance(token_addr):
    try:
        if not token_addr: # For ETH
            return w3.from_wei(w3.eth.get_balance(account.address), 'ether')
        contract = w3.eth.contract(address=w3.to_checksum_address(token_addr), abi=ERC20_ABI)
        return contract.functions.balanceOf(account.address).call() / 10**18
    except:
        return 0.0

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header():
    clear_console()
    print("="*50)
    print(f"       STABILIZER TESTNET MANAGER v2.0")
    print(f" Wallet: {account.address[:10]}...{account.address[-8:]}")
    print("="*50)
    print(" CURRENT BALANCES:")
    for name, addr in TOKENS.items():
        bal = get_token_balance(addr)
        print(f" [{name}]: {bal:,.2f}")
    print("="*50)

def run_script(script_name, args=None):
    try:
        print(f"\n🚀 Running module: {script_name}...")
        
        # Build the command list
        command = ["python", script_name]
        
        # If arguments (like amount) are provided, add them to the command
        if args:
            command.extend(args)
            
        # Execute the script with arguments
        subprocess.run(command, check=True)
        
        input("\n✅ Module finished. Press Enter to return to menu...")
    except Exception as e:
        print(f"\n❌ Error executing {script_name}: {e}")
        input("\nPress Enter to continue...")

def main():
    while True:
        show_header()
        print(" [1] 🎁 Claim All Tokens")
        print(" [2] 🔄 Volume Boost 2,000,000")
        print(" [3] ⚖️ Balancing & Pools")
        print(" [0] 🚪 Exit")
        print("="*50)
        
        choice = input(" Select action: ")

        if choice == "1":
            run_script("claim.py")
        elif choice == "2":
            # Sub-step: Get the amount from the user
            amount = input(" Enter USDT amount for swap (e.g., 5000): ")
            
            # Basic validation to ensure the amount is a number
            if amount.replace('.', '', 1).isdigit():
                print(f"🚀 Starting swap for {amount} USDT...")
                run_script("swap2M.py", [amount])
            else:
                print("\n⚠️ Invalid amount. Please enter a number.")
                time.sleep(1)
                
        elif choice == "3":
            run_script("liquidity.py")
        elif choice == "0":
            print("\nGood luck with the testnet! 🚀")
            break
        else:
            print("\n⚠️ Invalid choice, please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()
