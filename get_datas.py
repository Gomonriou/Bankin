import requests
import json
from dotenv import load_dotenv
import os

def get_bearer(client_id, client_secret, Bankin_Device, email, password):
    url = "https://sync.bankin.com/v2/authenticate"

    custom_data = {
        "email":email,
        "password": password,
        'token':''
    }

    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'bankin-version': '2019-08-22',
        'client-id': client_id,
        'client-secret': client_secret,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'fr',
        'Bankin-Device':Bankin_Device,
        'Content-Type': 'application/json',
    }

    response = requests.post(url, headers=custom_headers, json=custom_data)
    
    data = response.json()
    bearer_token = data["access_token"]
    print('Token refresh')

    return bearer_token

def requete_data(bearer, client_id, client_secret):
    url = 'https://sync.bankin.com/v2/transactions'

    periods = [
        ('2024-09-01', '2024-09-30'),
        ('2024-10-01', '2024-10-31'),
        ('2024-11-01', '2024-11-30'),
        ('2024-12-01', '2024-12-31'),
        ('2025-01-01', '2025-01-31'),
        ('2025-02-01', '2025-02-28'),
        ('2025-03-01', '2025-03-31'),
        ('2025-04-01', '2025-04-30'),
        ('2025-05-01', '2025-05-31'),
        ('2025-06-01', '2025-06-30'),
        ('2025-07-01', '2025-07-31'),
    ]

    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'authorization': bearer,
        'bankin-version': '2019-08-22',
        'client-id': client_id,
        'client-secret': client_secret,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'fr',
    }

    all_data = []

    if os.path.exists(save_file):
        with open(save_file, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
                all_data.extend(old_data["resources"])
            except Exception:
                pass


    for since_str, until_str in periods:
        params = {
            'limit': 500,
            'since': since_str,
            'until': until_str,
        }

        response = requests.get(url, headers=custom_headers, params=params)
        
        max_attempts = 2
        for attempt in range(max_attempts):
            response = requests.get(url, headers=custom_headers, params=params)
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('resources', [])
                all_data.extend(transactions)
                print(f"Données de {since_str} à {until_str} : {len(transactions)} éléments")
            elif response.status_code == 401 and attempt == 0:
                bearer = "Bearer " + get_bearer(client_id, client_secret, Bankin_Device, email, password)
            else:
                raise Exception(f"Erreur {response.status_code}: {response.text}")

    with open(save_file, "w", encoding="utf-8") as json_file:
        json.dump({"resources": all_data}, json_file, indent=4, ensure_ascii=False)
        print('Datas saved data.json')

    return all_data


def get_datas(update_data=False):
    if update_data :
        bearer = "Bearer " + get_bearer(client_id, client_secret, Bankin_Device, email, password)
        requete_data(bearer, client_id, client_secret)
        with open(save_file, 'r', encoding='utf-8') as fichier:
            datas = json.load(fichier)
            return datas
    else :
        with open(save_file, 'r', encoding='utf-8') as fichier:
            datas = json.load(fichier)
            return datas


# SECRETS
load_dotenv()
client_id = os.environ["client_id"]
client_secret = os.environ["client_secret"]
Bankin_Device = os.environ["Bankin_Device"]
email = os.environ["email"]
password = os.environ["password"]
save_file = 'datas/data.json'

datas = get_datas(update_data=True)



