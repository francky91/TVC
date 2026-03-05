from dataclasses import dataclass, field
from modules.Tableau import Tableau, TableauLevels
from modules.Poules import ListOfPoules
from modules.models import *
from modules.utils import read_filenames
import json

@dataclass
class Tournoi:
    category: str
    tour: int
    nb_tops: int
    nb_poules: int
    nb_joueurs: int
    tourInitial: Level
    
    tableauOk: Tableau = field(default_factory=lambda: Tableau(type="OK", tourInitial=tourInitial, tableauLevels=[]))
    tableauKo: Tableau = field(default_factory=lambda: Tableau(type="KO", tourInitial=tourInitial, tableauLevels=[]))
    tableauInterTops: Tableau = field(default_factory=lambda: Tableau(type="InterTops", tourInitial=Level(0), tableauLevels=[]))
    
    poules: ListOfPoules = field(default_factory=lambda: ListOfPoules())
    
    fichier_tableau: str = field(default_factory=str)
    
    def __init__(self, category: str, tour: int, nb_tops: int, nb_poules: int, nb_joueurs: int, tourInitial: Level):
        self.category = category
        self.tour = tour
        self.nb_tops = nb_tops
        self.nb_poules = nb_poules
        self.nb_joueurs = nb_joueurs
        self.tourInitial = tourInitial
        fichier_poule, fichier_tableau = read_filenames(self.category, self.tour)
        if nb_tops == 0:
            self.tableauOk = Tableau(type="OK", tourInitial=tourInitial, tableauLevels=[], fichier_tableau=fichier_tableau)
        else:
            self.tableauOk = Tableau(type="OK", tourInitial=Level(level=tourInitial.level*2), tableauLevels=[], fichier_tableau=fichier_tableau)
        self.tableauKo = Tableau(type="KO", tourInitial=tourInitial, tableauLevels=[], fichier_tableau=fichier_tableau)
        self.tableauInterTops = Tableau(type="InterTops", tourInitial=Level(0), tableauLevels=[], fichier_tableau=fichier_tableau)
        self.poules = ListOfPoules(fichier_poule)
        self.fichier_tableau = fichier_tableau
    
    def getPoule(self, poule_name):
        for poule in self.poules.poules:
            if f"{poule.type} {poule.num}" == poule_name:
                return poule
        return None
    
    def load_poules(self):
        self.poules.load_poules(True)
        self.poules_top = [p for p in self.poules.poules if p.type == "Top"]
        self.poules_standard = [p for p in self.poules.poules if p.type == "Poule"]
        self.nb_poules = len(self.poules_standard)
        self.nb_joueurs = sum(len(p.players) for p in self.poules_standard)
        self.nb_tops = len(self.poules_top)
        
        levelBase = 2 ** ((self.nb_poules - 1).bit_length())
        self.tableauKo.tourInitial = Level(level=2 ** ((self.nb_poules - 1).bit_length()))
        if self.nb_tops > 0:
            self.tableauOk.tourInitial = Level(level=self.tableauKo.tourInitial.level * 2) 
        else:
            self.tableauOk.tourInitial = Level(level=self.tableauKo.tourInitial.level)
        if self.nb_tops == 2:
            self.tableauInterTops.tourInitial = Level(level=1)
            tableauLevels = TableauLevels(level="1/1", matches=[])
            self.tableauInterTops.tableauLevels.append(tableauLevels)
        
        self.tourInitial.level = 2 ** ((self.nb_poules - 1).bit_length())
        
        ret = self.tableauOk.load_from_file()
        if ret:
            ret = self.tableauKo.load_from_file()
            if self.nb_tops == 2:
                ret = self.tableauInterTops.load_from_file()
        else:
            self.tableauOk.init_tableau_with_absent_players(self.nb_poules, self.nb_tops)
            self.tableauKo.init_tableau_with_absent_players(self.nb_poules, self.nb_tops, self.poules.poules)
        
    def save_poules(self):
        self.poules.save_poules()
    
    def getTourInitial(self, nb_tops=0) -> Level:
        if nb_tops==0:
            return Level(self.tourInitial.level)
        else:
            i= Level(self.tourInitial.level *2)
            return i
        
    def save_tableaux(self):
        data = {}
        data["category"] = self.category
        data["round"] = self.tour
        data["tourInitial"] = self.tourInitial.level
        data["nbTops"] = self.nb_tops
        data["nbPoules"] = self.nb_poules
        
        ordered_data = {}
    
        header_keys = ["category", "round", "tourInitial", "nbTops", "nbPoules"]
        for key in header_keys:
            if key in data:
                ordered_data[key] = data[key]
                
        ordered_data["Tableau OK"] = self.tableauOk.get_data_into_raw()
        ordered_data["Tableau KO"] = self.tableauKo.get_data_into_raw()
        if self.nb_tops == 2:
            ordered_data["InterTops"] = self.tableauInterTops.get_data_into_raw()

        with open(self.fichier_tableau, "w", encoding="utf-8") as f:
            json.dump(ordered_data, f, ensure_ascii=False, indent=4)    
