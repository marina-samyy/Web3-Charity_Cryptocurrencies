import csv
from app.config import RPC_URL, COIN_ADDRESS, COIN_ABI
from web3 import Web3

def export_balances():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    coin = w3.eth.contract(address=COIN_ADDRESS, abi=COIN_ABI)
    
    addresses = w3.eth.accounts 
    
    with open('analysis/balances_snapshot.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Address', 'DonorCoin Balance'])
        for addr in addresses:
            bal = coin.functions.balanceOf(addr).call()
            writer.writerow([addr, bal])
    print(" Exported to analysis/balances_snapshot.csv")