import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
from utils import charger_config,lire_prg_config
import os

# Dictionnaires pour suivre les fenêtres ouvertes par catégorie
opened_windows_poules = {}
opened_windows_tableaux = {}
opened_windows_intertops = {}

def check_all_processes():
    """Vérifie l'état de tous les processus ouverts."""
    for category, process in list(opened_windows_poules.items()):
        if process.poll() is not None:  # Si le processus est terminé
            del opened_windows_poules[category]
            print(f"Application 'Poules' fermée pour la catégorie '{category}'.")

    for category, process in list(opened_windows_tableaux.items()):
        if process.poll() is not None:  # Si le processus est terminé
            del opened_windows_tableaux[category]
            print(f"Application 'Tableaux' fermée pour la catégorie '{category}'.")

    # Replanifier la vérification
    root.after(1000, check_all_processes)

def open_app(category, round_number, app_type, prg_name):
    """Ouvre une application spécifique (poules ou tableaux) avec les paramètres donnés."""
    if app_type == "poules":
        if category in opened_windows_poules:
            messagebox.showwarning("Attention", f"L'application pour la catégorie '{category}' (Poules) est déjà ouverte.")
            return
        #app_name = 'saisie-resultats-poules-V2.3.py'
        opened_windows = opened_windows_poules
    elif app_type == "tableaux":
        if category in opened_windows_tableaux:
            messagebox.showwarning("Attention", f"L'application pour la catégorie '{category}' (Tableaux) est déjà ouverte.")
            return
        #app_name = 'Saisie-Tournoi-V1.py'  # Remplacez par le nom réel de votre application pour les tableaux
        opened_windows = opened_windows_tableaux
    else:
        raise ValueError("Type d'application non valide.")

    try:
        # Lancer le processus pour l'application correspondante
        process = subprocess.Popen(['python', prg_name, category, str(round_number)])
        opened_windows[category] = process
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir l'application '{app_type}' : {e}")

def on_open_button_click(action, prg_name):
    """Gère les clics sur les boutons 'Ouvrir Poules' et 'Ouvrir Tableau'."""
    selected_category = category_var.get()
    selected_round = round_var.get()

    if not selected_category or not selected_round:
        messagebox.showerror("Erreur", "Veuillez sélectionner une catégorie et un numéro de tour.")
        return

    if action == "poules":
        open_app(selected_category, selected_round, "poules", prg_name)
    elif action == "tableaux":
        open_app(selected_category, selected_round, "tableaux", prg_name)

# Création de la fenêtre principale
root = tk.Tk()
root.title("TVC : Gestion des Poules et Tableaux")

root.geometry("400x200")

# Lire la config
config_file = "config.ini"  # Assurez-vous que ce fichier existe

PoulesPrg = ""
TableauPrg = ""
try:
    PoulesPrg,TableauPrg = lire_prg_config(config_file)
    
except FileNotFoundError as e:
    print(e)
except Exception as e:
    print(f"Erreur : {e}")

# Combobox pour les catégories
category_var = tk.StringVar()
categories = ["Poussins", "Benjamins", "Minimes", "Cadets-Juniors", "Feminines"]
category_label = ttk.Label(root, text="Catégorie")
category_label.pack(pady=5)
category_combobox = ttk.Combobox(root, textvariable=category_var, values=categories, state="readonly")
category_combobox.pack(pady=5)
category_combobox.set(categories[0])  # Sélection par défaut

# Combobox pour les numéros de tour
round_var = tk.StringVar()
rounds = ["1", "2", "3", "4"]
round_label = ttk.Label(root, text="Numéro de Tour")
round_label.pack(pady=5)
round_combobox = ttk.Combobox(root, textvariable=round_var, values=rounds, state="readonly")
round_combobox.pack(pady=5)
round_combobox.set(rounds[0])  # Sélection par défaut

# Cadre pour les boutons "Ouvrir Poules" et "Ouvrir Tableau"
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# Bouton "Ouvrir Poules"
open_poules_button = ttk.Button(button_frame, text="Ouvrir Poules", command=lambda: on_open_button_click("poules", PoulesPrg))
open_poules_button.pack(side="left", padx=5)

# Bouton "Ouvrir Tableau"
open_tableau_button = ttk.Button(button_frame, text="Ouvrir Tableau", command=lambda: on_open_button_click("tableaux", TableauPrg))
open_tableau_button.pack(side="left", padx=5)

# Lancer la vérification périodique des processus
root.after(1000, check_all_processes)

# Lancer la boucle principale
root.mainloop()
