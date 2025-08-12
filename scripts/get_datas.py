import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scripts.logging_config import logger


def get_periods(months):
    periods = []
    today = datetime.today()

    current_month_start = today.replace(day=1)

    for i in range(months):
        month_start = current_month_start - relativedelta(months=i)
        next_month_start = month_start + relativedelta(months=1)
        month_end = next_month_start - timedelta(days=1)

        since_str = month_start.strftime('%Y-%m-%d')
        until_str = month_end.strftime('%Y-%m-%d')

        periods.append((since_str, until_str))
    
    return periods[::-1]

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
    logger.info('Token refresh')

    return bearer_token

def requete_data(bearer, client_id, client_secret, periods):
    url = 'https://sync.bankin.com/v2/transactions'

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

    if os.path.exists('datas/data.json'):
        with open('datas/data.json', "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
                all_data.extend(old_data["resources"])
            except Exception:
                pass

    existing_ids = {item['id'] for item in all_data}

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
                new_transactions = [t for t in transactions if t['id'] not in existing_ids]
                all_data.extend(new_transactions)
                existing_ids.update(t['id'] for t in new_transactions)
                logger.info(f"Données de {since_str} à {until_str} : {len(new_transactions)} nouveaux éléments")
                break
            elif response.status_code == 401 and attempt == 0:
                bearer = "Bearer " + get_bearer(client_id, client_secret, Bankin_Device, email, password)
            else:
                raise Exception(f"Erreur {response.status_code}: {response.text}")

    with open('datas/data.json', "w", encoding="utf-8") as json_file:
        json.dump({"resources": all_data}, json_file, indent=4, ensure_ascii=False)
        logger.info('Datas saved data.json')
    
    return all_data



