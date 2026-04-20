import csv
import io
from pathlib import Path
import re

import requests


def convert_book_data_to_csv(books_data: list[dict]) -> str:
    """ Convertit les données des livres en format CSV.

        Args:
            books_data (list[dict]) : Liste des dictionnaires contenant les données des livres

        Returns:
            str : Chaîne de caractères au format CSV avec en-têtes et données
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

     # Collecter tous les headers dynamiquement
    fixed_headers = ["title", "category", "price", "review_rating", "image_url", "description"]
    extra_headers = set()
    for book in books_data:
        extra_headers.update(k for k in book.keys() if k not in fixed_headers)

    all_headers = fixed_headers + sorted(extra_headers)
    writer.writerow(all_headers)

    for book in books_data:
        writer.writerow([book.get(header, "N/A") for header in all_headers])

    return output.getvalue()


def save_to_csv_file(books_data: list[dict]) -> bool:
    """ Sauvegarde les données des livres dans un fichier CSV.

        Crée un dossier portant le nom de la catégorie et y enregistre
        les données des livres dans un fichier CSV.

        Args:
            books_data (list[dict]) : Liste des dictionnaires contenant les données des livres

        Returns:
            bool : True si la sauvegarde a réussi, False en cas d'erreur
    """
    try:
        category_name = books_data[0]["category"]
        folder_path = Path("Data") / category_name
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / f"{category_name}.csv"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(convert_book_data_to_csv(books_data))
        return True
    except OSError:
        return False


def save_to_image_file(books_data: list[dict]) -> bool:
    """ Sauvegarde les images de chaque livre dans un fichier.

        Les images sont stockées dans le dossier Data/<category>/Images/
        et nommées d'après le titre du livre (ex: Its_Only_the_Himalayas.jpg).

        Args:
            books_data: Liste de dictionnaires contenant les données des livres.
                        Chaque dict doit avoir les clés "category", "image_url" et "title".

        Returns:
            True si toutes les images ont été sauvegardées avec succès, False sinon.
        """
    try:
        for book in books_data:
            category_name = book["category"]
            image_url = book["image_url"]

            folder_path = Path("Data") / category_name / "Images"
            folder_path.mkdir(parents=True, exist_ok=True)

            result = requests.get(image_url)
            image_name = re.sub(r'[^\w\s-]', '', book["title"])
            image_name = image_name.replace(" ", "_") + ".jpg"
            file_path = folder_path / image_name

            with open(file_path, "wb") as f:
                f.write(result.content)
        return True
    except OSError:
        return False

