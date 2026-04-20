import constants
from Scrapings.scraping import scrap_all


def display_menu():
    """Affiche le menu principal de l'application."""
    print(constants.MENU)

    user_choice = input("Entrez votre choix (1, 2 ou 3) : ")

    while user_choice not in ["1", "2", "3"]:
        print("Choix invalide. Veuillez entrer 1, 2 ou 3.")
        user_choice = input("Entrez votre choix (1, 2 ou 3) : ")

    if user_choice == "1":
        scrap_all(images=False)  # seulement les infos CSV
    elif user_choice == "2":
        scrap_all(books=False)  # seulement les images
    elif user_choice == "3":
        print("Merci d'avoir utilisé l'application. Au revoir !")

if __name__ == "__main__":
    display_menu()