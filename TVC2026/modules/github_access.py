import base64

import requests
from tkinter import messagebox, simpledialog

from modules.utils import lire_github_url


def get_github_url(config_file: str = "config.ini") -> str | None:
    """
    Récupère l'URL de base GitHub (API contents) depuis le fichier de configuration.

    Retourne:
        - str : l'URL GitHub si trouvé
        - None : en cas d'erreur (message déjà affiché)
    """
    try:
        url = lire_github_url(config_file)
    except Exception:
        messagebox.showerror("Erreur", "GithubUrl non trouvé dans config.ini")
        return None

    if not url:
        messagebox.showerror("Erreur", "GithubUrl non trouvé dans config.ini")
        return None

    return url


def get_github_headers(
    prompt_title: str = "Authentification GitHub",
    prompt_message: str = "Entrez votre Personal Access Token GitHub :",
) -> dict | None:
    """
    Demande à l'utilisateur un token GitHub et retourne les en-têtes HTTP associés.

    Retourne:
        - dict : headers HTTP avec le token
        - None : si l'utilisateur annule ou ne saisit rien
    """
    token = simpledialog.askstring(prompt_title, prompt_message, show="*")
    if not token:
        return None

    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }


def list_github_files(base_url: str, headers: dict) -> list[str] | None:
    """
    Liste les fichiers présents dans un répertoire GitHub (API contents).

    Retourne:
        - list[str] : noms des fichiers
        - None : en cas d'erreur (message déjà affiché)
    """
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            messagebox.showerror(
                "Erreur",
                f"Impossible de récupérer la liste des fichiers depuis GitHub.\nCode: {response.status_code}",
            )
            return None

        files_data = response.json()
        if not isinstance(files_data, list):
            messagebox.showerror("Erreur", "Format de réponse GitHub inattendu")
            return None

        file_names = [item.get("name") for item in files_data if item.get("type") == "file"]
        if not file_names:
            messagebox.showinfo("Info", "Aucun fichier trouvé dans le répertoire GitHub")
            return None

        return file_names

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Erreur lors de la communication avec GitHub : {e}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

    return None


def get_github_file(url: str, headers: dict) -> tuple[bytes | None, str | None]:
    """
    Récupère un fichier depuis GitHub via l'API contents.

    Retourne:
        - (content_bytes, sha) ou (None, None) en cas d'erreur.
    """
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            messagebox.showerror("Erreur", "Impossible de récupérer le fichier sur GitHub.")
            return None, None

        data = r.json()
        content_b64 = data.get("content")
        sha = data.get("sha")

        if content_b64 is None or sha is None:
            messagebox.showerror("Erreur", "Réponse GitHub invalide (contenu ou sha manquant).")
            return None, None

        content_bytes = base64.b64decode(content_b64)
        return content_bytes, sha

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Erreur lors de la communication avec GitHub : {e}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

    return None, None


def upload_github_file_by_url(
    url: str,
    headers: dict,
    content_bytes: bytes,
    sha: str,
    commit_message: str,
    branch: str = "main",
    success_message: str | None = "Points sauvegardés sur GitHub.",
) -> bool:
    """
    Envoie (PUT) un fichier sur GitHub via l'API contents.

    Retourne:
        - True si succès
        - False sinon (messages déjà affichés)
    """
    try:
        encoded = base64.b64encode(content_bytes).decode()

        payload = {
            "message": commit_message,
            "content": encoded,
            "sha": sha,
            "branch": branch,
        }

        r = requests.put(url, headers=headers, json=payload)
        if r.status_code in (200, 201):
            if success_message:
                messagebox.showinfo("Succès", success_message)
            return True

        messagebox.showerror("Erreur", f"Upload GitHub impossible :\n{r.text}")
        return False

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur upload GitHub : {e}")
        return False

