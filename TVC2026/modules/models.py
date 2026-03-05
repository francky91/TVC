from dataclasses import dataclass, field
from typing import List, Optional
from modules.bracket import construire_bracket
from modules.debug import *

LABEL_TABLEAU_OK = "Tableau OK"
LABEL_TABLEAU_KO = "Tableau KO"
LABEL_TOURNOI_OK = "Tournoi OK"
LABEL_TOURNOI_KO = "Tournoi KO"
LABEL_TABLEAU_INTERTOPS = "InterTops"
EMPTY_NAME = "---"
DOSSARD_NONE = "Unknown"

@dataclass
class Level:
    level: int
    
    @property
    def string(self) -> str:
        return f"1/{self.level}"
    
    def levelDown(self) -> int:
        new_val = self.level
        if new_val == 1:
            new_val = 0
        elif new_val > 1:
            new_val = int(new_val / 2)
        return Level(level=new_val)
      
@dataclass
class SelectedCheckBox:
    level: str
    matchNum:int
    status: bool = False
    
@dataclass(frozen=True)
class Player:
    nom: str
    prenom: str
    club: str
    dossard: str

    @property
    def key(self) -> str:
        return f"{self.nom} {self.prenom} {self.club}"
    @property
    def isEmpty(self) -> bool:
        return self.nom == EMPTY_NAME

@dataclass
class Match:
    num: int
    player1: Player
    player2: Player
    sets: List[str]
    idxPlayer1: Optional[int]
    idxPlayer2: Optional[int]
    checkbox_state: Optional[bool] = None
    print_state: Optional[bool] = None
    winner: Optional[Player] = None
    
@dataclass
class MatchTableau:
    num: int
    match: Match



    

          
