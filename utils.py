import configparser
import os

def charger_config(config_file):
    """
    Charge le fichier de configuration et retourne le répertoire et le fichier d'entrée.
    """
    
    config = configparser.ConfigParser()
    config.read(config_file)

    directory = config.get("Paths", "directory", fallback=".")
    input_file = config.get("Paths", "input_file", fallback="data.xlsx")

    # Vérifier si le fichier existe
    full_path = os.path.join(directory, input_file)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"Le fichier '{full_path}' est introuvable.")

    return directory, input_file
    
def charger_config_categorie(config_file, categorie):
    """
    Charge le fichier de configuration et retourne les confs par categorie.
    """
    
    config = configparser.ConfigParser()
    config.read(config_file)

    nbTopsDefaut = config.get("TopsDefaut", categorie, fallback=".")

    return nbTopsDefaut
    
def lire_prg_config(config_file):
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    poules_prg = config.get("Versions", "PoulesPy", fallback=".")
    tableau_py = config.get("Versions", "TableauPy", fallback=".")
    
    return poules_prg,tableau_py
