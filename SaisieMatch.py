import tkinter as tk
from tkinter import messagebox

def validate_input_set(action, value_if_allowed, results_modified=None):
    """
    Valide les entrées des sets (valeurs entre -30 et 30, avec possibilité de -).
    
    :param action: Type d'action (1 pour insertion de texte).
    :param value_if_allowed: La valeur après tentative de modification.
    :param results_modified: Référence à un booléen indiquant si les résultats ont été modifiés.
    :return: True si la valeur est valide, sinon False.
    """
    if action != '1':  # 1 correspond à l'insertion de texte
        return True
    if value_if_allowed == '':
        return True
    if value_if_allowed == '-':  # Autorise uniquement le signe '-' seul
        return True
    try:
        value = int(value_if_allowed)
        if results_modified is not None:
            results_modified[0] = True  # Mettre à jour si c'est un objet mutable (ex : liste)
        return -30 <= value <= 30
    except ValueError:
        return False
    
def update_set_visibility(mode, entries, max_sets=5):
    """
    Met à jour la visibilité des champs d'entrée des sets selon le mode (2 ou 3 sets).

    Args:
        mode (str): Le mode choisi, "2 sets" ou "3 sets".
        entries (list): Liste des champs d'entrée (tk.Entry ou ttk.Entry).
        max_sets (int): Le nombre maximum de sets (par défaut 5).
    """
    desired_num_sets = 3 if mode == "2 sets" else max_sets

    for i, entry in enumerate(entries):
        if i >= desired_num_sets:
            entry.pack_forget()  # Cache les champs excédentaires
            entry.configure(state="disabled")  # Optionnel pour désactiver
        else:
            entry.pack(side="left")  # Affiche les champs nécessaires
            entry.configure(state="normal")  # Optionnel pour activer
            
def clear_set_data(result_entries):
    """
    Efface les données courantes des sets.

    Args:
        result_entries (list): Liste contenant les champs des sets à réinitialiser.
    """
    for entries in result_entries:
        for entry in entries:
            entry.delete(0, tk.END)
            
def handle_mode_change(current_mode, new_mode, result_entries, results_modified):
    """
    Gère le changement de mode entre 2 et 3 sets, avec confirmation si nécessaire.

    Args:
        current_mode (str): Le mode actuel ("2 sets" ou "3 sets").
        new_mode (str): Le nouveau mode souhaité ("2 sets" ou "3 sets").
        result_entries (list): Liste des ensembles de champs d'entrée à mettre à jour.
        results_modified (bool): Indique si des résultats ont été modifiés.
        confirmation_message (str): Message de confirmation si des modifications non sauvegardées existent.

    Returns:
        bool: True si le changement de mode est accepté, False sinon.
    """
    if results_modified:
        response = messagebox.askyesno("Changement de mode",
            "Les données actuelles n'ont pas été sauvegardées. Voulez-vous continuer et effacer les données ?")
        if not response:
            return False  # Annule le changement

    for entries in result_entries:
        clear_set_data(result_entries)
        update_set_visibility(new_mode, entries)

    return True