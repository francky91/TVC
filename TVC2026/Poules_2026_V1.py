from hashlib import new
import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
from modules.utils import *
import sys
from modules.logic import *
from modules.SaisieMatch import validate_input_set,handle_mode_change
from modules.models import Player, Match, Level
from modules.Tournoi import Tournoi
from modules.debug import debug_print

class ResultEntryApp:        
    def __init__(self, root, category, round_number):
        self.root = root
        
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
        self.results_modified  = [False] # Suivre si des résultats ont été modifiés
        self.sets_mode_global = tk.StringVar(value="2 sets")
        self.current_poule = None  # Pour garder une trace de la poule actuelle
        self.current_poule_type = "Top"
        #self.interTops = Tableau(type="InterTops", tourInitial=0, tableauLevels=TableauLevels("1/1", matches=[]))
        
        self.tournoi = Tournoi(category=category, tour=round_number, nb_tops=0, nb_poules=0, nb_joueurs=0, tourInitial=Level(1))
        
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
        self.tournoi.load_poules()
        #self.tournoi.tableauOk.init_tableau_with_absent_players(self.tournoi.nb_poules, self.tournoi.nb_tops)
        #self.tournoi.tableauKo.init_tableau_with_absent_players(self.tournoi.nb_poules, 0)

        if getattr(self.tournoi, "nb_tops", 0) == 0:
            # forcer le mode Classique
            self.poule_type.set("Classique")
            self.current_poule_type = "Classique"
            # détruire le widget Top s'il existe
            if hasattr(self, "top_radioButton") and self.top_radioButton is not None:
                try:
                    self.top_radioButton.destroy()
                except Exception:
                    pass
                # repositionner le bouton Classique à la colonne 0
                try:
                    self.class_radioButton.grid_forget()
                    self.class_radioButton.grid(row=0, column=0, sticky="w", padx=5)
                except Exception:
                    pass

        
        self.update_poules()

        self.resize_window_to_fit_content()

    def update_poules(self):
        """Met à jour la liste des poules en fonction du type sélectionné."""
        if self.tournoi.nb_tops == 0:
            self.poule_type.set("Classique")
        selected_type = self.poule_type.get()  # "Top" ou "Classique"
        self.clear_inputs_and_labels()
        debug_print("Mise à jour des poules pour le type:", selected_type)

        # Récupérer les deux listes (on ne fait qu'un appel par méthode)
        try:
            top_labels = self.tournoi.poules.get_poules_top_labels() or []
        except Exception:
            top_labels = []
        try:
            std_labels = self.tournoi.poules.get_poules_std_labels() or []
        except Exception:
            std_labels = []

        # Heuristique : détecte la liste "Top" en cherchant un préfixe "Top" dans les labels
        debug_print("top_labels", top_labels, "std_labels", std_labels)
        '''def looks_like_top(lst):
            for s in lst:
                if isinstance(s, str) and s.lower().strip().startswith("top"):
                    return True
            return False

        # Si les noms sont inversés dans l'implémentation, on corrige ici
        if not looks_like_top(top_labels) and looks_like_top(std_labels):
            top_labels, std_labels = std_labels, top_labels
        '''
        # Choisir la liste à afficher suivant le radio bouton
        filtered_poules = top_labels if selected_type == "Top" else std_labels

        debug_print("filtered_poules", filtered_poules)

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
            debug_print("poule vide")
         
    def confirm_poule_type_change(self):
        if self.tournoi.nb_tops == 0:  # Ne rien demander si Top est vide
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
        self.current_poule =  new_poule
        self.results_modified = [False]
        self.update_match_inputs()
        self.resize_window_to_fit_content()                                                                                            #
                                                                                             
    def update_match_inputs(self):
        """Met à jour les champs de saisie en fonction des joueurs de la poule sélectionnée."""
        poule_name = self.selected_poule.get().strip()
        poule_idx = self.selected_poule.get()
        debug_print(f"poule_idx: {poule_idx}")
        debug_print(f"Poule sélectionnée pour mise à jour des matchs : '{poule_name}'")

        if not poule_name:
            debug_print("Aucune poule sélectionnée.")
            self.create_result_inputs([])  # Aucun joueur
            return

        poule_idx = self.tournoi.poules.get_poule_for_name(poule_name)
        joueurs = poule_idx.players
        if joueurs:
            self.create_result_inputs(joueurs)
        else:
            debug_print(f"Aucun joueur trouvé pour la poule {poule_name}.")
            self.create_result_inputs([])

    def create_result_inputs(self, joueurs):
        """Crée les champs pour saisir les résultats des joueurs."""
        # Suppression des anciens widgets
        for label in self.match_labels:
            label.destroy()
        for widget in self.frame_results.winfo_children():
            widget.destroy()

        self.match_labels = []
        self.result_entries = []
        self.player_scores = {player.key: 0 for player in joueurs}  # Initialise les scores

        # Désactiver le bouton d'enregistrement tant que rien n'est complet
        self.save_button.configure(state="disabled")

        if not joueurs:
            messagebox.showinfo("Information", "Aucun joueur à afficher pour cette poule.")
            return

        debug_print(f"Création des entrées pour les joueurs : {joueurs}")

        # Définir les matchups en fonction du nombre de joueurs
        matchups = self.get_matchups(len(joueurs))
        if not matchups:
            messagebox.showerror("Erreur", "Nombre de joueurs invalide pour la poule.")
            return

        for player1_idx, player2_idx in matchups:
            player1 = joueurs[player1_idx]
            player2 = joueurs[player2_idx]

            debug_print(f"Création du match : {player1.nom} {player1.prenom} ({player1.club}) vs {player2.nom} {player2.prenom} ({player2.club})")

            # Créer le cadre pour le match
            match_frame = ttk.Frame(self.frame_results)
            match_frame.pack(fill="x", padx=10, pady=5)

            # Ajouter le label pour le match
            match_label_text = f"{player1.key} vs {player2.key}"
            label = ttk.Label(match_frame, text=match_label_text)
            label.pack(side="left", padx=10)
            self.match_labels.append(label)

            victory_frame = ttk.Frame(self.frame_results)
            victory_frame.pack(fill="x", padx=10, pady=5)
            victory_label = ttk.Label(victory_frame, text="")
            victory_label.pack(anchor="w", padx=10)

            # Créer les champs de saisie pour les sets
            entries = self.create_set_entries(match_frame, player1, player2, victory_label)

            self.result_entries.append((entries, player1, player2, victory_label))

        self.create_ranking_labels(len(joueurs))
        debug_print("Résultats créés avec succès.")

    def get_matchups(self, num_players):
        """Retourne les matchups en fonction du nombre de joueurs."""
        if num_players == 4:
            return [
                (0, 3), (1, 2),
                (0, 2), (1, 3),
                (0, 1), (2, 3)
            ]
        elif num_players == 3:
            return [
                (1, 2),
                (0, 2),
                (0, 1)
            ]
        else:
            debug_print(f"Erreur: Nombre de joueurs invalide pour la poule, num_players: {num_players}")
            return None

    def create_set_entries(self, match_frame, player1, player2, victory_label):
        """Crée les champs de saisie pour les sets."""
        entries = []
        mode = self.sets_mode_global.get()
        max_sets = 5 if mode == "3 sets" else 3

        for j in range(5):
            set_var = tk.StringVar(value="")
            set_entry = ttk.Entry(
                match_frame, textvariable=set_var, width=5, validate="key",
                validatecommand=(self.root.register(lambda action, value: validate_input_set(action, value, self.results_modified)), '%d', '%P')
            )
            if j >= max_sets:
                set_entry.configure(state="disabled")
            set_entry.pack(side="left", padx=2)

            # Ajouter les événements pour gérer les interactions
            set_entry.bind("<Return>", lambda event, e=entries, p1=player1, p2=player2, v1=victory_label: self.handle_enter(event, e, p1, p2, v1))
            entries.append(set_entry)

        return entries
        
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
        debug_print("Sets mode updated. No additional actions needed as 5 fields are always present.")
               
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
        debug_print("Mise à jour du classement des joueurs.")
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
        debug_print("Scores réinitialisés.")
        
        # Réinitialiser les labels de classement
        for label in self.ranking_labels:
            label.config(text=" ")
            
        # Désactiver le bouton d'enregistrement tant que rien n'est complet
        self.save_button.configure(state="disabled")
        
        debug_print("Tous les champs et labels ont été réinitialisés.")      
        
        
    def update_match_in_poule(self, player1, player2, entries, winner):
        selected_poule_name = self.selected_poule.get()
        poule_obj = self.tournoi.poules.get_poule_for_name(selected_poule_name)
        
        sets = [entry.get() for entry in entries]
        
        match_existant = next((m for m in poule_obj.matches 
                             if m.player1 == player1 and m.player2 == player2), None)
        
        if match_existant:
            match_existant.sets = sets
            match_existant.winner = winner
            debug_print(f"Match mis à jour pour {player1.nom} vs {player2.nom}")
        else:
            new_match = Match(0, player1=player1, player2=player2, sets=sets, idxPlayer1=0, idxPlayer2=0, checkbox_state=False, winner=winner)
            poule_obj.matches.append(new_match)

    def handle_enter(self, event, entries, player1, player2, victory_label):
        """Gère la validation des scores et détermine le vainqueur."""
        mode = self.sets_mode_global.get()
        self.results_modified[0] = True

        # Navigation entre champs
        current_widget = event.widget
        current_index = entries.index(current_widget)

        # Remplir les champs vides ou invalides
        if current_widget.get() == "":
            current_widget.insert(0, "0")
        elif current_widget.get() == "-":
            current_widget.insert(0, "-0")

        # Calcul des sets gagnés par chaque joueur
        sets_player1 = sum(1 for entry in entries if entry.get().isdigit())
        sets_player2 = sum(1 for entry in entries if entry.get().startswith("-"))

        # Déterminer le vainqueur si les conditions sont remplies
        winning_sets = {"2 sets": 2, "3 sets": 3}
        required_sets = winning_sets.get(mode, 0)

        if sets_player1 == required_sets or sets_player2 == required_sets:
            winner = player1 if sets_player1 > sets_player2 else player2
            self.update_match_in_poule(player1, player2, entries, winner)

            # Mettre à jour le label de victoire
            victory_text = f"Victoire: {winner.nom} {winner.prenom} ({winner.club})"
            if victory_label.cget("text") != victory_text:
                victory_label.config(text=victory_text)
                self.update_player_scores(winner, player1, player2, victory_label)

            # Passer au premier champ du match suivant
            self.focus_next_match(entries, player1, player2, victory_label)
        else:
            # Réinitialiser le label de victoire si aucun vainqueur
            victory_label.config(text="")
            self.focus_next_field(entries, current_index)

    def update_player_scores(self, winner, player1, player2, victory_label):
        """Met à jour les scores des joueurs en fonction du vainqueur."""
        previous_winner_text = victory_label.cget("text")
        previous_winner = None

        if previous_winner_text.startswith("Victoire:"):
            previous_winner_name = previous_winner_text.split(":")[1].strip()
            if f"{player1.nom} {player1.prenom} ({player1.club})" == previous_winner_name:
                previous_winner = player1
            elif f"{player2.nom} {player2.prenom} ({player2.club})" == previous_winner_name:
                previous_winner = player2

        if previous_winner:
            if previous_winner == player1:
                self.player_scores[player2.key] -= 1
            elif previous_winner == player2:
                self.player_scores[player1.key] -= 1

        self.player_scores[winner.key] += 1
        self.calculate_ranking()

    def focus_next_match(self, entries, player1, player2, victory_label):
        """Place le focus sur le premier champ du match suivant."""
        current_match_index = self.result_entries.index((entries, player1, player2, victory_label))
        if current_match_index < len(self.result_entries) - 1:
            next_match_entries = self.result_entries[current_match_index + 1][0]
            if next_match_entries:
                next_match_entries[0].focus_set()

    def focus_next_field(self, entries, current_index):
        if current_index < len(entries) - 1:
            entries[current_index + 1].focus_set()
    
    def save_resultats_poules(self):
        selected_poule_name = self.selected_poule.get()
        if not selected_poule_name:
            messagebox.showwarning("Attention", "Veuillez sélectionner une poule.")
            return False

        debug_print("selected_poule_name", selected_poule_name)
        success = self.tournoi.poules.save_poules(selected_poule_name)

        if success:
            self.results_modified = [False]
            messagebox.showinfo("Succès", f"Résultats de la {selected_poule_name} enregistrés.")
            return True
        else:
            messagebox.showerror("Erreur", "Échec de l'enregistrement.")
            return False
        
    def create_interTopMatch(self, match_Index):
        match = Match(num=match_index, player1=player, player2=None)

    def save_tableaux(self):
        try:
            self.tournoi.tableauOk.updateTableauWithHoles()
            debug_print("Step2")
            self.tournoi.tableauKo.updateTableauWithHoles()
            debug_print("Step3")
            self.tournoi.save_tableaux()


            self.results_modified = [False]
            # Ne pas désactiver ici : clear_inputs_and_labels() s'en occupera après un succès global
            return True
        except Exception as e:
            debug_print("Erreur save_tableaux", e)
            messagebox.showerror("Erreur", "Échec de l'enregistrement des tableaux.")
            return False
        
    def save_results(self):
        success_poules = self.save_resultats_poules()
        success_tableaux = self.save_tableaux()

        if success_poules and success_tableaux:
            # Effacer tous les champs des sets et réinitialiser les labels et le bouton
            self.clear_inputs_and_labels()
        elif success_poules and not success_tableaux:
            messagebox.showwarning("Attention", "Résultats de la poule enregistrés mais échec lors de l'enregistrement des tableaux.")
        elif not success_poules and success_tableaux:
            messagebox.showwarning("Attention", "Tableaux enregistrés mais échec lors de l'enregistrement des résultats de la poule.")
        # si les deux ont échoué, les messages d'erreur ont déjà été affichés

    def searchTargetIndex(self, nb_poules, current_poule):
        if (nb_poules % 2 == 0): # Nb poules paire
            if (current_poule%2 == 0): # Poule paire               
                target_index = 2*nb_poules-current_poule + 2
            else:
                target_index = 2*nb_poules-current_poule
        else:
            target_index = 2*nb_poules - current_poule + 1
        return target_index
    
    def searchIndexInTab(self, cle, tableau, player, nb_tops=0):
        debug_print(f"Recherche de l'index pour le joueur {player} dans le tableau {tableau.type} avec clé {cle} et nb_tops {nb_tops}")
        tableau.set_match_pos_with_idxPlayer(cle, player)
    
    def update_tableau(self, final_ranking, poule_obj):      

        current_poule = int(self.selected_poule.get().split(" ")[1].strip())

        type_poule = self.poule_type.get()
        
        #debug_print(f"avant update: {self.tableauOk}")
        debug_print(f"Type de poule: {type_poule}, Poule numéro: {current_poule}")

        if (type_poule == "Top"):
            if (self.tournoi.nb_tops == 2):
                debug_print("current_poule", current_poule)
                self.tournoi.tableauInterTops.update_tableau_for_2top(current_poule, final_ranking)
            elif (self.tournoi.nb_tops == 1):
                self.tournoi.tableauOk.update_tableau_for_1top(final_ranking)
        else:
            for idx, player in enumerate(final_ranking):
                if (idx == 0):
                    self.searchIndexInTab(current_poule, self.tournoi.tableauOk, player, self.tournoi.nb_tops)
                elif (idx == 1):
                    target_index = self.searchTargetIndex(self.tournoi.nb_poules, current_poule)
                    self.searchIndexInTab(target_index, self.tournoi.tableauOk, player, self.tournoi.nb_tops) 
                elif (idx == 2):
                    self.searchIndexInTab(current_poule, self.tournoi.tableauKo, player)
                elif (idx == 3):
                    debug_print("player", player)
                    target_index = self.searchTargetIndex(self.tournoi.nb_poules, current_poule)
                    debug_print("target_", target_index)
                    self.searchIndexInTab(target_index, self.tournoi.tableauKo, player)
    
    def all_results_entered(self):
        """Retourne True si chaque match a un vainqueur (label de victoire présent et pas 'Pas de vainqueur')."""
        if not self.result_entries:
            return False
        for entries, p1, p2, victory_label in self.result_entries:
            text = victory_label.cget("text")
            if not text:
                return False
            if text.strip() == "Pas de vainqueur":
                return False
        return True

    def calculate_ranking(self):
        selected_poule_name = self.selected_poule.get()
        selected_poule_name = self.selected_poule.get()
        poule_obj = self.tournoi.poules.get_poule_for_name(selected_poule_name)
        players = calculate_ranking(poule_obj)
        
        # N'affiche le classement et n'active le bouton que si tous les résultats sont saisis
        if self.all_results_entered():
            for idx, player in enumerate(players):
                if idx < len(self.ranking_labels):
                    self.ranking_labels[idx].config(text=f"{player.nom} {player.prenom} ({player.club})")
            poule_obj.classement = players
            
            self.update_tableau(players, poule_obj)
            
            if players:
                self.save_button.configure(state="normal")
            else:
                self.save_button.configure(state="disabled")
        else:
            # Effacer l'affichage du classement tant que les résultats ne sont pas complets
            for label in self.ranking_labels:
                label.config(text=" ")
            poule_obj.classement = []
            self.save_button.configure(state="disabled")
    
    def load_results(self):
        poule = self.selected_poule.get()
        
        poule_name = self.selected_poule.get().strip()
        debug_print("POULE", poule_name)
        
        poule_obj = self.tournoi.getPoule(poule_name)
        
        if poule_obj != None:
            matches = poule_obj.matches

            if matches == []:
                messagebox.showerror("Erreur", f"Aucun résultat trouvé pour la poule {poule} dans le fichier.")
                return
        classement = poule_obj.classement
        
        # Mise à jour des résultats dans l'interface
        # self.result_entries contient les références aux widgets (Entry, Labels)
        for i, (match_obj, entry_row) in enumerate(zip(matches, self.result_entries)):
            # Désassemblage du tuple entry_row (défini lors de la création de l'interface)
            # Structure type: (list_of_entries, label_p1, label_p2, label_victory)
            entries, lbl_p1, lbl_p2, lbl_victory = entry_row

            # 1. Remplissage des scores (Sets)
            # match_obj.sets est une liste de chaînes ["11", "8", ...]
            for j, set_val in enumerate(match_obj.sets):
                if j < len(entries):
                    entries[j].delete(0, tk.END)
                    entries[j].insert(0, str(set_val))

            # 2. Mise à jour du label de victoire
            # On vérifie si un vainqueur est défini (objet Player)
            if match_obj.winner:
                nom_vainqueur = f"{match_obj.winner.nom} {match_obj.winner.prenom} {match_obj.winner.club}".strip()
                lbl_victory.config(text=nom_vainqueur, foreground="green")
            else:
                lbl_victory.config(text="Pas de vainqueur", foreground="black")

        # 3. Mise à jour du classement dans l'interface
        debug_print(f"classement loaded: {classement}")
        if classement:
            for idx, player in enumerate(classement):
                if idx < len(self.ranking_labels):
                    # Si player est un objet Player, on formate le texte
                    if idx ==0:
                        txt = f"1er {player.nom} {player.prenom} {player.club} "
                    else:
                        txt = f"{idx+1}eme {player.nom} {player.prenom} {player.club} "

                    self.ranking_labels[idx].config(text=txt)

        # Après avoir chargé, recalculer le classement (active le bouton si tout est complet)
        self.calculate_ranking()
        
        self.results_modified = [False]
        debug_print("Résultats et classement chargés avec succès.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        debug_print("Usage : python saisie-resultats-poules-V2.7.py <categorie> <tour>")
        sys.exit(1)

    category_arg = sys.argv[1]
    round_arg = sys.argv[2]
    
    root = tk.Tk()
    app = ResultEntryApp(root, category_arg, round_arg)
    root.mainloop()