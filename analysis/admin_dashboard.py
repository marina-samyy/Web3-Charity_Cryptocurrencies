from web3 import Web3
from collections import Counter
from app.config import RPC_URL, CORE_ADDRESS, COIN_ADDRESS, CORE_ABI, COIN_ABI

class AdminAnalytics:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.core = self.w3.eth.contract(address=CORE_ADDRESS, abi=CORE_ABI)
        self.coin = self.w3.eth.contract(address=COIN_ADDRESS, abi=COIN_ABI)

    def get_dashboard_data(self):
        if not self.w3.is_connected():
            return None

        latest_block = self.w3.eth.block_number
        total_tx = 0
        sender_counts = Counter()

        # Scanning the blockchain
        for block_num in range(0, latest_block + 1):
            block = self.w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                if tx['to'] and tx['to'].lower() == CORE_ADDRESS.lower():
                    total_tx += 1
                    sender_counts[tx['from']] += 1

        top_3 = sender_counts.most_common(3)
        
        return {
            "admin": self.core.functions.getAdmin().call(),
            "campaigns_count": self.core.functions.getCampaignCount().call(),
            "total_minted": self.coin.functions.totalSupply().call() / (10**18),
            "total_transactions": total_tx,
            "top_users": top_3
        }