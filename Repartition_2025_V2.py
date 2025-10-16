import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys

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
            nb_top = int(self.nb_poules_top_var.get())
            nb_3   = int(self.nb_poules_3_var.get())
            nb_4   = int(self.nb_poules_4_var.get())
            nb_5   = int(self.nb_poules_5_var.get())
            
            if (nb_top*4 + nb_3*3 + nb_4*4 + nb_5*5 != self.nbJoueurs):
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
                nb_poules_top=nb_top,
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
            self.item_to_poulepos[iid] = (poule_index, idx_j)
            
    def generer_poules(self):
        from tvc_V20 import update_word_and_json
    
        update_word_and_json(self.categorie, self.tourActif, self.top_poules, self.poules)

    def afficher_poules_dans_fenetre(self):
        """Ouvre une toplevel qui affiche les Treeviews, le bouton Échanger, etc."""
        print("In afficher_poules_dans_fenetre")
        fenetre = tk.Toplevel(self.root)
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
    
        btn_valider = tk.Button(button_frame, text="Valider Poules", command=self.generer_poules)
        btn_valider.pack(side="right", padx=5)
        
        self.btn_deselect = tk.Button(button_frame, text="Désélectionner", state="disabled", command=self.on_deselect)
        self.btn_deselect.pack(side="right", padx=5)

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
        '''    for tree in self.treeviews.values():
            tree.selection_remove(tree.selection())
            self.selected_item_1 = None
            self.selected_item_2 = None
            self.selected_poule1 = -1
            self.selected_poule2 = -1
            self.update_swap_button()
            if hasattr(self, 'btn_swap'):
                self.btn_swap.config(state="disabled")
        '''
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
            self.item_to_poulepos[iid] = (poule_index, idx_j)

        self.treeviews[poule_index] = tree

    '''def on_treeview_select(self, event, poule_index):
        """Callback sélection d'un joueur."""
        tree = event.widget
        sel = tree.selection()
        if not sel:
            return
        iid = sel[0]

        if self.selected_item_1 is None:
            self.selected_item_1 = iid
            self.selected_poule1 = poule_index
        elif self.selected_item_2 is None:
            self.selected_item_2 = iid
            self.selected_poule2 = poule_index

        self.update_swap_button()
    '''
        
    def on_treeview_select(self, event, poule_index):
        tree = event.widget
        sel = tree.selection()
        if not sel:
            return
        iid = sel[0]

        # If the clicked item is already one of the selected items, keep state and return
        '''if iid == self.selected_item_1 or iid == self.selected_item_2:
            print(f"iid {iid}, selected_item_1: {self.selected_item_1}, selected_item_2: {self.selected_item_2}")
            # update poule index in case selection came from another tree
            if iid == self.selected_item_1:
                self.selected_poule1 = poule_index
                print("selected_item_1 remains the same")
            if iid == self.selected_item_2:
                self.selected_poule2 = poule_index
                print("selected_item_2 remains the same")
            # ensure visual selection
            try:
                tree.selection_add(iid)
            except Exception:
                pass
            self.update_swap_button()
            return
        '''
        
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

        
        deselect_enabled = (self.selected_item_1 is not None) or (self.selected_item_2 is not None)
        print(f"update_swap_button: selected_item_1={self.selected_item_1}, selected_item_2={self.selected_item_2}, deselect_enabled={deselect_enabled}")
        if hasattr(self, 'btn_deselect'):
            try:
                print("Updating btn_deselect state")
                self.btn_deselect.config(state="normal" if deselect_enabled else "disabled")
            except Exception:
                print("Exception")
                pass
        else:
            print("No btn_deselect attribute")

    def on_swap(self):
        """Callback bouton Échanger."""
        if self.selected_item_1 is None or self.selected_item_2 is None:
            messagebox.showerror("Erreur", "Pas assez de joueurs sélectionnés.")
            return

        pouleA, indexA = self.item_to_poulepos[self.selected_item_1]
        pouleA = self.selected_poule1
        pouleB, indexB = self.item_to_poulepos[self.selected_item_2]
        pouleB = self.selected_poule2
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
                
        self.btn_swap["state"] = "disabled"
        self.btn_deselect["state"] = "disabled"

def main(categorie):
    root = tk.Tk()
    app = TVCApp(root, categorie)
    root.mainloop()

if __name__ == "__main__":
    import sys
    cat = sys.argv[1] if len(sys.argv) > 1 else "Poussins"
    main(cat)
