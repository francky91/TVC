import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
from utils import construire_bracket

# Imaginons que tvc_V20.py a la fonction "repartir_poules_sans_conflit"
# ainsi que charger_joueurs, filtrer_et_trier_joueurs, lire_excel_name, etc.

from tvc_V20 import repartir_poules_sans_conflit, charger_joueurs, filtrer_et_trier_joueurs, lire_excel_name
from utils import charger_config_categorie

class TVCApp:
    def __init__(self, root, categorie):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        """Constructeur: on initialise l'application pour la catégorie donnée."""
        self.root = root
        self.root.title(f"TVC - Catégorie {categorie}")

        self.categorie = categorie
        self.selected_item_1 = None
        self.selected_item_2 = None 
        self.selected_poule1 = -1
        self.selected_poule2 = -1
        self.nb_tops = 0

        # item_to_poulepos : {iid : (poule_index, joueur_index)}
        self.item_to_poulepos = {}
        self.treeviews = {}
        
        # Dans un usage plus sophistiqué, top_poules, poules, etc. seraient aussi des attributs.

        self.create_widgets()

    def create_widgets(self):
        """Crée les widgets principaux de la fenêtre (Label, Entry, Button, etc.)."""
        # 1) Charger / calculer ce qu'il faut
        fichier_entree = lire_excel_name()
        joueurs = charger_joueurs(fichier_entree, self.categorie)

        # On fait un filtrage pour connaître tourActif, nbJoueurs
        # (pour l'instant, on force nb_poules_top=0)
        self.joueursFiltres, self.tourActif, self.nbJoueurs = filtrer_et_trier_joueurs(joueurs, nb_poules_tops=0)

        # On place quelques labels / champs
        tk.Label(self.root, text=f"Catégorie : {self.categorie}").grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(self.root, text=f"Tour : {self.tourActif}").grid(row=1, column=0, columnspan=2, sticky="w")
        tk.Label(self.root, text=f"Nb Joueurs : {self.nbJoueurs}").grid(row=2, column=0, columnspan=2, sticky="w")

        print(f"tourActif = {self.tourActif}, nbJoueurs = {self.nbJoueurs}")
        if (self.tourActif == "tour1"):
            self.nb_tops_defaut = 0
        else:
            self.nb_tops_defaut = int(charger_config_categorie("config.ini", self.categorie))
    
        total_joueurs_poules = self.nbJoueurs - 4*self.nb_tops_defaut
        self.nb_poules_4 = total_joueurs_poules // 4
        self.nb_poules_3 = (total_joueurs_poules % 4) // 3
        
        while ( (self.nb_poules_4*4 + self.nb_poules_3*3) < total_joueurs_poules):
            self.nb_poules_4 = self.nb_poules_4 - 1
            self.nb_poules_3 = int( (total_joueurs_poules - (self.nb_poules_4 *4))/3)
        self.nb_poules_5 = 0
        self.nb_poules_top_var = tk.StringVar(value=self.nb_tops_defaut)
        self.nb_poules_3_var = tk.StringVar(value=self.nb_poules_3)
        self.nb_poules_4_var = tk.StringVar(value=self.nb_poules_4)
        self.nb_poules_5_var = tk.StringVar(value=self.nb_poules_5)

        # On affiche des champs
        tk.Label(self.root, text="Nb poules Top:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.nbPoulesTopsEntry = tk.Entry(self.root, textvariable=self.nb_poules_top_var, width=5).grid(row=3, column=1, sticky="w")

        tk.Label(self.root, text="Nb poules 3 :").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.nbPoules3Entry = tk.Entry(self.root, textvariable=self.nb_poules_3_var, width=5).grid(row=4, column=1, sticky="w")

        tk.Label(self.root, text="Nb poules 4 :").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.nbPoules4Entry = tk.Entry(self.root, textvariable=self.nb_poules_4_var, width=5).grid(row=5, column=1, sticky="w")

        tk.Label(self.root, text="Nb poules 5 :").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.nbPoules5Entry = tk.Entry(self.root, textvariable=self.nb_poules_5_var, width=5).grid(row=6, column=1, sticky="w")

        # Bouton Lancer
        tk.Button(self.root, text="Lancer", command=self.on_lancer).grid(row=7, column=0, columnspan=2, pady=10)

        self.root.geometry("400x300")

    def on_lancer(self):
        """Quand on clique sur Lancer : on lance repartir_poules_sans_conflit, puis on affiche la fenetre de poules."""
        try:
            self.nb_tops = int(self.nb_poules_top_var.get())
            nb_3   = int(self.nb_poules_3_var.get())
            nb_4   = int(self.nb_poules_4_var.get())
            nb_5   = int(self.nb_poules_5_var.get())
            
            if (self.nb_tops*4 + nb_3*3 + nb_4*4 + nb_5*5 != self.nbJoueurs):
                messagebox.showerror("Erreur", "Erreur dans la définition du nombre de poules")
                self.nb_poules_top_var.set(self.nb_tops_defaut)
                self.nb_poules_3_var.set(self.nb_poules_3)
                self.nb_poules_4_var.set(self.nb_poules_4)
                self.nb_poules_5_var.set(self.nb_poules_5)
                
                return
        except ValueError:
            messagebox.showerror("Erreur", "Les nombres de poules doivent être des entiers.")
            return

        try:
            self.top_poules, self.poules, tourActif, nbJoueurs = repartir_poules_sans_conflit(
                lire_excel_name(),
                self.categorie,
                nb_poules_top=self.nb_tops,
                nb_poules_3=nb_3,
                nb_poules_4=nb_4,
                nb_poules_5=nb_5
            )
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
            return

        # On affiche une nouvelle fenêtre avec top_poules, poules
        self.afficher_poules_dans_fenetre()
        
    def refresh_treeview(self, tree, poule_index, liste_joueurs):
        """
        Vider le tree, puis réinsérer tous les joueurs de la poule.
        On met à jour item_to_poulepos pour chaque ligne.
        """
        tree.delete(*tree.get_children())

        for idx_j, joueur in enumerate(liste_joueurs):
            dossard = str(int(joueur.get("dossard", "")))
            nom = joueur.get("nom", "")
            prenom = joueur.get("prenom", "")
            club = joueur.get("club", "")
            classement = joueur.get("classement", "")
            points = joueur.get("points", "")
            # etc...
            # On insère
            iid = tree.insert("", tk.END, values=(dossard, nom, prenom, club, classement, points))
            # On stocke dans item_to_poulepos
            
            self.item_to_poulepos[poule_index, iid] = (idx_j)
         
    def generer_poules(self):
        from tvc_V20 import update_word_and_json
    
        update_word_and_json(self.categorie, self.tourActif, self.top_poules, self.poules)

    def afficher_poules_dans_fenetre(self):
        """Ouvre une toplevel qui affiche les Treeviews, le bouton Échanger, etc."""
        self.fenetre_poules = tk.Toplevel(self.root)
        fenetre = self.fenetre_poules
        #fenetre = tk.Toplevel(self.root)
        fenetre.title("Aperçu des Poules")
        
            # Rendre la fenêtre modale
        fenetre.transient(self.root)  # Associe la fenêtre secondaire à la fenêtre principale
        fenetre.grab_set()  # Empêche les interactions avec la fenêtre principale

        self.selected_item_1 = None
        self.selected_item_2 = None
        self.selected_poule1 = -1
        self.selected_poule2 = -1
        
        top_frame = tk.Frame(fenetre)
        top_frame.pack(side="top", fill="x")
        
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(pady=10)

        self.btn_swap = tk.Button(button_frame, text="Échanger joueurs", state="disabled", command=self.on_swap)
        self.btn_swap.pack(side="right", padx=5)

        self.btn_valider = tk.Button(button_frame, text="Valider Poules", state="disabled", command=self.generer_poules)
        self.btn_valider.pack(side="right", padx=5)

        self.btn_deselect = tk.Button(button_frame, text="Désélectionner", state="disabled", command=self.on_deselect)
        self.btn_deselect.pack(side="right", padx=5)
        
        self.btn_depl = tk.Button(button_frame, text="Deplacer joueurs", state="disabled", command=self.deplacer_joueurs)
        self.btn_depl.pack(side="right", padx=5)

        #self.btn_completer = tk.Button(button_frame, text="Completer Poule", state="disabled", command=self.completer_poule)
        #self.btn_completer.pack(side="right", padx=5)

        self.btn_verif = tk.Button(button_frame, text="Verification tableau", state="normal", command=self.verif_tableau_ko)
        self.btn_verif.pack(side="right", padx=5)

        main_frame = tk.Frame(fenetre)
        main_frame.pack(side="top", fill="both", expand=True)
    
        # Canvas/scroll
        canvas = tk.Canvas(main_frame)
        vscroll = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        poules_frame = tk.Frame(canvas)
        canvas.create_window((0,0), window=poules_frame, anchor="nw")

        poules_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
         

        # Bouton Échanger
        #self.btn_swap = tk.Button(poules_frame, text="Échanger joueurs", state="disabled", command=self.on_swap)
        #self.btn_swap.pack(pady=10, anchor="e")

        # Dictionnaire pour stocker les Treeviews
        self.treeviews = {}

        global_poule_index = 0

        # Affichage top_poules
        for i, p in enumerate(self.top_poules):
            titre = f"Top {i+1}"
            self.create_treeview_for_poule(titre, poules_frame, global_poule_index, p)
            global_poule_index += 1

        # Affichage poules classiques
        for i, p in enumerate(self.poules):
            titre = f"Poule {i+1}"
            self.create_treeview_for_poule(titre, poules_frame, global_poule_index, p)
            global_poule_index += 1
            
        def _on_mousewheel(event):
            # Sur Windows, event.delta est par multiples de 120
            # Sur d'autres plateformes, la valeur peut différer
            # -1 * (event.delta/120) => en gros on normalise de +/-1 la rotation
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        fenetre.geometry("1000x400")
        fenetre.state("zoomed")
        
    def on_deselect(self):

        for tree in self.treeviews.values():
            tree.selection_remove(tree.selection())
        self.selected_item_1 = None
        self.selected_item_2 = None
        self.selected_poule1 = -1
        self.selected_poule2 = -1
        self.update_swap_button()
        if hasattr(self, 'btn_deselect'):
            if self.selected_item_1 is not None or self.selected_item_2 is not None:
                self.btn_deselect.config(state="normal")
            else:
                self.btn_deselect.config(state="disabled")                
        
        if hasattr(self, 'btn_swap'):
            self.btn_swap.config(state="disabled")
        if hasattr(self, 'btn_depl'):
            self.btn_depl.config(state="disabled")
        #if hasattr(self, 'btn_deselect'):
        #    self.btn_deselect.config(state="disabled")
        #if hasattr(self, 'btn_swap'):
        #    self.btn_swap.config(state="disabled")
    
    def create_treeview_for_poule(self, titre, parent, poule_index, liste_joueurs):
        """Crée un Treeview bindé sur on_treeview_select, insère les joueurs."""
        lbl = tk.Label(parent, text=titre, font=("Arial", 10, "bold"))
        lbl.pack(pady=(10,0), anchor="w")

        tree = ttk.Treeview(parent, columns=("dossard","nom","prenom","club","classement","points"), show="headings")
        tree.pack(fill="x", padx=10, pady=5)

        # config colonnes
        for col in ("dossard","nom","prenom","club","classement","points"):
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=100)

        # Bind
        tree.bind("<<TreeviewSelect>>", lambda e, pi=poule_index: self.on_treeview_select(e, pi))

        # Insert data
        for idx_j, joueur in enumerate(liste_joueurs):
            dossard = str(int(joueur.get("dossard","")))
            nom = joueur.get("nom","")
            prenom = joueur.get("prenom","")
            club = joueur.get("club","")
            classement = joueur.get("classement","")
            points = joueur.get("points","")

            iid = tree.insert("", tk.END, values=(dossard, nom, prenom, club, classement, points))
            
            self.item_to_poulepos[poule_index, iid] = (idx_j)

        self.treeviews[poule_index] = tree
        
    def on_treeview_select(self, event, poule_index):
        tree = event.widget
        sel = tree.selection()
        if not sel:
            return
        iid = sel[0]
        
        # identité complète de la sélection
        sel_id = (iid, poule_index)
        cur1 = (self.selected_item_1, self.selected_poule1) if self.selected_item_1 is not None else (None, None)
        cur2 = (self.selected_item_2, self.selected_poule2) if self.selected_item_2 is not None else (None, None)


        # Si on reclique sur un élément déjà sélectionné (même iid ET même poule), ne rien changer
        if sel_id == cur1 or sel_id == cur2:
            # réaffirmer la sélection visuelle
            try:
                tree.selection_add(iid)
            except Exception:
                pass
            self.update_swap_button()
            return
        
        #print(f"selected_item_1: {self.selected_item_1}, selected_item_2: {self.selected_item_2}")
        if self.selected_item_1 is None:
            self.selected_item_1 = iid
            self.selected_poule1 = poule_index
        elif self.selected_item_2 is None:
            self.selected_item_2 = iid
            self.selected_poule2 = poule_index
        else:
            # Si deux joueurs sont déjà sélectionnés, on remplace le deuxième
            # On désélectionne l'ancien deuxième joueur dans toutes les treeviews
            for t in self.treeviews.values():
                try:
                    t.selection_remove(self.selected_item_2)
                except Exception:
                    pass
            #print(f"Remplacement du joueur sélectionné 2 : {self.selected_item_2} par {iid}")
            # Mettre à jour le deuxième joueur avec le nouveau
            self.selected_item_2 = iid
            self.selected_poule2 = poule_index

        # S'assurer que le premier joueur reste visuellement selectionné
        if self.selected_item_1 is not None and self.selected_poule1 in self.treeviews:
            try:
                self.treeviews[self.selected_poule1].selection_add(self.selected_item_1)
            except Exception:
                pass

        # S'assurer que le deuxième joueur est aussi visuellement sélectionné
        if self.selected_item_2 is not None and self.selected_poule2 in self.treeviews:
            try:
                self.treeviews[self.selected_poule2].selection_add(self.selected_item_2)
            except Exception:
                pass

        self.update_swap_button()
        
    def update_swap_button(self):
        """Active/désactive le bouton Échanger."""
        '''if self.selected_item_1 is not None and self.selected_item_2 is not None:
            self.btn_swap.config(state="normal")
        else:
            self.btn_swap.config(state="disabled")
        '''
        
        swap_enabled = (self.selected_item_1 is not None and self.selected_item_2 is not None)
        if hasattr(self, 'btn_swap'):
            try:
                self.btn_swap.config(state="normal" if swap_enabled else "disabled")
            except Exception:
                pass
            
        if hasattr(self, 'btn_depl'):
            try:
                self.btn_depl.config(state="normal" if swap_enabled else "disabled")
            except Exception:
                pass
            
        '''if hasattr(self, 'btn_completer'):
            try:
                self.btn_completer.config(state="normal" if swap_enabled else "disabled")
            except Exception:
                pass    
        '''
        deselect_enabled = (self.selected_item_1 is not None) or (self.selected_item_2 is not None)
        print(f"update_swap_button: selected_item_1={self.selected_item_1}, selected_item_2={self.selected_item_2}, deselect_enabled={deselect_enabled}")
        
        if hasattr(self, 'btn_deselect'):
            try:
                print("Updating btn_deselect state")
                self.btn_deselect.config(state="normal" if deselect_enabled else "disabled")
            except Exception:
                print("Exception")
                pass

    def refresh_all_poules(self):
        """Rafraîchit l'affichage de toutes les poules."""
        for i, poule in enumerate(self.top_poules):
            #self.refresh_treeview(self.treeviews[i], i, poule)
            self.refresh_treeview(self.treeviews[i], i, self.top_poules[i])
        for i, poule in enumerate(self.poules):
            #self.refresh_treeview(self.treeviews[len(self.top_poules) + i], len(self.top_poules) + i, poule)
            self.refresh_treeview(self.treeviews[len(self.top_poules) + i], i, self.poules[i])
        for key, treeview in self.treeviews.items():
            for iid in treeview.get_children():
                values = treeview.item(iid, "values")  # Récupérer les valeurs de la ligne
                nom = values[1]  # Colonne "nom"
                prenom = values[2]  # Colonne "prenom"

    def calculer_nb_rectangles(self, nb_poules):
        nb_rect = 1
        while nb_rect < nb_poules * 2:
            nb_rect *= 2
        return nb_rect
    
    
    '''def verif_tableau_ko(self):
        nb_poules = len(self.poules)
        nb_rectangles = self.calculer_nb_rectangles(nb_poules)

        fenetre_verif = tk.Toplevel(self.fenetre_poules)
        fenetre_verif.title("Vérification du tableau")
        fenetre_verif.geometry("380x800")
        fenetre_verif.transient(self.fenetre_poules)
        
        # --- CONFIGURATION DU CANVAS ET SCROLLBAR ---
        frame_ext = tk.Frame(fenetre_verif)
        frame_ext.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame_ext, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_ext, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Support molette
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        tableauOk = construire_bracket(nb_rectangles)
        
        # --- 1. PRÉPARATION DES DONNÉES ---
        rect_data = [] 
        for i, element_dict in enumerate(tableauOk):
            valeur = list(element_dict.keys())[0]
            
            if valeur > nb_poules * 2:
                rect_data.append((True, "")) 
            elif valeur <= nb_poules:
                rect_data.append((False, f"1er Poule {valeur}"))
            else:
                X = nb_poules
                V = valeur
                if X % 2 != 0: index_poule = X - (V - (X + 1))
                else:
                    diff = V - X
                    index_poule = (X - 1) - (diff - 1) if diff % 2 != 0 else X - (diff - 2)
                
                is_poule_de_3 = (len(self.poules[index_poule-1]) == 3)
                rect_data.append((is_poule_de_3, f"2eme Poule {index_poule}"))

        # --- 2. DESSIN DE TOUS LES RECTANGLES ---
        rect_height = 40
        rect_width = 220
        spacing = 10
        x_offset = 40

        for i, (grise, texte) in enumerate(rect_data):
            y = i * (rect_height + spacing) + 20
            couleur_fond = "lightgrey" if grise else "white"
            canvas.create_rectangle(x_offset, y, x_offset + rect_width, y + rect_height, 
                                    fill=couleur_fond, outline="black", width=2)
            if texte:
                canvas.create_text(x_offset + 10, y + rect_height / 2, 
                                   anchor="w", text=texte, font=("Arial", 9))
            if i % 2 == 1:
                line_y = y + rect_height + (spacing / 2)
                canvas.create_line(x_offset - 20, line_y, x_offset + rect_width + 20, line_y, width=2, fill="gray")

        # Mise à jour de la zone de défilement
        total_height = len(rect_data) * (rect_height + spacing) + 60
        canvas.configure(scrollregion=(0, 0, 380, total_height))

        # --- 3. FORCER L'AFFICHAGE PUIS TEST LOGIQUE ---
        # Cette commande force Tkinter à dessiner la fenêtre avant de continuer
        canvas.update() 

        nb_non_grises = sum(1 for grise, txt in rect_data if not grise)
        if nb_non_grises >= 2:
            for i in range(0, len(rect_data), 2):
                if i + 1 < len(rect_data):
                    (g1, t1), (g2, t2) = rect_data[i], rect_data[i+1]
                    # Si les deux rectangles du match sont grisés
                    if g1 and g2:
                        messagebox.showwarning("Attention", f"Attention : {t1 if t1 else 'Vide'} et {t2 if t2 else 'Vide'}")
    '''
    def verif_tableau_ko(self):
        self.btn_valider.config(state="normal")
        nb_poules = len(self.poules)
        nb_rectangles = self.calculer_nb_rectangles(nb_poules)

        fenetre_verif = tk.Toplevel(self.fenetre_poules)
        fenetre_verif.title("Vérification et Réajustement")
        fenetre_verif.geometry("400x800")
        fenetre_verif.transient(self.fenetre_poules)
        
        frame_ext = tk.Frame(fenetre_verif)
        frame_ext.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame_ext, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_ext, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # --- 1. ANALYSE ET RÉAJUSTEMENT DES POULES DE 3/4 ---
        tableauOk = construire_bracket(nb_rectangles)
        
        def obtenir_infos_paires():
            data = []
            for element_dict in tableauOk:
                valeur = list(element_dict.keys())[0]
                if valeur > nb_poules * 2:
                    data.append({"grise": True, "poule_idx": -1, "type": "Vide"})
                elif valeur <= nb_poules:
                    data.append({"grise": False, "poule_idx": valeur - 1, "type": "1er"})
                else:
                    X = nb_poules
                    V = valeur
                    if X % 2 != 0: idx = X - (V - (X + 1))
                    else:
                        diff = V - X
                        idx = (X - 1) - (diff - 1) if diff % 2 != 0 else X - (diff - 2)
                    
                    is_3 = (len(self.poules[idx-1]) == 3)
                    data.append({"grise": is_3, "poule_idx": idx - 1, "type": "2eme"})
            return data

        rect_data = obtenir_infos_paires()
        modifications_effectuees = False

        for i in range(0, len(rect_data), 2):
            if i + 1 < len(rect_data):
                if rect_data[i]["grise"] and rect_data[i+1]["grise"]:
                    poule_P_idx = rect_data[i]["poule_idx"]
                    poule_Q_idx = -1
                    for q_idx, p_liste in enumerate(self.poules):
                        if len(p_liste) == 4 and q_idx != poule_P_idx:
                            poule_Q_idx = q_idx
                            break
                    
                    if poule_Q_idx != -1:
                        joueur = self.poules[poule_Q_idx].pop(3)
                        self.poules[poule_P_idx].append(joueur)
                        print(f"[RÉAJUSTEMENT] Poule {poule_P_idx+1} complétée avec un joueur de Poule {poule_Q_idx+1}")
                        modifications_effectuees = True
                        rect_data = obtenir_infos_paires()

        # --- 2. VÉRIFICATION DES CONFLITS DE CLUB (SI RÉAJUSTEMENT) ---
        if modifications_effectuees:
            self.refresh_all_poules()
            conflits = []
            for idx, poule in enumerate(self.poules):
                clubs_vus = {}
                for j in poule:
                    club = j.get("club", "").strip().upper()
                    if club and club != "SANS CLUB":
                        if club in clubs_vus:
                            conflits.append(f"Poule {idx+1} : {j.get('nom')} et {clubs_vus[club]} sont du club {club}")
                        clubs_vus[club] = j.get("nom")
            
            if conflits:
                msg_conflit = "Réajustement terminé, mais attention aux conflits de clubs :\n\n" + "\n".join(conflits)
                messagebox.showwarning("Conflits de Clubs", msg_conflit)
            else:
                messagebox.showinfo("Réajustement", "Le tableau a été réajusté avec succès et sans conflit de club.")

        # --- 3. DESSIN ---
        canvas.create_text(210, 30, text="Tableau KO", font=("Arial", 16, "bold"), fill="red")
        
        rect_height, rect_width, spacing, x_offset = 40, 220, 10, 40
        start_y = 70
        
        for i, info in enumerate(rect_data):
            y = i * (rect_height + spacing) + start_y
            couleur = "lightgrey" if info["grise"] else "white"
            texte = "" if info["poule_idx"] == -1 else f"{info['type']} Poule {info['poule_idx'] + 1}"
            
            canvas.create_rectangle(x_offset, y, x_offset + rect_width, y + rect_height, fill=couleur, outline="black", width=2)
            if texte:
                canvas.create_text(x_offset + 10, y + rect_height / 2, anchor="w", text=texte, font=("Arial", 9))
            if i % 2 == 1:
                line_y = y + rect_height + (spacing / 2)
                canvas.create_line(x_offset - 20, line_y, x_offset + rect_width + 20, line_y, width=2, fill="gray")

        canvas.configure(scrollregion=(0, 0, 380, len(rect_data) * (rect_height + spacing) + 60))
        canvas.update()
    
                        
    def completer_poule(self):
        """
        Logique : 
        P est la poule du joueur 1 (doit être une poule de 3).
        Q est la poule du joueur 2 (doit être une poule de 4).
        Action : On déplace le 4ème joueur de Q vers la 4ème place de P.
        """
        if self.selected_item_1 is None or self.selected_item_2 is None:
            return

        # 1. Identification des poules
        # On ajuste l'index si c'est une poule "classique" (hors top)
        idx_poule_P = self.selected_poule1 - self.nb_tops
        idx_poule_Q = self.selected_poule2 - self.nb_tops

        # Sécurité : on ne traite que les poules standards (pas les poules Top)
        if idx_poule_P < 0 or idx_poule_Q < 0:
            self._reset_selection_and_error("Le complément de poule ne s'applique pas aux poules Top.")
            return

        pouleP = self.poules[idx_poule_P]
        pouleQ = self.poules[idx_poule_Q]

        # 2. Vérification des critères
        # Critère 1 : P doit être une poule de 3
        # Critère 2 : Q doit être une poule de 4
        if len(pouleP) == 3 and len(pouleQ) == 4:
            # Action : Le 4ème joueur de Q (index 3) passe chez P
            joueur_a_deplacer = pouleQ.pop(3) # Retire le 4ème de Q
            pouleP.append(joueur_a_deplacer)  # L'ajoute en 4ème position de P

            # Mise à jour de l'affichage
            self.item_to_poulepos = {} # On reset les positions car les index ont changé
            self.refresh_all_poules()
            
            # Reset de la sélection après succès
            self.on_deselect()
            messagebox.showinfo("Succès", "Le joueur a été déplacé. La poule P est complétée.")
        
        else:
            # Message d'erreur si critères non respectés
            msg = "Critères non respectés :\n"
            if len(pouleP) != 3: msg += f"- La poule sélectionnée 1 doit avoir 3 joueurs (actuellement {len(pouleP)})\n"
            if len(pouleQ) != 4: msg += f"- La poule sélectionnée 2 doit avoir 4 joueurs (actuellement {len(pouleQ)})\n"
            
            self._reset_selection_and_error(msg)

    def _reset_selection_and_error(self, message):
        """Aide pour réinitialiser l'interface en cas d'erreur de critère."""
        messagebox.showwarning("Attention", message)
        self.on_deselect() # Utilise votre fonction existante pour vider sel_item1, 2 et inhiber les boutons
    
    def deplacer_joueurs(self):
        """Déplace un joueur et décale les autres joueurs en respectant le mode du serpent."""
        if self.selected_item_1 is None or self.selected_item_2 is None:
            messagebox.showerror("Erreur", "Pas assez de joueurs sélectionnés.")
            return

        if (self.selected_poule1 < self.nb_tops or  self.selected_poule2 < self.nb_tops):
            messagebox.showerror("Erreur", "Deplacement d'un joueur du top impossible")
        
            self.refresh_all_poules()
            self.selected_item_1 = None
            self.selected_item_2 = None
            self.selected_poule1 = -1
            self.selected_poule2 = -1
        
            if hasattr(self, 'btn_swap'):
                self.btn_swap["state"] = "disabled"
            if hasattr(self, 'btn_depl'):
                self.btn_depl["state"] = "disabled"
            return
        
        # Récupérer les indices des poules et des positions
        pouleX = self.selected_poule1 - self.nb_tops
        posP = self.item_to_poulepos[self.selected_poule1, self.selected_item_1]
        pouleY = self.selected_poule2 - self.nb_tops
        posQ = self.item_to_poulepos[self.selected_poule2, self.selected_item_2]
        
        if (pouleY < pouleX or ( pouleY == pouleX and posQ == posP)):
            messagebox.showerror("Erreur", "Le joueur à déplacer doit être après la position cible.")
            
            self.refresh_all_poules()
            self.selected_item_1 = None
            self.selected_item_2 = None
            self.selected_poule1 = -1
            self.selected_poule2 = -1
        
            if hasattr(self, 'btn_swap'):
                self.btn_swap["state"] = "disabled"
            if hasattr(self, 'btn_depl'):
                self.btn_depl["state"] = "disabled"
            return
            
        pouleTmp = pouleX

        print(f"Déplacement : joueur de poule {pouleY}, position {posQ} vers poule {pouleX}, position {posP}: {self.poules[pouleY][posQ].get('nom','')} {self.poules[pouleY][posQ].get('prenom','')}") 
        ended = False
        sens = 1  # 1 pour avancer, -1 pour reculer
        
        print(f"pouleX: {pouleX}, posP: {posP}, pouleY: {pouleY}, posQ: {posQ}")
        joueurTmp = self.poules[pouleX][posP]
        
        
        #print(f"contenu poule X: {self.poules[pouleX]}")
        #print(f"contenu poule Y: {self.poules[pouleY]}")
        self.poules[pouleX][posP] = self.poules[pouleY][posQ]
        #self.poules[pouleY][posQ] = joueurTmp
        #print(f"Déplacement : joueur de poule {pouleX}, position {posP} vers poule {pouleY}, position {posQ}: {joueurTmp.get('nom','')} {joueurTmp.get('prenom','')}") 
        
        #joueurTmp = self.poules[pouleX+1][posP]
        print(f"Joueur temporaire : {joueurTmp.get('nom','')} {joueurTmp.get('prenom','')}")
        while not ended:
            do_nothing = False
            if (sens ==  1):
                if (pouleTmp == len(self.poules)-1):
                    posP += 1
                    sens = -sens
                    if (posP >= len(self.poules[pouleTmp])):
                        do_nothing = True
                        print(f"sens: {sens}, do_nothing: {do_nothing}")
                else:
                    pouleTmp+=1
            else:
                if (pouleTmp == 0):
                    posP += 1
                    sens = -sens
                    if (posP >= len(self.poules[pouleTmp])):
                        do_nothing = True
                        print(f"sens: {sens}, do_nothing: {do_nothing}")
                else:
                    pouleTmp-=1
            
            print(f"pouleTmp: {pouleTmp}, posP: {posP}, pouleY: {pouleY}, posQ: {posQ}")
            if ( (pouleTmp == pouleY+1 and posP == posQ and sens==1) or
                 (pouleTmp == pouleY-1 and posP == posQ and sens==-1) ):
                ended = True
                break
            elif (do_nothing and pouleTmp == pouleY and (
                (posP == posQ + 1 and sens == -1) or
                (posP == posQ - 1 and sens == 1)) ):
                ended = True
                break
            elif not do_nothing:
                contenu_poule = self.poules[pouleTmp][posP]
                self.poules[pouleTmp][posP] = joueurTmp
                
                print(f"Déplacement : joueur {joueurTmp.get('nom')} {joueurTmp.get('prenom')} vers poule {pouleTmp}, position {posP}") 
                
                joueurTmp = contenu_poule
                

        if hasattr(self, 'btn_deselect'):
            self.btn_deselect["state"] = "disabled"
        
        self.item_to_poulepos = {}
        
        self.refresh_all_poules()
        
        self.selected_item_1 = None
        self.selected_item_2 = None
        self.selected_poule1 = -1
        self.selected_poule2 = -1
        
        if hasattr(self, 'btn_swap'):
            self.btn_swap["state"] = "disabled"
        if hasattr(self, 'btn_depl'):
            self.btn_depl["state"] = "disabled"
        
    def on_swap(self):
        """Callback bouton Échanger."""
        if self.selected_item_1 is None or self.selected_item_2 is None:
            messagebox.showerror("Erreur", "Pas assez de joueurs sélectionnés.")
            return
        
        pouleA = self.selected_poule1
        indexA = self.item_to_poulepos[self.selected_poule1, self.selected_item_1]
        pouleB = self.selected_poule2
        indexB = self.item_to_poulepos[self.selected_poule2, self.selected_item_2]
        #print(f"[on_swap] Échange entre pouleA={pouleA}:{indexA} et pouleB={pouleB}:{indexB}")
        print("Échange entre")
        print(f"selected_item_1: {self.selected_item_1}, selected_item_2: {self.selected_item_2}")
        print(f"pouleA: {pouleA}, indexA: {indexA}")
        print(f"pouleB: {pouleB}, indexB: {indexB}")
        l = len(self.top_poules)

        # Échange en mémoire (ex: self.top_poules ou self.poules),
        #   selon votre logique. On ne l'a pas stocké en attribut,
        #   donc il faudrait l'enregistrer plus haut (ex: self.top_poules).
        #
        # Après, on reset :
        self.selected_item_1 = None
        self.selected_item_2 = None
        self.selected_poule1 = -1
        self.selected_poule2 = -1
        
        if pouleA < len(self.top_poules):
            #print(f"poule Top {pouleA}: {self.top_poules[pouleA][indexA]["nom"]} {self.top_poules[pouleA][indexA]["prenom"]} {self.top_poules[pouleA][indexA]["club"]}")
            if pouleB < len(self.top_poules):
                #print(f"poule Top {pouleB}: {self.top_poules[pouleB][indexB]["nom"]} {self.top_poules[pouleB][indexB]["prenom"]} {self.top_poules[pouleB][indexB]["club"]}")
                self.top_poules[pouleA][indexA], self.top_poules[pouleB][indexB] = self.top_poules[pouleB][indexB], self.top_poules[pouleA][indexA]
            else:
                l = len(self.top_poules)
                self.top_poules[pouleA][indexA], self.poules[pouleB - l][indexB] = self.poules[pouleB - l][indexB], self.top_poules[pouleA][indexA]                      
        else:
            l = len(self.top_poules)
            
            if pouleB >= len(self.top_poules):
                self.poules[pouleA - l][indexA], self.poules[pouleB - l][indexB] = self.poules[pouleB - l][indexB], self.poules[pouleA - l][indexA]
            else:
                self.poules[pouleA - l][indexA], self.top_poules[pouleB][indexB] = self.top_poules[pouleB][indexB], self.poules[pouleA - l][indexA]
    
        # Rafraîchir l'affichage : refonction "refresh_treeview(tree, pouleA, poules[pouleA])", etc.
        l = len(self.top_poules)
        if pouleA < len(self.top_poules):
            self.refresh_treeview(self.treeviews[pouleA], pouleA, self.top_poules[pouleA])
            if (pouleB < len(self.top_poules)):
                self.refresh_treeview(self.treeviews[pouleB], pouleB, self.top_poules[pouleB])
            else:
                self.refresh_treeview(self.treeviews[pouleB], pouleB-l, self.poules[pouleB-l])
        else:
            self.refresh_treeview(self.treeviews[pouleA], pouleA-l, self.poules[pouleA-l])
            if (pouleB>=len(self.top_poules)):
                self.refresh_treeview(self.treeviews[pouleB], pouleB-l, self.poules[pouleB-l])
            else:
                self.refresh_treeview(self.treeviews[pouleB], pouleB, self.top_poules[pouleB])
        
        if hasattr(self, 'btn_swap'):        
            self.btn_swap["state"] = "disabled"
        if hasattr(self, 'btn_depl'):
            self.btn_depl["state"] = "disabled"
        if hasattr(self, 'btn_deselect'):
            self.btn_deselect["state"] = "disabled"

def main(categorie):
    root = tk.Tk()
    app = TVCApp(root, categorie)
    root.mainloop()

if __name__ == "__main__":
    import sys
    cat = sys.argv[1] if len(sys.argv) > 1 else "Poussins"
    main(cat)
