import hashlib
import logging
import os
import shutil
import sys
import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# List of Pokémon names for each generation
# Generation 1 Pokémon names in French
pokemon_gen = [
    [
        "Bulbizarre",
        "Herbizarre",
        "Florizarre",
        "Salamèche",
        "Reptincel",
        "Dracaufeu",
        "Carapuce",
        "Carabaffe",
        "Tortank",
        "Chenipan",
        "Chrysacier",
        "Papilusion",
        "Aspicot",
        "Coconfort",
        "Dardargnan",
        "Roucool",
        "Roucoups",
        "Roucarnage",
        "Rattata",
        "Rattatac",
        "Piafabec",
        "Rapasdepic",
        "Abo",
        "Arbok",
        "Pikachu",
        "Raichu",
        "Sabelette",
        "Sablaireau",
        "Nidoran♀",
        "Nidorina",
        "Nidoqueen",
        "Nidoran♂",
        "Nidorino",
        "Nidoking",
        "Mélofée",
        "Mélodelfe",
        "Goupix",
        "Feunard",
        "Rondoudou",
        "Grodoudou",
        "Nosferapti",
        "Nosferalto",
        "Mystherbe",
        "Ortide",
        "Rafflesia",
        "Paras",
        "Parasect",
        "Mimitoss",
        "Aéromite",
        "Taupiqueur",
        "Triopikeur",
        "Miaouss",
        "Persian",
        "Psykokwak",
        "Akwakwak",
        "Férosinge",
        "Colossinge",
        "Caninos",
        "Arcanin",
        "Ptitard",
        "Têtarte",
        "Tartard",
        "Abra",
        "Kadabra",
        "Alakazam",
        "Machoc",
        "Machopeur",
        "Mackogneur",
        "Chétiflor",
        "Boustiflor",
        "Empiflor",
        "Tentacool",
        "Tentacruel",
        "Racaillou",
        "Gravalanch",
        "Grolem",
        "Ponyta",
        "Galopa",
        "Ramoloss",
        "Flagadoss",
        "Magnéti",
        "Magnéton",
        "Canarticho",
        "Doduo",
        "Dodrio",
        "Otaria",
        "Lamantine",
        "Tadmorv",
        "Grotadmorv",
        "Kokiyas",
        "Crustabri",
        "Fantominus",
        "Spectrum",
        "Ectoplasma",
        "Onix",
        "Soporifik",
        "Hypnomade",
        "Krabby",
        "Krabboss",
        "Voltorbe",
        "Électrode",
        "Noeunoeuf",
        "Noadkoko",
        "Osselait",
        "Ossatueur",
        "Kicklee",
        "Tygnon",
        "Excelangue",
        "Smogo",
        "Smogogo",
        "Rhinocorne",
        "Rhinoféros",
        "Leveinard",
        "Saquedeneu",
        "Kangourex",
        "Hypotrempe",
        "Hypocéan",
        "Poissirène",
        "Poissoroy",
        "Stari",
        "Staross",
        "M._Mime",
        "Insécateur",
        "Lippoutou",
        "Élektek",
        "Magmar",
        "Scarabrute",
        "Tauros",
        "Magicarpe",
        "Léviator",
        "Lokhlass",
        "Métamorph",
        "Évoli",
        "Aquali",
        "Voltali",
        "Pyroli",
        "Porygon",
        "Amonita",
        "Amonistar",
        "Kabuto",
        "Kabutops",
        "Ptéra",
        "Ronflex",
        "Artikodin",
        "Électhor",
        "Sulfura",
        "Minidraco",
        "Draco",
        "Dracolosse",
        "Mewtwo",
        "Mew",
    ],
]

