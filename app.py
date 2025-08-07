import requests
import json
import jmespath
from dotenv import load_dotenv
import os

def requete_data(bearer, client_id, client_secret) :
    url = 'https://sync.bankin.com/v2/transactions'

    params = {
        'limit': 500,
        'until': '2024-08-01',
        'until': '2024-10-31',
    }

    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'authorization': bearer,
        'bankin-version': '2019-08-22',
        'client-id': client_id,
        'client-secret': client_secret,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'fr',
    }


    response = requests.get(url, headers=custom_headers, params=params)
    return response.json()


def update_data(data):
    with open("data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


# SECRETS
load_dotenv()
bearer = os.environ["bearer"]
client_id = os.environ["client_id"]
client_secret = os.environ["client_secret"]

# GET DATAS
#data = requete_data(bearer, client_id, client_secret)
#update_data(data)


noms = jmespath.search("[].nom", utilisateurs)
print("Noms :", noms)