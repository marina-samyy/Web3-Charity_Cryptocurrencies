import json
from web3 import Web3
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import RPC_URL, CORE_ABI, COIN_ABI
    
def get_bytecode(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        bytecode = data.get('bytecode', '')
        if isinstance(bytecode, dict):
            return bytecode.get('object', '')
        return bytecode

w3 = Web3(Web3.HTTPProvider(RPC_URL))


if not w3.is_connected():
    print("ensure ganche is working")
    exit()

admin_account = w3.eth.accounts[0]

def deploy_contracts():
    print("\n Starting Deployment to Ganache...")


    COIN_BYTECODE = get_bytecode("contracts/abis/DonorCoin.json")
    Coin = w3.eth.contract(abi=COIN_ABI, bytecode=COIN_BYTECODE)
    
    tx_hash_coin = Coin.constructor().transact({'from': admin_account})
    coin_addr = w3.eth.wait_for_transaction_receipt(tx_hash_coin).contractAddress
    print(f" DonorCoin Deployed at: {coin_addr}")


    CORE_BYTECODE = get_bytecode("contracts/abis/CharityCore.json")
    Core = w3.eth.contract(abi=CORE_ABI, bytecode=CORE_BYTECODE)
    
    tx_hash_core = Core.constructor(coin_addr).transact({'from': admin_account})
    core_addr = w3.eth.wait_for_transaction_receipt(tx_hash_core).contractAddress
    print(f" CharityCore Deployed at: {core_addr}")

    print("\n" + "="*50)
    print(" take core address , coin")
    print(f"CORE_ADDRESS = \"{core_addr}\"")
    print(f"COIN_ADDRESS = \"{coin_addr}\"")
    print("="*50)
    
    return core_addr, coin_addr

if __name__ == "__main__":
    deploy_contracts()