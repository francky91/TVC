
import os
import platform
import subprocess
from tkinter import messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from PIL import Image
from modules.utils import lire_pdf_directory
from modules.debug import debug_print


def print_bracket_to_pdf(self, canvas):
    pdf_directory = lire_pdf_directory()
    os.makedirs(pdf_directory, exist_ok=True)

    table_type = "OK" if canvas == getattr(self, "ok_canvas", None) else "KO"
    pdf_filename = os.path.join(pdf_directory, f"Tableau_{table_type}_{self.tournoi.category}_Tour{self.tournoi.tour}.pdf")

    bbox = canvas.bbox("all")
    if bbox is None:
        messagebox.showerror("Impression", "Rien à imprimer ou dimensions invalides.")
        return

    left, top, right, bottom = bbox
    width_canvas = right - left
    height_canvas = bottom - top

    if width_canvas <= 0 or height_canvas <= 0:
        messagebox.showerror("Impression", "Rien à imprimer ou dimensions invalides.")
        return

    ps_filename = os.path.join(pdf_directory, "temp_bracket.ps")
    try:
        canvas.postscript(file=ps_filename, colormode="color", x=left, y=top, width=width_canvas, height=height_canvas)
    except Exception as e:
        messagebox.showerror("Impression", f"Échec de l'export PostScript : {e}")
        return

    png_filename = os.path.join(pdf_directory, "temp_bracket.png")
    try:
        img = Image.open(ps_filename)
        if img.mode != "RGB":
            img = img.convert("RGB")

        scale_factor = 4
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img.save(png_filename, "PNG", dpi=(300, 300))
        img.close()
    except Exception as e:
        messagebox.showerror("Impression", f"Échec de la conversion en PNG : {e}")
        return

    try:
        pdf = pdf_canvas.Canvas(pdf_filename, pagesize=A4)
        pdf_width, pdf_height = A4

        scale_x = pdf_width / new_width
        scale_y = pdf_height / new_height
        scale = min(scale_x, scale_y)

        final_width = new_width * scale
        final_height = new_height * scale
        margin_x = (pdf_width - final_width) / 2
        margin_y = (pdf_height - final_height) / 2

        pdf.drawImage(png_filename, margin_x, margin_y, width=final_width, height=final_height)

        pdf.showPage()
        pdf.save()

        messagebox.showinfo("Impression", f"PDF généré avec succès : {pdf_filename}")
    except Exception as e:
        messagebox.showerror("Impression", f"Échec de la génération du PDF : {e}")
        return
    finally:
        try:
            if os.path.exists(ps_filename):
                os.remove(ps_filename)
            if os.path.exists(png_filename):
                os.remove(png_filename)
        except Exception:
            pass


def print_match_details_direct(self, line, dc, player1, player2, table_name, category, level):
    x = 100
    y = line

    dc.TextOut(x, y, f"Tableau {table_name} - {level} - {category}                                 TVC - Tour {self.tournoi.tour}")
    y += self.lh * 3

    header = f"{'Dossard':<4}   {'Nom':<15}   {'Prénom':<15}   {'Club':<7}1    2    3    4    5"
    dc.TextOut(x, y, header)
    y += self.lh

    dc.TextOut(x, y, f"______________________________________________________________________________")
    y += self.lh

    line1 = f"|{player1.dossard:<4} | {player1.nom:<15} | {player1.prenom:<15} | {player1.club:<7} | {' ':<2} | {' ':<2} | {' ':<2} | {' ':<2} | {' ':<2} |"
    dc.TextOut(x, y, line1)
    y += self.lh

    dc.TextOut(x, y, f"______________________________________________________________________________")
    y += self.lh

    line2 = f"|{player2.dossard:<4} | {player2.nom:<15} | {player2.prenom:<15} | {player2.club:<7} | {' ':<2} | {' ':<2} | {' ':<2} | {' ':<2} | {' ':<2} |"
    dc.TextOut(x, y, line2)
    y += self.lh

    dc.TextOut(x, y, f"______________________________________________________________________________")
    y += self.lh

    return y


def _render_matches_to_pdf(app, matches, pdf_filename):
    """Render a list of matches to a PDF using reportlab.
    matches: list of tuples (player1, player2, table_name, category, level)
    """
    try:
        pdf = pdf_canvas.Canvas(pdf_filename, pagesize=A4)
        pdf_width, pdf_height = A4
        margin = 50
        x = margin
        y = pdf_height - margin
        line_height = getattr(app, 'lh', 14)

        for (p1, p2, table_name, category, level) in matches:
            title = f"Tableau {table_name} - {level} - {category}                                 TVC - Tour {app.tournoi.tour}"
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(x, y, title)
            y -= line_height * 2

            pdf.setFont("Helvetica", 10)
            header = f"{'Dossard':<6} {'Nom':<15} {'Prénom':<15} {'Club':<10} 1  2  3  4  5"
            pdf.drawString(x, y, header)
            y -= line_height
            pdf.drawString(x, y, '_' * 100)
            y -= line_height

            def safe(attr):
                try:
                    return str(attr) if attr is not None else ''
                except Exception:
                    return ''

            line1 = f"{safe(getattr(p1,'dossard','')):<6} {safe(getattr(p1,'nom','')):<15} {safe(getattr(p1,'prenom','')):<15} {safe(getattr(p1,'club','')):<10}"
            pdf.drawString(x, y, line1)
            y -= line_height
            pdf.drawString(x, y, '_' * 100)
            y -= line_height

            line2 = f"{safe(getattr(p2,'dossard','')):<6} {safe(getattr(p2,'nom','')):<15} {safe(getattr(p2,'prenom','')):<15} {safe(getattr(p2,'club','')):<10}"
            pdf.drawString(x, y, line2)
            y -= line_height
            pdf.drawString(x, y, '_' * 100)
            y -= line_height * 2

            # Pagination
            if y < margin + 100:
                pdf.showPage()
                y = pdf_height - margin

        pdf.showPage()
        pdf.save()
        return True
    except Exception as e:
        debug_print("Erreur génération PDF matches:", e)
        return False


