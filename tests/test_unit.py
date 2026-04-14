"""
test_unit.py — Tests unitaires NexusGame
==========================================
Contexte : Suite de tests unitaires sur l'API GameStore.
Chaque test est isolé — BDD fraîche à chaque appel (fixture function scope).

Lancement :
    pytest tests/test_unit.py -v
    pytest tests/test_unit.py -v --cov=app_gamestore --cov-report=html
"""

import pytest

# Payload valide réutilisable dans plusieurs tests
SAMPLE_GAME = {
    "title": "Dragon Quest",
    "genre": "RPG",
    "price": 29.99,
    "rating": 4.5,
    "in_stock": True,
}

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Health & endpoints de base
# ════════════════════════════════════════════════════════════════════════════════

class TestHealth:

    def test_health_retourne_200(self, client):
        """
        TODO — Vérifier que GET /health retourne 200 et {"status": "ok"}.
        """
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json.get("status") == "ok"

    def test_health_contient_service(self, client):
        """
        TODO — Vérifier que la réponse contient la clé "service".
        """
        r = client.get("/health")
        assert "service" in r.json


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Liste des jeux
# ════════════════════════════════════════════════════════════════════════════════

class TestListGames:

    def test_liste_retourne_200(self, client):
        """
        TODO — GET /games retourne 200 et une liste non vide.
        """
        r = client.get("/games")
        assert r.status_code == 200
        assert isinstance(r.json, list)

    def test_liste_contient_les_champs_attendus(self, client):
        """
        TODO — Chaque jeu retourné contient au moins : id, title, genre, price, rating.
        """
        # On crée d'abord un jeu pour s'assurer que la liste n'est pas vide
        client.post("/games", json=SAMPLE_GAME)
        games = client.get("/games").json
        assert len(games) > 0
        for game in games:
            for field in ("id", "title", "genre", "price", "rating"):
                assert field in game, f"Champ manquant : {field}"

    def test_filtre_par_genre(self, client):
        """
        TODO — GET /games?genre=RPG retourne uniquement des jeux RPG.
        Vérifier que tous les éléments ont genre == "RPG".
        """
        client.post("/games", json=SAMPLE_GAME)
        client.post("/games", json={**SAMPLE_GAME, "title": "Space Shooter", "genre": "Action"})

        r = client.get("/games?genre=RPG")
        assert r.status_code == 200
        games = r.json
        assert all(g["genre"] == "RPG" for g in games)

    def test_tri_par_prix_croissant(self, client):
        """
        TODO — GET /games?sort=price&order=asc retourne les jeux triés par prix croissant.
        """
        client.post("/games", json={**SAMPLE_GAME, "title": "Cheap Game", "price": 5.0})
        client.post("/games", json={**SAMPLE_GAME, "title": "Expensive Game", "price": 59.99})

        r = client.get("/games?sort=price&order=asc")
        assert r.status_code == 200
        games = r.json
        prices = [g["price"] for g in games]
        assert prices == sorted(prices)


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Création de jeux
# ════════════════════════════════════════════════════════════════════════════════

class TestCreateGame:

    def test_creation_valide_retourne_201(self, client):
        """
        TODO — POST /games avec titre, genre, prix valides → 201 + id dans la réponse.
        """
        r = client.post("/games", json=SAMPLE_GAME)
        assert r.status_code == 201
        assert "id" in r.json

    def test_creation_sans_titre_retourne_400(self, client):
        """
        TODO — POST /games sans "title" → 400.
        """
        payload = {k: v for k, v in SAMPLE_GAME.items() if k != "title"}
        r = client.post("/games", json=payload)
        assert r.status_code == 400

    def test_creation_prix_negatif_retourne_400(self, client):
        """
        TODO — POST /games avec price = -5 → 400.
        """
        payload = {**SAMPLE_GAME, "price": -5}
        r = client.post("/games", json=payload)
        assert r.status_code == 400

    def test_creation_titre_duplique_retourne_409(self, client):
        """
        TODO — Créer le même jeu deux fois → second appel retourne 409.
        """
        assert client.post("/games", json=SAMPLE_GAME).status_code == 201
        assert client.post("/games", json=SAMPLE_GAME).status_code == 409

    @pytest.mark.parametrize("payload,expected_status", [
        # TODO — Ajouter vos cas de validation ici
        # Titre manquant
        ({"genre": "RPG", "price": 10.0, "rating": 4.0}, 400),
        # Genre manquant
        ({"title": "No Genre", "price": 10.0, "rating": 4.0}, 400),
        # Prix manquant
        ({"title": "No Price", "genre": "RPG", "rating": 4.0}, 400),
        # Prix négatif
        ({"title": "Negative Price", "genre": "RPG", "price": -1.0, "rating": 4.0}, 400),
        # Rating hors limites (> 5)
        ({"title": "Bad Rating", "genre": "RPG", "price": 10.0, "rating": 6.0}, 400),
        # Payload valide → doit retourner 201
        ({"title": "Valid Game", "genre": "Action", "price": 19.99, "rating": 3.5}, 201),
    ])
    def test_validation_parametree(self, client, payload, expected_status):
        """TODO — POST /games avec le payload, vérifier le status code."""
        r = client.post("/games", json=payload)
        assert r.status_code == expected_status


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Récupération, mise à jour, suppression
# ════════════════════════════════════════════════════════════════════════════════

