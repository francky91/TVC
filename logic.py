# logic.py

import json
from collections import defaultdict

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
        player1_key = f"{player1['nom']} {player1['prenom']}"
        player2_key = f"{player2['nom']} {player2['prenom']}"
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
        player1_key = f"{player1['nom']} {player1['prenom']}"
        player2_key = f"{player2['nom']} {player2['prenom']}"
            
        if (players_stats[player1_key]["wins"] == 3):
            players_stats[player1_key]["ratio_sets"] = 2
                          
    def sort_2players(relevant_players):
        tied_players = []
        first_player = list(relevant_players)[0]
        second_player = list(relevant_players)[1]
        sets_a, sets_b = matches_between_players_sets[first_player][second_player]
        if (sets_a > sets_b):
            tied_players.append(first_player)
            tied_players.append(second_player)
        else:
            tied_players.append(second_player)
            tied_players.append(first_player)
        return tied_players

    # Classement des joueurs
    players = list(players_stats.keys())
    # Trier les joueurs selon le nombre de victoires
    players.sort(key=lambda p: players_stats[p]["wins"], reverse=True)

    # Identifier les groupes d'égalité
    groups = defaultdict(list)
    for player in players:
        groups[players_stats[player]["wins"]].append(player)

    final_ranking = []
    for group in sorted(groups.keys(), reverse=True):
        if len(groups[group]) > 1:
            # Résolution des égalités dans le groupe
            tied_players = groups[group]
            relevant_players = set(tied_players)

            # Isoler les résultats entre joueurs concernés
            for player in tied_players:
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
                #tied_players.sort(key=lambda x: sorted(tied_players, key=lambda y: compare_players_2p(x, y, relevant_players)))
                tied_players = sort_2players(relevant_players)
            elif (len(groups[group]) == 3):
                tied_players.sort(
                    key=lambda x: (players_stats[x]["ratio_sets"], players_stats[x]["ratio_points"]),
                    reverse=True
                )
            #tied_players.sort(key=lambda x: sorted(tied_players, key=lambda y: compare_players(x, y, relevant_players)))
            final_ranking.extend(tied_players)
        else:
            final_ranking.extend(groups[group])
            #Mettre à jour le vainqueur dans le tableau des vainqueurs

    return final_ranking