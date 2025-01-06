import tkinter as tk
from tkinter import ttk
import json
import math
import sys

class TournamentBracket:
    def __init__(self, root, category, round_number):
        '''self.root = root
        self.category = category
        self.round_number = round_number
        self.root.title("Tournoi à Élimination Directe")


        # Canvas pour dessiner le tableau
        self.canvas = tk.Canvas(root, width=1000, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Bouton pour charger le tournoi
        self.load_button = ttk.Button(root, text="Charger le Tournoi", command=self.load_tournament)
        self.load_button.pack(pady=10)
        '''#self.load_tournament()
        self.root = root
        self.category = category
        self.round_number = round_number
        self.root.title("Tournoi à Élimination Directe")

        # Conteneur pour le canevas
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill="both", expand=True)

        # Canvas pour dessiner le tableau avec défilement
        '''self.canvas = tk.Canvas(self.canvas_frame, width=1500, height=1000, bg="white")
        self.scrollbar_y = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        '''
        self.canvas = tk.Canvas(self.canvas_frame, width=1000, height=600, bg="white")
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bouton pour charger le tournoi
        self.load_button = ttk.Button(root, text="Charger le Tournoi", command=self.load_tournament)
        self.load_button.pack(pady=10)

    def load_tournament(self):
        self.root = root
        file_name = f"Tableau_{self.category}_tour{self.round_number}.json"
        print("filename:", file_name)

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Fichier non trouvé : {file_name}")
            return
        tourInitial = int(data.get("tourInitial"))
        nbTops = int(data.get("nbTops"))
        nbPoules = int(data.get("nbPoules"))
        print("tourInitial: ", tourInitial)
        #tableau = data.get("Tableau OK", {}).get("1/16", [])  # Charger les matchs de "1/16"
        tableau = data.get("Tableau OK")
        self.draw_bracket(tableau, tourInitial, nbPoules, nbTops)
        
        
    def handle_enter(self, event, entries, player1, player2, set_choice):
        """Gère la validation des scores et détermine le vainqueur."""
        print("in handle-enter")
        sets_player1 = 0
        sets_player2 = 0
        #mode = self.sets_mode_global.get()
        self.results_modified = True

        # Navigation entre champs
        current_widget = event.widget
        current_index = entries.index(current_widget)

        # Vérifier que la case précédente est remplie, sauf pour la première case
        if current_widget.get() == "":
            current_widget.insert(0, "0")  # Considérer vide comme 0
        elif current_widget.get() == "-":
            current_widget.insert(0, "-0")  # Considérer "-" comme "-0"
                
        mode = set_choice.get()

        if current_index < len(entries) - 1:
            # Validation et calcul des scores
            print("Validating scores...")
            for entry in entries:
                value = entry.get()
                print("value:", value)
                if value.startswith("-"):
                    sets_player2 += 1
                elif value.isdigit():
                    print("digit")
                    sets_player1 += 1
                if (int(mode) == 2 and (sets_player1 >= 2 or sets_player2 >= 2)) or \
                   (int(mode) == 3 and (sets_player1 >= 3 or sets_player2 >= 3)):
                    print("winner found")
                    current_widget.focus_set()
                else:
                    print("No winner yet")
                    next_widget = entries[current_index + 1]  # Passer au champ suivant
                    next_widget.focus_set()
                
    #def validate_set_input(self, action, value_if_allowed):
    def validate_set_input(self, action, value_if_allowed):
        
        """Valide les entrées des sets (valeurs entre -30 et 30, avec possibilité de -)."""
        print(f"Validating input: action={action}, value={value_if_allowed}")
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
        
        '''
        try:
            val = int(value)
            if (val <= 30 and val >= -30):
                self.results_modified = True
            return True
        except ValueError:
            return False
        return False
        '''
           
    def update_set_visibility(self, set_choice, set_entries):

        for i, entry in enumerate(set_entries):
            if set_choice.get() == 2 and i > 2:
                entry.pack_forget()  # Masque les champs des sets 3 à 5
            else:
                entry.pack(side="left")  # Affiche les champs des sets
        
        # Afficher les champs des sets en fonction de 2 ou 3 sets sélectionnés, sans les masquer
        '''max_sets = 2 if set_choice.get() == 2 else 5

        for i, entry in enumerate(set_entries):
            entry.config(state="normal" if i == 0 else "disabled")  # Réinitialise l'état des champs
            entry.delete(0, tk.END)

            # Réinitialiser les champs visibles au bon état
            if i < max_sets:
                entry.config(state="normal" if i == 0 else "disabled")
            else:
                entry.delete(0, tk.END)
                entry.config(state="disabled")        
        '''        
    def open_match_window(self, player1, player2):
        # Créer une nouvelle fenêtre
        match_window = tk.Toplevel(self.root)
        match_window.title("Détails du Match")

        # Ajouter les noms des joueurs
        tk.Label(match_window, text=f"{player1} vs {player2}", font=("Arial", 14)).pack(pady=10)

        # Radio buttons pour 2 sets ou 3 sets
        set_choice = tk.IntVar(value=2)  # Initialise à 2 sets par défaut
        tk.Radiobutton(match_window, text="2 sets", variable=set_choice, value=2, command=lambda: self.update_set_visibility(set_choice, set_entries)).pack()
        tk.Radiobutton(match_window, text="3 sets", variable=set_choice, value=3, command=lambda: self.update_set_visibility(set_choice, set_entries)).pack()

        '''def validate_next_set(current_index):
            # Activer le champ suivant uniquement si le champ actuel est rempli
            if current_index < len(set_entries) - 1:
                next_entry = set_entries[current_index + 1]
                if set_entries[current_index].get().strip():
                    next_entry.config(state="normal")
                else:
                    next_entry.delete(0, tk.END)
                    next_entry.config(state="disabled")
        set_entries = []
        '''
        '''for i in range(5):
            row = tk.Frame(match_window)
            row.pack(pady=5)
            tk.Label(row, text=f"Set {i + 1}:", font=("Arial", 10)).pack(side="left")
            entry = tk.Entry(row, width=5, validate="key", validatecommand=(self.root.register(self.validate_set_input), '%P'))
            entry.pack(side="left")
            entry.bind("<KeyRelease>", lambda e, idx=i: validate_next_set(idx))
            entry.bind("<Return>", lambda event, e=set_entries, p1=player1, p2=player2: self.handle_enter(event, e, p1, p2, set_choice))
            set_entries.append(entry)

            # Désactiver tous les champs sauf le premier au départ
            if i > 0:
                entry.config(state="disabled")
         
        '''
        def on_focus_in(event, current_index):
            print("current_index:", current_index, ",len:", len(set_entries))
            if current_index < len(set_entries) - 1:
                for idx in range(0, current_index):
                    print ("IDX: ", idx)
                    if (set_entries[idx].get() == ""):
                        print("Empty set idx:", idx)
                        set_entries[idx].focus_set()
                        break 
                    else:
                        print("idx: ", idx, ",val:", set_entries[idx].get())
          
        '''
        def validate_next_set(current_index):
            # Activer le champ suivant uniquement si le champ actuel est rempli
            print("We are in validate_next_set, current_index:", current_index)
            if current_index < len(set_entries) - 1:
                for idx in (0, current_index):
                    if (set_entries[idx].get() == ""):
                        print("Empty set idx:", idx)
                        set_entries[idx].focus_set()
                #next_entry = set_entries[current_index + 1]
                if set_entries[current_index].get().strip():
                    next_entry.config(state="normal")
                else:
                    next_entry.delete(0, tk.END)
                    next_entry.config(state="disabled")
            
            # Lire la valeur du set précédent si disponible
            if current_index > 0:
                previous_value = set_entries[current_index - 1].get()
                print(f"Valeur du Set {current_index}: {previous_value}")
        '''    
        # Champs pour les scores des sets
        set_entries = []
        for i in range(5):
            row = tk.Frame(match_window)
            row.pack(pady=5)
            tk.Label(row, text=f"Set {i + 1}:", font=("Arial", 10)).pack(side="left")
            entry = tk.Entry(row, width=5, validate="key", validatecommand=(self.root.register(self.validate_set_input), '%d', '%P'))
            entry.pack(side="left")
            entry.bind("<Return>", lambda event, e=set_entries, p1=player1, p2=player2: self.handle_enter(event, e, p1, p2, set_choice))
            #entry.bind("<KeyRelease>", lambda e, idx=i: validate_next_set(idx))
            entry.bind("<FocusIn>", lambda e, idx=i: on_focus_in(e, idx))
            set_entries.append(entry)

        # Bouton pour fermer la fenêtre
        tk.Button(match_window, text="Fermer", command=match_window.destroy).pack(pady=10)
        
        # Mettre à jour la visibilité initiale des sets
        self.update_set_visibility(set_choice, set_entries)
        
    def draw_bracket(self, matches, tourInitial, nbPoules, nbTops):
        print("draw_bracket")
        self.canvas.delete("all")

        #if hasattr(self, 'canvas_frame'):
        #        self.canvas_frame.destroy()
        
        nb_players = 0
        if (nbPoules <= 8):
            nb_players = 8
        elif (nbPoules <= 16):
            nb_players = 16
        elif (nbPoules <= 32):
            nb_players = 32
        # Dimensions
        #canvas_width = self.canvas.winfo_width()
        #canvas_height = self.canvas.winfo_height()
        
        # Ajuster la hauteur dynamique du canevas
        canvas_height = max(600, 400 + nb_players * 70 * 2)
        #canvas_width = max(1200, 100 + (math.ceil(math.log2(nb_players)) + 1) * 300)
        #self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        self.canvas.config(scrollregion=(0, 0, 1200, canvas_height))
        
        #player_spacing = canvas_height // (len(matches) * 2)
        player_spacing = canvas_height // nb_players // 4
        gap = 10  # Espace entre les cadres
         
        next_round_positions = []
        nb_matches = int(tourInitial)

        # Créer des cadres pour les joueurs et connecter les lignes                    
        nb_players_top = nbTops * 4
        
        index_match = 0
        for idx in range (0, nb_players*2):
                y1_top = idx * 2 * (player_spacing + gap) + 10
                y1_bottom =  y1_top + player_spacing
                mid_y = (y1_top + y1_bottom) / 2
                #mid_y = mid_y1 + (mid_y2 - mid_y1) / 2
                index_match = 0
                next_round_positions.append(mid_y)
            
            
        print("matches:", matches)
        # Créer les cadres pour le prochain niveau
        new_positions = []
        last_match_y = 0
        start_x = 20
        
        while (nb_matches >=1):
            new_positions = []
            index_player = 1    
            longueur_rectangle = 180
            longueur_fleche = 100
            
            level_found_in_matches = False
            string_level = f"1/{tourInitial}"
            if (string_level in matches):
                matches_list = matches[string_level]
                level_found_in_matches = True
            
            joueur = 1
            index_matches = 0
            for round_mid_y in next_round_positions:
                #print ("nb_matches:", nb_matches, ",round_mid:", round_mid_y)
                j1 = ""
                j2 = ""
                if (level_found_in_matches):
                    print("Match:", matches_list[index_matches]['match'], ",index_matches", index_matches)
                    j1 = matches_list[index_matches]['match'].split("vs")[0].strip()
                    j2 = matches_list[index_matches]['match'].split("vs")[1].strip()
                    print("j1:", j1, ",j2:", j2)
                    
                if (index_player == 1):
                    y1_top = (round_mid_y - player_spacing//2)
                    y1_bottom = y1_top + player_spacing
                    mid_y1 = (y1_top + y1_bottom) // 2
                    self.canvas.create_rectangle(start_x, y1_top, start_x + longueur_rectangle, y1_bottom, outline="black", width=1)
                    if (j1 != ""):
                        self.canvas.create_text(start_x + 10, y1_top + 15, text=j1, anchor="w", font=("Arial", 10))
                    index_player = index_player + 1
                    if (nb_matches == 2*nb_players_top):
                       new_positions.append(round_mid_y) 
                else:
                    y2_top = (round_mid_y - player_spacing//2)
                    y2_bottom = y2_top + player_spacing
                    mid_y2 = (y2_top + y2_bottom) // 2
                    mid_y = (mid_y1 + mid_y2) // 2
                    #print ("y1_top", y1_top, "y1_bottom:", y1_bottom, "y2_top: ", y2_top, "y2_bottom:", y2_bottom)
                    #print("MID_Y:", mid_y)
                    if (nb_matches == 2*nb_players_top):
                        new_positions.append(round_mid_y)
                    else:
                        new_positions.append(mid_y) 
                    index_player = 1
                
                    self.canvas.create_rectangle(start_x, y2_top, start_x + longueur_rectangle, y2_bottom, outline="black", width=1)
                    if (j2 != ""):
                        self.canvas.create_text(start_x + 10, y2_top + 15, text=j2, anchor="w", font=("Arial", 10))
                    self.canvas.create_line(start_x + longueur_rectangle, mid_y1, start_x + longueur_rectangle + longueur_fleche, mid_y, fill="black")
                    self.canvas.create_line(start_x + longueur_rectangle, mid_y2, start_x + longueur_rectangle + longueur_fleche, mid_y, fill="black")
                    
                    #button_x = start_x - longueur_fleche // 2
                    button_x = start_x + 20
                    button_y = mid_y
                    #state = "normal" if j1 not in ["", "---"] and j2 not in ["", "---"] else "disabled"
                    state = "normal"
                    btn = tk.Button(self.canvas, text="Détails", state = state, command=lambda p1=j1, p2=j2: self.open_match_window(p1, p2))
                    self.canvas.create_window(button_x, button_y, window=btn)

                    if (nb_matches == 1):
                        last_match_y = mid_y                    
                    index_matches = index_matches + 1
            start_x = start_x + longueur_rectangle + longueur_fleche
            if (nb_matches == 2*nb_players_top):
                nb_players_top = 0
            else:
                nb_matches = nb_matches / 2        
            next_round_positions = new_positions
            tourInitial = tourInitial // 2
        
        # Affiche la case du vainqueur
        self.canvas.create_rectangle(start_x, last_match_y - player_spacing//2, start_x + longueur_rectangle, last_match_y + player_spacing, outline="black", width=1)                

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python Saisie-Tournoi-V1.py <categorie> <tour>")
        sys.exit(1)

    category_arg = sys.argv[1]
    round_arg = sys.argv[2]
    
    root = tk.Tk()
    app = TournamentBracket(root, category_arg, round_arg)
    root.mainloop()
