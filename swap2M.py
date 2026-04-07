import sys
import os
import time
import math
from dotenv import load_dotenv
from web3 import Web3

# Load environment variables
load_dotenv('accounts.txt')

# Configuration
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
RPC_URL = "https://blockchain.googleapis.com/v1/projects/forward-garden-300612/locations/us-central1/endpoints/ethereum-sepolia/rpc?key=AIzaSyA1HjwEETcJWJAA1hR3QsnQ_CNa11BC61o"
TOTAL_GOAL_VOLUME = 2000000 

# --- Handling Argument from Main Menu ---
if len(sys.argv) > 1:
    try:
        AMOUNT_PER_SWAP = float(sys.argv[1])
    except ValueError:
        print("Invalid amount passed. Using default 30000.")
        AMOUNT_PER_SWAP = 30000
else:
    AMOUNT_PER_SWAP = 30000
# ----------------------------------------

# Addresses
ROUTER_ADDR = "0xFa6419a3d3503a016dF3A59F690734862CA2A78D"
USDT = "0xee0418Bd560613fbcF924C36235AB1ec301D4933"
USDC = "0x77Ef087024f87976aaDA0aA7f73Bb8eAe6E9Dda1"
USDS = "0xF85938e2Bfc178026f60c5Ea50cC347D42C73b3D"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# ABIs
ROUTER_ABI = [
    {
        "inputs": [
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenOut", "type": "address"},
            {"name": "amountIn", "type": "uint256"},
            {"name": "minAmountOut", "type": "uint256"}
        ],
        "name": "swap",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

router_contract = w3.eth.contract(address=w3.to_checksum_address(ROUTER_ADDR), abi=ROUTER_ABI)

def run_swap(token_in, token_out, amount_human, label, nonce):
    t_in_contract = w3.eth.contract(address=w3.to_checksum_address(token_in), abi=ERC20_ABI)
    decimals = t_in_contract.functions.decimals().call()
    amount_in_wei = int(amount_human * (10**decimals))

    # Building transaction
    tx = router_contract.functions.swap(
        w3.to_checksum_address(token_in),
        w3.to_checksum_address(token_out),
        amount_in_wei,
        0
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 800000,
        'gasPrice': int(w3.eth.gas_price * 1.5),
        'chainId': 11155111
    })
    
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"🚀 [{label}] Swapping {amount_human}. Hash: {w3.to_hex(tx_hash)}")
    return w3.eth.wait_for_transaction_receipt(tx_hash)

def main():
    print(f"\n[INFO] Target Volume: {TOTAL_GOAL_VOLUME}")
    print(f"[INFO] Amount per Swap: {AMOUNT_PER_SWAP}")
    
    # Calculate circles (1 circle = 3 swaps: USDT->USDC->USDS->USDT)
    needed_circles = math.ceil(TOTAL_GOAL_VOLUME / (AMOUNT_PER_SWAP * 3))
    current_nonce = w3.eth.get_transaction_count(account.address)

    for i in range(1, needed_circles + 1):
        print(f"\n💎 CYCLE {i}/{needed_circles}")
        steps = [
            (USDT, USDC, "USDT -> USDC"),
            (USDC, USDS, "USDC -> USDS"),
            (USDS, USDT, "USDS -> USDT")
        ]
        for t_in, t_out, lbl in steps:
            try:
                receipt = run_swap(t_in, t_out, AMOUNT_PER_SWAP, lbl, current_nonce)
                if receipt.status == 1:
                    current_nonce += 1
                    print(f"✅ Success: {lbl}")
                    time.sleep(2)
                else:
                    print(f"❌ Transaction failed in {lbl}. Check your balance for {t_in}.")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Error during {lbl}: {e}")
                sys.exit(1)

    print("\n🎉 Volume Boost Completed!")

if __name__ == "__main__":
    main()
