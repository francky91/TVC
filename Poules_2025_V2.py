import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import json
import os
import math
from collections import defaultdict
from utils import *
import sys
from json_access import *
from logic import *
from SaisieMatch import validate_input_set,handle_mode_change

class ResultEntryApp:        
    def __init__(self, root, category, round_number):
        self.root = root
        self.category = category
        self.round_number = round_number
        #self.root.title("Saisie des résultats des poules")
        
        # Variables pour le type de poule, la poule sélectionnée, la catégorie, et le numéro de tour
        self.selected_category = tk.StringVar()
        self.selected_round = tk.IntVar(value=1)
        
        title = f"Saisie des résultats - {category} - Tour {round_number}"
        self.root.title(title)
        
        # Calculer la largeur du titre
        temp_label = ttk.Label(self.root, text=title, font=("TkDefaultFont", 10))
        temp_label.update_idletasks()
        title_width = temp_label.winfo_width()
        temp_label.destroy()

        # Définir une largeur et une hauteur minimales
        min_width = max(title_width + 50, 400)  # Assurez-vous que la largeur minimale est suffisante
        min_height = 700  # Hauteur fixe minimale
        self.root.geometry(f"{min_width}x{min_height}")
        self.root.minsize(min_width, min_height)

        # Variables pour le type de poule, la poule sélectionnée, la catégorie, et le numéro de tour
        self.poule_type = tk.StringVar(value="Top")
        self.selected_poule = tk.StringVar()
        self.match_results = []
        self.match_data = {}
        self.results_modified  = [False] # Suivre si des résultats ont été modifiés
        self.sets_mode_global = tk.StringVar(value="2 sets")
        self.current_poule = None  # Pour garder une trace de la poule actuelle
        self.current_poule_type = "Top"
        self.tableauResuPoules = []
        self.interTops = {}
        self.top_count = 0
        self.classique_count = 0
        self.nb_joueurs_tops= 0
        self.nb_joueurs_poules= 0
        
        # Variables pour les scores des joueurs
        self.player_scores = {}        

        # Cadre pour sélectionner le type de poule
        frame_type = ttk.LabelFrame(root, text="Type de Poule")
        frame_type.pack(fill="x", padx=10, pady=5)

        #self.top_radioButton = ttk.Radiobutton(frame_type, text="Top", variable=self.poule_type, value="Top", command=self.confirm_poule_type_change).grid(row=0, column=0, sticky="w", padx=5)
        self.top_radioButton = ttk.Radiobutton(
            frame_type, text="Top", variable=self.poule_type, value="Top",
            command=self.confirm_poule_type_change)
        ttk.Radiobutton(frame_type, text="Classique", variable=self.poule_type, value="Classique", command=self.confirm_poule_type_change).grid(row=0, column=1, sticky="w", padx=5)
        self.top_radioButton.grid(row=0, column=0, sticky="w", padx=5)
        
        # Cadre pour sélectionner une poule
        frame_poule = ttk.LabelFrame(root, text="Sélection de la Poule")
        frame_poule.pack(fill="x", padx=10, pady=5)

        self.poule_list = ttk.Combobox(frame_poule, textvariable=self.selected_poule, state="readonly")
        self.poule_list.pack(fill="x", padx=5, pady=5)
        self.poule_list.bind("<<ComboboxSelected>>", self.confirm_poule_change)

        # Nouveau cadre pour les boutons
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(fill="x", padx=10, pady=5)

        load_poules_button = ttk.Button(frame_buttons, text="Charger les Poules", command=self.load_match_data)
        load_poules_button.pack(side="left", padx=5)

        load_results_button = ttk.Button(frame_buttons, text="Charger les Résultats", command=self.load_results)
        load_results_button.pack(side="left", padx=5)

        # Cadre pour les boutons "2 sets" ou "3 sets"
        frame_global_sets = ttk.LabelFrame(self.root, text="Mode Global des Sets")
        frame_global_sets.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(frame_global_sets, text="2 sets", variable=self.sets_mode_global, value="2 sets", command=self.reset_inputs_on_mode_change).pack(side="left", padx=5)
        ttk.Radiobutton(frame_global_sets, text="3 sets", variable=self.sets_mode_global, value="3 sets", command=self.reset_inputs_on_mode_change).pack(side="left", padx=5)
        
        # Cadre pour saisir les résultats
        self.frame_results = ttk.LabelFrame(root, text="Résultats des Matchs")
        self.frame_results.pack(fill="both", expand=True, padx=10, pady=5)

        self.match_labels = []  # Initialisation vide
        self.result_entries = []  # Initialisation vide

        # Bouton pour enregistrer les résultats
        self.save_button = ttk.Button(root, text="Enregistrer les Résultats", command=self.save_results, state="disabled")
        self.save_button.pack(pady=10)

        self.validate_command_set = self.root.register(
            lambda action, value_if_allowed: validate_input_set(action, value_if_allowed, self.results_modified)
        )
        # Cadre pour le classement des poules
        self.frame_ranking = ttk.LabelFrame(root, text="Classement Poule")
        self.frame_ranking.pack(fill="x", padx=10, pady=10)

        self.ranking_labels = []  # Stocke les labels du classement
        
        self.tableauOk = []
        self.tableauKo = []
        
        self.fichier_Poules, self.fichier_Tableau = read_config_files(self.category, self.round_number)
        self.previous_mode = "2 sets"
        
    def resize_window_to_fit_content(self):
        """Ajuste la taille de la fenêtre pour s'adapter au contenu visible."""
        self.root.update_idletasks()  # Met à jour les dimensions des widgets
        content_width = self.root.winfo_reqwidth()  # Largeur requise
        content_height = self.root.winfo_reqheight()  # Hauteur requise

        # Définir les nouvelles dimensions minimales
        min_width = max(content_width, 400)  # Largeur minimale par défaut
        min_height = max(content_height, 700)  # Hauteur minimale par défaut
        self.root.geometry(f"{min_width}x{min_height}")  # Ajuster la fenêtre
        self.root.minsize(min_width, min_height)  # Appliquer la nouvelle taille minimale
        
    def load_match_data(self):
        """Charge les données des matchs depuis un fichier JSON pour la poule sélectionnée."""
        self.match_data = load_poules(self.fichier_Poules)
        
        # calcule le nombre de joueurs
        
        self.nb_joueurs_tops= 0
        self.nb_joueurs_poules= 0
        self.count_poule_types()  
        # Classifier les poules en "Top" ou "Classique"
        for poule_name, poule_data in self.match_data.items():
            if poule_name.startswith("Top"):
                poule_data["type"] = "Top"
                self.nb_joueurs_tops += 4
            else:
                poule_data["type"] = "Classique"
                for player in poule_data.get("joueurs", []):
                    self.nb_joueurs_poules += 1

        self.joueurs_info = {}
        for poule_name, poule_data in self.match_data.items():
            for player in poule_data.get("joueurs", []):
                full_name = player["nom"] + " " + player["prenom"] + " " + player["club"]
                dossard = player.get("dossard", "Unknown")
                self.joueurs_info[full_name] = {
                    "nom": player["nom"],
                    "prenom": player["prenom"],
                    "club": player["club"],
                    "dossard": dossard
                }
                
                if dossard == "Unknown" and nom != "---":
                    messagebox.showerror(
                    "Erreur de données",
                    f"Le joueur {nom} {prenom} ({club}) a un dossard inconnu. Veuillez vérifier les données."
                )

        # Mettre à jour les poules pour le type sélectionné  
        self.updateEmptyLinesInTab() 
        
        self.update_poules()
            
        # Redimensionner la fenêtre après la mise à jour
        self.resize_window_to_fit_content()
        
        self.load_tableau()        

    def update_poules(self):
        """Met à jour la liste des poules en fonction du type sélectionné."""
        selected_type = self.poule_type.get()  # "Top" ou "Classique"
        self.clear_inputs_and_labels()
        
        # Classification des poules
        poules_top = [name for name in self.match_data if "Top" in name]
        poules_classique = [name for name in self.match_data if "Top" not in name]
        
        # Filtrer en fonction du type sélectionné
        if selected_type == "Top":
            filtered_poules = poules_top
        else:  # Classique
            filtered_poules = poules_classique

        if filtered_poules:
            self.poule_list["values"] = filtered_poules

            # Sélectionner automatiquement la première poule si aucune n'est sélectionnée
            if not self.selected_poule.get() or self.selected_poule.get() not in filtered_poules:
                self.selected_poule.set(filtered_poules[0])

            # Actualiser les matchs pour la poule sélectionnée
            self.update_match_inputs()
            self.current_poule = self.selected_poule.get()
        else:
            # Si aucune poule n'est disponible, réinitialiser
            self.poule_list["values"] = []
            self.selected_poule.set("")
            self.create_result_inputs([])  # Aucun match à afficher
            print("poule vide")
         
    def confirm_poule_type_change(self):
        if self.top_count == 0:  # Ne rien demander si Top est vide
            self.poule_type.set("Classique")
            self.current_poule_type = "Classique"
            self.update_poules()
            self.resize_window_to_fit_content()      
            return  # Sortir de la fonction sans afficher de messagebox
    
        if self.results_modified[0]:
            response = messagebox.askyesno(
                "Changement de type de poule",
                "Des résultats ont été modifiés et non enregistrés. Voulez-vous continuer sans enregistrer ?"
            )
            if not response:
                self.poule_type.set(self.current_poule_type)
                return


        # 🔒 Désactiver le bouton d'enregistrement lors du changement de type de poule
        self.save_button.configure(state="disabled")

        # Mettre à jour le type de poule actuel
        self.current_poule_type = self.poule_type.get()
        self.results_modified = [False]
        self.update_poules()
        self.resize_window_to_fit_content()
        
    def confirm_poule_change(self, event):
        new_poule = self.selected_poule.get()
        
        if self.results_modified[0]:
            response = messagebox.askyesno(
                "Changement de poule",
                "Des résultats ont été modifiés et non enregistrés. Voulez-vous continuer sans enregistrer ?"
            )
            if not response:
                # Rétablir la sélection sur la poule actuelle
                self.poule_list.set(self.current_poule)
                return

        # Désactiver le bouton d'enregistrement quand on change de poule
        self.save_button.configure(state="disabled")

        # Mettre à jour la poule actuelle
        #self.current_poule = self.selected_poule.get()
        self.current_poule =  new_poule
        self.results_modified = [False]
        self.update_match_inputs()
        self.resize_window_to_fit_content()                                                                                            #
                                                                                             
    def update_match_inputs(self):
        """Met à jour les champs de saisie en fonction des joueurs de la poule sélectionnée."""
        poule_name = self.selected_poule.get().strip()

        if not poule_name:
            print("Aucune poule sélectionnée.")
            self.create_result_inputs([])  # Aucun joueur
            return

        #poule_data = self.match_data.get("poules", {}).get(poule_name, {})
        poule_data = self.match_data.get(poule_name, {})
        joueurs = poule_data.get("joueurs", [])
        print("Joueurs: ", joueurs)
        if joueurs:
            self.create_result_inputs(joueurs)
        else:
            print(f"Aucun joueur trouvé pour la poule {poule_name}.")
            self.create_result_inputs([])
    
        #def create_result_inputs(self, joueurs):
        
    def create_result_inputs(self, joueurs):
        """Crée les champs pour saisir les résultats des joueurs."""
        # Suppression des anciens widgets
        for label in self.match_labels:
            label.destroy()

        for widget in self.frame_results.winfo_children():
            widget.destroy()

        self.match_labels = []
        self.result_entries = []
        self.player_scores = {f"{player['nom']} {player['prenom']} {player['club']}": 0 for player in joueurs}  # Initialise les scores

        if not joueurs:
            messagebox.showinfo("Information", "Aucun joueur à afficher pour cette poule.")
            return

        print(f"Création des entrées pour les joueurs : {joueurs}")

        # Créer les matchs pour la poule de 3 ou 4 joueurs
        num_players = len(joueurs)
        if num_players == 4:
            matchups = [
                (0, 3), (1, 2),
                (0, 2), (1, 3),
                (0, 1), (2, 3)
            ]
        elif num_players == 3:
            matchups = [
                (1, 2),
                (0, 2),
                (0, 1)
            ]
        else:
            print ("Erreur: Nombre de joueurs invalide pour la poule, num_players: ", num_players)
            messagebox.showerror("Erreur", "Nombre de joueurs invalide pour la poule.")
            return

        for i, (player1_idx, player2_idx) in enumerate(matchups):
            player1 = joueurs[player1_idx]
            player2 = joueurs[player2_idx]

            print(f"Création du match : {player1['nom']} vs {player2['nom']} ")

            # Cadre contenant le match et les sets
            match_frame = ttk.Frame(self.frame_results)
            match_frame.pack(fill="x", padx=10, pady=5)

            match_label_text = (
                f"{player1['nom']} {player1['prenom']} ({player1['club']}) vs "
                f"{player2['nom']} {player2['prenom']} ({player2['club']})"
            )

            label = ttk.Label(match_frame, text=match_label_text)
            label.pack(side="left", padx=10)
            self.match_labels.append(label)

            entries = []

            # Déplacer le label "Victoire" sur une nouvelle ligne
            victory_frame = ttk.Frame(self.frame_results)
            victory_frame.pack(fill="x", padx=10, pady=5)
            victory_label = ttk.Label(victory_frame, text="")
            victory_label.pack(anchor="w", padx=10)

            def on_focus_in(event, current_index, e):
                if current_index < len(e) - 1:
                    for idx in range(0, current_index):
                        if (e[idx].get() == ""):
                            e[idx].focus_set()
                            break 

            mode = self.sets_mode_global.get()
            for j in range(5):
                set_var = tk.StringVar(value="")

                set_entry = ttk.Entry(
                    match_frame, textvariable=set_var, width=5, validate="key",
                    validatecommand=(self.root.register(lambda action, value: validate_input_set(action, value, self.results_modified)
                        ), 
                        '%d', '%P'
                     )
                )
                if mode == "2 sets" and j >= 3:
                    set_entry.configure(state="disabled")
                set_entry.pack(side="left", padx=2)
                
                # Ajouter un événement pour vérifier les résultats à chaque modification
                set_entry.bind("<Return>", lambda event, e=entries, p1=player1, p2=player2, vl=victory_label: self.handle_enter(event, e, p1, p2, vl))
                set_entry.bind("<FocusIn>", lambda event, idx=j, e=entries: on_focus_in(event, idx, e))
                entries.append(set_entry)

            self.result_entries.append((entries, player1, player2, victory_label))
        self.create_ranking_labels(len(joueurs))
        print("Résultats créés avec succès.")            
        
    def create_ranking_labels(self, num_players):
        """Crée les labels pour le classement des joueurs."""
        for widget in self.frame_ranking.winfo_children():
            widget.destroy()  # Supprime les anciens labels

        ranking_positions = ["1er", "2ème", "3ème", "4ème"][:num_players]

        self.ranking_labels = []
        for position in ranking_positions:
            frame = ttk.Frame(self.frame_ranking)
            frame.pack(fill="x", padx=5, pady=2)

            label_position = ttk.Label(frame, text=position)
            label_position.pack(side="left", padx=10)

            label_name = ttk.Label(frame, text=" ")  # Initialisé à un espace
            label_name.pack(side="left", padx=10)

            self.ranking_labels.append(label_name)
            
    def update_result_labels(self):
        """Met à jour l'état des labels en fonction du mode choisi."""
        print("Sets mode updated. No additional actions needed as 5 fields are always present.")
               
    def reset_inputs_on_mode_change(self):
        new_mode = self.sets_mode_global.get()
        success = handle_mode_change(
            current_mode=self.sets_mode_global.get(),
            new_mode=new_mode,
            result_entries=[entries for entries, _, _, _ in self.result_entries],
            results_modified=self.results_modified
        )
        if success:
            self.results_modified = [False]
            self.previous_mode = new_mode
        else:
            self.sets_mode_global.set(self.previous_mode)
        
    def update_ranking(self):
        """Mise à jour des labels de classement selon les scores des joueurs."""
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1], reverse=True)
        for idx, (player, _) in enumerate(sorted_players):
            if idx < len(self.ranking_labels):
                self.ranking_labels[idx].config(text=player)
                
    def clear_inputs_and_labels(self):
        """Efface toutes les entrées et réinitialise les labels de victoire."""
        for entries, _, _, victory_label in self.result_entries:
            for entry in entries:
                entry.delete(0, tk.END)  # Efface les données saisies
            victory_label.config(text="")  # Réinitialise le label de victoire
            
        # Réinitialiser les scores des joueurs
        self.player_scores = {key: 0 for key in self.player_scores}
        print("Scores réinitialisés.")
        
        # Réinitialiser les labels de classement
        for label in self.ranking_labels:
            label.config(text=" ")
            
        print("Tous les champs et labels ont été réinitialisés.")      
        
    def handle_enter(self, event, entries, player1, player2, victory_label):
        """Gère la validation des scores et détermine le vainqueur."""
        sets_player1 = 0
        sets_player2 = 0
        mode = self.sets_mode_global.get()
        self.results_modified = [True]

        # Navigation entre champs
        current_widget = event.widget
        current_index = entries.index(current_widget)

        # Vérifier que la case précédente est remplie, sauf pour la première case
        if current_widget.get() == "":
            current_widget.insert(0, "0")  # Considérer vide comme 0
        elif current_widget.get() == "-":
            current_widget.insert(0, "-0")  # Considérer "-" comme "-0"
                
        # Récupérer le vainqueur précédent
        previous_winner_text = victory_label.cget("text")
        previous_winner = None
        if previous_winner_text.startswith("Victoire:"):
            previous_winner_name = previous_winner_text.split(":")[1].strip()
            if f"{player1['nom']} {player1['prenom']} ({player1['club']})" == previous_winner_name:
                previous_winner = player1
            elif f"{player2['nom']} {player2['prenom']} ({player2['club']})" == previous_winner_name:
                previous_winner = player2    

        if current_index <= len(entries) - 1:
            # Validation et calcul des scores
            for entry in entries:
                value = entry.get()
                if value.startswith("-"):
                    sets_player2 += 1
                elif value.isdigit():
                    sets_player1 += 1

            # Vérifier le vainqueur
            if (mode == "2 sets" and (sets_player1 == 2 or sets_player2 == 2)) or \
               (mode == "3 sets" and (sets_player1 == 3 or sets_player2 == 3)):
                winner = player1 if sets_player1 > sets_player2 else player2
                print(f"Winner found: {winner['nom']} {winner['prenom']} {winner['club']}")             
                
                last_victory_label = victory_label.cget("text")
                victory_label.config(text=f"Victoire: {winner['nom']} {winner['prenom']} ({winner['club']})") 

                if (last_victory_label != victory_label.cget("text")):
                    self.player_scores[f"{winner['nom']} {winner['prenom']} {winner['club']}"] += 1  # Augmenter le score du vainqueur
                    if (last_victory_label != ""):
                        
                        if (winner["nom"] == player1["nom"] and winner["prenom"] == player1["prenom"] and winner["club"] == player1["club"]):
                            self.player_scores[f"{player2['nom']} {player2['prenom']} {player2['club']}"] -= 1
                        elif (winner["nom"] == player2["nom"] and winner["prenom"] == player2["prenom"] and winner["club"] == player2["club"]):
                            self.player_scores[f"{player1['nom']} {player1['prenom']} {player1['club']}"] -= 1
                key = f"{winner['nom']} {winner['prenom']} {winner['club']}"
                self.calculate_ranking()
                
                # Placer la souris sur le premier set du match suivant
                current_match_index = self.result_entries.index((entries, player1, player2, victory_label))
                if current_match_index < len(self.result_entries) - 1:
                    next_match_entries = self.result_entries[current_match_index + 1][0]
                    if next_match_entries:
                        next_match_entries[0].focus_set()
            else:
                if (previous_winner and previous_winner["nom"] == player1["nom"] and previous_winner["prenom"] == player1["prenom"] and previous_winner["club"] == player1["club"]):
                    self.player_scores[f"{player2['nom']} {player2['prenom']} {player2['club']}"] -= 1
                elif (previous_winner and previous_winner["nom"] == player2["nom"] and previous_winner["prenom"] == player2["prenom"] and previous_winner["club"] == player2["club"]):
                    self.player_scores[f"{player1['nom']} {player1['prenom']} {player1['club']}"] -= 1
                victory_label.config(text="")
                next_widget = entries[current_index + 1]  # Passer au champ suivant
                next_widget.focus_set()                      
    
    def save_resultats_poules(self):
        """Enregistre les résultats saisis dans un fichier JSON."""
        poule = self.selected_poule.get()
        type_poule = selected_type = self.poule_type.get()
        # Charger les données existantes si le fichier existe
        #data = {"ca()tegory": self.category, "round": self.round_number, "poules": {}}
        
        data = load_poules(self.fichier_Poules, True)
        poules = data.get("poules", {})
        print ("POULE:", poule)

        if (type_poule == "Classique" or type_poule == "Top"):
            # Préserver les joueurs et mettre à jour les résultats
            if poule not in poules:
                poules[poule] = {"joueurs": [], "matches": [], "classement": []}

            # Collecter les résultats des matchs
            results = []
            for entries, player1, player2, victory_label in self.result_entries:
                dossard_joueur1 = player1.get("dossard", "Unknown")
                dossard_joueur2 = player2.get("dossard", "Unknown")
                match_result = {
                    "player1": player1,
                    "player2": player2,
                    "dossard_joueur1": dossard_joueur1,   
                    "dossard_joueur2": dossard_joueur2,
                    "sets": [entry.get() for entry in entries],
                    "winner": victory_label.cget("text")
                }
                
                if dossard_joueur1 == "Unknown" and player1.nom != "---":
                    messagebox.showerror(
                    "Erreur de données",
                    f"Le joueur {player1.nom} {player1.prenom} ({player1.club}) a un dossard inconnu. Veuillez vérifier les données."
                )
                    
                if dossard_joueur2 == "Unknown" and player2.nom != "---":
                    messagebox.showerror(
                    "Erreur de données",
                    f"Le joueur {player2.nom} {player2.prenom} ({player2.club}) a un dossard inconnu. Veuillez vérifier les données."
                )
                results.append(match_result)

            # Mettre à jour les résultats dans le fichier tout en conservant les joueurs
            poule_data = poules[poule]
            if "joueurs" not in poule_data:
                poule_data["joueurs"] = [{"nom": player["nom"], "prenom": player["prenom"], "club": player["club"], "dossard": player["dossard"]}
                                     for _, player, _, _ in self.result_entries]

            poule_data["matches"] = results

            # Ajouter le classement si calculé
            classement = []
            for label in self.ranking_labels:
                text = label.cget("text").strip()
                if text:
                    classement.append(text)
            poule_data["classement"] = classement    

        status = save_poules(self.fichier_Poules, data)
        if status:
            self.results_modified = [False]
            
        # 🔒 Désactiver le bouton d'enregistrement lors du changement de type de poule
        self.save_button.configure(state="disabled")

    def updateTableauWithHoles(self, tableau, niveauBase, is_level_ok):       
        
        def addPlayerInTab(niveau, matchId, joueur, dossard, is_top_tour):
            '''if dossard == "Unknown" and joueur != "---":
                messagebox.showerror(
                    "Erreur de données",
                    f"Le joueur {joueur} a un dossard inconnu. Veuillez vérifier les données."
                )
            '''
            label_niveau = f"1/{niveau}"
            if label_niveau not in tableau:
                tableau[label_niveau] = {}
            if (self.top_count > 0 and is_top_tour):                
                newMatchId = matchId
                label_newMatchId = str(newMatchId)
            else:
                newMatchId =  (matchId + 1)/2
                label_newMatchId= str(int((matchId + 1)/2))
                    
            if label_newMatchId not in tableau[label_niveau]:
                tableau[label_niveau][label_newMatchId] = {}
            
            if (self.top_count > 0 and is_top_tour):
                tableau[label_niveau][label_newMatchId]["joueur2"] = joueur
                tableau[label_niveau][label_newMatchId]["dossard_joueur2"] = dossard
            else:
                if (matchId %2 == 1):
                    print("Add ", joueur, " in tableau[", label_niveau, "][", label_newMatchId, "][joueur1]")
                    tableau[label_niveau][label_newMatchId]["joueur1"] = joueur
                    tableau[label_niveau][label_newMatchId]["dossard_joueur1"] = dossard
                else:
                    print("Add ", joueur, " in tableau[", label_niveau, "][", label_newMatchId, "][joueur2]")
                    tableau[label_niveau][label_newMatchId]["joueur2"] = joueur
                    tableau[label_niveau][label_newMatchId]["dossard_joueur2"] = dossard
            
        
        niveau = niveauBase
        
        currentNiveau = niveau
        found_holes = 2
        while (currentNiveau >=2 and found_holes >= 1):
            label_ok = f"1/{str(currentNiveau)}"
            niveauDown = int(currentNiveau / 2)
            label_niveauDown = f"1/{niveauDown}"
            found_holes = 0
            for match_id, players in list(tableau.get(label_ok, {}).items()):
                joueur1 = players.get("joueur1", "Unknown")
                joueur2 = players.get("joueur2", "Unknown")

                # Obtenir les dossards depuis `self.joueurs_info`
                joueur1_dossard = self.joueurs_info.get(joueur1, {}).get("dossard", "Unknown")
                joueur2_dossard = self.joueurs_info.get(joueur2, {}).get("dossard", "Unknown")
            
                if "joueur1" in players:
                    joueur1 = players["joueur1"]
                if "joueur2" in players:
                    joueur2 = players["joueur2"]
                is_top_tour = False

                if (niveauDown == self.top_count*4 and is_level_ok != False):
                    is_top_tour =True
                if (joueur1 == "---"):
                    addPlayerInTab(niveauDown, int(match_id), joueur2, joueur2_dossard, is_top_tour)
                    found_holes += 1
                elif (joueur2 == "---"):
                    addPlayerInTab(niveauDown, int(match_id), joueur1, joueur1_dossard, is_top_tour)
                    found_holes += 1
            currentNiveau = int(currentNiveau / 2)
    
    def create_list_match(self, tableau, joueurs_info, nb_top_players):
        """
        Construit un dictionnaire de matchs à partir d'un tableau.
        Pour chaque entrée du tableau, si la valeur du joueur est "" et que la clé (convertie en entier)
        est supérieure à (len(tableau) - nb_top_players), la valeur est remplacée par "---".
        Les matchs sont constitués de deux entrées successives.
        """
        
        list_match = {}
        idx = 0
        for entry in tableau:
            key = list(entry.keys())[0]
            player_val = entry[key]
            try:
                key_int = int(key)
            except Exception:
                key_int = 0
            # Si le joueur est vide et que la clé est supérieure à (taille du tableau - nb_top_players),
            # on remplace par "---"
            if player_val == "" and key_int > (len(tableau) - nb_top_players):
                player_val = "---"
            # Regrouper par paires
            if idx % 2 == 0:
                joueur1_nom = player_val
                print(f"Joueur1: {joueur1_nom}")
                joueur1_dossard = joueurs_info.get(joueur1_nom, {}).get("dossard", "Unknown")
                print(f"Joueur1 dossard: {joueur1_dossard}")
            else:
                joueur2_nom = player_val
                print(f"Joueur2: {joueur2_nom}")
                joueur2_dossard = joueurs_info.get(joueur2_nom, {}).get("dossard", "Unknown")
                print(f"Joueur2 dossard: {joueur2_dossard}")
                match_index = 1 + idx // 2
                list_match[match_index] = {
                    "joueur1": joueur1_nom,
                    "dossard_joueur1": joueur1_dossard,
                    "joueur2": joueur2_nom,
                    "dossard_joueur2": joueur2_dossard
                }
            idx += 1
        return list_match                
        
    def save_tableaux(self):
        """Enregistre les tableaux dans un fichier JSON séparé en ne mettant à jour que le tour initial.
        Les tours suivants, éventuellement modifiés par Saisie_Tournoi, restent inchangés.
        """
        # Calcul de l'index et du tour initial
        index = 2 ** ((self.classique_count - 1).bit_length())
            
        tourInitial = index  # tourInitial correspond à la valeur calculée avant modification
        # Pour OK, si des poules Top existent, le niveau est doublé
        print(f"Nb poules: {self.classique_count}, Nb tops: {self.top_count}, Index: {index}")
        if self.top_count > 0:
            index *= 2
        # Définir les clés pour le tour initial dans OK et KO
        key_ok = f"1/{index}"   # pour OK, avec top_count > 0, ce sera le tour initial
        key_ko = f"1/{tourInitial}"  # pour KO, on garde le tour initial non modifié

        # Création des listes de matchs à partir de self.tableauOk et self.tableauKo
        #tableau_ok_clean = [list(entry.values())[0] for entry in self.tableauOk]
        #tableau_ko_clean = [list(entry.values())[0] for entry in self.tableauKo]
        
        # Reconstruction de joueurs_info à partir de self.match_data
        nb_top_players = self.top_count * 4 if self.top_count > 0 else 0
        self.joueurs_info = {
            player["nom"] + " " + player["prenom"] + " " + player["club"]: player
            for poule in self.match_data.values()
            for player in poule.get("joueurs", [])
        }
        print(f"Joueurs info reconstruits: {self.joueurs_info}")

        list_match_ok = self.create_list_match(self.tableauOk, self.joueurs_info, nb_top_players)
        list_match_ko = self.create_list_match(self.tableauKo, self.joueurs_info, nb_top_players)

        # Charger l'existant (si le fichier existe) pour ne mettre à jour que le tour initial
        try:
            tableau_ok_data, tableau_ko_data = load_all_tableau(self.fichier_Tableau)
        except Exception:
            print("Err")

        # Si des données existent déjà, on conserve les autres tours.
        # On met à jour uniquement la partie correspondant au tour initial.

        tableau_ok_data[key_ok] = list_match_ok
        # Pour la partie intertops, si applicable, on laisse telle quelle
        if self.top_count == 1 and self.interTops:
            tableau_ok_data["1/4"] = self.interTops
        elif self.top_count == 2 and self.interTops:
            tableau_ok_data["intertops"] = self.interTops


        tableau_ko_data[key_ko] = list_match_ko

        # Optionnel : Si vous souhaitez mettre à jour éventuellement les trous (holes)
        self.updateTableauWithHoles(tableau_ok_data, index, True)
        self.updateTableauWithHoles(tableau_ko_data, tourInitial, False)

        # Structurer les données JSON en préservant les autres tours non modifiés
        #tableau_data = existing_data  # On part des données existantes
        #tableau_data.update({
        tableau_data = {
            "category": self.category,
            "round": self.round_number,
            "tourInitial": tourInitial,
            "nbTops": self.top_count,
            "nbPoules": self.classique_count,
            "Tableau OK": tableau_ok_data,
            "Tableau KO": tableau_ko_data
        }

        # Sauvegarder dans le fichier JSON
        save_tableau(self.fichier_Tableau, tableau_data)
        
    def save_results(self):
        self.save_resultats_poules()
        self.save_tableaux()

    def count_poule_types(self):
        """Compter le nombre de poules 'Top' et 'Classique'."""
        #poules = self.match_data.get("poules", {})
        self.top_count = 0
        self.classique_count = 0
        for poule_name, poule_data in self.match_data.items():
            if "Top" in poule_name:
                self.top_count += 1
            elif "Poule" in poule_name:
                self.classique_count += 1
        if self.top_count == 0:
            self.poule_type.set("Classique")
    
    def searchTargetIndex(self, nb_poules, current_poule):
        if (nb_poules % 2 == 0): # Nb poules paire
            if (current_poule%2 == 0): # Poule paire               
                target_index = 2*nb_poules-current_poule + 2
            else: # Poule impaire
                target_index = 2*nb_poules-current_poule
        else:  # Nb poules impaire
            target_index = 2*nb_poules - current_poule + 1
        return target_index
    
    def searchIndexInTab(self, cle, tableau, texte):
        for index, element in enumerate(tableau):
            if cle in element:
                element[cle] = texte
        return -1
    
    
    def update_tableau(self, final_ranking):      
        #found_4rdPlace = False
        # Compter le nombre de poules de chaque type
        current_poule = int(self.selected_poule.get().split(" ")[1].strip())

        type_poule = selected_type = self.poule_type.get()
        if (type_poule == "Top"):
            if (self.top_count == 2):
                idx = 1
                for player in final_ranking:
                    # Si la clé 1 n'existe pas dans self.interTops, on la crée
                    if str(idx) not in self.interTops:
                        self.interTops[str(idx)] = {}
                        
                    info = self.joueurs_info.get(player, {})
                    doss = info.get("dossard", "Unknown")
                    self.interTops[str(idx)][f"joueur{current_poule}"] = player
                    self.interTops[str(idx)][f"dossard_joueur{current_poule}"] = doss
                    idx += 1
            elif (self.top_count == 1):
                corr_top1 = { 1: 3, 2: 2, 3: 4, 4: 1}
                for idx, player in enumerate(final_ranking):
                    index_table = str(corr_top1[idx+1]) 
                    if idx not in self.interTops:
                        self.interTops[index_table] = {}
                    info = self.joueurs_info.get(player, {})
                    doss = info.get("dossard", "Unknown")
                    
                    self.interTops[index_table]["joueur1"] = player 
                    self.interTops[index_table]["dossard_joueur1"] = doss
                    
                    print("---Intertops:", self.interTops)
        else:
            wait_for_last_idx=False
            for idx, player in enumerate(final_ranking):
                if (idx == 0):
                    self.searchIndexInTab(current_poule, self.tableauOk, player)
                elif (idx == 1):
                    target_index = self.searchTargetIndex(self.classique_count, current_poule)
                    self.searchIndexInTab(target_index, self.tableauOk, player) 
                elif (idx == 2):
                    self.searchIndexInTab(current_poule, self.tableauKo, player)
                    wait_for_last_idx = True
                elif (idx == 3):
                    target_index = self.searchTargetIndex(self.classique_count, current_poule)
                    self.searchIndexInTab(target_index, self.tableauKo, player)
                    wait_for_last_idx = False
            if (wait_for_last_idx):
                target_index = self.searchTargetIndex(self.classique_count, current_poule)
                self.searchIndexInTab(target_index, self.tableauKo, "---")
                
    def updateEmptyLinesInTab(self):
        #poules = self.match_data.get("poules", {})

        if (self.classique_count == 2):
            nb_joueurs_max = 4
        elif (self.classique_count <= 4):
            nb_joueurs_max = 8
        elif (self.classique_count <= 8):
            nb_joueurs_max = 16
        elif (self.classique_count <= 16):
            nb_joueurs_max = 32
        elif (self.classique_count <= 32):
            nb_joueurs_max = 64
        self.tableauOk = construire_bracket(nb_joueurs_max)
        self.tableauKo = construire_bracket(nb_joueurs_max)
        
        poule_number = 1
        #for poule_name, poule_data in poules.items():
        for poule_name, poule_data in self.match_data.items():
            if ("Poule" in poule_data):
                joueurs = poule_data.get("joueurs", [])
                nb_joueurs = len(joueurs)
                if (nb_joueurs == 3):
                    target_index = self.searchTargetIndex(self.classique_count, poule_number)
                    self.searchIndexInTab(target_index, self.tableauKo, "---")

        nb_joueurs_max = self.classique_count *2
        for idx in self.tableauOk:
            for key, value in idx.items():
                if (key > nb_joueurs_max):
                    idx[key] = "---"
              
        for idx in self.tableauKo:
            for key, value in idx.items():
                if (key > nb_joueurs_max):
                    idx[key] = "---"
                    
    def calculate_ranking(self):
        players = calculate_ranking(self.player_scores, self.result_entries)
        
        for idx, player in enumerate(players):
            if idx < len(self.ranking_labels):
                self.ranking_labels[idx].config(text=f"{player}")   
        self.update_tableau(players)
        
        if players:
            self.save_button.configure(state="normal")  
        else:
            self.save_button.configure(state="disabled")
        
    def load_tableau(self):
        tableau_sauve_OK, tableau_sauve_KO = load_all_tableau(self.fichier_Tableau)
        if tableau_sauve_OK=={} and tableau_sauve_KO == {}:
            return
        
        # Calcul de l'index
        index = 2 ** ((self.classique_count - 1).bit_length())
        niveau_ok = index
        niveau_ko = index
        #if any("Top" in key for key in self.match_data.get("poules", {})):
        if self.top_count > 0:
            niveau_ok *= 2
        else:
            self.top_radioButton.destroy()
        
        niveau_ok = f"1/{niveau_ok}"
        niveau_ko = f"1/{niveau_ko}"
        
        idx=0

        # Extraire les joueurs de tableau_sauve_OK
        joueurs = []
        if tableau_sauve_OK and niveau_ok in tableau_sauve_OK:
            for match_id, players in tableau_sauve_OK.get(niveau_ok, {}).items():
                joueurs.append(players.get('joueur1', 'Unknown'))
                joueurs.append(players.get('joueur2', 'Unknown'))
            
            for item, joueur in zip(self.tableauOk, joueurs):
                key = list(item.keys())[0]  # Extraire la clé de l'élément actuel
                item[key] = joueur  # Mettre à jour la valeur
            
        # Extraire les joueurs de tableau_sauve_KO
        joueurs = []
        if tableau_sauve_KO and niveau_ko in tableau_sauve_KO:
            for match_id, players in tableau_sauve_KO.get(niveau_ko, {}).items():
                joueurs.append(players.get('joueur1', 'Unknown'))
                joueurs.append(players.get('joueur2', 'Unknown'))

            for item, joueur in zip(self.tableauKo, joueurs):
                key = list(item.keys())[0]  # Extraire la clé de l'élément actuel               
                item[key] = joueur  # Mettre à jour la valeur  
                
        if "intertops" in tableau_sauve_OK:
            self.interTops = tableau_sauve_OK["intertops"]
        
    def load_results(self):
        """Charge les résultats des matchs sauvegardés dans un fichier JSON."""
        #category = self.selected_category.get()
        #round_number = self.selected_round.get()
        poule = self.selected_poule.get()

        if not poule:
            messagebox.showerror("Erreur", "Aucune poule sélectionnée.")
            return

        poules = load_poules(self.fichier_Poules)

        if poule not in poules:
            messagebox.showerror("Erreur", f"Aucun résultat trouvé pour la poule {poule} dans le fichier.")
            return

        poule_results = poules[poule]
        matches = poule_results.get("matches", [])
        classement = poule_results.get("classement", [])

        # Mise à jour des résultats dans l'interface
        for match, (entries, player1, player2, victory_label) in zip(matches, self.result_entries):
            sets = match["sets"]
            winner = match["winner"]

            # Remplir les champs de sets
            for set_value, entry in zip(sets, entries):
                entry.delete(0, tk.END)
                entry.insert(0, set_value)

            # Mettre à jour le vainqueur
            victory_label.config(text=winner)

        # Mettre à jour le classement
        if classement:
            for idx, rank in enumerate(classement):
                if idx < len(self.ranking_labels):
                    self.ranking_labels[idx].config(text=rank)

        self.results_modified = [False]
        print("Résultats et classement chargés avec succès.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python saisie-resultats-poules-V2.7.py <categorie> <tour>")
        sys.exit(1)

    category_arg = sys.argv[1]
    round_arg = sys.argv[2]
    
    root = tk.Tk()
    app = ResultEntryApp(root, category_arg, round_arg)
    root.mainloop()