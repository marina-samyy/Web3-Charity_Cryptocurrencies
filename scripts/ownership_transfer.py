# scripts/ownership_transfer.py
from web3 import Web3
from app.config import RPC_URL, CORE_ADDRESS, CORE_ABI

def transfer_admin(new_admin_address, private_key):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=CORE_ADDRESS, abi=CORE_ABI)
    admin_account = w3.eth.account.from_key(private_key)

    print(f" Transferring ownership to: {new_admin_address}")
    
    tx = contract.functions.transferOwnership(new_admin_address).build_transaction({
        'from': admin_account.address,
        'nonce': w3.eth.get_transaction_count(admin_account.address),
        'gas': 100000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f" Transfer Tx Sent: {w3.to_hex(tx_hash)}")

if __name__ == "__main__":
    pass