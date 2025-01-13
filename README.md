# TVC
Fichiers pour le logiciel du TVC

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
