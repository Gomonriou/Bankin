import json
import csv

with open('id.json', 'r', encoding='utf-8') as f:
    id_file = json.load(f)

with open('data.json', 'r', encoding='utf-8') as f:
    data_file = json.load(f)

category_map = {}
for resource in id_file['resources']:
    for category in resource.get('categories', []):
        category_id = category['id']
        category_name = category['name']
        category_map[category_id] = category_name


with open('output.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['description', 'montant', 'category.id', 'category_name', 'date', 'année', 'mois'])

    for item in data_file.get('resources', []):
        description = item.get('description', '')
        montant = item.get('amount', '')
        category_id = item.get('category', {}).get('id')
        category_name = category_map.get(category_id, '') if category_id is not None else ''
        date = item.get('date', '')
        annee = date.split('-')[0] if date else ''
        mois = date.split('-')[1] if date else ''
        writer.writerow([description, montant, category_id, category_name, date, annee, mois])
