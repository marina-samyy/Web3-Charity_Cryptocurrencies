import time
import sys
import os
from tabulate import tabulate
from blockchain_handler import BlockchainHandler
from config import ADMIN_ADDRESS, ADMIN_PRIVATE_KEY, ADMIN_SECRET_PASSWORD


handler = BlockchainHandler()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(user_name="Guest"):
    print("="*60)
    print(f" CHARITY DONATION TRACKER | Welcome, {user_name} ")
    print("="*60)




def user_registration_flow():
    clear_screen()
    print_header()
    print("\n[!] It seems you are not registered yet.")

    name = input("Enter your display name to register: ")
    address = input("Enter your wallet address: ")
    priv_key = input("Enter your private key: ")

    print("\n Registering on-chain...")
    try:
        handler.register_user_tx(address, priv_key, name)
        print(" Registration Successful!")
        return name, address, priv_key
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def show_user_menu(user_name, user_address, priv_key):
    while True:
        clear_screen()
        print_header(user_name)

        print("1. View Campaigns & Donate")
        print("2. My Personal Activity History")
        print("3. Check Balances (Coin & ETH)")
        print("4. Logout")

        choice = input("\nSelect an option: ")

       
        if choice == "1":
            campaigns = handler.get_all_campaigns()

            table = []
            for c in campaigns:
                if not c['active'] or c['raised'] >= c['goal']:
                    status = " Closed"
                else:
                    status = " Active"
                
                table.append([
                    c['id'],
                    c['name'],
                    f"{c['goal']} DNR",
                    f"{c['raised']} DNR",
                    status
                ])

            print("\n" + tabulate(
                table,
                headers=["ID", "Name", "Goal", "Raised", "Status"],
                tablefmt="grid"
            ))

            c_id = input("\nEnter Campaign ID to donate (or 'b' to go back): ")
            if c_id.lower() != 'b':
                try:
                    selected = next((c for c in campaigns if str(c['id']) == c_id), None)
                    
                    if not selected:
                        print("incorrect the number of Campaign")
                    
                    elif not selected['active'] or selected['raised'] >= selected['goal']:
                        print("\n" + "!" * 45)
                        print("closed ")
                        print(" bec :(Goal Reached).")
                        print("!" * 45)
                    
                    else:
                        amount = input("Enter amount of Donor Coins: ")
                        
                        remaining = selected['goal'] - selected['raised']
                        
                        if float(amount) > remaining:
                            print(f" Error: Amount too large! The campaign only needs [Amount] : {remaining} DNR .")
                        else:
                            handler.send_donation_tx(
                                user_address,
                                priv_key,
                                int(c_id),
                                float(amount)
                            )
                            print(" Donation Successful! Thank you for your kindness.")
                            
                except Exception as e:
                    print(f" Transaction Failed: {e}")

            input("\nPress Enter to continue...")

        elif choice == "2":
            print(f"\n Scanning history for {user_address}...")
            history = handler.scan_history(user_address)

            if history:
                table = [
                    [
                        h['block'],
                        h['type'],
                        f"{h['value']} DNR",
                        f"Campaign #{h['campaign_id']}"
                    ]
                    for h in history
                ]

                print("\n" + tabulate(
                    table,
                    headers=["Block", "Action", "Value", "Details"],
                    tablefmt="pretty"
                ))
            else:
                print("\nNo activity found for this address.")

            input("\nPress Enter to continue...")

        elif choice == "3":
            balances = handler.get_balances(user_address)

            table = [
                ["Donor Coin Balance", f"{balances['coin']} DNR"],
                ["ETH Balance", f"{balances['eth']} ETH"]
            ]

            print("\n" + tabulate(
                table,
                headers=["Asset", "Amount"],
                tablefmt="fancy_grid"
            ))

            input("\nPress Enter to continue...")

        elif choice == "4":
            break





