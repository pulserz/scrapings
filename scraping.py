import re

from bs4 import BeautifulSoup
import requests
import math

import constants
from utils import save_to_image_file, save_to_csv_file


def parse_html(url: str) -> BeautifulSoup:
    """ Parse le contenu HTML d'une URL.

        Args:
            url (str) : URL de la page à parser

        Returns:
            BeautifulSoup : Objet BeautifulSoup contenant l'arborescence HTML
    """
    response = requests.get(url)
    return BeautifulSoup(response.content, "html.parser")


def get_all_categories_url() -> list[str]:
    """ Récupère les URLs de toutes les catégories de livres.

        Returns:
            list[str] : Liste des URLs des catégories, ou liste vide si aucune catégorie trouvée
    """
    soup = parse_html(constants.URL)
    categories_url = []

    all_categories = soup.find("div", class_="side_categories")
    if not all_categories:
        return []

    ul = all_categories.find("ul")
    if not ul:
        return []

    li_tags = ul.find_all("li")[1:]

    for li in li_tags:
        link = li.find("a")
        if link:
            href = link.get("href")
            if href:
                categories_url.append(f"{constants.URL}/{href}")

    return categories_url


def get_book_data(base_url: str) -> dict:
    """ Récupère les données complètes d'un livre depuis une page.

        Args:
            base_url (str) : L'URL de la page du livre

        Returns:
            dict: Dictionnaire contenant les données du livre avec les clés
                – title: Titre du livre
                – category: Catégorie du livre
                – price: Prix du livre
                – review_rating: Note/évaluation du livre
                – image_url: URL de l'image de couverture
                – description: Description du livre
                – additional_information: Dict avec les infos supplémentaires (UPC, Type, etc.)
    """
    soup = parse_html(base_url)
    book_record = {}

    # Titre
    if book_tags := soup.find("div", class_="product_main"):
        h1 = book_tags.find("h1")
        book_record["title"] = h1.get_text(strip=True) if h1 else "N/A"
    else:
        return {}

    # Catégorie
    if breadcrumb := soup.find("ul", class_="breadcrumb"):
        links = breadcrumb.find_all("a")
        book_record['category'] = links[2].get_text(strip=True) if len(links) > 2 else "N/A"

    # Prix
    price = book_tags.find("p", class_="price_color")
    book_record["price"] = price.get_text(strip=True).replace("Â", "") if price else "N/A"

    # Note
    if rating := book_tags.find(class_="star-rating"):
        classes = rating.get("class") or []
        book_record["review_rating"] = " ".join(classes).replace("star-rating", "").strip()
    else:
        book_record["review_rating"] = "N/A"

    # Image
    if thumbnail := soup.find(class_="thumbnail"):
        if img := thumbnail.find("img"):
            src = img.get("src")
            # Gérer le cas où src est une liste
            if isinstance(src, list):
                src = src[0] if src else None

            if src:
                book_record["image_url"] = str(src).replace("../../", "https://books.toscrape.com/")
            else:
                book_record["image_url"] = "N/A"
        else:
            book_record["image_url"] = "N/A"
    else:
        book_record["image_url"] = "N/A"

    # Description
    if description := soup.find("div", id="product_description"):
        sibling = description.find_next_sibling("p")
        book_record["description"] = sibling.get_text(strip=True) if sibling else "N/A"
    else:
        book_record["description"] = "N/A"

    # Product Information
    if additional_information := soup.find(string="Product Information"):
        if book_product_table := additional_information.find_next("table"):
            for row in book_product_table.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    header = th.get_text(strip=True)
                    # Convertir en minuscules + remplacer espaces par underscores
                    header = header.lower().replace(" ", "_")
                    header = re.sub(r"\W", "", header)  # Enlever caractères spéciaux
                    value = td.get_text(strip=True).replace("Â", "")
                    book_record[header] = value

    return book_record


def get_number_of_pages(category_url: str) -> int:
    """ Retourne le nombre de pages présentes dans la catégorie.

        Args:
            category_url (str) : L'URL de la catégorie à scraper.

        Returns:
            int: Il y a 20 livres par page, on récupère le nombre total de livres dans la catégorie
            et on divise ce nombre par 20 et on arrondit au nombre supérieur pour récupérer le nombre de pages.
    """
    content = parse_html(category_url)
    number_of_books_in_category = content.select("strong")[1].text
    if not number_of_books_in_category.isdigit():
        raise ValueError(f"Le nombre de livres dans la catégorie n'est pas valide.")

    return math.ceil(int(number_of_books_in_category) / 20)


def get_all_pages_url(category_url: str) -> list:
    """ Récupère les URLs de toutes les pages d'un catalogue.

        Vérifie l'existence de chaque page en effectuant une requête HTTP
        et arrête quand une page n'existe plus.

        Args:
            category_url (str) : URL de base du catalogue

        Returns:
            list: Liste des URLs de toutes les pages du catalogue
    """
    page = 1
    pages_urls = []

    while True:

        page_url = (category_url + f"catalogue/page-{page}.html")
        page += 1
        response = requests.get(page_url)
        if response.status_code == 200:
            pages_urls.append(page_url)
        else:
            break

    return pages_urls


def get_pages_urls(category_url: str) -> list:
    """ Récupère les URLs de toutes les pages d'une catégorie.

        Args:
            category_url (str) : URL de la première page de la catégorie

        Returns:
            list : Liste contenant les URLs de toutes les pages de la catégorie
    """
    number_of_pages = get_number_of_pages(category_url)
    if number_of_pages == 1:
        return [category_url]

    url_placeholder = category_url.replace("index", "page-{}")
    return [url_placeholder.format(page + 1) for page in range(number_of_pages)]


def get_books_urls(category_url: str) -> list:
    """ Récupère les URLs de tous les livres d'une catégorie.

        Parcourt toutes les pages de la catégorie et extrait les URLs
        complètes de chaque livre.

        Args:
            category_url (str) : URL de la catégorie

        Returns:
            list : Liste des URLs complètes de tous les livres de la catégorie
    """
    pages_urls = get_pages_urls(category_url=category_url)

    books_url = []
    for page_url in pages_urls:
        content = parse_html(page_url)
        titles = content.find_all("h3")
        for title in titles:
            link = title.find("a")
            href = link.get("href") if link else None

            if not href:
                continue

            href = str(href)

            if (relative_pattern := "../../../") in href:
                full_url = href.replace(relative_pattern, f"{constants.URL}catalogue/")
            else:
                full_url = f"{constants.URL}{href}"

            books_url.append(full_url)

    return books_url


def get_books_data(category_url: str) -> list[dict]:
    """ Récupère les données de tous les livres d'une catégorie.

        Args:
            category_url (str) : URL de la catégorie

        Returns:
            list[dict] : Liste des dictionnaires contenant les données de chaque livre
        """
    return [get_book_data(book_url) for book_url in get_books_urls(category_url)]


def scrap_all(books=True, images=True):
    """Récupération des livres et/ou des images"""
    categories_urls = get_all_categories_url()
    print(f"📂 {len(categories_urls)} catégories trouvées")

    for category_url in categories_urls:
        books_data = get_books_data(category_url=category_url)
        category_name = books_data[0]["category"]

        if books:
            save_to_csv_file(books_data)
            print(f"✅ [{category_name}] CSV sauvegardé")

        if images:
            save_to_image_file(books_data)
            print(f"🖼️  [{category_name}] Images sauvegardées")