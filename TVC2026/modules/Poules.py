from dataclasses import dataclass, asdict
import json
import re
from modules.models import *
from modules.utils import charger_config_json
from modules.debug import debug_print

@dataclass
class Poule:
    type: str
    num: int
    players: List[Player]
    matches: List[Match]
    classement: List[Player]

@dataclass
class ListOfPoules:
    poules: List[Poule]
    fichier_poule: Optional[str] = ""
    
    def __init__(self, fichier_poule):
        self.fichier_poule = fichier_poule
        debug_print("FICHIER_POULE:", fichier_poule)
        
    def get_poule_for_name(self, poule_name):
        for p in self.poules:
            print ("p", p)
            if f"{p.type} {p.num}" == poule_name:
                return p
        return None
        
    def get_poules_std_labels(self):
        return [f"{p.type} {p.num}" for p in self.poules if p.type == "Poule"]
    
    def get_poules_top_labels(self):
        return [f"{p.type} {p.num}" for p in self.poules if p.type == "Top"]
        
    def save_poules(self, poule_name):
        directory = charger_config_json("config.ini")
        json_file = os.path.join(directory, self.fichier_poule)
        debug_print("Fichier poules:", json_file)
    
        try:
            if os.path.exists(self.fichier_poule):
                with open(self.fichier_poule, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"poules": {}}
                
            poule_obj = self.get_poule_for_name(poule_name)
            debug_print("poule_obj", poule_obj)

            # 2. Préparer la clé de la poule (ex: "Top 1")
            #poule_key = f"{poule_obj.type} {poule_obj.num}"
        
            # 3. Convertir l'objet en dictionnaire
            # On nettoie un peu pour correspondre exactement à votre format JSON
            p_dict = asdict(poule_obj)
        
            # Votre JSON utilise la clé "joueurs" au pluriel, asdict utilise le nom du champ
            # Si votre champ dans la dataclass est "players", on le renomme pour le JSON
            formatted_poule = {
                "joueurs": p_dict.get("players", []),
                "matches": p_dict.get("matches", []),
                "classement": p_dict.get("classement", [])
            }

            # 4. Mettre à jour uniquement cette poule
            data["poules"][poule_name] = formatted_poule

            # 5. Sauvegarder
            with open(self.fichier_poule, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            debug_print(f"Succès : Poule '{poule_name}' mise à jour dans {json_file}")
            return True
        except Exception as e:
            debug_print(f"Erreur lors de la sauvegarde de l'objet Poule : {e}")
            return False
    
    def load_poules(self, withMatches=False):
        directory = charger_config_json("config.ini")
        json_file = os.path.join(directory, self.fichier_poule)
        debug_print("Fichier poules:", json_file)
    
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            debug_print(f"Fichier non trouvé : {json_file}")
            return -1
        
        poules_raw = data.get("poules", {})
        self.poules = []

        for name, content in poules_raw.items():
            # --- Analyse du nom de la poule (Top x ou Poule x) ---
            poule_type = ""
            poule_num = ""
        
            match_top = re.match(r"Top\s+(\d+)", name, re.IGNORECASE)
            match_poule = re.match(r"Poule\s+(\d+)", name, re.IGNORECASE)
        
            if match_top:
                poule_type = "Top"
                poule_num = match_top.group(1)
            elif match_poule:
                poule_type = "Poule"
                poule_num = match_poule.group(1)

            # --- Conversion des joueurs ---
            joueurs_list = []
            for j in content.get("joueurs", []):
                joueurs_list.append(Player(
                    nom=j.get("nom", ""),
                    prenom=j.get("prenom", ""),
                    club=j.get("club", ""),
                    dossard=str(j.get("dossard", ""))
                ))
        
            # --- Conversion des matches ---
            matches_list = []
            if (withMatches):
                for m in content.get("matches", []):
                    p1_d = m.get("player1", {})
                    p2_d = m.get("player2", {})
                    winner_d = m.get("winner", None)
            
                    p1 = Player(nom=p1_d.get("nom",""), prenom=p1_d.get("prenom",""), 
                        club=p1_d.get("club",""), dossard=str(p1_d.get("dossard","")))
                    p2 = Player(nom=p2_d.get("nom",""), prenom=p2_d.get("prenom",""), 
                        club=p2_d.get("club",""), dossard=str(p2_d.get("dossard","")))
                    if winner_d:
                        print("winner:", winner_d)
                        winner = Player(nom=winner_d.get("nom",""), prenom=winner_d.get("prenom",""), 
                            club=winner_d.get("club",""), dossard=str(winner_d.get("dossard","")))
                    else:
                        winner = None

                    matches_list.append(Match(
                        num=0,
                        player1=p1,
                        player2=p2,
                        sets=m.get("sets", []),
                        idxPlayer1=0,
                        idxPlayer2=0,
                        winner=winner # Logique à définir si besoin de retrouver l'objet Player gagnant
                    ))

            poule_obj = Poule(
                type=poule_type,
                num=poule_num,
                players=joueurs_list,
                matches=matches_list,
                classement=content.get("classement", [])
            )
            # Ajout des propriétés demandées
            self.poules.append(poule_obj)
        
        debug_print("POULES:", self.poules)