def show_admin_menu():
    input_address = input("\n Enter Admin Wallet Address: ").strip()
    password = input(" Enter Admin Secret Password: ").strip()

    try:
        current_onchain_admin = handler.charity_contract.functions.getAdmin().call()
    except Exception:
        current_onchain_admin = handler.charity_contract.functions.owner().call()

    print(f"\n--- Debugging Info ---")
    print(f"Address You Entered: [{input_address.lower()}]")
    print(f"Admin on Blockchain: [{current_onchain_admin.lower()}]")
    print(f"Password in Config:  [{ADMIN_SECRET_PASSWORD}]")
    print(f"Password You Entered: [{password}]")
    print(f"----------------------\n")



    if (
        input_address.lower() != current_onchain_admin.lower() 
        or password != ADMIN_SECRET_PASSWORD
    ):
        print(" Access Denied: Authentication Failed.")
        time.sleep(3)
        return

    while True:
        clear_screen()
        print_header("ADMIN PANEL")


        print(f"Status:  Authenticated as Authorized Controller")
        print("-" * 20)
        print("1. Add New Charity Campaign (Single)")
        print("2. Mint Donor Coins (Give to Users)")
        print("3. Emergency Stop (Pause/Resume)")
        print("4. View System Stats & Top 3 Donors")
        print("5. Transfer Ownership (Move Admin Rights)")
        print("6. Batch Add Campaigns")
        print("7. Back to Main Menu")

        choice = input("\nSelect Admin Action: ")


        if choice == "1":
            name = input("Campaign Name: ")
            goal = input("Goal Amount (DNR): ")
            try:
                handler.add_campaign_tx(
                    ADMIN_ADDRESS,
                    ADMIN_PRIVATE_KEY,
                    name,
                    float(goal)
                )
                print(" Campaign Added Successfully On-Chain!")
            except Exception as e:
                print(f" Error: {e}")
            input("\nPress Enter...")


        elif choice == "2":
            target = input("User Address To Receive Coins: ")
            amount = input("Amount To Mint: ")
            try:
                handler.mint_donor_coins(
                    ADMIN_ADDRESS,
                    ADMIN_PRIVATE_KEY,
                    target,
                    float(amount)
                )
                print(f" Minted {amount} DNR To {target}")
            except Exception as e:
                print(f" Minting Failed: {e}")
            input("\nPress Enter...")


        elif choice == "3":
            is_paused = handler.charity_contract.functions.paused().call()
            action = "Resume" if is_paused else "Pause"
            confirm = input(f"Are You Sure You Want To {action}? (y/n): ")
            if confirm.lower() == "y":
                try:
                    handler.toggle_pause(
                        ADMIN_ADDRESS,
                        ADMIN_PRIVATE_KEY,
                        not is_paused
                    )
                    print(f" System {action}d Successfully.")
                except Exception as e:
                    print(f" Failed To {action}: {e}")
            input("\nPress Enter...")


        elif choice == "4":
            print("\n Scanning Blockchain For Full Report...")
            stats = handler.get_system_stats()
            print("\n --- ADMIN SYSTEM REPORT ---")
            report_data = [
                ["Total Charity Campaigns", stats["total_campaigns"]],
                ["Total Coins Minted", f"{stats['total_minted']} DNR"],
                ["Total On-Chain Transactions", stats["total_transactions"]]
            ]
            print(tabulate(report_data, tablefmt="fancy_grid"))
            print("\n Top 3 Most Active User Addresses:")
            try:
                top_users = handler.get_top_donors(limit=3)
            except Exception:
                top_users = None
            if top_users:
                print(tabulate(top_users, headers=["Address", "Total Donated"], tablefmt="pretty"))
            else:
                print("No Transactions Found Yet.")
            input("\nPress Enter...")


        elif choice == "5":
            new_admin = input("Enter NEW Admin Wallet Address: ").strip()
            confirm = input(" Are You Sure? You Will Lose Admin Rights! (y/n): ")

            if confirm.lower() == "y":
                try:
                    nonce = handler.w3.eth.get_transaction_count(ADMIN_ADDRESS)
                    
                    txn = handler.charity_contract.functions.transferOwnership(
                        new_admin
                    ).build_transaction({
                        'chainId': handler.w3.eth.chain_id,
                        'gas': 100000,
                        'gasPrice': handler.w3.eth.gas_price,
                        'nonce': nonce,
                    })

                    signed_txn = handler.w3.eth.account.sign_transaction(
                        txn, private_key=ADMIN_PRIVATE_KEY
                    )

                    tx_hash = handler.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                    print(f" Processing Transfer On-Chain... Hash: {tx_hash.hex()}")
                    handler.w3.eth.wait_for_transaction_receipt(tx_hash)

                    print(f" Ownership Transferred Successfully to: {new_admin}")
                    print(" Logging out as you are no longer the admin.")
                    time.sleep(3)
                    break 

                except Exception as e:
                    print(f" Transfer Failed: {e}")
            input("\nPress Enter...")

        elif choice == "6":
            names_input = input("Enter Names (Comma Separated): ")
            goals_input = input("Enter Goals In ETH (Comma Separated): ")
            names = [n.strip() for n in names_input.split(",")]
            goals = [float(g.strip()) for g in goals_input.split(",")]
            try:
                handler.batch_add_campaigns_tx(
                    ADMIN_ADDRESS,
                    ADMIN_PRIVATE_KEY,
                    names,
                    goals
                )
                print(" Batch Campaigns Added Successfully!")
            except Exception as e:
                print(f" Error: {e}")
            input("\nPress Enter...")


        elif choice == "7":
            print(" Exiting Admin Panel...")
            return
        else:
            print(" Invalid Choice.")
            input("\nPress Enter...")




# --- Main  Point ---

def main_menu():
    while True:
        clear_screen()
        print_header()

        print("1. Login as User")
        print("2. Login as Admin")
        print("3. Exit")

        role = input("\nWho are you? ")

        if role == "1":
            address = input("Enter your wallet address: ")
            name = handler.charity_contract.functions.userNames(address).call()

            if not name:
                name, address, priv_key = user_registration_flow()
            else:
                priv_key = input("Enter your private key to continue: ")

            show_user_menu(name, address, priv_key)

        elif role == "2":
            show_admin_menu()

        elif role == "3":
            print(" exit ")
            break


if __name__ == "__main__":
    main_menu()