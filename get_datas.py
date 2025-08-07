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


def sums_categories(datas, categories, include=True):
    total = 0
    for item in datas.get('resources', []):
        if item.get('category'):
            cat_id = item['category'].get('id')
            if (include and cat_id in categories) or (not include and cat_id not in categories):
                print(f"Montant ajouté : {item['amount']} (category.id={cat_id})")
                total += item['amount']
    return total


def sums_marchant(datas, marchants):
    total = 0
    count = 0
    for item in datas.get('resources', []):
        if (item.get('metadata')
            and item['metadata'].get('merchant')
            and item['metadata']['merchant'].get('code', '').lower() == marchants.lower()):
            
            total += item['amount']
            count += 1
            print(f"Achats comptabilisés : {count}")  
            print(f"{count} > Achat le {item['date']} de {item['amount']} €")  
    
    print(f"Nombre total d'achats pour le marchand '{marchants}': {count}")
    print(f"Somme totale des montants : {total}")
    return total


# SECRETS
load_dotenv()
bearer = os.environ["bearer"]
client_id = os.environ["client_id"]
client_secret = os.environ["client_secret"]

datas = get_datas(update_data=True)


# entrees = {3, 80, 230, 231, 232, 233, 271, 279, 282, 283, 289, 314, 327, 441893, 441894}
# fixe = {265, 277, 245, 242, 90, 235}
# exclude = {89, 326}
# restes = fixe.union(exclude).union(entrees)
# print(restes)

# sums_fixe = 0
# sums_envie = 0
# sums_restes = 0

# sums_fixe = sums_categories(datas, fixe)
# sums_envie = sums_categories(datas, exclude)
# sums_restes = sums_categories(datas, restes, include=False)

# print(f"""Total des dépenses pour : 
#       besoin : {sums_fixe} €
#       restes : {sums_restes} €
#       """)

# sums_marchant = sums_marchant(datas, "CARREFOUR")
# print(f"Total des dépenses pour CARREFOUR : {sums_marchant} €")