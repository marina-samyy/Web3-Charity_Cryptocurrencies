import json
import os
import sys


RPC_URL = "http://127.0.0.1:7545"


ADMIN_ADDRESS = "0xC0c3effF21D39ea1FeD8E90cc6729dEA1b50b758"
ADMIN_PRIVATE_KEY = "0x8db2a6c197e750f14694e36fb63ed6089945e65cba45d6be3012d1d8dd77903e"
ADMIN_SECRET_PASSWORD = "admin123"


CORE_ADDRESS = "0x5bF55903d07A4ACC0F0aaC1dCc9DBD69D4CA41fb"
COIN_ADDRESS = "0x0C6ce50848150eA05e3dfE22c251fE057d6606D6"



def load_abi(file_name):
    base_path = r"C:\Users\Matrix\OneDrive\Desktop\project crypto"
    file_path = os.path.join(base_path, "contracts", "abis", file_name)
    
    print(f" Testing path: {file_path}")
    
    try:
        if not os.path.exists(file_path):
            print(f" File not found at path!")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "abi" in data:
                return data["abi"]
            else:
                return data
    except Exception as e:
        print(f" Error: {e}")
        return None


CORE_ABI = load_abi("CharityCore.json")
COIN_ABI = load_abi("DonorCoin.json")


if CORE_ABI is None or COIN_ABI is None:
    print("\n" + "!"*60)
    print("FATAL ERROR: Could not load Smart Contract ABIs.")
    print("Check if the folder exists at the path printed above.")
    print("!"*60)
    sys.exit(1)
else:
    print(" ABIs loaded successfully!")