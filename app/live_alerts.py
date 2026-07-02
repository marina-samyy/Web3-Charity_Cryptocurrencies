from app.config import RPC_URL, CORE_ADDRESS, CORE_ABI
import time

def monitor_donations(callback_func):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=CORE_ADDRESS, abi=CORE_ABI)
    
    event_filter = contract.events.DonationMade.create_filter(from_block='latest')
    
    while True:
        for event in event_filter.get_new_entries():
            callback_func(event['args'])
        time.sleep(2) # فحص كل ثانيتين
