"""
test_ui.py — Tests UI Playwright NexusGame
===========================================
Contexte : Tests de l'interface utilisateur GameStore avec Playwright.
Pattern Page Object Model (POM) obligatoire — les sélecteurs ne doivent
pas être écrits directement dans les tests.

Lancement :
    pytest tests/test_ui.py -v --headed          # avec navigateur visible
    pytest tests/test_ui.py -v                   # headless (CI)
    pytest tests/test_ui.py -v --html=reports/ui.html

Prérequis :
    playwright install chromium
    # L'API GameStore doit tourner sur http://localhost:5000
"""
import pytest
import time
from playwright.sync_api import Page, expect

from tests.pages.home_page import HomePage
from tests.pages.add_game_modal import AddGameModal

BASE_URL = "http://localhost:5000"


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Tests basiques (sans POM)
# ════════════════════════════════════════════════════════════════════════════════

@pytest.mark.ui
class TestPageBasique:

    def test_page_se_charge(self, page: Page):
        page.goto(BASE_URL)

        assert page.title() == "GameStore"

        expect(page.locator('[data-testid="game-list"]')).to_be_visible()

    def test_compteur_jeux_positif(self, page: Page):
        page.goto(BASE_URL)

        counter = page.locator('[data-testid="game-count"]')
        text = counter.text_content()

        # extrait le nombre
        number = int("".join(filter(str.isdigit, text)))

        assert number > 0

    def test_annuler_ferme_le_modal(self, page: Page):
        page.goto(BASE_URL)

        page.locator('[data-testid="add-game-btn"]').click()
        page.locator('[data-testid="cancel-btn"]').click()

        modal = page.locator('[data-testid="add-game-modal"]')
        expect(modal).not_to_be_visible()


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Tests avec Page Object Model
# ════════════════════════════════════════════════════════════════════════════════

@pytest.mark.ui
class TestAvecPOM:

    def test_page_charge_via_pom(self, page: Page):
        home = HomePage(page)

        home.navigate()

        expect(home.game_list).to_be_visible()

    def test_ajouter_jeu_via_pom(self, page: Page):
        home = HomePage(page)
        modal = AddGameModal(page)

        home.navigate()
        home.open_add_form()

        modal.fill_and_submit("UI Test Game", "RPG", 19.99)

        expect(home.get_game_cards().first).to_contain_text("UI Test Game")

    def test_recherche_filtre_resultats(self, page: Page):
        home = HomePage(page)

        home.navigate()
        home.search("Zelda")

        cards = home.get_game_cards()

        expect(cards.first).to_contain_text("Zelda")

    def test_filtre_genre_rpg(self, page: Page):
        home = HomePage(page)

        home.navigate()
        home.filter_genre("RPG")

        cards = home.get_game_cards()

        count = cards.count()
        assert count > 0

        for i in range(count):
            expect(cards.nth(i).locator('[data-testid="game-genre"]')).to_contain_text("RPG")


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Choix libres (à justifier dans le README)
# ════════════════════════════════════════════════════════════════════════════════

@pytest.mark.ui
class TestChoixLibresUI:

    def test_ajout_plus_filtre(self, page: Page):
        home = HomePage(page)
        modal = AddGameModal(page)

        home.navigate()

        home.open_add_form()
        modal.fill_and_submit("E2E Game", "Action", 29.99)

        home.filter_genre("Action")

        expect(page.get_by_text("E2E Game")).to_be_visible()