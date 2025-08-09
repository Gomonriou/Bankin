import requests
import json
from dotenv import load_dotenv
import os


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

    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
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
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('resources', [])
            all_data.extend(transactions)
            print(f"Données récupérées de {since_str} à {until_str} : {len(transactions)} éléments")
        else:
            print(f"Erreur lors de la requête : {response.status_code} - {response.text}")
            raise Exception(f"Erreur lors de la requête : {response.status_code} - {response.text}")

    with open("data.json", "w", encoding="utf-8") as json_file:
        json.dump({"resources": all_data}, json_file, indent=4, ensure_ascii=False)
        print('Toutes les données sauvegardées dans data.json')

    return all_data


def get_datas(update_data=False):
    if update_data :
        requete_data(bearer, client_id, client_secret)
        with open('data.json', 'r', encoding='utf-8') as fichier:
            datas = json.load(fichier)
            return datas
    else :
        with open('data.json', 'r', encoding='utf-8') as fichier:
            datas = json.load(fichier)
            return datas


# SECRETS
load_dotenv()
bearer = os.environ["bearer"]
client_id = os.environ["client_id"]
client_secret = os.environ["client_secret"]

datas = get_datas(update_data=True)


