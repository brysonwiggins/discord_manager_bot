from datetime import datetime
import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import hashlib
import requests
###########
from models.DailyStats import DailyStats
from models.answer import Answer

MODES = ["classic", "quote", "ability", "emoji", "splash"]
DAILY_STATS_FOLDER = "stats_by_day" # Folder to store submissions


def get_today_date():
    """Returns today's date as a string in 'YYYY-MM-DD' format."""
    return datetime.now().strftime("%Y-%m-%d")


def save_submission(user_id, data):
    filename = f"{DAILY_STATS_FOLDER}/{get_today_date()}.json"
    
    if os.path.exists(filename):
        saved_data = read_json_file(filename)
        for submission in saved_data:
            if(submission["userId"] == user_id):
                print("ERROR DUPLICATE SUBMISSION")
                return
    else:
        saved_data = []
    
    jsonObj = DailyStats(user_id, data)

    saved_data.append(jsonObj.__dict__)

    write_json_file(filename, saved_data)

def get_submissions_by_date(date: str):
    filename = f"{DAILY_STATS_FOLDER}/{date}.json"

    if os.path.exists(filename):
        saved_data = read_json_file(filename)
    else:
        saved_data = []

    return saved_data


def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                print("The JSON file doesn't contain an array.")
                return []
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return []
    
def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_todays_answers():
    answers = Answer(get_today_date())
    for mode in MODES:
        print(mode)
        if mode == "ability" or mode == "splash":
            response = requests.get(f"https://loldle.apimeko.link/games/{mode}/answer?utc=-6")
        else:
            response = requests.get(f"https://loldle.apimeko.link/games/{mode}/answer/name?utc=-6")
        
        if response.status_code == 200:
            dataString = decrypt_data(response.text)
            data = json.loads(dataString)
            if mode == "ability":
                answers.set(mode, [data["champion_name"], data[mode + "_letter"]])
            elif mode == "splash":
                answers.set(mode, [data["champion_name"], data[mode + "_name"]])
            else:
                answers.set(mode, data["champion_name"])
        else:
            print("FAILED TO FETCH DATA")
            print(response.reason)
    return answers

def evp_bytes_to_key(password, key_len, iv_len, salt, hash_algo='md5'):
    password = password.encode('utf-8')
    derived_data = b''
    block = None

    while len(derived_data) < key_len + iv_len:
        if block is None:
            block = password + salt
        else:
            block = block + password + salt
        block = hashlib.new(hash_algo, block).digest()
        derived_data += block

    return derived_data[:key_len], derived_data[key_len:key_len + iv_len]


def decrypt_data(encrypted_text):
    key = hashlib.md5(os.getenv("ENCRYPT_KEY").encode()).digest()

    encrypted_data = base64.b64decode(encrypted_text)
        
    # Extract the IV from the encrypted data (assuming it's prepended)
    if encrypted_data[:8] != b"Salted__":
        raise ValueError("Missing salt in encrypted data")
    salt = encrypted_data[8:16]
    encrypted_message = encrypted_data[16:]

    key, iv = evp_bytes_to_key(os.getenv("ENCRYPT_KEY"), key_len=32, iv_len=16, salt=salt)

    # Create the AES cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the encrypted message
    decrypted_data = unpad(cipher.decrypt(encrypted_message), AES.block_size)

    return decrypted_data.decode('utf-8')