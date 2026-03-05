import win32print
import win32ui
from modules.models import Player, Match, Level

def init_printer():
        # --- Impression Windows ---
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        dc = win32ui.CreateDC()
        dc.CreatePrinterDC(printer_name)
        dc.StartDoc(f"impression Feuilles de match")
        return hprinter, dc
        
def close_printer(dc, hprinter):
        dc.EndDoc()
        dc.DeleteDC()
        win32print.ClosePrinter(hprinter)
        
def print_match(chk_print_vars, player1, player2, table_name, category, level):
        """Imprime les détails des matchs cochés et décoche toutes les cases chk_print."""
        # Récupérer les cases cochées
        checked_matches = [
         (level, match_index)
            for (level, match_index), var in chk_print_vars.items()
            if var.get()
        ]

        hprinter, dc = init_printer()
        dc.StartPage()
        line = 100
        
        checked_count = len(checked_matches)
        
        # Si une seule case est cochée, imprimer ce match
        if checked_count == 1 or checked_count == 0:
            print_match_details_direct(line, dc, player1, player2, table_name, category, level)
            #self.generate_pdf_with_table_pdf(player1, player2, table_name, category, level)

        # Si plusieurs cases sont cochées, afficher tous les matchs
        else:
            matches = []
            for level, match_index in checked_matches:
                match = self.tableauOK.get(level, {}).get(str(match_index), {})
                if not match:
                    match = self.tableauKO.get(level, {}).get(str(match_index), {})

                player1 = match.get("joueur1", "---")
                player2 = match.get("joueur2", "---")
                matches.append((player1, player2, level))

                print(f"Match à imprimer: {player1} vs {player2} Level: {level}")
                line = self.print_match_details_direct(line, dc, player1, player2, table_name, category, level)
                
                if line > 6000:
                    dc.EndPage()
                    dc.StartPage()
                    line=100
                else:
                    line += self.lh * 2  # Espace entre les matchs
        close_printer(dc, hprinter)
        dc.EndPage()   
        
def print_match_details_direct(self, line, dc, player1, player2, table_name, category, level):
        """Imprime un match dans un format tableau lisible (comme dans l'image)."""
        import re

        # Récupérer dossards, nom, prénom, club dans les structures tableau
        def extract_infos(player_string):
            # Format attendu : "Nom Prénom Club" OU "Nom Prénom"
            parts = player_string.split()
            nom = parts[0] if len(parts) > 0 else ""
            prenom = parts[1] if len(parts) > 1 else ""
            club = parts[2] if len(parts) > 2 else ""
            return nom, prenom, club

        nom1, prenom1, club1 = extract_infos(player1)
        nom2, prenom2, club2 = extract_infos(player2)
        doss1 =self.dossards.get(player1, "")
        doss2 =self.dossards.get(player2, "")
        if doss1 == "Unknown":
            doss1 = ""
        if doss2 == "Unknown":
            doss2 = ""
    
        string_2_players = f"{player1} {player2}"
        level = self.levelMatches.get(string_2_players)

        x = 100
        y = line

        # Titre tableau
        dc.TextOut(x, y, f"Tableau {table_name} - {level} - {category}                                 TVC - Tour {self.round_number}")
        y += self.lh * 3

        # En-têtes

        header = f"{'Dossard':<4}   {'Nom':<15}   {'Prénom':<15}   {'Club':<7}1    2    3    4    5"
        #header = "Dossard:<5 Nom:<15 Prénom:<15 Club:<6 Set1   Set2   Set3   Set4   Set5"
        
        dc.TextOut(x, y, header)
        y += self.lh
        
        dc.TextOut(x, y, f"______________________________________________________________________________")
        y += self.lh

        # Joueur 1
        line1 = f"|{doss1:<4} | {nom1:<15} | {prenom1:<15} | {club1:<7} | {' ':<2} | {' ':<2} | {' ':<2} | {' ':<2} | {' ':<2} |"
        dc.TextOut(x, y, line1)
        y += self.lh
        
        dc.TextOut(x, y, f"______________________________________________________________________________")
        y += self.lh

        # Joueur 2
        line2 = f"|{doss2:<4} | {nom2:<15} | {prenom2:<15} | {club2:<7} | {' ':<2} | {' ':<2} | {' ':<2} | {' ':<2} | {' ':<2} |"
        dc.TextOut(x, y, line2)
        y += self.lh
        
        dc.TextOut(x, y, f"______________________________________________________________________________")
        y += self.lh

        return y