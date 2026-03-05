import json
import tkinter as tk
import os
from tkinter import ttk, messagebox
from modules.utils import *
from modules.models import Player, Match
from modules.Tournoi import Tournoi
from modules.Poules import Poule
from modules.Tableau import Tableau, TableauLevels
import re
from dataclasses import asdict
from modules.debug import debug_print

def load_all_tableau(json_file, all = False):
    directory = charger_config_json("config.ini")
    json_file = os.path.join(directory, json_file)
    try:
        debug_print(f"json_file: {json_file}")
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        #messagebox.showerror("Erreur", f"Fichier {json_file} non trouvé")
        debug_print(f"fichier {json_file} non trouvé dans load_all_tableau")
        return None,None
            
    if (all):
        return data
        
    tableau_sauve_OK = data.get("Tableau OK")
    tableau_sauve_KO = data.get("Tableau KO")
    return tableau_sauve_OK, tableau_sauve_KO

def save_tableau_all_levels_per_object(json_file, tableau, tournoi, type_tableau="Tableau OK"):
    #debug_print("--------- IN save_tableau_all_levels_per_object ---, type(tableau)", type(tableau), ",tableau", tableau)
    if isinstance(tableau, Tableau):
        for level_obj in tableau.tableauLevels:
            save_tableau_level_per_object(json_file, level_obj, tournoi, type_tableau)

def save_tableau_level_per_object(json_file, level_obj, tournoi, type_tableau="Tableau OK"):
    directory = charger_config_json("config.ini")
    filepath = os.path.join(directory, json_file)
    
    # 1. Charger l'existant ou créer un dict vide
    data = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

    if tournoi.category is not None: data["category"] = tournoi.category
    if tournoi.tour is not None: data["round"] = tournoi.tour
    if tournoi.tourInitial is not None: data["tourInitial"] = tournoi.tourInitial.level
    if tournoi.nb_tops is not None: data["nbTops"] = tournoi.nb_tops
    if tournoi.nb_poules is not None: data["nbPoules"] = tournoi.nb_poules
    
    # 2. Préparer les données du niveau (conversion dataclass -> dict)
    level_data = {
        "matches": [
            {
                "num": m.num,
                "player1": asdict(m.player1) if m.player1 else None,
                "player2": asdict(m.player2) if m.player2 else None,
                "sets": m.sets,
                "idxPlayer1": m.idxPlayer1,
                "idxPlayer2": m.idxPlayer2,
                "winner": asdict(m.winner) if m.winner else None
            } for m in level_obj.matches
        ]
    }

    # 3. Mise à jour sécurisée de la clé (OK ou KO)
    # C'est ici que le KeyError se produit si on manipule mal le dictionnaire
    if type_tableau not in data:
        data[type_tableau] = {}
    if type_tableau == "InterTops":
        data[type_tableau] = level_data
    else:
        data[type_tableau][level_obj.level] = level_data
    
    ordered_data = {}
    
    # Étape A : On insère d'abord les clés d'en-tête
    header_keys = ["category", "round", "tourInitial", "nbTops", "nbPoules"]
    for key in header_keys:
        if key in data:
            ordered_data[key] = data[key]
            
    # Étape B : On insère les tableaux (OK et KO)
    for key in ["Tableau OK", "Tableau KO"]:
        if key in data:
            ordered_data[key] = data[key]
            
    # Étape C : On insère tout le reste (comme InterTops s'il existe)
    for key, value in data.items():
        if key not in ordered_data:
            ordered_data[key] = value

    # 3. ÉCRITURE
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(ordered_data, f, indent=4, ensure_ascii=False)

