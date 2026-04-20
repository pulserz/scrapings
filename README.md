# 📚 Books Scraper

Un scraper Python qui extrait les données de livres depuis [books.toscrape.com](https://books.toscrape.com), les sauvegarde en CSV et télécharge les couvertures.

## Fonctionnalités

- Scraping de toutes les catégories de livres
- Export des données en fichiers CSV par catégorie
- Téléchargement des images de couverture
- Menu interactif en ligne de commande

## Structure du projet

```
Scrapings/
├── __main__.py       # Point d'entrée + menu
├── scraping.py       # Logique de scraping (requêtes, parsing HTML)
├── utils.py          # Sauvegarde CSV et images
├── constants.py      # URL de base et constantes
└── Data/             # Données générées (ignoré par git)
    └── <Catégorie>/
        ├── <Catégorie>.csv
        └── Images/
            └── <Titre>.jpg
```

## Installation

```bash
git clone https://github.com/ton-pseudo/nom-du-repo.git
cd nom-du-repo
pip install -r requirements.txt
```

## Dépendances

```
requests
beautifulsoup4
lxml
```

## Utilisation

```bash
python -m Scrapings
```

Le menu propose :
1. Scraper les informations de tous les livres (CSV)
2. Scraper les couvertures des livres (images)
3. Quitter

## Données extraites

| Champ | Description |
|-------|-------------|
| title | Titre du livre |
| category | Catégorie |
| price | Prix |
| review_rating | Note |
| image_url | URL de la couverture |
| description | Description |
| upc | Code produit |
| availability | Disponibilité |
| ... | Autres infos produit |
