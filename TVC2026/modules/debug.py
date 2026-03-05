import inspect
import os

def debug_print(*args):
    """
    Affiche le fichier, la fonction appelante et une suite de couples (message, variable).
    Usage: debug_print("Ma var", x, "Liste", ma_liste)
    """
    # 1. Récupérer les infos sur l'appelant
    # stack()[1] correspond à l'endroit où debug_print a été appelée
    caller_frame = inspect.stack()[1]
    filename = os.path.basename(caller_frame.filename)
    func_name = caller_frame.function
    line_no = caller_frame.lineno

    # 2. Construire l'en-tête du message
    header = f"[{filename} > {func_name}:{line_no}]"
    
    # 3. Formater les arguments par paires
    # zip(args[0::2], args[1::2]) permet de grouper (arg0, arg1), (arg2, arg3)...
    details = []
    for i in range(0, len(args), 2):
        label = args[i]
        # On vérifie s'il y a bien une valeur après le label
        value = args[i+1] if i+1 < len(args) else "???"
        details.append(f"{label}: {value}")

    # 4. Affichage final
    print(f"{header} {' | '.join(details)}")
    print ("----------------------------------------------------------------------------------------------")
    
def print_tableau_debug(tableau_obj):
    """
    Affiche le contenu d'un objet Tableau (ex: tableauOk)
    Affiche pour chaque niveau la liste des joueurs trouvés dans les matches.
    """
    if not tableau_obj or not tableau_obj.tableauLevels:
        print(f"--- Tableau {getattr(tableau_obj, 'type', 'Inconnu')} est vide ---")
        return

    print(f"\n{'='*60}")
    print(f"DEBUG TABLEAU : {tableau_obj.type}")
    print(f"{'='*60}")

    for lvl in tableau_obj.tableauLevels:
        print(f"\nNiveau : {lvl.level}")
        print("-" * 20)
        
        joueurs_trouves = []
        
        for match in lvl.matches:
            # On vérifie le joueur 1
            if match.player1 and not match.player1.isEmpty:
                p1_info = f"{match.player1.nom} {match.player1.prenom} (M{match.num}-P1)"
                joueurs_trouves.append(p1_info)
            
            # On vérifie le joueur 2
            if match.player2 and not match.player2.isEmpty:
                p2_info = f"{match.player2.nom} {match.player2.prenom} (M{match.num}-P2)"
                joueurs_trouves.append(p2_info)

        if joueurs_trouves:
            for j in joueurs_trouves:
                print(f"  [Match] {j}")
        else:
            print("  (Aucun joueur assigné pour ce niveau)")
    
    print(f"{'='*60}\n")