def save_poule_per_object(json_file, poule_obj):
    """
    Met à jour une poule spécifique dans le fichier JSON à partir d'un objet Poule.
    """
    # Utilise la logique de chemin existante dans votre projet
    directory = charger_config_json("config.ini")
    path = os.path.join(directory, json_file)
    
    try:
        # 1. Charger l'intégralité du fichier pour ne pas perdre les autres données
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"poules": {}}

        # 2. Préparer la clé de la poule (ex: "Top 1")
        poule_key = f"{poule_obj.type} {poule_obj.num}"
        
        # 3. Convertir l'objet en dictionnaire
        # On nettoie un peu pour correspondre exactement à votre format JSON
        p_dict = asdict(poule_obj)
        
        # Votre JSON utilise la clé "joueurs" au pluriel, asdict utilise le nom du champ
        # Si votre champ dans la dataclass est "players", on le renomme pour le JSON
        formatted_poule = {
            "joueurs": p_dict.get("players", []),
            "matches": p_dict.get("matches", []),
            "classement": p_dict.get("classement", [])
        }

        # 4. Mettre à jour uniquement cette poule
        data["poules"][poule_key] = formatted_poule

        # 5. Sauvegarder
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        debug_print(f"Succès : Poule '{poule_key}' mise à jour dans {json_file}")
        return True
    except Exception as e:
        debug_print(f"Erreur lors de la sauvegarde de l'objet Poule : {e}")
        return False
'''
def save_tableau_interTops_per_object(json_file, interTops):
    directory = charger_config_json("config.ini")
    filepath = os.path.join(directory, json_file)
    
    # 1. Charger l'existant ou créer un dict vide
    data = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

    level_data = {
        "matches": [
            {
                "num": m.num,
                "player1": asdict(m.player1) if m.player1 else None,
                "player2": asdict(m.player2) if m.player2 else None,
                "sets": m.sets,
                "idxPlayer1": m.idxPlayer1,
                "idxPlayer2": m.idxPlayer2,
                "winner": None
            } for m in interTops
        ]
    }
    
        # 3. Mise à jour sécurisée de la clé (OK ou KO)
    # C'est ici que le KeyError se produit si on manipule mal le dictionnaire
    if type_tableau not in data:
        data[type_tableau] = {}
    
    # On sauvegarde par niveau (ex: data["Tableau KO"]["1/8"] = ...)
    #debug_print("******** level_obj.level = ", level_obj.level)
    if (level_obj.level == "InterTops"):
        data[type_tableau] = level_data
    else:
        data[type_tableau][level_obj.level] = level_data

    # 4. Écriture
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
'''   
def load_intertops_per_object(tableau_raw, interTops):
    matches_list = []
    
    #debug_print("tableau_raw: ", tableau_raw)
    
    if tableau_raw == {}:
        return interTops
    
    for match in tableau_raw['matches']:
        num = int(match.get("num"))
        p1_d = match.get("player1", {})
        p2_d = match.get("player2", {})
        if (p1_d != None):
            p1 = Player(nom=p1_d.get("nom",""), prenom=p1_d.get("prenom",""), 
                club=p1_d.get("club",""), dossard=str(p1_d.get("dossard","")))
        else:
            p1 = None
        if (p2_d != None):
            p2 = Player(nom=p2_d.get("nom",""), prenom=p2_d.get("prenom",""), 
                club=p2_d.get("club",""), dossard=str(p2_d.get("dossard","")))
        else:
            p2 = None
        match_obj = Match(
                num=int(num),
                player1=p1,
                player2=p2,
                sets=match.get("score", []),
                idxPlayer1=0,
                idxPlayer2=0,
                winner=None # Logique à définir si besoin de retrouver l'objet Player gagnant
        )

        matches_list.append(match_obj)
    if matches_list != []:
        level_pos = interTops.get_level_pos()
        level_pos.matches = matches_list
    return interTops    

