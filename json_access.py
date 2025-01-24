import json
import tkinter as tk
import os
from tkinter import ttk, messagebox
from utils import *

def load_tableau(json_file, all = False):
    directory = charger_config_json("config.ini")
    json_file = os.path.join(directory, json_file)
    try:
        print(f"json_file: {json_file}")
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        #messagebox.showerror("Erreur", f"Fichier {json_file} non trouvé")
        print(f"ichier {json_file} non trouvé")
        return {},{}
            
    if (all):
        return data
        
    tableau_sauve_OK = data.get("Tableau OK")
    tableau_sauve_KO = data.get("Tableau KO")
    return tableau_sauve_OK, tableau_sauve_KO

def load_poules(json_file, all=False):
    directory = charger_config_json("config.ini")
    json_file = os.path.join(directory, json_file)
    print("JSON File: ", json_file)
    try:
        with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
    except FileNotFoundError:
        print(f"Fichier non trouvé : {json_file}")
        return -1
     
    if all:
        return data
        
    poules = data.get("poules")
    return poules

def read_config_files(category, round_number):
    config_file = "config.ini"  # Assurez-vous que ce fichier existe
    fichier_Poules = ""
    fichier_Tableau = ""
    try:
        directory = charger_config_json(config_file)
        print(f"Répertoire : {directory}")

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
        messagebox.showinfo("Info", f"Tableaux enregistrés dans {json_file}.")
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
        messagebox.showinfo("Succès", f"Résultats enregistrés dans {json_file}.")
        return True
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")
        return False