def on_print_and_uncheck(self, nbPlayers, player1, player2, table_name, category, level):
    """Cross-platform print helper.
    On Windows uses the win32 printing path (init_printer). On macOS/Linux generates a PDF and sends it to the system printer via 'lp'.
    After printing, clears match.print_state flags for matches printed.
    """
    # collect matches to print
    matches_to_print = []  # list of (p1,p2,table_name,category,level_label)

    debug_print("nb_players", nbPlayers)
    if nbPlayers <= 1:
        if player1 and player2:
            matches_to_print.append((player1, player2, table_name, category, getattr(level, 'string', str(level))))
    else:
        if hasattr(self, "tournoi"):
            tables = []
            if getattr(self.tournoi, "tableauOk", None):
                tables.append(self.tournoi.tableauOk)
            if getattr(self.tournoi, "tableauKo", None):
                tables.append(self.tournoi.tableauKo)
            if getattr(self.tournoi, "tableauInterTops", None):
                tables.append(self.tournoi.tableauInterTops)

            for tbl in tables:
                tbl_name = getattr(tbl, "type", "Tableau")
                for lvl in getattr(tbl, "tableauLevels", []) or []:
                    lvl_label = getattr(lvl, "level", "")
                    for match in getattr(lvl, "matches", []) or []:
                        debug_print(f"Vérification match {match.num} - print_state: {getattr(match, 'print_state', None)}")
                        try:
                            if getattr(match, "print_state", False):
                                if getattr(match, "player1", None) and getattr(match, "player2", None):
                                    matches_to_print.append((match.player1, match.player2, tbl_name, category, lvl_label))
                                # clear model flag
                                match.print_state = False
                        except Exception:
                            continue

    if not matches_to_print:
        messagebox.showinfo("Impression", "Aucun match sélectionné pour impression.")
        return

    system = platform.system()

    if system == 'Windows':
        self.lh = 100
        # Import Windows printing helpers here to avoid import error on non-Windows
        try:
            from modules.print import init_printer, close_printer
        except Exception as e:
            debug_print("Impossible d'importer les helpers d'impression Windows:", e)
            messagebox.showerror("Impression", f"Impossible d'utiliser l'impression Windows: {e}")
            return

        try:
            hprinter, dc = init_printer()
            try:
                dc.StartPage()
                line = 100
                for (p1, p2, tbl_name, cat, lvl_label) in matches_to_print:
                    line = print_match_details_direct(self, line, dc, p1, p2, tbl_name, cat, lvl_label)
                    if line > 6000:
                        dc.EndPage()
                        dc.StartPage()
                        line = 100
                dc.EndPage()
            finally:
                debug_print("Fermeture de l'imprimante")
                close_printer(dc, hprinter)
        except Exception as e:
            debug_print("Erreur impression Win32:", e)
            messagebox.showerror("Impression", f"Erreur d'impression Windows : {e}")
            return

    else:
        # Generate temporary PDF and send to system printer via lp (macOS/Linux)
        pdf_dir = lire_pdf_directory()
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_filename = os.path.join(pdf_dir, f"matches_print_{os.getpid()}.pdf")

        ok = _render_matches_to_pdf(self, matches_to_print, pdf_filename)
        if not ok:
            messagebox.showerror("Impression", "Échec de la génération du PDF pour impression.")
            return

        try:
            # Try system print command
            subprocess.run(["lp", pdf_filename], check=True)
        except FileNotFoundError:
            # lp not available, open the PDF instead
            try:
                if system == 'Darwin':
                    subprocess.run(["open", pdf_filename])
                else:
                    subprocess.run(["xdg-open", pdf_filename])
                messagebox.showinfo("Impression", "Commande d'impression non trouvée ; le PDF a été ouvert à la place.")
            except Exception as e:
                messagebox.showerror("Impression", f"Impossible d'imprimer ou d'ouvrir le PDF : {e}")
        except Exception as e:
            messagebox.showerror("Impression", f"Erreur lors de l'appel à la commande d'impression : {e}")
        finally:
            try:
                if os.path.exists(pdf_filename):
                    os.remove(pdf_filename)
            except Exception:
                pass

    messagebox.showinfo("Impression", "Les matchs ont été imprimés.")


def print_pdf(pdf_filename):
    if platform.system() == "Windows":
        acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\AcroRd32.exe"
        if not os.path.exists(acrobat_path):
            messagebox.showerror("Erreur", "Adobe Acrobat Reader n'est pas installé.")
            return
        try:
            subprocess.run([acrobat_path, "/t", pdf_filename], check=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'impression : {e}")
    elif platform.system() == "Linux":
        try:
            subprocess.run(["lp", pdf_filename], check=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'impression : {e}")
    elif platform.system() == "Darwin":
        try:
            subprocess.run(["lp", pdf_filename], check=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'impression : {e}")
    else:
        messagebox.showerror("Erreur", "Système d'exploitation non pris en charge.")