import tkinter as tk
from tkinter import ttk, messagebox
import math
import sys
from modules.utils import *
import os
import pandas as pd
import PIL
from modules.SaisieMatch import validate_input_set,handle_mode_change,update_set_visibility
from modules.models import *
from modules.debug import debug_print
from modules.Tableau import Tableau
from modules.Tournoi import Tournoi
import modules.printing_utils as printing_utils
from modules import points_utils

class TournamentBracket:
    def __init__(self, root, category, round_number):

        self.root = root
        self.fichier_Tableau = ""
        self.results_modified = [False]
        self.previous_mode = "2 sets"
        self.ok_window_open = False  # État pour la fenêtre "Tournoi OK"
        self.ko_window_open = False  # État pour la fenêtre "Tournoi KO"
        self.intertops_window = None  # Référence à la fenêtre "InterTops"
        self.intertops_window_open = False  # État pour "InterTops"
        
        self.joueur1_selected = ""
        self.joueur2_selected = ""
        self.indexMatch = -1
        self.levelMatch = -1
        self.matchOk = False
      
        self.root.title(f"Tournoi {category} Tour {round_number}")
        
        # Conteneur pour les boutons
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(fill="both", expand=True, padx=30, pady=10)

        # Bouton pour "Charger le Tournoi OK"
        self.load_button_ok = ttk.Button(frame_buttons, text="Charger le Tournoi OK", command=lambda: self.load_tournament("Tournoi OK"))
        self.load_button_ok.pack(fill="x", pady=5)

        # Bouton pour "Charger le Tournoi KO"
        self.load_button_ko = ttk.Button(frame_buttons, text="Charger le Tournoi KO", command=lambda: self.load_tournament("Tournoi KO"))
        self.load_button_ko.pack(fill="x", pady=5)

        # Bouton pour "InterTops"
        self.inter_tops_button = ttk.Button(frame_buttons, text="InterTops", command=lambda: self.load_tournament("InterTops"))
        self.inter_tops_button.pack(fill="x", pady=5)
        
        self.fichier_Poules, self.fichier_Tableau = read_config_files(category, round_number)
        tourInitial,nb_tops,nb_poules = get_info_tableau(self.fichier_Tableau)        
        
        self.tournoi = Tournoi(category=category,tour=round_number,nb_tops=nb_tops,nb_poules=nb_poules,nb_joueurs=0,tourInitial=Level(tourInitial))
        self.tournoi.tableauOk.load_from_file()
        self.tournoi.tableauKo.load_from_file()
        self.tournoi.tableauInterTops.load_from_file(nb_tops)


        # Désactiver le bouton InterTops si nb_tops < 2
        if nb_tops < 2:
            self.inter_tops_button.config(state="disabled")
        
        # Bouton pour "Calcul de points"
        self.calcul_points_button = ttk.Button(frame_buttons, text="Calcul de points", command=self.show_points_window)
        self.calcul_points_button.pack(fill="x", pady=5)
        
        #  bouton pour Gestion des règles de points
        self.config_points_button = ttk.Button(frame_buttons, text="Gestion des points", command=self.show_config_points_window)
        self.config_points_button.pack(fill="x", pady=5)
        
        # bouton pour tableaux croisées
        self.gen_tableaux_croises_button = ttk.Button(frame_buttons, text="Génération Tableaux croisés", command=self.gen_tableaux_croises)
        self.gen_tableaux_croises_button.pack(fill="x", pady=5)

        # Ajuster la taille minimale de la fenêtre principale
        self.root.geometry("300x250")  # Largeur x Hauteur

        self.sets_mode_global = tk.StringVar(value="2 sets")
        self.nbPlayersToPrint = 0
        self.debugStatus = lire_status_debug("config.ini")

    def show_points_window(self):
        return points_utils.show_points_window(self)

    def quit_match(self, window):
        if (self.results_modified[0]):
            response = messagebox.askyesno(
                    "Info",
                    f"Ders données n'ont pas été sauvées, continuez-vous ?")
            if response:
                self.results_modified = [False]
                window.destroy()
            else:
                window.focus_set()
        else:
            window.destroy()
        
    def save_points_in_excel(self, new_points):
        return points_utils.save_points_in_excel(self, new_points)

    def load_tournament(self, Tableau):
        # Vérifier si la fenêtre correspondante est déjà ouverte
        self.currentTableau = []
        if Tableau == "Tournoi OK" and self.ok_window_open:
            self.ok_window.focus_set()  # Donner le focus à la fenêtre "Tournoi OK"
            self.current_table = "Tournoi OK"
            self.currentTableau = self.tournoi.tableauOk
            return
        elif Tableau == "Tournoi KO" and self.ko_window_open:
            self.ko_window.focus_set()  # Donner le focus à la fenêtre "Tournoi KO"
            self.current_table = "Tournoi KO"
            self.currentTableau = self.tournoi.tableauKo
            return
        elif Tableau == "InterTops" and hasattr(self, "intertops_window_open") and self.intertops_window_open:
            self.intertops_window.focus_set()  # Donner le focus à la fenêtre "InterTops"
            self.current_table = "InterTops"
            return
        
        if self.tournoi.nb_tops < 2:
            self.inter_tops_button.config(state="disabled")   
        
        self.current_table = Tableau
        
        # Créer une nouvelle fenêtre Toplevel
        new_window = tk.Toplevel(self.root)
        new_window.title(f"{Tableau} - {self.tournoi.category} Tour {self.tournoi.tour}")
        new_window.geometry("1200x800")  # Taille de la fenêtre
        
        # Ajouter un gestionnaire d'événements pour mettre à jour self.current_table
        new_window.bind("<FocusIn>", lambda e: self.update_current_table(Tableau))

        # Ajouter un label pour indiquer le type de tableau
        label = ttk.Label(new_window, text=f"{self.tournoi.category} - {Tableau}", font=("Arial", 16, "bold"))
        label.pack(pady=10)

        # Conteneur pour le canevas
        canvas_frame = tk.Frame(new_window)
        canvas_frame.pack(fill="both", expand=True)

        # Canvas pour dessiner le tableau avec défilement
        canvas = tk.Canvas(canvas_frame, width=1000, height=600, bg="white")
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
  
      # Conteneur pour les boutons "Refresh" et "Exporter en PDF"
        button_frame = ttk.Frame(new_window)
        button_frame.pack(pady=10)

        # Bouton "Refresh"
        refresh_button = ttk.Button(button_frame, text="Refresh", command=lambda: self.refresh_tableau(Tableau, canvas))
        refresh_button.pack(side="left", padx=5)
        
        # Bouton "Exporter en PDF"
        if Tableau in ["Tournoi OK", "Tournoi KO"]:
            pdf_button = ttk.Button(button_frame, text="Exporter en PDF", command=lambda: self.print_bracket_to_pdf(canvas))
            pdf_button.pack(side="left", padx=5)
            
        if Tableau == LABEL_TOURNOI_OK:
            self.tournoi.tableauOk.load_from_file()
            self.draw_bracket(self.tournoi.tableauOk, LABEL_TOURNOI_OK, canvas, self.tournoi.nb_tops)
            self.ok_window_open = True  # Marquer la fenêtre comme ouverte
            self.ok_window = new_window  # Stocker la référence à la fenêtre
            self.ok_canvas = canvas  # Stocker le canevas pour le PDF

        elif Tableau == LABEL_TOURNOI_KO:
            self.tournoi.tableauKo.load_from_file()
            self.draw_bracket(self.tournoi.tableauKo, LABEL_TOURNOI_KO, canvas, 0)
            self.ko_window_open = True  # Marquer la fenêtre comme ouverte
            self.ko_window = new_window  # Stocker la référence à la fenêtre
            self.ko_canvas = canvas  # Stocker le canevas pour le PDF

        elif Tableau == LABEL_TABLEAU_INTERTOPS:
            self.tournoi.tableauInterTops.load_from_file()
            self.draw_intertops(canvas=canvas)
            self.intertops_window_open = True  # Marquer la fenêtre comme ouverte
            self.intertops_window = new_window  # Stocker la référence à la fenêtre
            self.intertops_canvas = canvas  # Stocker le canevas pour le PDF
            
        def on_close():
            if Tableau == LABEL_TOURNOI_OK:
                self.ok_window_open = False
                self.ok_window = None  # Réinitialiser la référence
                self.ok_canvas = None  # Réinitialiser le canevas
            elif Tableau == LABEL_TOURNOI_KO:
                self.ko_window_open = False
                self.ko_window = None  # Réinitialiser la référence
                self.ko_canvas = None  # Réinitialiser le canevas
            elif Tableau == LABEL_TABLEAU_INTERTOPS:
                self.intertops_window_open = False
                self.intertops_window = None  # Réinitialiser la référence
                self.intertops_canvas = None  # Réinitialiser le canevas
            new_window.destroy()

        new_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def update_current_table(self, Tableau):
        """Met à jour self.current_table en fonction de la fenêtre active."""
        self.current_table = Tableau
        
    def refresh_tableau(self, Tableau, canvas):
        """Rafraîchit les données et redessine le tableau."""
        if Tableau == "Tournoi OK":
            self.tournoi.tableauOk.load_from_file()
            self.draw_bracket(self.tournoi.tableauOk, LABEL_TOURNOI_OK, canvas, self.tournoi.nb_tops)
        elif Tableau == "Tournoi KO":
            self.tournoi.tableauKo.load_from_file()
            self.draw_bracket(self.tournoi.tableauKo, LABEL_TOURNOI_KO, canvas, 0)
        elif Tableau == "InterTops":
            self.tournoi.tableauInterTops.load_from_file()#
            self.draw_intertops(canvas=canvas)
    
    def set_new_player(self, level, idx, player, nb_tops, tableau, intertop=False):
            new_level = ""
            
            try:
                if (not intertop):
                    current_level = int(level.split("/")[1])  # Extrait la partie numérique
                    next_level = current_level // 2
                    new_level = f"1/{next_level}"
                else:
                    new_level = "1/8"
                #debug_print("current_level", current_level, " new_level", new_level)
            except (ValueError, IndexError):
                print(f"Erreur : Niveau '{level}' est invalide.")
            # Initialiser le niveau dans tableauOK s'il n'existe pas
            level_pos=tableau.get_level_pos(new_level)
            
            if (level_pos == None):
                tableau.tableauLevels.append(TableauLevels(level=new_level, matches=[]))
                level_pos=tableau.get_level_pos(new_level)
                
            if (not intertop):
                if (int(current_level) == 2*nb_tops):
                    index_table = idx
                else:
                    index_table = int(1 + ((idx - 1) // 2))
                # Initialiser l'entrée pour ce match si elle n'existe pas
                
                #print("level_pos: ", level_pos, ", index_table:", index_table)
                
                match_pos = level_pos.get_match_pos(index_table)
                if match_pos == None:
                    level_pos.matches.append(Match(num=index_table, player1=None, player2=None, sets=[], idxPlayer1=0, idxPlayer2=0))
                    match_pos = level_pos.get_match_pos(index_table)
                    
                # Mettre à jour ou ajouter le joueur dans le niveau suivant
                if (int(current_level) == 2*nb_tops):
                    match_pos.player2 = player
                    
                else:
                    if (idx %2 == 1):
                        match_pos.player1 = player
                    else:
                        match_pos.player2 = player

                return match_pos
            else:
                #print("*** level_pos: ", level_pos)
                
                match_pos = level_pos.get_match_pos(idx)

                if (match_pos == None):
                    level_pos.matches.append(Match(num=idx, player1=None, player2=None, sets=[], idxPlayer1=0, idxPlayer2=0))
                    match_pos = level_pos.get_match_pos(idx)
                match_pos.player1 = player

                print(f"{player} placé en position {idx}")
                return match_pos

    def gestion_vainqueur(self, player1, player2, level, index_match, tableau, nb_tops, intertop, scores_sets, match_window):
        if (intertop):
            table_intertops = [(2, 7), (6, 3), (4, 5), (8, 1)]
            #Le 1er du top va en position 2
            #Le 2e du top va en position 7
            #Le 3e du top va en position 6
            #etc ...
            
            # Déterminer les classements en fonction du résultat
            
            #match_pos = get_match_pos(self)

            position1 = index_match*2 - 1
            position2 = position1 + 1

            classement2 = f"{position2}ème"
            if position1 == 1:
                classement1 = f"{position1}er"
            else:
                classement1 = f"{position1}ème"
                
            msg_clst = f"{classement1} Intertop: {player1.key}\n{classement2} Intertop: {player2.key}"
            
            level_pos = self.tournoi.tableauInterTops.get_level_pos()
            current_match_pos = level_pos.get_match_pos(index_match)
            current_match_pos.sets = scores_sets
            current_match_pos.winner = player1
            
            self.set_new_player(level, table_intertops[index_match-1][0], player1, nb_tops, tableau, intertop)
            self.set_new_player(level, table_intertops[index_match-1][1], player2, nb_tops, tableau, intertop)

            # Afficher un message avec les classements
            self.root.withdraw()  # Masquer la fenêtre principale
            
            messagebox.showinfo(title="Info", message=msg_clst)
            self.root.deiconify()  # Réafficher la fenêtre principale
            self.matchOk = True
        else:
            level_pos = tableau.get_level_pos(level)
            print("level:", level, "level_pos:", level_pos)
            current_match_pos = level_pos.get_match_pos(index_match)
            current_match_pos.sets = scores_sets
            current_match_pos.winner = player1
            
            match = self.set_new_player(level, index_match, player1, nb_tops, tableau, intertop)
            self.root.withdraw()  # Masquer la fenêtre principale
            messagebox.showinfo(title="Info", message=f"{player1.nom} {player1.prenom} {player1.club} vainqueur")
            self.matchOk = True
            self.root.deiconify()  # Réafficher la fenêtre principale
        
        # Remettre le focus sur la fenêtre "Détails du Match"
        match_window.focus_set()        
        
    def handle_enter(self, event, entries, player1, player2, level, index_match, tableau, nb_tops, intertop):
        """Gère la validation des scores et détermine le vainqueur."""
        sets_player1 = 0
        sets_player2 = 0
        self.results_modified = [True]
        mode = self.sets_mode_global.get()
        

        # Navigation entre champs
        current_widget = event.widget
        current_index = entries.index(current_widget)

        # Vérifier que la case précédente est remplie, sauf pour la première case
        if current_widget.get() == "":
            current_widget.insert(0, "0")  # Considérer vide comme 0
        elif current_widget.get() == "-":
            current_widget.insert(0, "-0")  # Considérer "-" comme "-0"
            
        if current_index < len(entries):
            # Validation et calcul des scores
            scores_sets =  []
            for entry in entries:
                value = entry.get()
                if value.startswith("-"):
                    sets_player2 += 1
                elif value.isdigit():
                    sets_player1 += 1
                scores_sets.append(value)
                 
            match_window = event.widget.master  # Référence à la fenêtre "Détails du Match"
            
            if ( (sets_player1 == 2 and mode == "2 sets") or
                (sets_player1 == 3 and mode == "3 sets") ):  
                self.gestion_vainqueur(player1, player2, level, index_match, tableau, nb_tops, intertop, scores_sets, match_window)   
                
            elif ( (sets_player2 == 2 and mode == "2 sets") or
                (sets_player2 == 3 and mode == "3 sets") ):                        
                self.gestion_vainqueur(player2, player1, level, index_match, tableau, nb_tops, intertop, scores_sets, match_window)
            else:
                next_widget = entries[current_index + 1]  # Passer au champ suivant
                next_widget.focus_set()                    
    
    def update_set_visibility(self, current_mode, set_entries, window=None):
        new_mode = self.sets_mode_global.get()
        confirmation_message = "Les données actuelles n'ont pas été sauvées. Voulez-vous continuer et effacer les données ?"
        success = handle_mode_change(
            current_mode=self.sets_mode_global.get(),
            new_mode=new_mode,
            result_entries=[set_entries],
            results_modified=self.results_modified
        )
        if success:
            self.results_modified = [False]
            self.previous_mode = new_mode
        else:
            self.sets_mode_global.set(self.previous_mode)
        if window != None:
            window.focus_set()
        update_set_visibility(self.previous_mode, set_entries)
           
    def save_results(self, window=None):
        mode = self.sets_mode_global.get()
        #print(f"Mode de sets sélectionné : {mode}")
        if mode in ["2 sets", "3 sets"]:
            if not self.matchOk:
                        messagebox.showerror(
                            "Erreur",
                            f"Le vainqueur n'est pas déterminé pour le match {self.joueur1_selected} vs {self.joueur2_selected}. "
                        )
                        return
        self.tournoi.save_tableaux()
        
        if (window != None):
            window.destroy()
            
            if self.ok_window_open:
                self.refresh_tableau(LABEL_TOURNOI_OK, self.ok_canvas)
            if self.ko_window_open:
                self.refresh_tableau(LABEL_TOURNOI_KO, self.ko_canvas)
            if self.intertops_window_open:
                self.refresh_tableau(LABEL_TABLEAU_INTERTOPS, self.intertops_canvas)
            
            self.results_modified = [False]
            self.load_tournament(self.current_table)
            
        self.matchOk = False
        
    def open_match_window(self, player1, player2, string_level, index_match, tableau, nb_tops, intertop=False):
        # Créer une nouvelle fenêtre
        match_window = tk.Toplevel(self.root)
        match_window.title("Détails du Match")
        
        
        self.joueur1_selected = player1
        self.joueur2_selected = player2
        self.indexMatch = index_match
        self.levelMatch = string_level

        # Déterminer la fenêtre parent
        if self.current_table == "Tournoi OK":
            parent_window = self.ok_window
        elif self.current_table == "Tournoi KO":
            parent_window = self.ko_window
        elif self.current_table == "InterTops":
            parent_window = self.intertops_window

        # Associer la fenêtre "Détails du Match" à la fenêtre parent
        match_window.transient(parent_window)  # Associer à la fenêtre parent
        match_window.grab_set()  # Rendre la fenêtre modale
        
        # Définir self.current_table sur la fenêtre d'origine
        match_window.bind("<FocusIn>", lambda e: self.update_current_table(self.current_table))

        # Ajouter les noms des joueurs
        tk.Label(match_window, text=f"{player1.key} vs {player2.key}", font=("Arial", 14)).pack(pady=10)

        # Radio buttons pour 2 sets ou 3 sets
        
        self.sets_mode_global = tk.StringVar(value=self.previous_mode)
        ttk.Radiobutton(match_window, text="2 sets", variable=self.sets_mode_global, value="2 sets", 
            command=lambda: self.update_set_visibility(self.sets_mode_global.get(), set_entries, match_window)).pack()

        ttk.Radiobutton(match_window, text="3 sets", variable=self.sets_mode_global, value="3 sets", 
            command=lambda: self.update_set_visibility(self.sets_mode_global.get(), set_entries, match_window)).pack()
        
        # Lorsque l'on choisit un forfait, on déclare directement le vainqueur
        def handle_forfait(selected_mode, p1, p2):
            # Mettre à jour la variable de mode
            self.sets_mode_global.set(selected_mode)
            # Déterminer vainqueur / perdant selon le forfait
            if selected_mode == "Forfaitj1":
                winner = p2
                loser = p1
            else:
                winner = p1
                loser = p2

            # Marquer l'état interne
            self.joueur1_selected = p1
            self.joueur2_selected = p2
            self.indexMatch = index_match
            self.levelMatch = string_level
            self.matchOk = True

            # Score unique pour forfait
            scores_sets = ["WO"]

            # Appeler la gestion du vainqueur (affiche aussi le message)
            try:
                self.gestion_vainqueur(winner, loser, string_level, index_match, tableau, nb_tops, intertop, scores_sets, match_window)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de traiter le forfait : {e}")

        ttk.Radiobutton(match_window, text="Forfait Joueur 1", variable=self.sets_mode_global, value="Forfaitj1", 
            command=lambda p1=player1, p2=player2: handle_forfait("Forfaitj1", p1, p2)).pack()
        
        ttk.Radiobutton(match_window, text="Forfait Joueur 2", variable=self.sets_mode_global, value="Forfaitj2", 
            command=lambda p1=player1, p2=player2: handle_forfait("Forfaitj2", p1, p2)).pack()

        def on_focus_in(event, current_index):
            if current_index < len(set_entries) - 1:
                for idx in range(0, current_index):
                    if (set_entries[idx].get() == ""):
                        set_entries[idx].focus_set()
                        break 
   
        # Champs pour les scores des sets
        set_entries = []
        for i in range(5):
            row = tk.Frame(match_window)
            row.pack(pady=5)
            tk.Label(row, text=f"Set {i + 1}:", font=("Arial", 10)).pack(side="left")

            entry = tk.Entry(row, width=5, validate="key",
                                  validatecommand=(self.root.register(lambda action, value: validate_input_set(action, value, self.results_modified)
                            ), '%d', '%P'))
            entry.pack(side="left")
            entry.bind("<Return>", lambda event, e=set_entries, p1=player1, p2=player2, lvl=string_level, idx=index_match, nbt=nb_tops*4: self.handle_enter(event, e, p1, p2, lvl, idx, tableau, nbt, intertop))
            entry.bind("<FocusIn>", lambda e, idx=i: on_focus_in(e, idx))
            set_entries.append(entry)

        button_frame = ttk.Frame(match_window)
        button_frame.pack(fill="x", pady=10)

        # Bouton pour fermer la fenêtre
        quit_button = ttk.Button(button_frame, text="Fermer", command=lambda w=match_window: self.quit_match(w))
        quit_button.pack(side="right", padx=5)

        # Bouton pour valider
        validate_button = ttk.Button(button_frame, text="Valider", command=lambda w=match_window: self.save_results(w))
        validate_button.pack(side="left", padx=5)
        
        # Mettre à jour la visibilité initiale des sets
        self.update_set_visibility("2 sets", set_entries)
        
        # Forcer un redimensionnement
        root.update_idletasks()  # Mettre à jour l'interface
        
        
    def on_enter(self, event, joueur, canvas): 
        if joueur == None:
            return       

        self._tooltip_window = tk.Toplevel(canvas)
        self._tooltip_window.wm_overrideredirect(True)  # supprime la barre d’entête
        self._tooltip_window.geometry(f"+{event.x_root+10}+{event.y_root+10}")
        dossard_text = joueur.dossard
        label = tk.Label(self._tooltip_window, text=dossard_text,
            background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
        
    def on_leave(self, event):
        """Détruit la fenêtre Toplevel quand la souris sort du rectangle."""
        if getattr(self, "_tooltip_window", None) is not None:
            self._tooltip_window.destroy()
            self._tooltip_window = None
     
    def idxIntoClst(self, idx):
        if idx == 1:
            return f"{idx}er"
        else:
            return f"{idx}ème"

    def draw_intertops(self, canvas):
        index_match = 0
        canvas.delete("all")
            
        canvas_height = max(600, 400 + 8 * 70 * 2)
        start_x = 20
        player_spacing = canvas_height // 8 // 4
        gap = 10  # Espace entre les cadres
        longueur_rectangle = 180
        longueur_fleche = 100
        
        for idx in range (1, 5):
            joueur1 = ""
            joueur2 = ""
            y1_top = (idx-1) * 2 * (player_spacing + gap) + 10
            y1_bottom =  y1_top + player_spacing
            mid_y1 = (y1_top + y1_bottom) / 2
            match_nb = str(idx + 1)
            rect_id_1 = canvas.create_rectangle(start_x, y1_top, start_x + longueur_rectangle, y1_bottom, outline="black", width=1)
            
            level_pos = self.tournoi.tableauInterTops.get_level_pos()
            match_pos = level_pos.get_match_pos(idx)
            
            classement1 = ""
            classement2 = ""
            player1 = ""
            player2 = ""
            doss1= ""
            doss2=""
            if (match_pos != None):  
                player1 = match_pos.player1
                player2 = match_pos.player2
         
                if match_pos.winner != None:
                    if match_pos.winner.key == player1.key:
                        classement1 = self.idxIntoClst(idx*2 -1)
                        classement2 = self.idxIntoClst(idx*2)
                    elif match_pos.winner.key == player2.key:
                        classement1 = self.idxIntoClst(idx*2)
                        classement2 = self.idxIntoClst(idx*2 - 1)   
            else:
                player1=None
                player2=None

            if (player1 == None):
                canvas.create_text(start_x + 10, y1_top + 15, text="", anchor="w", font=("Arial", 10))
            else:
                canvas.create_text(start_x + 10, y1_top + 15, text=player1.key, anchor="w", font=("Arial", 10))
                canvas.create_text(start_x + 10, y1_top + 30, text=classement1, anchor="w", font=("Arial", 8, "italic"))    

            y2_top = y1_bottom + 10
            y2_bottom = y2_top + player_spacing
            
            mid_y2 = (y2_top + y2_bottom) // 2
            rect_id_2 = canvas.create_rectangle(start_x, y2_top, start_x + longueur_rectangle, y2_bottom, outline="black", width=1)
            
            if (player2 == None):
                canvas.create_text(start_x + 10, y2_top + 15, text="", anchor="w", font=("Arial", 10))
            else:
                canvas.create_text(start_x + 10, y2_top + 15, text=player2.key, anchor="w", font=("Arial", 10))
                canvas.create_text(start_x + 10, y2_top + 30, text=classement2, anchor="w", font=("Arial", 8, "italic"))

            # Lier les événements <Enter> et <Leave> au rectangle
            if (player1 == None):
                doss1 = ""
            else:
                doss1 = player1.dossard
                
            if (player2 == None):
                doss2 = ""
            else:
                doss2 = player2.dossard
                
            canvas.tag_bind(rect_id_1, "<Enter>", 
                lambda e, jr=player1: self.on_enter(e, jr, canvas))
            canvas.tag_bind(rect_id_1, "<Leave>", self.on_leave)

            canvas.tag_bind(rect_id_2, "<Enter>", 
                lambda e, jr=player2: self.on_enter(e, jr, canvas))
            canvas.tag_bind(rect_id_2, "<Leave>", self.on_leave)
            
            mid_y = (mid_y1 + mid_y2) // 2
            
            button_x = start_x + longueur_rectangle + 20
            button_y = mid_y
            state = "normal" if player1 and player2 else "disabled"
            intertop = True
            btn = tk.Button(canvas, text="Détails", state=state, command=lambda p1=player1, p2=player2, lvl="InterTops", match_index=idx: self.open_match_window(p1, p2, lvl, match_index, self.tournoi.tableauOk, self.tournoi.nb_tops, intertop))
            canvas.create_window(button_x, button_y, window=btn)
            
            checkbox_x = button_x + 50  # Décalage pour la case
            var = tk.BooleanVar()
            
            if (match_pos != None and match_pos.checkbox_state != None):
                var.set(match_pos.checkbox_state)

            def checkbox_change_intertops(var, match_index, tableau):
                """Callback pour mettre à jour le 'checkbox_state' d’un match Intertops."""
                self.results_modified[0] = True
                match_pos.checkbox_state = var.get()
            
            chk = tk.Checkbutton(
                canvas, variable=var,state=state, 
                command=lambda v=var, m=idx: self.on_checkbox_change(v, Level(level=1), m, self.tournoi.tableauInterTops, self.root)
                )
            canvas.create_window(checkbox_x, button_y, window=chk)

            print_button_x = button_x + 100
            print_btn = tk.Button(
                        canvas,
                        text="Print",
                        state=state,
                        command=lambda p1=player1, p2=player2: self.print(self.nbPlayersToPrint, p1, p2, table_name, self.tournoi.category, Level(level=1))
                        )

            canvas.create_window(print_button_x, button_y, window=print_btn)

            checkbox_x = checkbox_x + 80
            var_print = tk.BooleanVar()
            #self.chk_print_vars[(table_name, string_level, idx)] = var_print
            chk_print = tk.Checkbutton(canvas, variable=var_print, command=lambda elt=var_print, match_index=idx: self.on_checkbox_print_change(elt, Level(level=1), match_index, self.tournoi.tableauInterTops))
            chk_print.configure(state=state)
            canvas.create_window(checkbox_x, button_y, window=chk_print)

    def print_bracket_to_pdf(self, canvas):
        """Délègue l'export PDF au module printing_utils."""
        return printing_utils.print_bracket_to_pdf(self, canvas)
    
    def gen_tableaux_croises(self):
        return points_utils.gen_tableaux_croises(self)

    def show_config_points_window(self):
        return points_utils.show_config_points_window(self)

    def calculate_points(self):
        return points_utils.calculate_points(self)

    def save_points_config(self, config):
        return points_utils.save_points_config_for_app(self, config)


    def draw_bracket(self, tableau, table_name, canvas, nb_tops):
        """Point d'entrée principal pour dessiner le tableau de tournoi."""
        canvas.delete("all")
    
        # 1. Calcul des dimensions et configuration initiale
        nb_players = self._get_required_slots()
        canvas_height = max(600, 300 + nb_players * 50 * 2)
        canvas.config(scrollregion=(0, 0, 1200, canvas_height))

        # 2. Dessin de l'en-tête
        self._draw_header(canvas, table_name)
    
        # 3. Initialisation des positions verticales du premier tour
        player_spacing = canvas_height // nb_players // 6
        gap = 5
        current_positions = [
            idx * 2 * (player_spacing + gap) + 60 
            for idx in range(nb_players * 2)
        ]

        # 4. Itération sur les niveaux du tableau
        start_x = 20
        current_tour = tableau.tourInitial
        nb_matches = current_tour.level
        longueur_rect = 130
        longueur_fleche = 50

        while nb_matches >= 0:
            next_positions = []
            string_level = current_tour.string
        
            # Dessiner le libellé de la colonne (ex: Finale, 1/8)
            self._draw_column_label(canvas, start_x, longueur_rect, current_tour)

            level_pos = tableau.get_level_pos(current_tour)
        
            # On traite les positions deux par deux pour former un match
            for i in range(0, len(current_positions), 2):
                match_idx = (i // 2) + 1
                current_match = level_pos.get_match_pos(match_idx) if level_pos else None
                #debug_print(f"Processing match index {match_idx} at level {current_tour.string}: current_match={current_match}")

            
                # Dessin des deux joueurs du match
                y1 = current_positions[i]

                if len(current_positions) > 1:
                    y2 = current_positions[i+1]
            
                    mid_y1 = self._draw_player_slot(canvas, start_x, y1, player_spacing, current_match, 1)
                    mid_y2 = self._draw_player_slot(canvas, start_x, y2, player_spacing, current_match, 2)
            
                    # Calcul du point central pour le tour suivant
                    match_mid_y = (mid_y1 + mid_y2) // 2
                    next_positions.append(match_mid_y)
                else:
                    match_mid_y = mid_y1
                    self._draw_player_slot(canvas, start_x, y1, player_spacing, current_match, 1)

                # Dessin des connecteurs et des contrôles (boutons/checkbox)
                if nb_matches > 0:
                    self._draw_match_controls(canvas, start_x, longueur_rect, match_mid_y, 
                                        current_match, match_idx, string_level, tableau, nb_tops, table_name)
                    self._draw_connectors(canvas, start_x, longueur_rect, longueur_fleche, mid_y1, mid_y2, match_mid_y)
                    

            # Mise à jour pour la colonne suivante
            start_x += (longueur_rect + longueur_fleche)
            
            if current_tour.level != nb_tops*8:
                current_positions = next_positions
            current_tour = current_tour.levelDown()

            nb_matches = -1 if nb_matches == 0 else nb_matches // 2

    # --- Méthodes privées de support ---

    def _get_required_slots(self):
        """Calcule le nombre de slots nécessaires basé sur les poules."""
        if self.tournoi.nb_poules <= 0: return 2
        return max(2, 2 ** math.ceil(math.log2(self.tournoi.nb_poules)))

    def _draw_header(self, canvas, table_name):
        header_text = f"{table_name} {self.tournoi.category} - Tour {self.tournoi.tour}"
        canvas.create_text(500, 50, text=header_text, font=("Arial", 16, "bold"))

    def _draw_column_label(self, canvas, x, width, tour):
        label = "Vainqueur" if tour.level == 0 else ("Finale" if tour.level == 1 else tour.string)
        canvas.create_text(x + (width / 2), 20, text=label, anchor="center", font=("Arial", 10, "bold"))

    def _draw_player_slot(self, canvas, x, y_mid, spacing, match, player_num):
        """Dessine un rectangle de joueur et retourne le point Y central."""
        y_top = y_mid - (spacing // 2)
        y_bottom = y_top + spacing
    
        player = None
        if match:
            player = match.player1 if player_num == 1 else match.player2
    
        name = player.key if player and player.nom != EMPTY_NAME else ""
        fill_color = "grey" if player and player.nom == EMPTY_NAME else "white"
    
        rect_id = canvas.create_rectangle(x, y_top, x + 130, y_bottom, outline="black", fill=fill_color)
        canvas.create_text(x + 3, y_top + 8, text=name, anchor="w", font=("Arial", 9))
    
        # Tooltip binding
        canvas.tag_bind(rect_id, "<Enter>", lambda e: self.on_enter(e, player, canvas))
        canvas.tag_bind(rect_id, "<Leave>", self.on_leave)
    
        return (y_top + y_bottom) // 2

    def _draw_match_controls(self, canvas, x, rect_w, mid_y, match, idx, lvl_str, tableau, nb_tops, table_name):
         """Gère l'affichage des boutons Détails, Print et Checkboxes."""
         # Logique d'activation
         p1, p2 = (match.player1, match.player2) if match else (None, None)
         is_ready = p1 and p2 and p1.nom != EMPTY_NAME and p2.nom != EMPTY_NAME
         state = "normal" if (is_ready or self.debugStatus == "True") else "disabled"

         # Bouton Détails
         btn_det = tk.Button(canvas, text="Détails", state=state, 
                        command=lambda: self.open_match_window(p1, p2, lvl_str, idx, tableau, nb_tops))
         canvas.create_window(x + 10, mid_y, window=btn_det)

         # Bouton Print
         btn_prt = tk.Button(canvas, text="Print", state=state,
                        command=lambda: self.print(self.nbPlayersToPrint, p1, p2, table_name, self.tournoi.category, Level(lvl_str)))
         canvas.create_window(x + 110, mid_y, window=btn_prt)

         # Checkbox de validation
         var_val = tk.BooleanVar(value=match.checkbox_state if match else False)
         chk_val = tk.Checkbutton(canvas, variable=var_val, state=state,
                             command=lambda: self.on_checkbox_change(var_val, lvl_str, idx, tableau, self.root))
         canvas.create_window(x + 60, mid_y, window=chk_val)
        
         # Checkbox d'impression (visible près du bouton Print)
         try:
            var_print = tk.BooleanVar(value=getattr(match, 'print_state', False))
         except Exception:
             var_print = tk.BooleanVar(value=False)

         chk_print = tk.Checkbutton(canvas, variable=var_print, state=state,
                                   command=lambda: self.on_checkbox_print_change(var_print, lvl_str, idx, tableau))
         canvas.create_window(x + 160, mid_y, window=chk_print)

    def _draw_connectors(self, canvas, x, rect_w, arrow_w, y1, y2, mid_y):
        """Dessine les lignes reliant les matches."""
        canvas.create_line(x + rect_w, y1, x + rect_w + arrow_w, mid_y, fill="black")
        canvas.create_line(x + rect_w, y2, x + rect_w + arrow_w, mid_y, fill="black")

    def print(self, nbPlayersToPrint, player1, player2, table_name, category, level):
        """Délègue l'impression au module printing_utils."""
        printing_utils.on_print_and_uncheck(self, nbPlayersToPrint, player1, player2, table_name, category, level)
        if self.ok_window_open:
            self.refresh_tableau(LABEL_TOURNOI_OK, self.ok_canvas)
        if self.ko_window_open:
            self.refresh_tableau(LABEL_TOURNOI_KO, self.ko_canvas)
        if self.intertops_window_open:
            self.refresh_tableau(LABEL_TABLEAU_INTERTOPS, self.intertops_canvas)
        
    def print_match_details_direct(self, line, dc, player1, player2, table_name, category, level):
        """Délègue au module printing_utils."""
        return printing_utils.print_match_details_direct(self, line, dc, player1, player2, table_name, category, level)
    
    def print_pdf(self, pdf_filename):
        """Délègue l'envoi au système au module printing_utils."""
        return printing_utils.print_pdf(pdf_filename)
    
    def restore_focus_to_main_window(self):
        """Remet le focus sur la fenêtre principale (Tableau OK ou Tableau KO)."""
        if self.current_table == "Tournoi OK" and self.ok_window:
            self.ok_window.focus_set()
        elif self.current_table == "Tournoi KO" and self.ko_window:
            self.ko_window.focus_set()
            
    def on_checkbox_change(self, var, level, match_index, tableau, root_window=None):
        """Gestionnaire pour la checkbox de validation d'un match.
        Met à jour l'état dans le modèle (checkbox_state), marque les données comme modifiées
        et conserve la variable Tkinter pour un usage ultérieur.
        """
        try:
            status = var.get() if hasattr(var, "get") else bool(var)
        except Exception:
            status = bool(var)

        # Marquer comme modifié
        try:
            self.results_modified[0] = True
        except Exception:
            self.results_modified = [True]

        # Mettre explicitement à jour checkbox_state sur l'objet match
        try:
            level_pos = tableau.get_level_pos(level)
            if level_pos:
                match_obj = level_pos.get_match_pos(match_index)
                if match_obj is not None:
                    match_obj.checkbox_state = True if status else False
                else:
                    debug_print(f"on_checkbox_change: match introuvable level={level} idx={match_index}")
            else:
                debug_print(f"on_checkbox_change: niveau introuvable: {level}")
        except Exception as e:
            debug_print("Erreur on_checkbox_change update model:", e)

        # Mémoriser la variable pour pouvoir la relire/sauver
        try:
            tname = getattr(tableau, 'type', None) or 'tableau'
            level_key = level if isinstance(level, str) else (getattr(level, 'string', str(level)))
            key = (tname, level_key, int(match_index))
        except Exception:
            key = (getattr(tableau, 'type', 'tableau'), str(level), match_index)

    def on_checkbox_print_change(self, var, level, match_index, tableau):
        """Gestionnaire pour la checkbox d'impression d'un match.
        Met à jour la sélection d'impression dans le modèle et marque les données comme modifiées.
        """
        try:
            status = var.get() if hasattr(var, 'get') else bool(var)
        except Exception:
            status = bool(var)

        if status == True:
            self.nbPlayersToPrint += 1
        else:
            self.nbPlayersToPrint -= 1

        try:
            self.results_modified[0] = True
        except Exception:
            self.results_modified = [True]

        # Mettre explicitement à jour print_state sur l'objet match
        try:
            level_pos = tableau.get_level_pos(level)
            if level_pos:
                match_obj = level_pos.get_match_pos(match_index)
                if match_obj is not None:
                    match_obj.print_state = True if status else False
                else:
                    debug_print(f"on_checkbox_print_change: match introuvable level={level} idx={match_index}")
            else:
                debug_print(f"on_checkbox_print_change: niveau introuvable: {level}")
        except Exception as e:
            debug_print("Erreur on_checkbox_print_change:", e)
     
     # --- CONFIGURATION DES POINTS ---
    def load_points_config(self):
         return points_utils.load_points_config(self)

    def save_points_config(self, config):
        return points_utils.save_points_config_for_app(self, config)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python Saisie-Tournoi-V1.7.py <categorie> <tour>")
        sys.exit(1)

    category_arg = sys.argv[1]
    round_arg = sys.argv[2]    
        
    root = tk.Tk()
    app = TournamentBracket(root, category_arg, round_arg)
    root.mainloop()