def load_one_tableau_per_object(tableau_raw, tableau):
    debug_print("LOAD TABLEAU, tableau=", tableau)
    #list_levels = []

    for level, content in tableau_raw.items():
        if tableau.tableauLevels == None:
            tableau.tableauLevels = [TableauLevels(level=level, matches=[])]
        tableauLevel = tableau.get_level_pos(level)
        if (tableauLevel is None):
            debug_print("Add new level: ", level)
            tableau.tableauLevels.append(TableauLevels(level=level, matches=[]))
            tableauLevel = tableau.get_level_pos(level)
        #tableauLevel = TableauLevels(level=level, matches=[])
        matches_json = content.get("matches", [])
        
        #debug_print("level", level, " content", content, " matches:", matches_json)
        for match_data in matches_json:
            num = int(match_data.get("num"))
            p1_d = match_data.get("player1", {})
            p2_d = match_data.get("player2", {})
            if (p1_d != None):
                p1 = Player(nom=p1_d.get("nom",""), prenom=p1_d.get("prenom",""), 
                            club=p1_d.get("club",""), dossard=str(p1_d.get("dossard","")))
            else:
                p1 = None
            if (p2_d != None):
                p2 = Player(nom=p2_d.get("nom",""), prenom=p2_d.get("prenom",""), 
                            club=p2_d.get("club",""), dossard=str(p2_d.get("dossard","")))
            else:
                p2 = None
            new_match_obj = Match(
                num=int(num),
                player1=p1,
                player2=p2,
                sets=match_data.get("score", []),
                idxPlayer1=0,
                idxPlayer2=0,
                winner=None # Logique à définir si besoin de retrouver l'objet Player gagnant
            )
            match_obj = tableauLevel.get_match_pos(num)
            if (match_obj == None):
                tableauLevel.matches.append(new_match_obj)
            else:
                match_obj.player1 = p1
                match_obj.player2 = p2
                match_obj.sets = match_obj.sets
                match_obj.winner = match_obj.winner
                
        debug_print("TABLEAULEVEL", tableauLevel)
        #tableau.tableauLevels.append(tableauLevel)
        #debug_print("LISTLEVELS", list_levels)
        #list_levels.append(tableauLevel)
        debug_print("AFTER LOAD TABLEAU, tableau=", tableau)
    #tableau.tableauLevels = list_levels
    #debug_print("tableau.tableauLevels", tableau.tableauLevels)
    return tableau

def get_info_tableau(json_file):
    data ={}
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        debug_print(f"Fichier non trouvé : {json_file}")
        
    initialTour = data.get("tourInitial")
    nb_Tops = int(data.get("nbTops"))
    nb_Poules = int(data.get("nbPoules"))
    
    return initialTour, nb_Tops, nb_Poules
    
def load_all_tableau_per_object(json_file, tableauOk=None, tableauKo=None, interTops=None):
    directory = charger_config_json("config.ini")
    json_file = os.path.join(directory, json_file)
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        debug_print(f"Fichier non trouvé : {json_file}")
        return tableauOk,tableauKo,interTops 
    
    tableau_raw = data.get("Tableau OK", {})
    tableauOk = load_one_tableau_per_object(tableau_raw, tableauOk)
    
    tableau_raw = data.get("Tableau KO", {})
    tableauKo = load_one_tableau_per_object(tableau_raw, tableauKo)
    
    tableau_raw = data.get("InterTops", {})
    #debug_print("InterTops: ", interTops)
    interTops = load_intertops_per_object(tableau_raw, interTops)
    
    #debug_print("type intertops:", type(interTops), ",intertops:", interTops)
    return tableauOk, tableauKo, interTops

    

def load_poules_per_object(json_file, withMatches=False):
    directory = charger_config_json("config.ini")
    json_file = os.path.join(directory, json_file)
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        debug_print(f"Fichier non trouvé : {json_file}")
        return -1
        
