import tkinter as tk
from tkinter import ttk

def simulate_mac_ui():
    root = tk.Tk()
    root.title("Simulation Tournoi (Mac UI)")
    root.geometry("1000x600")

    canvas_frame = tk.Frame(root)
    canvas_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(canvas_frame, width=1000, height=600, bg="white")
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    start_x = 20
    start_y = 20
    longueur_rectangle = 120
    hauteur_rectangle = 40
    espace = 60

    matches = [
        ("Joueur 1", "Joueur 2"),
        ("Joueur 3", "Joueur 4"),
        ("Joueur 5", "Joueur 6"),
        ("Joueur 7", "Joueur 8"),
    ]

    for idx, (joueur1, joueur2) in enumerate(matches):
        y_position = start_y + idx * (hauteur_rectangle + espace)

        canvas.create_rectangle(start_x, y_position, start_x + longueur_rectangle, y_position + hauteur_rectangle, outline="black", width=1)
        canvas.create_text(start_x + 10, y_position + 15, text=joueur1, anchor="w", font=("Helvetica", 10))

        canvas.create_rectangle(start_x, y_position + hauteur_rectangle, start_x + longueur_rectangle, y_position + 2 * hauteur_rectangle, outline="black", width=1)
        canvas.create_text(start_x + 10, y_position + hauteur_rectangle + 15, text=joueur2, anchor="w", font=("Helvetica", 10))

        button_x = start_x + longueur_rectangle + 10
        button_y = y_position + hauteur_rectangle // 2
        btn = ttk.Button(root, text="Détails")
        canvas.create_window(button_x, button_y, window=btn)

        label_x = button_x + 60
        lbl = ttk.Label(root, text="Table")
        canvas.create_window(label_x, button_y, window=lbl)

        entry_x = label_x + 40
        table_entry = ttk.Entry(root, width=5)
        canvas.create_window(entry_x, button_y, window=table_entry)

    root.mainloop()

simulate_mac_ui()