python -m venv BankinVenv
(powershell) Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
BankinVenv\Scripts\activate

python -m pip install -r .\requirements.txt

add .env file and fill : 
client_id = ''
client_secret = ''


first run datas = get_datas(update_data=True) puis false pour eviter de requete pour rien

streamlit run .\streamlit.py


remplir ces filtres avec ses besoins de trie :
    depenses_fixes = ["Notes de frais", "Téléphonie mobile", "Mutuelle", "Sport", "Dépenses pro - Autres", "Coiffeur"]
    a_ignorer = ["Remboursement emprunt", "Virements internes", "Autres rentrées"]
    entrees = ["Salaires"]

    