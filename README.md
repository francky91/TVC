# TVC
Fichiers pour le logiciel du TVC

Le 12/02/2025:
Ajout tvc-V16
Ajout General-V1.4 avec resultats-poules-V2.7, Tournoi-V1.5 et nouveau utils.py

Evolutions:
tvc-V16:
- Mise à jour dans le fichier Word des bonnes oppositions
- Ajout ligne totale
- Aggrandissement de la derniere ligne (du coup seulement 4 poules par page au lieu de 6)
- Prise en compte des dossards dans le json

General-V1.4:
- Affichage des tours uniquement connus (ceux dont il existe un json)

Saisie-resultats-poules:
- Plein, je sais plus lesquels 🙂

Saisie-Tournoi:
entre autres:
- Ajout du dossard sous forme de tooltip
- Ajout au titre: Tournoi OK|KO <Categorie> Tour<Tour>
- Ajout en entete du table le niveau (1/16, 1/8, ...)
- Quand on saisie un resultat il est tout de suite mis dans le tableau (contrairement à avant ou il fallait appuyer sur Tournoi OK)
- Le bouton OK sert maintenant à recharger le fichier json: comme les applis poules et tableau peuvent fonctionner ensemble, il se peut que toutes les poules ne soient pas encore toutes saisies. Il fallait donc relance l'appli Tableau quand une nouvelle poule etait entrée 

Le 24/01/2025
Ajout General-V1.3 avec resultats-poules-V2.6, Tournoi-V1.4 et config.ini
ainsi que les modules SaisieMatch, json_access, utils, config, logic

Le fichier config.ini permet de définir
[Paths]
directory = C:\\Users\\franck\\TVC\\
input_file = TVC2425.xlsx  -> Nom fichier TVC
directoryJson = C:\\Users\\franck\\TVC\\Json  -> Rep. JSON
directoryExcel = C:\\Users\\franck\\TVC\\Excel -> Rep. Excel (fichier TVC)
directoryWord = C:\\Users\\franck\\TVC\\Word -> Rep. Poules

[Versions]
TableauPy = Saisie-Tournoi-V1.4.py
PoulesPy = saisie-resultats-poules-V2.6.py

[TopsDefaut]
Poussins = 2
Benjamins = 2
Minimes = 2
Cadets-Juniors = 2
Feminines = 0

Le 17/01/2024

resultats-poules-V2.5, Tournoi-V1.3 et config.ini

Le 15/01/2025

Ajout General-V1.2 avec resultats-poules-V2.4, Tournoi-V1.2 et config.ini


TVC.py
11/01/2025:
  Changement ordre de rencontres en poules (1-4, 2-3, 1-3, 2-4, 1-2, 3-4)
  Ajout d'un fichier config.ini, ou sont renseignés le path et le fichier excel.
  Ne pas oublier d'ajouter aussi le fichier utils.py
  Ajout du nombre de tops par défaut par catgegorie s'il n'est pas renseigné dans la ligne de commande 
    (pour avoir par défaut 0 tops pour les féminines)
08/01/2025:
  Ajout tvc-V11.py
    Principales modifications:
      - Ajout de la catégorie dans les feuilles de match
      - Reconstruction totale de l'algorithme de gestion de conflit des clubs. Préalablement, il y avait 2 phases:
          . Placement en suivant le serpent
          . gerer les conflits
          En V11, tout est fait en une phase
    Tests faits:
      - Test fait sur TVC2223 Tour 4 sur les 5 categories:
        Vérification nombre de joueurs OK 
        Vérification pas plus d'1 club par pourl (sauf si nécessaire), mais certainement à revérifier
        Vérification les 1ers de poule restent présents

07/01/2025:
    Ajout V10

Saisie-Resultats-Poules.py
13/01/2025:
  Ajout V2.3. Est lancé par General.py
07/01/2025:
   Ajout

Saisie-Tournoi.py
13/01/2025:
  Ajout V1. Est lancé par General.py
07/01/2025!
    Ajout

General.py
13/01/2025:
  Non instancié par version. Est testé avec 13/01/2025 V2.3 et Saisie-Tournoi V1
07/01/2025: 
    Ajout
