# logic.py

import json
from collections import defaultdict
from modules.models import Player, Match
from modules.Poules import Poule

'''
def calculate_ranking_without_scores(result_entries):
    """
    Calcule le classement des joueurs uniquement via les 'radio buttons' 
    (winner_var) contenus dans result_entries.

    Renvoie :
      - [] si on ne peut pas établir de classement (pas assez de vainqueurs cochés 
        OU égalité pour la première place).
      - Une liste de noms de joueurs (ordre décroissant de victoires) 
        si un classement est établi sans ex æquo en tête.
    """
    if not result_entries:
        return []

    # 1) Détermine le nombre de matches attendus (poules de 3 ou 4 joueurs)
    required_matches = 6 if len(result_entries) == 6 else 3

    # 2) Préparer un dict pour compter les victoires par joueur
    victory_counts = {}

    completed_matches = 0
    for (entries, p1, p2, victory_label, winner_var, rd_p1, rd_p2) in result_entries:
        # Construire 2 clés uniques
        key1 = f"{p1['nom']} {p1['prenom']} {p1['club']}"
        key2 = f"{p2['nom']} {p2['prenom']} {p2['club']}"

        # Initialiser à 0 si non existant
        if key1 not in victory_counts:
            victory_counts[key1] = 0
        if key2 not in victory_counts:
            victory_counts[key2] = 0

        # Lire la sélection du radio
        winner = winner_var.get()  # "player1", "player2", ou ""

        if winner == "player1":
            victory_counts[key1] += 1
            completed_matches += 1
        elif winner == "player2":
            victory_counts[key2] += 1
            completed_matches += 1
        # sinon match pas complété => on ne fait rien

    # 3) Vérifier si on a tous les matches complétés
    if completed_matches < required_matches:
        # Si tous les vainqueurs ne sont pas renseignés, on renvoie un classement vide
        return []

    # 4) Trier les joueurs par nb de victoires (ordre décroissant)
    sorted_players = sorted(victory_counts.items(), key=lambda x: x[1], reverse=True)
    # => sorted_players = [( "Nom complet", nbVictoires ), ...]

    # 5) Vérifier si le premier et le deuxième ont le même nombre de victoires
    #    => si oui, on ne parvient pas à déterminer un vainqueur unique => []
    if len(sorted_players) > 1 and sorted_players[0][1] == sorted_players[1][1]:
        # Cas d'égalité en tête => pas de vainqueur clair
        return []

    # 6) Retourner la liste des noms par ordre de victoires décroissantes
    return [elt[0] for elt in sorted_players]

def calculate_ranking(player_scores, result_entries):
    """Calcule le classement des joueurs en suivant les règles spécifiées."""
    if not result_entries:
        return

    # Vérifier que tous les matchs ont été saisis
    required_matches = 6 if len(result_entries) == 6 else 3
    completed_matches = 0

    for nom, pts in player_scores.items():
        completed_matches += pts

    if completed_matches < required_matches:
        return []

    wins = [pts for pts in player_scores.values()]
    if len(wins) == len(set(wins)):
        sorted_players = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)       
        resultat = [elt[0] for elt in sorted_players]
        return resultat
        
    # Collecte des données des matchs
    players_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "sets_won": 0, "sets_lost": 0, "points_won": 0, "points_lost": 0, "ratio_sets": 0, "ratio_points": 0})
    matches_between_players_sets = defaultdict(dict)
    matches_between_players_points = defaultdict(dict)

    for entries, player1, player2, victory_label in result_entries:
        player1_key = f"{player1['nom']} {player1['prenom']} {player1['club']}"
        player2_key = f"{player2['nom']} {player2['prenom']} {player2['club']}"
        sets_player1 = 0
        sets_player2 = 0
        points_player1 = 0
        points_player2 = 0

        # Analyse des résultats des sets
        for set_result in entries:
            try:
                score = set_result.get()
                if score.startswith("-"):
                    p1 = abs(int(score))
                    p2 = 11 if p1 < 10 else p1 + 2
                    points_player1 += p1
                    points_player2 += p2
                    sets_player2 += 1
                else:
                    p2 = int(score)
                    p1 = 11 if p2 < 10 else p2 + 2
                    points_player1 += p1
                    points_player2 += p2
                    sets_player1 += 1
            except ValueError:
                continue  # Ignore les entrées invalides

        # Mise à jour des statistiques
        if sets_player1 > sets_player2:
            players_stats[player1_key]["wins"] += 1
            players_stats[player2_key]["losses"] += 1
        elif sets_player2 > sets_player1:
            players_stats[player2_key]["wins"] += 1
            players_stats[player1_key]["losses"] += 1

        players_stats[player1_key]["sets_won"] += sets_player1
        players_stats[player1_key]["sets_lost"] += sets_player2
        players_stats[player1_key]["points_won"] += points_player1
        players_stats[player1_key]["points_lost"] += points_player2

        players_stats[player2_key]["sets_won"] += sets_player2
        players_stats[player2_key]["sets_lost"] += sets_player1
        players_stats[player2_key]["points_won"] += points_player2
        players_stats[player2_key]["points_lost"] += points_player1

        # Enregistrer les résultats entre joueurs
        matches_between_players_sets[player1_key][player2_key] = (sets_player1, sets_player2)
        matches_between_players_sets[player2_key][player1_key] = (sets_player2, sets_player1)
        matches_between_players_points[player1_key][player2_key] = (points_player1, points_player2)
        matches_between_players_points[player2_key][player1_key] = (points_player2, points_player1)
        
    for entries, player1, player2, victory_label in result_entries:
        player1_key = f"{player1['nom']} {player1['prenom']} {player1['club']}"
        player2_key = f"{player2['nom']} {player2['prenom']} {player1['club']}"
            
        if (players_stats[player1_key]["wins"] == 3):
            players_stats[player1_key]["ratio_sets"] = 2
                          
    def sort_2players(relevant_players):
        p1, p2 = list(relevant_players)
        stats_p1 = players_stats[p1]
        stats_p2 = players_stats[p2]

        rp1 = stats_p1["ratio_points"]
        rp2 = stats_p2["ratio_points"]

        if rp1 > rp2:
            return [p1, p2]
        elif rp1 < rp2:
            return [p2, p1]
        else:
            # Si ratio_points identiques, on regarde la confrontation directe
            sets_p1, sets_p2 = matches_between_players_sets[p1][p2]
            if sets_p1 > sets_p2:
                return [p1, p2]
            else:
                return [p2, p1]
    
    # Classement des joueurs
    players = list(players_stats.keys())
    # Trier les joueurs selon le nombre de victoires
    players.sort(key=lambda p: players_stats[p]["wins"], reverse=True)

    # Identifier les groupes d'égalité
    groups = defaultdict(list)
    for player in players:
        groups[players_stats[player]["wins"]].append(player)
        print("---PLAYER:", player)

    final_ranking = []
    idx=1
    for group in sorted(groups.keys(), reverse=True):
        if len(groups[group]) > 1:
            # Résolution des égalités dans le groupe
            tied_players = groups[group]
            relevant_players = set(tied_players)
            print("RELEVANT PLAYERS: ", relevant_players, ",len:", len(groups[group]), "idx:", idx)
            idx += 1

            # Isoler les résultats entre joueurs concernés
            for player in tied_players:
                print("PLAYER:", player)
                players_stats[player]["sets_won"] = sum(matches_between_players_sets[player][opponent][0] for opponent in relevant_players if opponent != player)
                players_stats[player]["sets_lost"] = sum(matches_between_players_sets[player][opponent][1] for opponent in relevant_players if opponent != player)

                players_stats[player]["points_won"] = sum(matches_between_players_points[player][opponent][0] for opponent in relevant_players if opponent != player)
                players_stats[player]["points_lost"] = sum(matches_between_players_points[player][opponent][1] for opponent in relevant_players if opponent != player)
                if (players_stats[player]["sets_lost"] > 0):
                    players_stats[player]["ratio_sets"] = players_stats[player]["sets_won"] / players_stats[player]["sets_lost"]
                else:
                    players_stats[player]["ratio_sets"] = players_stats[player]["sets_won"]
                if (players_stats[player]["points_lost"] > 0):
                    players_stats[player]["ratio_points"] = players_stats[player]["points_won"] / players_stats[player]["points_lost"]
                else:
                    players_stats[player]["ratio_points"] = players_stats[player]["points_won"]
                print ("player:", player, ",points_won:", players_stats[player]["points_won"], ",points_lost:", players_stats[player]["points_lost"], "ratio:", players_stats[player]["ratio_points"])
                print ("player:", player, ",sets_won", players_stats[player]["sets_won"], ",sets_lost", players_stats[player]["sets_lost"], ",ratio_sets:", players_stats[player]["ratio_sets"], ",ratio_points:", players_stats[player]["ratio_points"] )
            
               
            if (len(groups[group]) == 2): 
                tied_players = sort_2players(relevant_players)
            elif (len(groups[group]) == 3):
                tied_players.sort(
                    key=lambda x: (players_stats[x]["ratio_sets"], players_stats[x]["ratio_points"]),
                    reverse=True
                )
            #tied_players.sort(key=lambda x: sorted(tied_players, key=lambda y: compare_players(x, y, relevant_players)))
            final_ranking.extend(tied_players)
            print("FINAL RANKING: ", final_ranking)
        else:
            final_ranking.extend(groups[group])
            #Mettre à jour le vainqueur dans le tableau des vainqueurs
    return final_ranking
'''

