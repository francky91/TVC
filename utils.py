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
    #if not os.path.isfile(full_path):
    #    raise FileNotFoundError(f"Le fichier '{full_path}' est introuvable.")

    return directory, input_file

def charger_config_json(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    directoryForJson = config.get("Paths", "directoryJson")
    return directoryForJson
    
def lire_excel_name(config_file="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    
    directoryForExcel = config.get("Paths", "directoryExcel")
    input_file = config.get("Paths", "input_file")
    excelName = f"{directoryForExcel}\\{input_file}"
    return excelName

def lire_word_name(name, config_file="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    
    directoryForWord = config.get("Paths", "directoryWord")
    wordName = f"{directoryForWord}\\{name}"
    return wordName

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

def construire_bracket(n, start=1):
    def fusion_bracket(top, bottom):
        """
        'top' et 'bottom' sont deux listes de même taille.
        On les combine en suivant le « pattern » qui
        reproduit l’ordre 1,8,5,4,3,6,7,2 pour n=8, etc.
        """
        m = len(top)
        result = []
    
        # On suppose m est pair (ce sera le cas si n = 2^k >= 4)
        for i in range(0, m, 2):
            # On "tresse" 4 éléments à la fois :
            #  top[i], bottom[i+1], bottom[i], top[i+1]
            result.append(top[i])
            result.append(bottom[i+1])
            result.append(bottom[i])
            result.append(top[i+1])
        return result

    # ---------------------------------------------
    # 2) Fonction récursive principale
    # ---------------------------------------------
    def construire_ordre_bracket(n, start=1):
        """
        Construit l'ordre exact désiré pour un tableau de n joueurs 
        (n = 2^k) numérotés de 'start' à 'start+n-1'.
    
        Exemple : construire_ordre_bracket(8, 1) => [1, 8, 5, 4, 3, 6, 7, 2]
        """
        # Cas de base : quand n=2, on retourne [start, start+1]
        if n == 2:
            return [start, start+1]
  
        # On construit récursivement la "moitié du haut" et la "moitié du bas"
        half = n // 2
        top = construire_ordre_bracket(half, start)          # ex: bracket(4) si n=8
        bottom = construire_ordre_bracket(half, start+half)  # ex: bracket(4) pour seeds 5..8
    
        # On fusionne selon le pattern voulu
        return fusion_bracket(top, bottom)

    # ---------------------------------------------
    # 3) Petite fonction utilitaire pour sortir
    #    directement une liste de dict {seed: ""}
    # ---------------------------------------------
    
    ordre = construire_ordre_bracket(n, start)
    return [{s: ""} for s in ordre]