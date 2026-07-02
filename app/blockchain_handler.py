from web3 import Web3
from config import (
    RPC_URL,
    CORE_ADDRESS,
    CORE_ABI,
    COIN_ADDRESS,
    COIN_ABI
)

import time


class BlockchainHandler:

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))

        if not self.w3.is_connected():
            raise Exception(
                " Failed To Connect To Blockchain. "
                "Make Sure Ganache Is Running."
            )

        self.charity_contract = self.w3.eth.contract(
            address=CORE_ADDRESS,
            abi=CORE_ABI
        )

        self.coin_contract = self.w3.eth.contract(
            address=COIN_ADDRESS,
            abi=COIN_ABI
        )

    def _send_transaction(
        self,
        function_call,
        address,
        priv_key
    ):

        nonce = self.w3.eth.get_transaction_count(address)

        tx = function_call.build_transaction({
            "from": address,
            "nonce": nonce,
            "gas": 2000000,
            "gasPrice": self.w3.to_wei("20", "gwei")
        })

        signed_tx = self.w3.eth.account.sign_transaction(
            tx,
            private_key=priv_key
        )

        tx_hash = self.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        return self.w3.eth.wait_for_transaction_receipt(
            tx_hash
        )

    def add_campaign_tx(
        self,
        admin_address,
        priv_key,
        name,
        goal_eth
    ):

        goal_wei = self.w3.to_wei(goal_eth, "ether")

        func = self.charity_contract.functions.addCampaign(
            name,
            goal_wei
        )

        return self._send_transaction(
            func,
            admin_address,
            priv_key
        )

    def mint_donor_coins(
        self,
        admin_address,
        priv_key,
        to_address,
        amount
    ):

        amount_wei = self.w3.to_wei(amount, "ether")

        func = self.coin_contract.functions.mint(
            to_address,
            amount_wei
        )

        return self._send_transaction(
            func,
            admin_address,
            priv_key
        )

    def toggle_pause(
        self,
        admin_address,
        priv_key,
        should_pause
    ):

        if should_pause:
            func = self.charity_contract.functions.pause()

        else:
            func = self.charity_contract.functions.resume()

        return self._send_transaction(
            func,
            admin_address,
            priv_key
        )

    def register_user_tx(
        self,
        user_address,
        priv_key,
        name
    ):

        func = self.charity_contract.functions.registerUser(
            name
        )

        return self._send_transaction(
            func,
            user_address,
            priv_key
        )

    def send_donation_tx(
        self,
        user_address,
        priv_key,
        campaign_id,
        amount_coin
    ):

        amount_wei = self.w3.to_wei(
            amount_coin,
            "ether"
        )

        approve_func = self.coin_contract.functions.approve(
            CORE_ADDRESS,
            amount_wei
        )

        self._send_transaction(
            approve_func,
            user_address,
            priv_key
        )

        donate_func = self.charity_contract.functions.donate(
            campaign_id,
            amount_wei
        )

        return self._send_transaction(
            donate_func,
            user_address,
            priv_key
        )


    def get_balances(self, address):

        eth_balance = self.w3.eth.get_balance(address)

        coin_balance = (
            self.coin_contract.functions.balanceOf(
                address
            ).call()
        )

        return {
            "eth": self.w3.from_wei(
                eth_balance,
                "ether"
            ),

            "coin": self.w3.from_wei(
                coin_balance,
                "ether"
            )
        }

    def get_all_campaigns(self):

        count = (
            self.charity_contract.functions
            .getCampaignsCount()
            .call()
        )

        campaigns = []

        for i in range(count):

            details = (
                self.charity_contract.functions
                .getCampaignDetails(i)
                .call()
            )

            campaigns.append({
                "id": i,
                "name": details[0],

                "goal": self.w3.from_wei(
                    details[1],
                    "ether"
                ),

                "raised": self.w3.from_wei(
                    details[2],
                    "ether"
                ),

                "active": details[3]
            })

        return campaigns

    def scan_history(self, target_address):
        """
        Search Blockchain For User Transaction History
        """

        history = []

        donation_events = (
            self.charity_contract.events
            .DonationReceived
            .get_logs(
                from_block=0,
                argument_filters={
                    "donor": target_address
                }
            )
        )

        for event in donation_events:

            history.append({
                "block": event["blockNumber"],

                "type": "Donation",

                "value": self.w3.from_wei(
                    event["args"]["amount"],
                    "ether"
                ),

                "campaign_id": (
                    event["args"]["campaignId"]
                )
            })

        return sorted(
            history,
            key=lambda x: x["block"],
            reverse=True
        )

    def get_system_stats(self):
        """
        Get System Statistics
        """

        total_campaigns = (
            self.charity_contract.functions
            .getCampaignsCount()
            .call()
        )

        # NOTE:
        total_minted = (
            self.coin_contract.functions
            .totalSupply()
            .call()
        )

        all_donations = (
            self.charity_contract.events
            .DonationReceived
            .get_logs(
                from_block=0
            )
        )

        return {

            "total_campaigns": total_campaigns,

            "total_minted": self.w3.from_wei(
                total_minted,
                "ether"
            ),

            "total_transactions": len(
                all_donations
            )
        }


    def batch_add_campaigns_tx(
        self,
        admin_address,
        priv_key,
        names,
        goals_eth
    ):


        goals_wei = [
            self.w3.to_wei(goal, "ether")
            for goal in goals_eth
        ]


        print("\n DEBUG INFO")
        print("Sender:", admin_address)

        print(
            "Contract Admin:",
            self.charity_contract.functions
            .getAdmin()
            .call()
        )

        nonce = self.w3.eth.get_transaction_count(
            admin_address
        )

        tx = (
            self.charity_contract.functions
            .batchAdminOperations(
                names,
                goals_wei
            )
            .build_transaction({

                "from": admin_address,
                "nonce": nonce,
                "gas": 6000000,

                "gasPrice": self.w3.to_wei(
                    "20",
                    "gwei"
                )
            })
        )

        signed_tx = (
            self.w3.eth.account.sign_transaction(
                tx,
                private_key=priv_key
            )
        )

        tx_hash = self.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = (
            self.w3.eth.wait_for_transaction_receipt(
                tx_hash
            )
        )

        return receipt
    
    def get_contract_owner(self):

        try:
            return self.charity_contract.functions.owner().call()
        except Exception as e:
            try:
                return self.charity_contract.functions.getAdmin().call()
            except:
                print(f" Error fetching owner: {e}")
                return None