# Generation 2 Pokémon names in French
pokemon_gen2 = [
    [
        "Germignon", "Macronium", "Méganium",
        "Héricendre", "Feurisson", "Typhlosion",
        "Kaiminus", "Crocrodil", "Aligatueur",
        "Fouinette", "Fouinar", "Hoothoot",
        "Noarfang", "Coxy", "Coxyclaque",
        "Mimigal", "Migalos", "Nostenfer",
        "Loupio", "Lanturn", "Pichu",
        "Mélo", "Toudoudou", "Togepi",
        "Togetic", "Natu", "Xatu",
        "Wattouat", "Lainergie", "Pharamp",
        "Joliflor", "Marill", "Azumarill",
        "Simularbre", "Tarpaud", "Granivol",
        "Floravol", "Cotovol", "Capumain",
        "Tournegrin", "Héliatronc", "Yanma",
        "Axoloto", "Maraiste", "Mentali",
        "Noctali", "Cornèbre", "Roigada",
        "Feuforêve", "Zarbi", "Qulbutoké",
        "Girafarig", "Pomdepik", "Foretress",
        "Insolourdo", "Scorplane", "Steelix",
        "Snubbull", "Granbull", "Qwilfish",
        "Cizayox", "Caratroc", "Scarhino",
        "Farfuret", "Teddiursa", "Ursaring",
        "Limagma", "Volcaropod", "Marcacrin",
        "Cochignon", "Corayon", "Rémoraid",
        "Octillery", "Cadoizo", "Démanta",
        "Airmure", "Malosse", "Démolosse",
        "Hyporoi", "Phanpy", "Donphan",
        "Porygon2", "Cerfrousse", "Queulorior",
        "Debugant", "Kapoera", "Lippouti",
        "Élekid", "Magby", "Écrémeuh",
        "Leuphorie", "Raikou", "Entei",
        "Suicune", "Embrylex", "Ymphect",
        "Tyranocif", "Lugia", "Ho-Oh",
        "Celebi"
    ]
]

BASE_URL = "https://www.pokepedia.fr/"
HEADERS = {"User-Agent": "Pokebot/1.0 (+pokepedia.fr)"}
OUTPUT_DIR = "pokemon_dataset"

# Function to create a safe filename from a Pokémon name
def safe_filename(name):
    try:
        decoded = requests.utils.unquote(name)
        decoded = decoded.replace("/", "_")
    except Exception:
        decoded = name

    if len(decoded.encode("utf-8")) > 100:
        url_hash = hashlib.sha256(name.encode("utf-8")).hexdigest()[:10]
        decoded = decoded[:50] + "_" + url_hash

    return decoded


# Function to download a Pokémon page from Poképédia
def download_pokemon_page(pokemon_name):
    # Encodage du nom pour l'URL
    encoded_name = quote(pokemon_name, safe="")
    url = BASE_URL + encoded_name

    try:
        print(f"Téléchargement de : {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        time.sleep(0.5)

        if response.status_code != 200:
            print(f"Échec ({response.status_code}) : {url}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        page_title = soup.title.string if soup.title else "Sans titre"
        print("Titre de la page :", page_title)

        filename = safe_filename(pokemon_name)
        filepath = os.path.join(OUTPUT_DIR, f"{filename}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Page enregistrée : {filepath}")

    except requests.RequestException as e:
        print(f"Erreur pour {pokemon_name} : {e}")


# Function to download the dataset of Pokémon pages from Poképédia
def download_dataset(gen=None):
    """Downloads the dataset of Pokémon pages from Poképédia."""

    if gen is None:
        logger.info("No generation specified, downloading Gen 1 and Gen 2 by default.")
        gens_to_download = [1, 2]
    else:
        try:
            gen = int(gen)
        except ValueError:
            logger.error(f"Invalid generation value: {gen}. Must be an integer.")
            sys.exit(1)
        if gen not in range(1, 10):
            logger.error(f"Invalid generation number: {gen}. There are 9 generations max.")
            sys.exit(1)
        gens_to_download = [gen]

    if os.path.exists(OUTPUT_DIR):
        logger.info(f"Clearing existing dataset directory: '{OUTPUT_DIR}'...")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for gen in gens_to_download:
        logger.info(f"Downloading Pokémon dataset for generation {gen}...")
        if gen == 1:
            pokemon_list = pokemon_gen[0]
        elif gen == 2:
            pokemon_list = pokemon_gen2[0]
        else:
            logger.error(f"Sorry! Generation {gen} is not implemented yet.")
            continue

        for pokemon in pokemon_list:
            download_pokemon_page(pokemon)

