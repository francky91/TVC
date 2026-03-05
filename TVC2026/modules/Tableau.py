from dataclasses import dataclass, field, asdict
from modules.models import *
from modules.debug import *
import json
from modules.bracket import charger_config_json
import re

@dataclass
class TableauLevels:
    level: str
    matches: List[Match]
    
    def get_match_pos(self, num):
        return next((m for m in self.matches if m.num == num), None)
    
    def set_match_pos_with_idxPlayer(self, idx, player):
        
        #for match in self.matches:
        match = next((m for m in self.matches if m.idxPlayer1 == idx), None)
        if match != None:
            match.player1 = player

        else:
            match = next((m for m in self.matches if m.idxPlayer2 == idx), None)
            if match != None:
                match.player2 = player
            else:
                return None
            
@dataclass
class Tableau:
    type: str
    tourInitial: Level
    tableauLevels: List[TableauLevels]
    fichier_tableau: Optional[str] = ""
    
    selectedPrint: List[SelectedCheckBox] = field(default_factory=list)
    selectedMatch: List[SelectedCheckBox] = field(default_factory=list)
        
    def __init__(self, type, tourInitial, tableauLevels, fichier_tableau):
        self.type = type
        self.tourInitial = tourInitial
        self.tableauLevels = tableauLevels
        self.fichier_tableau = fichier_tableau
        self.selectedPrint = []
        self.selectedMatch = []
        

    def from_string(self, s) -> 'Level':
        """
        Crée un objet Level à partir d'une chaîne.
        Exemples acceptés : "1/8", "1 / 8", "8", None (lève ValueError).
        """
        if isinstance(s, Level):
            return s
        if s is None:
            raise ValueError("Chaîne de niveau nulle")
        s_clean = str(s).strip()
        # Cherche un entier après un '/' (ex: "1/8") sinon prend le premier entier trouvé
        m = re.search(r"/\s*(\d+)", s_clean)
        if m:
            val = int(m.group(1))
            return Level(level=val)
        m2 = re.search(r"(\d+)", s_clean)
        if m2:
            return Level(level=int(m2.group(1)))
        raise ValueError(f"Impossible de parser le niveau depuis la chaîne: '{s}'")
      
    def get_level_pos(self, level=""):
        if isinstance(level, str) and level != "":
            level = self.from_string(level)
        if (self.type == "InterTops"):
            return next((t for t in self.tableauLevels if f"{t.level}" == "1/1"), None)
        else:
            return next((t for t in self.tableauLevels if f"{t.level}" == level.string), None)    
        
    def get_level_tour_initial(self):
        return self.get_level_pos(self.tourInitial)
    
    
    def set_match_pos_with_idxPlayer(self, idx, player):
        tab = self.get_level_tour_initial()
        tab.set_match_pos_with_idxPlayer(idx, player)
        
    def update_tableau_for_2top(self, poule, final_ranking):
        if self.type != "InterTops":
            return
        
        level_pos = self.get_level_pos()
        if level_pos == None:
            self.tableauLevels.append(TableauLevels(level="1/1", matches=[]))
            level_pos = self.get_level_pos()
        for idx, player in enumerate(final_ranking):
            if level_pos.matches == []:
                if (poule == 1):
                    level_pos.matches = [Match(num=idx+1, player1=player, player2=None, sets=[], idxPlayer1=0, idxPlayer2=0, checkbox_state=False, winner=None)]
                elif (poule == 2):
                    match_pos.matches = [Match(num=idx+1, player1=None, player2=player, sets=[], idxPlayer1=0, idxPlayer2=0, checkbox_state=False, winner=None)]
            else:
                match_pos = level_pos.get_match_pos(idx+1)
                if (match_pos == None):
                    if (poule == 1):
                        level_pos.matches.append(Match(num=idx+1, player1=player, player2=None, sets=[], idxPlayer1=0, idxPlayer2=0, checkbox_state=False, winner=None))
                    elif (poule == 2):
                        level_pos.matches.append(Match(num=idx+1, player1=None, player2=player, sets=[], idxPlayer1=0, idxPlayer2=0, checkbox_state=False, winner=None))
                else:
                    if (poule == 1):
                        match_pos.player1 = player
                    else:
                        match_pos.player2 = player
        
    def update_tableau_for_1top(self, final_ranking):
        if self.type != "OK":
            return
        
        corr_top1 = { 1: 3, 2: 2, 3: 4, 4: 1}
        for idx, player in enumerate(final_ranking):
            index_table = str(corr_top1[idx+1])
            level_pos=self.get_level_pos(Level(level=4))
            
            if level_pos == None:
                self.tableauLevels.append(TableauLevels(level="1/4", matches=[]))
                level_pos=self.get_level_pos(Level(level=4))
                        
            match_pos=level_pos.get_match_pos(index_table)
            if match_pos == None:
                level_pos.matches.append(Match(index_table, player1=player, player2=None, sets=[], idxPlayer1=0, idxPlayer2=0, checkbox_state=False, winner=None))
            else:
                match_pos.player1 = player
    
    def save_tableau(self, header_name, category, tour, nb_tops, nb_poules, tourInitial):
        data = {
            "category": category,
            "round": tour,
            "tourInitial": tourInitial.level,
            "nbTops": nb_tops,
            "nbPoules": nb_poules,
            header_name: {
                level.level: [
                        {
                            "num": match.num,
                            "player1": {
                                "nom": match.player1.nom if match.player1 else None,
                                "prenom": match.player1.prenom if match.player1 else None,
                                "club": match.player1.club if match.player1 else None,
                                "dossard": match.player1.dossard if match.player1 else None
                            } if match.player1 else None,
                            "player2": {
                                "nom": match.player2.nom if match.player2 else None,
                                "prenom": match.player2.prenom if match.player2 else None,
                                "club": match.player2.club if match.player2 else None,
                                "dossard": match.player2.dossard if match.player2 else None
                            } if match.player2 else None,
                            "sets": match.sets,
                            "idxPlayer1": match.idxPlayer1,
                            "idxPlayer2": match.idxPlayer2,
                            "winner": match.winnerf
                        } for match in level.matches
                    ] for level in self.tableauLevels
                } 
            }

        with open(self.fichier_tableau, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_data_into_raw(self):
        level_data = {}
        for level in self.tableauLevels:
            matches_list = []
            for match in level.matches:
                # player1
                if match.player1:
                    p1 = {
                        "nom": match.player1.nom,
                        "prenom": match.player1.prenom,
                        "club": match.player1.club,
                        "dossard": match.player1.dossard
                    }
                else:
                    p1 = None

                # player2
                if match.player2:
                    p2 = {
                        "nom": match.player2.nom,
                        "prenom": match.player2.prenom,
                        "club": match.player2.club,
                        "dossard": match.player2.dossard
                    }
                else:
                    p2 = None

                # winner (peut être None, Player ou déjà sérialisé)
                winner = None
                if getattr(match, "winner", None) is not None:
                    w = match.winner
                    if isinstance(w, Player):
                        winner = {
                            "nom": w.nom,
                            "prenom": w.prenom,
                            "club": w.club,
                            "dossard": w.dossard
                        }
                    else:
                        # conserver la valeur telle quelle si ce n'est pas un Player
                        winner = w

                # Construire l'entrée du match
                match_entry = {
                    "num": match.num,
                    "player1": p1,
                    "player2": p2,
                    "sets": match.sets,
                    "idxPlayer1": match.idxPlayer1,
                    "idxPlayer2": match.idxPlayer2,
                    "winner": winner
                }

                # Ajouter checkbox_state seulement si True
                if getattr(match, "checkbox_state", False) is True:
                    match_entry["checkbox_state"] = True

                matches_list.append(match_entry)

            level_data[level.level] = matches_list
        return level_data


    def get_match_pos(self, num):
        """
        Retourne le match correspondant à num (accepte num int ou string).
        """
        try:
            num_int = int(num)
        except Exception:
            # fallback : comparaison directe si conversion impossible
            return next((m for m in self.matches if m.num == num), None)
        return next((m for m in self.matches if int(m.num) == num_int), None)
            
    def build_tableau_from_raw(self, tableau_raw):
        for level, content in tableau_raw.items():
            # level peut être "1/8" etc. on récupère un objet Level si besoin
            levelCls = self.from_string(level)

            # s'assurer que la liste existe
            if not self.tableauLevels:
                self.tableauLevels = []

            # chercher le niveau existant (TableauLevels) ou le créer
            tableauLevel = self.get_level_pos(levelCls)
            if tableauLevel is None:
                self.tableauLevels.append(TableauLevels(level=level, matches=[]))
                tableauLevel = self.get_level_pos(levelCls)

            # content peut être soit une liste de matches, soit un dict contenant "matches"
            if isinstance(content, dict):
                matches_json = content.get("matches", [])
            elif isinstance(content, list):
                matches_json = content
            else:
                matches_json = []

            for match_data in matches_json:
                # numéro du match (accepte string ou int)
                num_raw = match_data.get("num")
                try:
                    num = int(num_raw)
                except Exception:
                    # si tout échoue, on garde tel quel (mais on essaie d'utiliser int plus tard)
                    num = num_raw

                p1_d = match_data.get("player1")
                p2_d = match_data.get("player2")

                p1 = None
                p2 = None
                if p1_d is not None:
                    p1 = Player(
                        nom=p1_d.get("nom", ""),
                        prenom=p1_d.get("prenom", ""),
                        club=p1_d.get("club", ""),
                        dossard=str(p1_d.get("dossard", "")) if p1_d.get("dossard", "") is not None else ""
                    )
                if p2_d is not None:
                    p2 = Player(
                        nom=p2_d.get("nom", ""),
                        prenom=p2_d.get("prenom", ""),
                        club=p2_d.get("club", ""),
                        dossard=str(p2_d.get("dossard", "")) if p2_d.get("dossard", "") is not None else ""
                    )

                # sets peut être sous "sets" ou "score" suivant les fichiers
                sets = match_data.get("sets", match_data.get("score", []))
                idx1 = match_data.get("idxPlayer1", 0)
                idx2 = match_data.get("idxPlayer2", 0)
                winner = None
                winner_d = match_data.get("winner", None)
                if winner_d is not None:
                    winner = Player(
                        nom=winner_d.get("nom", ""),
                        prenom=winner_d.get("prenom", ""),
                        club=winner_d.get("club", ""),
                        dossard=str(winner_d.get("dossard", "")) if winner_d.get("dossard", "") is not None else ""
                    )

                # checkbox_state : ne toucher que si la clé existe dans le fichier
                checkbox_state = None
                if "checkbox_state" in match_data:
                    raw_cb = match_data.get("checkbox_state")
                    if isinstance(raw_cb, str):
                        raw_cb_l = raw_cb.strip().lower()
                        if raw_cb_l in ("true", "1", "yes", "y"):
                            checkbox_state = True
                        elif raw_cb_l in ("false", "0", "no", "n", "none", "null", ""):
                            checkbox_state = False
                        else:
                            # valeur inattendue -> considérer True si non vide
                            checkbox_state = True if raw_cb_l else False
                    elif isinstance(raw_cb, bool):
                        checkbox_state = raw_cb
                    elif raw_cb is None:
                        checkbox_state = None
                    else:
                        # nombre, etc.
                        checkbox_state = bool(raw_cb)

                new_match_obj = Match(
                    num=int(num) if isinstance(num, (int, str)) and str(num).isdigit() else num,
                    player1=p1,
                    player2=p2,
                    sets=sets,
                    idxPlayer1=idx1,
                    idxPlayer2=idx2,
                    checkbox_state=checkbox_state,
                    winner=winner
                )

                match_obj = tableauLevel.get_match_pos(num)
                if match_obj is None:
                    tableauLevel.matches.append(new_match_obj)
                else:
                    # mettre à jour les champs existants
                    match_obj.player1 = p1
                    match_obj.player2 = p2
                    match_obj.sets = sets
                    match_obj.idxPlayer1 = idx1
                    match_obj.idxPlayer2 = idx2
                    match_obj.winner = winner
                    # Mettre à jour checkbox_state seulement si la clé existe dans le JSON
                    if "checkbox_state" in match_data:
                        match_obj.checkbox_state = checkbox_state
                  
                  
    def load_from_file(self, nb_tops = 0):
        directory = charger_config_json()
        json_file = os.path.join(directory, self.fichier_tableau)
    
        try:
            with open(self.fichier_tableau, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            debug_print(f"Fichier non trouvé : {self.fichier_tableau}")
            return False 

        if self.type == "OK":
            header_name=LABEL_TABLEAU_OK
        elif self.type == "KO":
            header_name = LABEL_TABLEAU_KO
        elif self.type == "InterTops":
            header_name = LABEL_TABLEAU_INTERTOPS
            
        raw_data = data.get(header_name, {})
        if raw_data != {} :
            self.build_tableau_from_raw(raw_data)
        if self.type == "InterTops":
            if raw_data == {} and nb_tops == 2:
                self.tableauLevels.append(TableauLevels(level="1/1", matches=[]))

        return True
        
    def get_nb_tours(self):
        level_to_tours = {64: 7, 32: 6, 16: 5, 8: 4, 4: 3,2: 2}
        return level_to_tours.get(self.tourInitial.level, 1)
        
    def modifySelectedPrint(self, level, match, status):
        if status:
            new_checkbox = SelectedCheckBox(level=level, matchNum=match, status=status)
            self.selectedPrint.append(new_checkbox)
        else:
            self.selectedPrint = [checkbox for checkbox in self.selectedPrint if not (checkbox.level == level and checkbox.matchNum == match)]
        
    def modifySelectedMatch(self, level, match, status):
        level_pos = self.get_level_pos(level)
        if level_pos is None:
            debug_print("modifySelectedMatch: niveau introuvable", level)
            return

        # Essayer de convertir match en int pour la recherche
        try:
            match_num = int(match)
        except Exception:
            match_num = match

        match_obj = level_pos.get_match_pos(match_num)
        if match_obj is None:
            debug_print("modifySelectedMatch: match introuvable", match)
            return

        if status:
            match_obj.checkbox_state = True
        else:
            debug_print(f"modifySelectedMatch: status=False pour level={level_pos.level} match={match_num} -> aucune modification du checkbox_state")
        
    def init_holes_for_uncomplete_poules(self, nb_poules, poules, nb_tops):
        if self.tableauLevels == []:
            return
        for level in  self.tableauLevels:
            for match in level.matches:
                if match.player1 == None:
                    if match.idxPlayer1 > nb_poules:
                        poule_number = self.search_number_of_poule(match.idxPlayer1, nb_poules)  + nb_tops   
                        nb_players = len(poules[poule_number - 1].players)
                        if nb_players == 3:
                            match.player1 = Player(nom=EMPTY_NAME, prenom="", club="", dossard=DOSSARD_NONE)
                            
                if match.player2 == None:
                    if match.idxPlayer2 > nb_poules:
                        poule_number = self.search_number_of_poule(match.idxPlayer2, nb_poules) + nb_tops
                        nb_players = len(poules[poule_number - 1].players)
                        if nb_players == 3:
                            match.player2 = Player(nom=EMPTY_NAME, prenom="", club="", dossard=DOSSARD_NONE)
                            
    def init_tableau_with_absent_players(self, nb_poules, nb_tops, poules=None):
        if self.tableauLevels != []:
            return
        

        if self.type == "KO":
            nb_joueurs_max = self.tourInitial.level * 2
        elif self.type == "OK":
            if nb_tops == 0:
                nb_joueurs_max = self.tourInitial.level * 2
            else:
                nb_joueurs_max = self.tourInitial.level
        playersOnInitialTour = construire_bracket(nb_joueurs_max)

        self.tableauLevels = []
        
        matches = []
        for i in range(int(nb_joueurs_max / 2)):
                # Récupération des indices des joueurs pour le match
                idx1 = list(playersOnInitialTour[i * 2].keys())[0]
                idx2 = list(playersOnInitialTour[i * 2 + 1].keys())[0]

                # Initialisation des joueurs
                player1 = Player(nom=EMPTY_NAME, prenom="", club="", dossard="") if idx1 > nb_poules * 2 else None
                player2 = Player(nom=EMPTY_NAME, prenom="", club="", dossard="") if idx2 > nb_poules * 2 or idx2 == -1 else None

                # Création du match
                match = Match(
                    num=i + 1,
                    player1=player1,
                    player2=player2,
                    sets=[],
                    idxPlayer1=idx1,
                    idxPlayer2=idx2,
                    checkbox_state=None,
                    winner=None
                )
                matches.append(match)

            # Ajout des matches au niveau initial du tableau
        self.tableauLevels.append(TableauLevels(level=self.tourInitial.string, matches=matches))
        
        if poules != None:
            self.init_holes_for_uncomplete_poules(nb_poules, poules, nb_tops)
        
    def search_number_of_poule(self, idx, nb_poules):
        if nb_poules%2 == 1:
            return 2*nb_poules - idx + 1
        else:
            if (idx%2 == 0): # Poule paire               
                #return 2*nb_poules-current_poule + 2
                return  2*nb_poules - idx + 2
            else: # Poule impaire
                #return 2*nb_poules-current_poule
                return  2*nb_poules - idx
            
    def get_value_for_index(self, idx):
            index = self.search_number_of_poule(idx)
            return ""         
    
    def addPlayerInTab(self, tableau_pos, level, matchId, player):
        level_pos = self.get_level_pos(level)
        if level_pos == None:
            self.tableauLevels.append(TableauLevels(level=level.string, matches=[]))
            level_pos = self.get_level_pos(level)
                
        newMatchId =  int((int(matchId) + 1)/2)
        label_newMatchId= str(newMatchId)
            
        match_tableau = level_pos.get_match_pos(newMatchId)

        if match_tableau is None:
            nouveau_match = Match(
                    num=newMatchId,
                    player1=None, 
                    player2=None, 
                    sets=[], 
                    idxPlayer1=0, 
                    idxPlayer2=0
            )
            level_pos.matches.append(nouveau_match)

            match_tableau =level_pos.get_match_pos(newMatchId)
            
        if (matchId %2 == 1):
            match_tableau.player1 = player
        else:
            match_tableau.player2 = player
    
    def updateTableauWithHoles(self):
        currentNiveau = self.tourInitial
        found_holes = 2
        while (found_holes >= 1):
            label_ok = currentNiveau.string
            niveauDown = currentNiveau.levelDown()

            found_holes = 0
            tableau_level_obj = self.get_level_pos(currentNiveau)
            for match in tableau_level_obj.matches:
                if match.player1 != None and match.player1.isEmpty:
                    self.addPlayerInTab(tableau_level_obj, niveauDown, match.num, match.player2)
                    found_holes += 1
                elif  match.player2 != None and match.player2.isEmpty:
                    self.addPlayerInTab(tableau_level_obj, niveauDown, match.num, match.player1)
                    found_holes += 1

            currentNiveau = niveauDown              
                