# logic.py


def calculate_ranking_without_scores(result_entries, players_list):
    """
    Calcule le classement uniquement via les objets Player.
    players_list: Liste des objets Player de la poule.
    """
    if not result_entries:
        return []

    # victory_counts utilise maintenant l'objet Player comme clé
    victory_counts = {p: 0 for p in players_list}

    for (entries, p1_obj, p2_obj, victory_label, winner_var, rd_p1, rd_p2) in result_entries:
        winner_idx = winner_var.get()
        if winner_idx == 1:
            victory_counts[p1_obj] += 1
        elif winner_idx == 2:
            victory_counts[p2_obj] += 1

    # Tri des objets Player par nombre de victoires (décroissant)
    sorted_players = sorted(victory_counts.keys(), key=lambda p: victory_counts[p], reverse=True)
    
    # Vérification d'égalité en tête pour la validité du classement
    if len(sorted_players) > 1:
        v1 = victory_counts[sorted_players[0]]
        v2 = victory_counts[sorted_players[1]]
        if v1 == v2:
            return []  # Égalité, classement non établi

    return sorted_players

def calculate_ranking(poule_obj):
    """
    Calcule le classement complet à partir de l'objet Poule.
    Retourne une List[Player].
    """
    players = poule_obj.players
    matches = poule_obj.matches
    
        # Vérifier que tous les matchs ont été saisis
    required_matches = 6 if len(players) == 4 else 3
    completed_matches = len(matches)
    print(f"Completed matches: {completed_matches}, Required matches: {required_matches}")
    
    if completed_matches < required_matches:
        return []
    
    # Statistiques par objet Player
    players_stats = {p: {
        "points": 0, "sets_won": 0, "sets_lost": 0, 
        "points_won": 0, "points_lost": 0, "matches_won": 0
    } for p in players}

    for m in matches:
        if not m.winner or not m.sets:
            continue
            
        p1, p2 = m.player1, m.player2
        
        # Attribution des points de match (3 pour victoire, 1 pour défaite)
        if m.winner == p1:
            players_stats[p1]["points"] += 3
            players_stats[p2]["points"] += 1
            players_stats[p1]["matches_won"] += 1
        else:
            players_stats[p2]["points"] += 3
            players_stats[p1]["points"] += 1
            players_stats[p2]["matches_won"] += 1

        # Calcul des sets et points (selon votre format de sets ['11-5', '8-11', ...])
        for s in m.sets:
            if '-' in s:
                try:
                    s1, s2 = map(int, s.split('-'))
                    players_stats[p1]["points_won"] += s1
                    players_stats[p1]["points_lost"] += s2
                    players_stats[p2]["points_won"] += s2
                    players_stats[p2]["points_lost"] += s1
                    if s1 > s2:
                        players_stats[p1]["sets_won"] += 1
                        players_stats[p2]["sets_lost"] += 1
                    else:
                        players_stats[p2]["sets_won"] += 1
                        players_stats[p1]["sets_lost"] += 1
                except: continue

    # Calcul des ratios pour le départage
    for p in players:
        stats = players_stats[p]
        stats["ratio_sets"] = stats["sets_won"] / max(1, stats["sets_lost"])
        stats["ratio_points"] = stats["points_won"] / max(1, stats["points_lost"])

    # Tri final : Points > Matches gagnés > Ratio Sets > Ratio Points
    ranked_players = sorted(players, key=lambda p: (
        players_stats[p]["points"],
        players_stats[p]["matches_won"],
        players_stats[p]["ratio_sets"],
        players_stats[p]["ratio_points"]
    ), reverse=True)

    return ranked_players