from web3 import Web3
from app.config import RPC_URL, CORE_ADDRESS, CORE_ABI

class HistoryReporter:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.core = self.w3.eth.contract(address=CORE_ADDRESS, abi=CORE_ABI)

    def generate_text_report(self, filename="analysis/report.txt"):
        count = self.core.functions.getCampaignCount().call()
        with open(filename, "w", encoding="utf-8") as f:
            f.write("="*55 + "\n")
            f.write("       CHARITY TRACKER — FUNDS RAISED REPORT\n")
            f.write("="*55 + "\n")
            f.write(f"{'ID':<4} {'Campaign Name':<22} {'Raised':>8} {'Goal':>8} {'Status'}\n")
            f.write("-" * 55 + "\n")
            
            for i in range(count):
                c = self.core.functions.campaigns(i).call()
                status = "Active" if c[3] else "Paused"
                f.write(f"{i:<4} {c[0]:<22} {c[2]:>8} {c[1]:>8}   {status}\n")
            
            f.write("="*55 + "\n")
        return filename