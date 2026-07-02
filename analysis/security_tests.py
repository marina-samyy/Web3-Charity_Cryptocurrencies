from web3 import Web3
from app.config import RPC_URL, CORE_ADDRESS, CORE_ABI

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def run_audit():
    if not CORE_ADDRESS or CORE_ADDRESS == "0x...":
        return " Error: CORE_ADDRESS not set in config.py"

    core = w3.eth.contract(address=CORE_ADDRESS, abi=CORE_ABI)
    admin = w3.eth.accounts[0]
    hacker = w3.eth.accounts[1]
    
    results = []
    results.append(f"Audit Target: {CORE_ADDRESS}")

    # Test: Access Control
    try:
        core.functions.addCampaign("Hacker Campaign", 999).transact({'from': hacker})
        results.append("SECURITY BREACH: Unauthorized user added a campaign!")
    except Exception as e:
        results.append(" PASS: Unauthorized access blocked (Reverted).")

    return "\n".join(results)

if __name__ == "__main__":
    print(run_audit())