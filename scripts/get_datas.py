import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from scripts.logging_config import logger
import streamlit as st

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

def get_bearer():
    url = "https://sync.bankin.com/v2/authenticate"

    custom_data = {
        "email":st.session_state.email,
        "password": st.session_state.password,
        'token':''
    }

    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'bankin-version': '2019-08-22',
        'client-id': st.session_state.client_id,
        'client-secret': st.session_state.client_secret,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'fr',
        'Bankin-Device':st.session_state.Bankin_Device,
        'Content-Type': 'application/json',
    }

    response = requests.post(url, headers=custom_headers, json=custom_data)
    
    data = response.json()
    bearer_token = data["access_token"]
    logger.info('Token refresh')

    return bearer_token

def requete_data(periods):
    url = 'https://sync.bankin.com/v2/transactions'

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

        max_attempts = 2
        for attempt in range(max_attempts):

            custom_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'authorization': st.session_state.bearer,
                'bankin-version': '2019-08-22',
                'client-id': st.session_state.client_id,
                'client-secret': st.session_state.client_secret,
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'fr',
            }

            print(f"requete_data attempts : {attempt}")
            response = requests.get(url, headers=custom_headers, params=params)

            if response.status_code == 200:
                data = response.json()
                transactions = data.get('resources', [])

                new_transactions = [t for t in transactions if t['id'] not in existing_ids]
                all_data.extend(new_transactions)
                existing_ids.update(t['id'] for t in new_transactions)

                logger.info(f"Données {since_str} → {until_str} : {len(new_transactions)} nouvelles transactions")
                break

            elif response.status_code == 401 and attempt == 0:
                logger.info('requete_data 401 - tentative de rafraîchir le token')
                st.session_state.bearer = "Bearer " + get_bearer()

            else:
                raise Exception(f"Erreur requete_data {response.status_code}: {response.text}")

    with open('datas/data.json', "w", encoding="utf-8") as json_file:
        json.dump({"resources": all_data}, json_file, indent=4, ensure_ascii=False)
        logger.info('Datas saved data.json')

    return all_data


def requete_accounts():
    url = 'https://sync.bankin.com/v2/accounts?limit=200'
    max_attempts = 2
    accounts = []

    for attempt in range(max_attempts):
        custom_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'authorization': st.session_state.bearer,
            'bankin-version': '2019-08-22',
            'client-id': st.session_state.client_id,
            'client-secret': st.session_state.client_secret,
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'fr',
        }

        print(f"requete_accounts attempt : {attempt}")
        response = requests.get(url, headers=custom_headers)

        if response.status_code == 200:
            data = response.json()
            accounts = data.get('resources', [])
            break

        elif response.status_code == 401 and attempt == 0:
            logger.info('requete_accounts 401 - tentative de rafraîchir le token')
            st.session_state.bearer = "Bearer " + get_bearer()

        else:
            raise Exception(f"Erreur requete_accounts function {response.status_code}: {response.text}")

    with open('datas/accounts.json', "w", encoding="utf-8") as json_file:
        json.dump({"resources": accounts}, json_file, indent=4, ensure_ascii=False)
        logger.info('Datas saved accounts.json')