class TestGameCRUD:

    def test_get_jeu_existant(self, client):
        """
        TODO — Créer un jeu, récupérer son id, GET /games/{id} → 200.
        """
        created = client.post("/games", json=SAMPLE_GAME).json
        game_id = created["id"]
        r = client.get(f"/games/{game_id}")
        assert r.status_code == 200
        assert r.json["id"] == game_id

    def test_get_jeu_inexistant_retourne_404(self, client):
        """
        TODO — GET /games/99999 → 404.
        """
        r = client.get("/games/99999")
        assert r.status_code == 404

    def test_update_prix(self, client):
        """
        TODO — Créer un jeu, PUT /games/{id} avec nouveau prix, vérifier la mise à jour.
        """
        created = client.post("/games", json=SAMPLE_GAME).json
        game_id = created["id"]
        new_price = 9.99
        r = client.put(f"/games/{game_id}", json={**SAMPLE_GAME, "price": new_price})
        assert r.status_code == 200
        updated = client.get(f"/games/{game_id}").json
        assert updated["price"] == new_price

    def test_delete_jeu(self, client):
        """
        TODO — Créer un jeu, DELETE /games/{id} → 204, puis GET → 404.
        """
        created = client.post("/games", json=SAMPLE_GAME).json
        game_id = created["id"]
        r = client.delete(f"/games/{game_id}")
        assert r.status_code == 204
        assert client.get(f"/games/{game_id}").status_code == 404


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Choix libres (à justifier dans le README)
# ════════════════════════════════════════════════════════════════════════════════

class TestChoixLibres:
    """
    Ajoutez ici les tests que vous jugez critiques.
    Documentez vos choix dans le README.
    """

    def test_rating_zero_est_valide(self, client):
        """Un jeu avec rating=0 doit être accepté (valeur limite basse)."""
        payload = {**SAMPLE_GAME, "title": "Zero Rated", "rating": 0.0}
        r = client.post("/games", json=payload)
        assert r.status_code == 201

    def test_rating_cinq_est_valide(self, client):
        """Un jeu avec rating=5 doit être accepté (valeur limite haute)."""
        payload = {**SAMPLE_GAME, "title": "Perfect Game", "rating": 5.0}
        r = client.post("/games", json=payload)
        assert r.status_code == 201

    def test_prix_zero_est_valide(self, client):
        """Un jeu gratuit (price=0) doit être accepté."""
        payload = {**SAMPLE_GAME, "title": "Free Game", "price": 0.0}
        r = client.post("/games", json=payload)
        assert r.status_code == 201

    def test_body_vide_retourne_400(self, client):
        """POST /games avec un body vide → 400."""
        r = client.post("/games", json={})
        assert r.status_code == 400


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Endpoint /games/featured (NGS-108)
# ════════════════════════════════════════════════════════════════════════════════

class TestFeatured:
    """
    Tests sur l'endpoint GET /games/featured.
    Consultez la documentation de l'endpoint dans app_gamestore.py.
    Si un test échoue alors que votre assertion est correcte, documentez
    ce que vous observez dans le README.
    """

    def _create_game(self, client, title, price, rating, in_stock=True):
        payload = {
            "title": title,
            "genre": "Action",
            "price": price,
            "rating": rating,
            "in_stock": in_stock,
        }
        return client.post("/games", json=payload).json.get("id")

    def test_featured_retourne_200(self, client):
        """TODO — GET /games/featured retourne 200."""
        r = client.get("/games/featured")
        assert r.status_code == 200

    def test_featured_retourne_liste(self, client):
        """TODO — La réponse contient une clé 'featured' qui est une liste."""
        r = client.get("/games/featured")
        data = r.json
        assert "featured" in data
        assert isinstance(data["featured"], list)

    def test_featured_max_5_par_defaut(self, client):
        """TODO — Sans paramètre, au maximum 5 jeux sont retournés."""
        for i in range(8):
            self._create_game(client, f"Game {i}", price=10.0 + i, rating=4.0)
        featured = client.get("/games/featured").json["featured"]
        assert len(featured) <= 5

    def test_featured_limit_param(self, client):
        """TODO — ?limit=3 retourne au maximum 3 jeux."""
        for i in range(6):
            self._create_game(client, f"LimitGame {i}", price=10.0 + i, rating=4.0)
        featured = client.get("/games/featured?limit=3").json["featured"]
        assert len(featured) <= 3

    def test_featured_tries_par_rating_decroissant(self, client):
        """TODO — Les jeux sont triés par rating décroissant."""
        self._create_game(client, "Low Rated",  price=10.0, rating=2.0)
        self._create_game(client, "Mid Rated",  price=10.0, rating=3.5)
        self._create_game(client, "High Rated", price=10.0, rating=4.9)

        featured = client.get("/games/featured").json["featured"]
        ratings = [g["rating"] for g in featured]
        assert ratings == sorted(ratings, reverse=True)

    def test_featured_sans_jeux_gratuits(self, client):
        """TODO — Les jeux gratuits ne doivent pas apparaître dans featured."""
        self._create_game(client, "Free Game", price=0.0, rating=5.0)
        featured = client.get("/games/featured").json["featured"]
        assert all(g["price"] > 0 for g in featured)

    def test_featured_sans_jeux_hors_stock(self, client):
        """TODO — Les jeux hors stock ne doivent pas apparaître dans featured."""
        self._create_game(client, "Out Of Stock", price=19.99, rating=5.0, in_stock=False)
        featured = client.get("/games/featured").json["featured"]
        assert all(g.get("in_stock", True) for g in featured)