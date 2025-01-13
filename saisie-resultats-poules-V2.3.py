import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import json
import os
import math
from collections import defaultdict
from utils import charger_config
import sys

class ResultEntryApp:
    def validate_input_set(self, action, value_if_allowed):
        """Valide les entrées des sets (valeurs entre -30 et 30, avec possibilité de -)."""
        if action != '1':  # 1 correspond à l'insertion de texte
            return True
        if value_if_allowed == '':
            return True
        if value_if_allowed == '-':  # Autorise uniquement le signe '-' seul
            return True
        try:
            value = int(value_if_allowed)
            self.results_modified = True
            return -30 <= value <= 30
        except ValueError:
            return False
                
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
        #self.selected_category = tk.StringVar()
        #self.selected_round = tk.IntVar(value=1)
        self.match_results = []
        self.match_data = {}
        self.results_modified = False  # Suivre si des résultats ont été modifiés
        self.sets_mode_global = tk.StringVar(value="2 sets")
        self.current_poule = None  # Pour garder une trace de la poule actuelle
        self.current_poule_type = "Top"
        self.tableauResuPoules = []
        self.interTops = {}
        
        # Variables pour les scores des joueurs
        self.player_scores = {}        
        self.fichier_Tableau = ""
        self.fichier_Poules = ""
        self.read_config_files()

        # Cadre pour sélectionner le type de poule
        frame_type = ttk.LabelFrame(root, text="Type de Poule")
        frame_type.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(frame_type, text="Top", variable=self.poule_type, value="Top", command=self.confirm_poule_type_change).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Radiobutton(frame_type, text="Classique", variable=self.poule_type, value="Classique", command=self.confirm_poule_type_change).grid(row=0, column=1, sticky="w", padx=5)
        #ttk.Radiobutton(frame_type, text="Top", variable=self.poule_type, value="Top").grid(row=0, column=0, sticky="w", padx=5)
        #ttk.Radiobutton(frame_type, text="Classique", variable=self.poule_type, value="Classique").grid(row=0, column=1, sticky="w", padx=5)
        
        # Cadre pour sélectionner une poule
        frame_poule = ttk.LabelFrame(root, text="Sélection de la Poule")
        frame_poule.pack(fill="x", padx=10, pady=5)

        self.poule_list = ttk.Combobox(frame_poule, textvariable=self.selected_poule, state="readonly")
        self.poule_list.pack(fill="x", padx=5, pady=5)
        #self.poule_list.bind("<<ComboboxSelected>>", lambda event: self.update_match_inputs())  # Charger automatiquement
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
        save_button = ttk.Button(root, text="Enregistrer les Résultats", command=self.save_results)
        save_button.pack(pady=10)

        # Enregistrer validate_input_set après la définition de toutes les méthodes
        print("Registering validate_input_set...")

        self.validate_command_set = self.root.register(self.validate_input_set)
        # Cadre pour le classement des poules
        self.frame_ranking = ttk.LabelFrame(root, text="Classement Poule")
        self.frame_ranking.pack(fill="x", padx=10, pady=10)

        self.ranking_labels = []  # Stocke les labels du classement
        
        self.tableauOk = []
        self.tableauKo = []
        
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
        file_path = os.path.join("C:\\Users\\franck\\TVC\\", f"{self.category}_tour{self.round_number}.json")

        try:
            # Charger les données depuis le fichier JSON
            with open(self.fichier_Poules, "r", encoding="utf-8") as f:
                self.match_data = json.load(f)

            # Classifier les poules en "Top" ou "Classique"
            for poule_name, poule_data in self.match_data.get("poules", {}).items():
                if poule_name.startswith("Top"):
                    poule_data["type"] = "Top"
                else:
                    poule_data["type"] = "Classique"

            # Mettre à jour les poules pour le type sélectionné
            self.update_poules()

        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Fichier non trouvé : {self.fichier_Poules}")
        except json.JSONDecodeError:
            messagebox.showerror("Erreur", "Erreur lors du chargement du fichier JSON.")
            
             
        self.updateEmptyLinesInTab()    
            
        # Calculer le nombre de poules "Classique"
        nbPoules = sum(
            1 for poule_data in self.match_data.get("poules", {}).values()
            if poule_data.get("type") == "Classique"
        )
        #print(f"Nombre de poules Classique : {nbPoules}")
        
        # Redimensionner la fenêtre après la mise à jour
        self.resize_window_to_fit_content()
        
        self.load_tableau() 

    def update_poules(self):
        """Met à jour la liste des poules en fonction du type sélectionné."""
        selected_type = self.poule_type.get()  # "Top" ou "Classique"
        poules = self.match_data.get("poules", {})

        # Classification des poules
        poules_top = [name for name in poules if "Top" in name]
        poules_classique = [name for name in poules if "Top" not in name]

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
        else:
            # Si aucune poule n'est disponible, réinitialiser
            self.poule_list["values"] = []
            self.selected_poule.set("")
            self.create_result_inputs([])  # Aucun match à afficher
          
    def confirm_poule_type_change(self):
        if self.results_modified:
            response = messagebox.askyesno(
                "Changement de type de poule",
                "Des résultats ont été modifiés et non enregistrés. Voulez-vous continuer sans enregistrer ?"
            )
            if not response:
                # Rétablir le type de poule actuel
                self.poule_type.set(self.current_poule_type)
                return

        # Mettre à jour le type de poule actuel
        self.current_poule_type = self.poule_type.get()
        self.results_modified = False
        self.update_poules()
        
    def confirm_poule_change(self, event):
        if self.results_modified:
            response = messagebox.askyesno(
                "Changement de poule",
                "Des résultats ont été modifiés et non enregistrés. Voulez-vous continuer sans enregistrer ?"
            )
            if not response:
                # Rétablir la sélection sur la poule actuelle
                #self.poule_list.set(self.current_poule)
                return

        # Mettre à jour la poule actuelle
        self.current_poule = self.selected_poule.get()
        self.results_modified = False
        self.update_match_inputs()
        
    def update_match_inputs(self):
        """Met à jour les champs de saisie en fonction des joueurs de la poule sélectionnée."""
        poule_name = self.selected_poule.get().strip()

        if not poule_name:
            print("Aucune poule sélectionnée.")
            self.create_result_inputs([])  # Aucun joueur
            return

        poule_data = self.match_data.get("poules", {}).get(poule_name, {})
        joueurs = poule_data.get("joueurs", [])
        
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
        self.player_scores = {f"{player['nom']} {player['prenom']}": 0 for player in joueurs}  # Initialise les scores

        if not joueurs:
            messagebox.showinfo("Information", "Aucun joueur à afficher pour cette poule.")
            return

        print(f"Création des entrées pour les joueurs : {joueurs}")

        # Créer les matchs pour la poule de 3 ou 4 joueurs
        num_players = len(joueurs)
        if num_players == 4:
            matchups = [
                (0, 1), (2, 3),
                (0, 2), (1, 3),
                (0, 3), (1, 2)
            ]
        elif num_players == 3:
            matchups = [
                (0, 1),
                (1, 2),
                (0, 2)
            ]
        else:
            messagebox.showerror("Erreur", "Nombre de joueurs invalide pour la poule.")
            return

        for i, (player1_idx, player2_idx) in enumerate(matchups):
            player1 = joueurs[player1_idx]
            player2 = joueurs[player2_idx]

            print(f"Création du match : {player1['nom']} vs {player2['nom']}")

            # Cadre contenant le match et les sets
            match_frame = ttk.Frame(self.frame_results)
            match_frame.pack(fill="x", padx=10, pady=5)

            match_label_text = (
                f"{player1['nom']} {player1['prenom']} {player1['club']} vs "
                f"{player2['nom']} {player2['prenom']} {player2['club']}"
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

                set_entry = ttk.Entry(match_frame, textvariable=set_var, width=5, validate="key",
                                      validatecommand=(self.root.register(self.validate_input_set), '%d', '%P'))
                if mode == "2 sets" and j >= 3:
                    set_entry.configure(state="disabled")
                set_entry.pack(side="left", padx=2)
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
        if self.results_modified:
            # Demander une confirmation si des données sont non sauvegardées
            response = messagebox.askyesno(
                "Changement de mode",
                "Les données actuelles n'ont pas été sauvegardées. Voulez-vous continuer et effacer les données ?"
            )
            if not response:
               # Réinitialiser la sélection sur le mode précédent
                current_mode = self.sets_mode_global.get()
                new_mode = "3 sets" if current_mode == "2 sets" else "2 sets"
                self.sets_mode_global.set(new_mode)
                return

        # Si confirmé, effacer les données
        self.clear_inputs_and_labels()
        self.results_modified = False
        print("Mode changé et données réinitialisées.")
    
    def update_ranking(self):
        """Mise à jour des labels de classement selon les scores des joueurs."""
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1], reverse=True)
        #print(f"Updated ranking: {sorted_players}")
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
        self.results_modified = True

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
            if f"{player1['nom']} {player1['prenom']}" == previous_winner_name:
                previous_winner = player1
            elif f"{player2['nom']} {player2['prenom']}" == previous_winner_name:
                previous_winner = player2    

        if current_index < len(entries) - 1:
            # Validation et calcul des scores
            for entry in entries:
                value = entry.get()
                if value.startswith("-"):
                    sets_player2 += 1
                elif value.isdigit():
                    sets_player1 += 1

            # Vérifier le vainqueur
            if (mode == "2 sets" and (sets_player1 >= 2 or sets_player2 >= 2)) or \
               (mode == "3 sets" and (sets_player1 >= 3 or sets_player2 >= 3)):
                winner = player1 if sets_player1 > sets_player2 else player2
                print(f"Winner found: {winner['nom']} {winner['prenom']}")             
                
                last_victory_label = victory_label.cget("text")
                victory_label.config(text=f"Victoire: {winner['nom']} {winner['prenom']}") 
                
                if (last_victory_label != victory_label.cget("text")):
                    self.player_scores[f"{winner['nom']} {winner['prenom']}"] += 1  # Augmenter le score du vainqueur
                    if (last_victory_label != ""):
                        if (winner == player1):
                            self.player_scores[f"{player1['nom']} {player1['prenom']}"] -= 1
                        elif previous_winner == player2:
                            self.player_scores[f"{player2['nom']} {player2['prenom']}"] -= 1
                key = f"{winner['nom']} {winner['prenom']}"
                self.calculate_ranking()
                #self.update_ranking()  # Mettre à jour le classement
                
                # Placer la souris sur le premier set du match suivant
                current_match_index = self.result_entries.index((entries, player1, player2, victory_label))
                if current_match_index < len(self.result_entries) - 1:
                    next_match_entries = self.result_entries[current_match_index + 1][0]
                    if next_match_entries:
                        next_match_entries[0].focus_set()
            else:
                if (previous_winner == player1):
                    self.player_scores[f"{player1['nom']} {player1['prenom']}"] -= 1
                elif (previous_winner == player2):
                    self.player_scores[f"{player1['nom']} {player1['prenom']}"] -= 1
                #print("No winner yet")
                victory_label.config(text="")
                next_widget = entries[current_index + 1]  # Passer au champ suivant
                next_widget.focus_set()

    def toggle_sets_mode(self):
        """Ajoute ou supprime les cases en fonction du mode sélectionné."""
        for entries, player1, player2 in self.result_entries:
            current_num_sets = len(entries)
            desired_num_sets = 3 if self.sets_mode_global.get() == "2 sets" else 5
            #print(f"Current sets: {current_num_sets}, Desired sets: {desired_num_sets}")

            if current_num_sets < desired_num_sets:
                # Ajouter des champs
                for _ in range(desired_num_sets - current_num_sets):
                    set_var = tk.StringVar(value="")

                    set_entry = ttk.Entry(entries[0].master, textvariable=set_var, width=5, validate="key", validatecommand=self.root.register(self.validate_input_set))
                    set_entry.pack(side="left", padx=2)
                    set_entry.bind("<Return", lambda event, e=entries, p1=player1, p2=player2: self.handle_enter(event, e, p1, p2, self.match_labels[0]))
                    entries.append(set_entry)

            elif current_num_sets > desired_num_sets:
                #print("Removing extra sets")
                # Supprimer des champs
                for _ in range(current_num_sets - desired_num_sets):
                    entry_to_remove = entries.pop()
                    entry_to_remove.destroy()                          
    
    def save_resultats_poules(self):
        """Enregistre les résultats saisis dans un fichier JSON."""
        #category = self.selected_category.get()
        #round_number = self.selected_round.get()
        poule = self.selected_poule.get()

        # Charger les données existantes si le fichier existe
        data = {"category": self.category, "round": self.round_number, "poules": {}}
        if os.path.exists(self.fichier_Poules):
            try:
                with open(self.fichier_Poules, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier existant : {e}")
                return

        type_poule = selected_type = self.poule_type.get()
        if (type_poule == "Classique"):
            # Préserver les joueurs et mettre à jour les résultats
            if poule not in data.get("poules", {}):
                data["poules"][poule] = {"joueurs": [], "matches": [], "classement": []}

            # Collecter les résultats des matchs
            results = []
            for entries, player1, player2, victory_label in self.result_entries:
                match_result = {
                    "player1": player1,
                    "player2": player2,
                    "sets": [entry.get() for entry in entries],
                    "winner": victory_label.cget("text")
                }
                results.append(match_result)

            # Mettre à jour les résultats dans le fichier tout en conservant les joueurs
            poule_data = data["poules"][poule]
            if "joueurs" not in poule_data:
                poule_data["joueurs"] = [{"nom": player["nom"], "prenom": player["prenom"], "club": player["club"]}
                                     for _, player, _, _ in self.result_entries]

            poule_data["matches"] = results

            # Ajouter le classement si calculé
            classement = []
            for label in self.ranking_labels:
                text = label.cget("text").strip()
                if text:
                    classement.append(text)
            poule_data["classement"] = classement

        # Enregistrer dans le fichier
        try:
            with open(self.fichier_Poules, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Succès", f"Résultats enregistrés dans {self.fichier_Poules}.")
            self.results_modified = False  # Réinitialiser après sauvegarde
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")

    #def updaTableauIntertops(self):
        #print("intertops: ", self.interTops)

    def updateTableauWithHoles(self, tableau, niveauBase, is_level_ok):
        
        
        def addPlayerInTab(niveau, matchId, joueur, is_level_ok):
            top_count, nb_poules = self.count_poule_types()
            label_niveau = f"1/{niveau}"
            if label_niveau not in tableau:
                tableau[label_niveau] = {}
            if (top_count == 2 and is_level_ok):
                newMatchId = matchId
                label_newMatchId = str(newMatchId)
            else:
                newMatchId =  (matchId + 1)/2
                label_newMatchId= str(int((matchId + 1)/2))
            if label_newMatchId not in tableau[label_niveau]:
                #print("label_matchId :", label_newMatchId, " NOT FOUND")
                tableau[label_niveau][label_newMatchId] = {}
            
            if (top_count == 2 and is_level_ok):
                tableau[label_niveau][label_newMatchId]["joueur2"] = joueur
            else:
                #print("newMatchId:", newMatchId, ", matchId:", matchId, ", label_newMatchId", label_newMatchId, "joueur:", joueur, "label_niveau:", label_niveau)
                if (newMatchId %2 == 1):
                    #print("tableau[",label_niveau,"][", label_newMatchId,"][-joueur1-]=", joueur)
                    tableau[label_niveau][label_newMatchId]["joueur1"] = joueur
                else:
                    #print("tableau[",label_niveau,"][", label_newMatchId,"][-joueur2-]=", joueur)
                    tableau[label_niveau][label_newMatchId]["joueur2"] = joueur
            
        
        niveau = niveauBase
        
        currentNiveau = niveau
        found_holes = 2
        while (currentNiveau >=4 and found_holes >= 1):
            label_ok = f"1/{str(currentNiveau)}"
            niveauDown = int(currentNiveau / 2)
            label_niveauDown = f"1/{niveauDown}"
            found_holes = 0
            for match_id, players in list(tableau.get(label_ok, {}).items()):
                #print("match_id=", match_id)
                joueur1 = ""
                joueur2 = ""
                if "joueur1" in players:
                    joueur1 = players["joueur1"]
                if "joueur2" in players:
                    joueur2 = players["joueur2"]
                print ("joueur1", joueur1, ",joueur2", joueur2, ",match_id:", match_id)
                if (joueur1 == "---"):
                    #print ("joueur1", joueur1, ",joueur2", joueur2)
                    addPlayerInTab(niveauDown, int(match_id), joueur2, is_level_ok)
                    found_holes += 1
                elif (joueur2 == "---"):
                    addPlayerInTab(niveauDown, int(match_id), joueur1, is_level_ok)
                    found_holes += 1
            currentNiveau = int(currentNiveau / 2)
        
    def save_tableaux(self):
        """Enregistre les tableaux dans un fichier JSON séparé."""
        top_count, nb_poules = self.count_poule_types()

        # Calcul de l'index
        index = 2 ** ((nb_poules - 1).bit_length())
        tourInitial = index
        label_ko = f"1/{index}"
        niveau_ok = index
        if any("Top" in key for key in self.match_data.get("poules", {})):
            index *= 2
            
        label_ok = f"1/{index}"
        

        tableau_ok_clean = [list(entry.values())[0] for entry in self.tableauOk]
        tableau_ko_clean = [list(entry.values())[0] for entry in self.tableauKo]

        # Nouveau format : créer des entrées pour les matchs
        def create_list_match(tableau_clean):
            list_match = {}
            idx = 0
            for i in range(0, len(tableau_clean), 2):
                joueur1 = tableau_clean[i]
                joueur2 = tableau_clean[i + 1] if i + 1 < len(tableau_clean) else ""
                match_index = 1 + idx // 2
                list_match[match_index] = {"joueur1": joueur1, "joueur2": joueur2}
                idx += 2
            return list_match
            
        list_match_ok = create_list_match(tableau_ok_clean)
        list_match_ko = create_list_match(tableau_ko_clean)
        
        
        # Préparation des données pour les intertops
        #self.updaTableauIntertops()

        # Structuration des données JSON
        tableau_ok_data = {label_ok: list_match_ok}
 
        if top_count == 1 and self.interTops:                
            tableau_ok_data["1/4"] = self.interTops
        elif top_count == 2 and self.interTops:
            tableau_ok_data["intertops"] = self.interTops
        tableau_ko_data= {}
        tableau_ko_data[label_ko] = {}
        tableau_ko_data[label_ko] = list_match_ko

        # Mettre à jour le tableau si matches 
        self.updateTableauWithHoles(tableau_ok_data, index, True)
        self.updateTableauWithHoles(tableau_ko_data, tourInitial, False)
        
        # Structurer les données JSON
        tableau_data = {
            "category": self.category,
            "round": self.round_number,
            "tourInitial": tourInitial,
            "nbTops": top_count,
            "nbPoules": nb_poules,
            "Tableau OK": tableau_ok_data,
            "Tableau KO": tableau_ko_data
        }                    
            
        try:
            with open(self.fichier_Tableau, "w", encoding="utf-8") as f:
                json.dump(tableau_data, f, indent=4, ensure_ascii=False)
            print(f"Tableaux enregistrés dans {self.fichier_Tableau}.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des tableaux : {e}")
            
    def save_results(self):
        self.save_resultats_poules()
        self.save_tableaux()

    def count_poule_types(self):
        """Compter le nombre de poules 'Top' et 'Classique'."""
        poules = self.match_data.get("poules", {})
        top_count = 0
        classique_count = 0

        for poule_name, poule_data in poules.items():
            poule_type = poule_data.get("type", "")
            if poule_type == "Top":
                top_count += 1
            elif poule_type == "Classique":
                classique_count += 1

        #print(f"Nombre de poules 'Top': {top_count}, 'Classique': {classique_count}")
        return top_count, classique_count
    
    def searchTargetIndex(self, nb_poules, current_poule):
        #print("In searchTargetIndex, nb_poules =", nb_poules, ",current_poule =", current_poule)
        if (nb_poules % 2 == 0): # Nb poules paire
            if (current_poule%2 == 0): # Poule paire               
                target_index = 2*nb_poules-current_poule + 2
            else: # Poule impaire
                #target_index = 2*nb_poules-current_poule - 1
                target_index = 2*nb_poules-current_poule
        else:  # Nb poules impaire
            target_index = 2*nb_poules - current_poule + 1
        return target_index
    
    def searchIndexInTab(self, cle, tableau, texte):
        #print("Search cle:", cle)
        for index, element in enumerate(tableau):
            if cle in element:
                #print("cle found in ", element)
                element[cle] = texte
        return -1
    
    
    def update_tableau(self, final_ranking):      
        #found_4rdPlace = False
        # Compter le nombre de poules de chaque type
        top_count, nb_poules = self.count_poule_types()
        current_poule = int(self.selected_poule.get().split(" ")[1].strip())

        type_poule = selected_type = self.poule_type.get()
        if (type_poule == "Top"):
            if (top_count == 2):
                idx = 1
                #print("current-poule", current_poule)
                for player in final_ranking:
                    # Si la clé 1 n'existe pas dans self.interTops, on la crée
                    if str(idx) not in self.interTops:
                        self.interTops[str(idx)] = {}
    
                    # On ajoute player sous la forme "joueur{current_poule}"
                    self.interTops[str(idx)][f"joueur{current_poule}"] = player[0]
                    idx += 1
            elif (top_count == 1):
                for idx, player in enumerate(final_ranking):
                    index_table = str(idx+1)
                    if idx not in self.interTops:
                        self.interTops[index_table] = {}
                    self.interTops[index_table]["joueur1"] = player[0]    
        else:
            for idx, player in enumerate(final_ranking):
                if (idx == 0):
                    self.searchIndexInTab(current_poule, self.tableauOk, player[0])
                elif (idx == 1):
                    target_index = self.searchTargetIndex(nb_poules, current_poule)
                    self.searchIndexInTab(target_index, self.tableauOk, player[0]) 
                elif (idx == 2):
                    self.searchIndexInTab(current_poule, self.tableauKo, player[0])
                elif (idx == 3):
                    #found_4rdPlace = True
                    target_index = self.searchTargetIndex(nb_poules, current_poule)
                    self.searchIndexInTab(target_index, self.tableauKo, player[0])
                
    def updateEmptyLinesInTab(self):
        tableau8joueurs_ok = [{1,""},{8,""},{5,""},{4,""},{3,""},{6,""},{7,""},{2,""}]
        tableau16joueurs_ok = [
            {1: ""}, {16: ""}, {9: ""}, {8: ""}, {5: ""}, {12: ""}, {13: ""}, {4: ""},
            {3: ""}, {14: ""}, {11: ""}, {6: ""}, {7: ""}, {10: ""}, {15: ""}, {2: ""}
        ]
        tableau32joueurs_ok = [
            {1: ""}, {32: ""}, {17: ""}, {16: ""}, {9: ""}, {24: ""}, {25: ""}, {8: ""},
            {5: ""}, {28: ""}, {21: ""}, {12: ""}, {13: ""}, {20: ""}, {29: ""}, {4: ""},
            {3: ""}, {30: ""}, {19: ""}, {14: ""}, {11: ""}, {22: ""}, {27: ""}, {6: ""},
            {7: ""}, {26: ""}, {23: ""}, {10: ""}, {15: ""}, {18: ""}, {31: ""}, {2: ""}
        ]
        
        tableau8joueurs_ko = [{1,""},{8,""},{5,""},{4,""},{3,""},{6,""},{7,""},{2,""}]
        tableau16joueurs_ko = [
            {1: ""}, {16: ""}, {9: ""}, {8: ""}, {5: ""}, {12: ""}, {13: ""}, {4: ""},
            {3: ""}, {14: ""}, {11: ""}, {6: ""}, {7: ""}, {10: ""}, {15: ""}, {2: ""}
        ]
        tableau32joueurs_ko = [
            {1: ""}, {32: ""}, {17: ""}, {16: ""}, {9: ""}, {24: ""}, {25: ""}, {8: ""},
            {5: ""}, {28: ""}, {21: ""}, {12: ""}, {13: ""}, {20: ""}, {29: ""}, {4: ""},
            {3: ""}, {30: ""}, {19: ""}, {14: ""}, {11: ""}, {22: ""}, {27: ""}, {6: ""},
            {7: ""}, {26: ""}, {23: ""}, {10: ""}, {15: ""}, {18: ""}, {31: ""}, {2: ""}
        ]
        
        
        
        poules = self.match_data.get("poules", {})
        top_count = 0
        classique_count = 0
        top_count, nb_poules = self.count_poule_types()
        if (nb_poules <= 4):
            self.tableauOk = tableau8joueurs_ok
            self.tableauKo = tableau8joueurs_ko
        elif (nb_poules <= 8):
            self.tableauOk = tableau16joueurs_ok
            self.tableauKo = tableau16joueurs_ko
        elif (nb_poules <= 16):
            self.tableauOk = tableau32joueurs_ok
            self.tableauKo = tableau32joueurs_ko

        poule_number = 1
        for poule_name, poule_data in poules.items():
            poule_type = poule_data.get("type", "")
            if (poule_data.get("type", "")) == "Classique":
                joueurs = poule_data.get("joueurs", [])
                nb_joueurs = len(joueurs)
                if (nb_joueurs == 3):
                    target_index = self.searchTargetIndex(nb_poules, poule_number)
                    self.searchIndexInTab(target_index, self.tableauKo, "---")

        nb_joueurs_max = nb_poules *2
        for idx in self.tableauOk:
            for key, value in idx.items():
                if (key > nb_joueurs_max):
                    idx[key] = "---"
              
        for idx in self.tableauKo:
            for key, value in idx.items():
                if (key > nb_joueurs_max):
                    idx[key] = "---"                           
        
    def calculate_ranking(self):
        """Calcule le classement des joueurs en suivant les règles spécifiées."""
        if not self.result_entries:
            return

        from collections import defaultdict

        # Vérifier que tous les matchs ont été saisis
        required_matches = 6 if len(self.result_entries) == 6 else 3
        completed_matches = 0

        for nom, pts in self.player_scores.items():
            completed_matches += pts

        if completed_matches < required_matches:
            return []

        wins = [pts for pts in self.player_scores.values()]
        if len(wins) == len(set(wins)):
            sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1], reverse=True)
                       
            # Mettre à jour les labels de classement
            for idx, player in enumerate(sorted_players):
                if idx < len(self.ranking_labels):
                    self.ranking_labels[idx].config(text=f"{player[0]}")   
            self.update_tableau(sorted_players)
            return sorted_players

        # Collecte des données des matchs
        players_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "sets_won": 0, "sets_lost": 0, "points_won": 0, "points_lost": 0, "ratio_sets": 0, "ratio_points": 0})
        matches_between_players_sets = defaultdict(dict)
        matches_between_players_points = defaultdict(dict)

        for entries, player1, player2, victory_label in self.result_entries:
            player1_key = f"{player1['nom']} {player1['prenom']}"
            player2_key = f"{player2['nom']} {player2['prenom']}"
            sets_player1 = 0
            sets_player2 = 0
            points_player1 = 0
            points_player2 = 0

            # Analyse des résultats des sets
            for set_result in entries:
                try:
                    score = set_result.get()
                    if score.startswith("-"):
                        p1 = abs(int(score))
                        p2 = 11 if p1 < 10 else p1 + 2
                        points_player1 += p1
                        points_player2 += p2
                        sets_player2 += 1
                    else:
                        p2 = int(score)
                        p1 = 11 if p2 < 10 else p2 + 2
                        points_player1 += p1
                        points_player2 += p2
                        sets_player1 += 1
                except ValueError:
                    continue  # Ignore les entrées invalides

            # Mise à jour des statistiques
            if sets_player1 > sets_player2:
                players_stats[player1_key]["wins"] += 1
                players_stats[player2_key]["losses"] += 1
            elif sets_player2 > sets_player1:
                players_stats[player2_key]["wins"] += 1
                players_stats[player1_key]["losses"] += 1

            players_stats[player1_key]["sets_won"] += sets_player1
            players_stats[player1_key]["sets_lost"] += sets_player2
            players_stats[player1_key]["points_won"] += points_player1
            players_stats[player1_key]["points_lost"] += points_player2

            players_stats[player2_key]["sets_won"] += sets_player2
            players_stats[player2_key]["sets_lost"] += sets_player1
            players_stats[player2_key]["points_won"] += points_player2
            players_stats[player2_key]["points_lost"] += points_player1

            # Enregistrer les résultats entre joueurs
            matches_between_players_sets[player1_key][player2_key] = (sets_player1, sets_player2)
            matches_between_players_sets[player2_key][player1_key] = (sets_player2, sets_player1)
            matches_between_players_points[player1_key][player2_key] = (points_player1, points_player2)
            matches_between_players_points[player2_key][player1_key] = (points_player2, points_player1)
        
        for entries, player1, player2, victory_label in self.result_entries:
            player1_key = f"{player1['nom']} {player1['prenom']}"
            player2_key = f"{player2['nom']} {player2['prenom']}"
            
            if (players_stats[player1_key]["wins"] == 3):
                players_stats[player1_key]["ratio_sets"] = 2
                
        def compare_players_2p(player_a, player_b, relevant_players):
            # Cas 1 : Match direct (entre joueurs concernés uniquement)
            if player_b in matches_between_players_sets[player_a] and player_b in relevant_players:
                sets_a, sets_b = matches_between_players_sets[player_a][player_b]
                if sets_a > sets_b:
                    return -1
                elif sets_b > sets_a:
                    return 1
                    
        def sort_2players(relevant_players):
            tied_players = []
            first_player = list(relevant_players)[0]
            second_player = list(relevant_players)[1]
            sets_a, sets_b = matches_between_players_sets[first_player][second_player]
            if (sets_a > sets_b):
                tied_players.append(first_player)
                tied_players.append(second_player)
            else:
                tied_players.append(second_player)
                tied_players.append(first_player)
            return tied_players

        def compare_players_3p(player_a, player_b, relevant_players):
            # Cas 2 : Ratio sets gagnés/perdus (entre joueurs concernés uniquement)
            sets_ratio_a = players_stats[player_a]["sets_won"] - players_stats[player_a]["sets_lost"]
            sets_ratio_b = players_stats[player_b]["sets_won"] - players_stats[player_b]["sets_lost"]
            print ("sets_ratio_a: ", sets_ratio_a, ",sets_ratio_b", sets_ratio_b)
            if sets_ratio_a != sets_ratio_b:
                return -1 if sets_ratio_a > sets_ratio_b else 1

            # Cas 3 : Ratio points gagnés/perdus (entre joueurs concernés uniquement)
            points_ratio_a = players_stats[player_a]["points_won"] - players_stats[player_a]["points_lost"]
            points_ratio_b = players_stats[player_b]["points_won"] - players_stats[player_b]["points_lost"]
            if points_ratio_a != points_ratio_b:
                return -1 if points_ratio_a > points_ratio_b else 1

            return 0  # Égalité parfaite

        # Classement des joueurs
        players = list(players_stats.keys())
        # Trier les joueurs selon le nombre de victoires
        players.sort(key=lambda p: players_stats[p]["wins"], reverse=True)

        # Identifier les groupes d'égalité
        groups = defaultdict(list)
        for player in players:
            groups[players_stats[player]["wins"]].append(player)

        final_ranking = []
        for group in sorted(groups.keys(), reverse=True):
            if len(groups[group]) > 1:
                # Résolution des égalités dans le groupe
                tied_players = groups[group]
                relevant_players = set(tied_players)

                # Isoler les résultats entre joueurs concernés
                for player in tied_players:
                    players_stats[player]["sets_won"] = sum(matches_between_players_sets[player][opponent][0] for opponent in relevant_players if opponent != player)
                    players_stats[player]["sets_lost"] = sum(matches_between_players_sets[player][opponent][1] for opponent in relevant_players if opponent != player)

                    players_stats[player]["points_won"] = sum(matches_between_players_points[player][opponent][0] for opponent in relevant_players if opponent != player)
                    players_stats[player]["points_lost"] = sum(matches_between_players_points[player][opponent][1] for opponent in relevant_players if opponent != player)
                    if (players_stats[player]["sets_lost"] > 0):
                        players_stats[player]["ratio_sets"] = players_stats[player]["sets_won"] / players_stats[player]["sets_lost"]
                    else:
                        players_stats[player]["ratio_sets"] = players_stats[player]["sets_won"]
                    if (players_stats[player]["points_lost"] > 0):
                        players_stats[player]["ratio_points"] = players_stats[player]["points_won"] / players_stats[player]["points_lost"]
                    else:
                        players_stats[player]["ratio_points"] = players_stats[player]["points_won"]
                    #print ("player:", player, ",points_won:", players_stats[player]["points_won"], ",points_lost:", players_stats[player]["points_lost"], "ratio:", players_stats[player]["ratio_points"])
                    #print ("player:", player, ",sets_won", players_stats[player]["sets_won"], ",sets_lost", players_stats[player]["sets_lost"], ",ratio_sets:", players_stats[player]["ratio_sets"], ",ratio_points:", players_stats[player]["ratio_points"] )
                
                if (len(groups[group]) == 2):
                    #tied_players.sort(key=lambda x: sorted(tied_players, key=lambda y: compare_players_2p(x, y, relevant_players)))
                    tied_players = sort_2players(relevant_players)
                elif (len(groups[group]) == 3):
                    tied_players.sort(
                        key=lambda x: (players_stats[x]["ratio_sets"], players_stats[x]["ratio_points"]),
                        reverse=True
                    )
                #tied_players.sort(key=lambda x: sorted(tied_players, key=lambda y: compare_players(x, y, relevant_players)))
                final_ranking.extend(tied_players)
            else:
                final_ranking.extend(groups[group])
                #Mettre à jour le vainqueur dans le tableau des vainqueurs

        for idx, player in enumerate(final_ranking):
            if idx < len(self.ranking_labels):
                self.ranking_labels[idx].config(text=f"{player}")                                    
        if (self.current_poule_type == "Classique"):
            #print ("poule classique")
            self.update_tableau(final_ranking)
        
    def load_tableau(self):
        self.root = root

        try:
            with open(self.fichier_Tableau, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Fichier non trouvé : {self.fichier_Tableau}")
            return
            
        tableau_sauve_OK = data.get("Tableau OK")
        tableau_sauve_KO = data.get("Tableau KO")

        
        # Calcul de l'index
        top_count, nb_poules = self.count_poule_types()
        index = 2 ** ((nb_poules - 1).bit_length())
        niveau_ok = index
        niveau_ko = index
        if any("Top" in key for key in self.match_data.get("poules", {})):
            niveau_ok *= 2
        
        niveau_ok = f"1/{niveau_ok}"
        niveau_ko = f"1/{niveau_ko}"
        
        idx=0

        # Extraire les joueurs de tableau_sauve_OK
        joueurs = []
        if tableau_sauve_OK and niveau_ok in tableau_sauve_OK:
            for match_id, players in tableau_sauve_OK.get(niveau_ok, {}).items():
                joueurs.append(players.get('joueur1', 'Unknown'))
                joueurs.append(players.get('joueur2', 'Unknown'))

            # Mise à jour de toto
            for item, joueur in zip(self.tableauOk, joueurs):
                key = list(item.keys())[0]  # Extraire la clé de l'élément actuel
                item[key] = joueur  # Mettre à jour la valeur
            
            
        # Extraire les joueurs de tableau_sauve_OK
        joueurs = []
        if tableau_sauve_KO and niveau_ko in tableau_sauve_KO:
            for match_id, players in tableau_sauve_KO.get(niveau_ko, {}).items():
                joueurs.append(players.get('joueur1', 'Unknown'))
                joueurs.append(players.get('joueur2', 'Unknown'))

            # Mise à jour de toto
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

        try:
            # Charger les résultats depuis le fichier JSON
            with open(self.fichier_Poules, "r", encoding="utf-8") as f:
                data = json.load(f)

            if poule not in data.get("poules", {}):
                messagebox.showerror("Erreur", f"Aucun résultat trouvé pour la poule {poule} dans le fichier.")
                return

            poule_results = data["poules"][poule]
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

            self.results_modified = False
            print("Résultats et classement chargés avec succès.")

        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Fichier non trouvé : {self.fichier_Poules}")
        except json.JSONDecodeError:
            messagebox.showerror("Erreur", "Erreur lors du chargement du fichier JSON.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
 
    def read_config_files(self):
        config_file = "config.ini"  # Assurez-vous que ce fichier existe
        try:
            directory, input_file = charger_config(config_file)
            print(f"Répertoire : {directory}")

            # Utiliser les paramètres pour exécuter le reste du script
        
            self.fichier_Poules = os.path.join(directory, f"{self.category}_tour{self.round_number}.json")
            self.fichier_Tableau = os.path.join(directory, f"Tableau_{self.category}_tour{self.round_number}.json")
        
            print ("Fichier Poules:", self.fichier_Poules, ", Fichier Tableau:", self.fichier_Tableau)
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"Erreur : {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python saisie-resultats-poules-V2.2.py <categorie> <tour>")
        sys.exit(1)

    category_arg = sys.argv[1]
    round_arg = sys.argv[2]
    
    root = tk.Tk()
    app = ResultEntryApp(root, category_arg, round_arg)
    root.mainloop()