#    if all:
#        return data
        
    poules_raw = data.get("poules", {})
    liste_objets_poules = []

    for name, content in poules_raw.items():
        # --- Analyse du nom de la poule (Top x ou Poule x) ---
        poule_type = ""
        poule_num = ""
        
        match_top = re.match(r"Top\s+(\d+)", name, re.IGNORECASE)
        match_poule = re.match(r"Poule\s+(\d+)", name, re.IGNORECASE)
        
        if match_top:
            poule_type = "Top"
            poule_num = match_top.group(1)
        elif match_poule:
            poule_type = "Poule"
            poule_num = match_poule.group(1)

        # --- Conversion des joueurs ---
        joueurs_list = []
        for j in content.get("joueurs", []):
            joueurs_list.append(Player(
                nom=j.get("nom", ""),
                prenom=j.get("prenom", ""),
                club=j.get("club", ""),
                dossard=str(j.get("dossard", ""))
            ))
        
        # --- Conversion des matches ---
        matches_list = []
        if (withMatches):
            
            for m in content.get("matches", []):
                p1_d = m.get("player1", {})
                p2_d = m.get("player2", {})
                winner_d = m.get("winner", None)
            
                p1 = Player(nom=p1_d.get("nom",""), prenom=p1_d.get("prenom",""), 
                        club=p1_d.get("club",""), dossard=str(p1_d.get("dossard","")))
                p2 = Player(nom=p2_d.get("nom",""), prenom=p2_d.get("prenom",""), 
                        club=p2_d.get("club",""), dossard=str(p2_d.get("dossard","")))
                if winner_d:
                    print("winner:", winner_d)
                    winner = Player(nom=winner_d.get("nom",""), prenom=winner_d.get("prenom",""), 
                            club=winner_d.get("club",""), dossard=str(winner_d.get("dossard","")))
                else:
                    winner = None

                matches_list.append(Match(
                    num=0,
                    player1=p1,
                    player2=p2,
                    sets=m.get("sets", []),
                    idxPlayer1=0,
                    idxPlayer2=0,
                    winner=winner # Logique à définir si besoin de retrouver l'objet Player gagnant
                ))

        # --- Création de l'objet Poule ---
        # Note : J'ajoute type et num comme attributs dynamiques si votre dataclass ne les a pas,
        # ou assurez-vous que votre classe Poule dans models.py possède ces champs.
        poule_obj = Poule(
            type=poule_type,
            num=poule_num,
            players=joueurs_list,
            matches=matches_list,
            classement=content.get("classement", [])
        )
        # Ajout des propriétés demandées
        liste_objets_poules.append(poule_obj)
        
    return liste_objets_poules


'''def load_poules(json_file, all=False):
    directory = charger_config_json("config.ini")
    json_file = os.path.join(directory, json_file)
    try:
        with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
    except FileNotFoundError:
        debug_print(f"Fichier non trouvé : {json_file}")
        return -1
     
    if all:
        return data
        
    poules = data.get("poules")
    return poules
'''
def read_config_files(category, round_number):
    config_file = "config.ini"  # Assurez-vous que ce fichier existe
    fichier_Poules = ""
    fichier_Tableau = ""
    try:
        directory = charger_config_json(config_file)
        debug_print(f"Répertoire : {directory}")

        # Utiliser les paramètres pour exécuter le reste du script
        
        fichier_Poules = os.path.join(directory, f"{category}_tour{round_number}.json")
        fichier_Tableau = os.path.join(directory, f"Tableau_{category}_tour{round_number}.json")
    
        print ("Fichier Poules:", fichier_Poules, ", Fichier Tableau:", fichier_Tableau)
    except FileNotFoundError as e:
        messagebox.showerror("Erreur", f"Fichier {json_file} non trouvé")
        return ""
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur de lecture des fichiers poules et tableau : {e}")
        return ""
    return fichier_Poules, fichier_Tableau


def save_tableau(json_file, tableau_data):    
    try:
        directory = charger_config_json("config.ini")
        json_file = os.path.join(directory, json_file)
        with open(json_file, "w", encoding="utf-8") as f:
                json.dump(tableau_data, f, indent=4, ensure_ascii=False)
        #messagebox.showinfo("Info", f"Tableaux enregistrés dans {json_file}.")
        debug_print(f"Tableaux enregistrés dans {json_file}.")
        return True
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des tableaux : {e}")
        return False
   
def save_poules(json_file, data):
    try:
        directory = charger_config_json("config.ini")
        json_file = os.path.join(directory, json_file)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        #messagebox.showinfo("Succès", f"Résultats enregistrés dans {json_file}.")
        print(f"Résultats enregistrés dans {json_file}.")
        return True
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")
        return False
