"""
test_integration.py — Tests d'intégration NexusGame
=====================================================
Tests de bout en bout sur l'API GameStore avec un serveur réel.
Ces tests valident le comportement complet, pas seulement la logique unitaire.

Lancement :
    pytest tests/test_integration.py -v -m integration
    pytest tests/test_integration.py -v --html=reports/integration.html
"""
import signal
import subprocess
import threading
import pytest
import requests
import time
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ════════════════════════════════════════════════════════════════════════════════
# FIXTURE — Serveur GameStore en processus réel
# ════════════════════════════════════════════════════════════════════════════════

def _wait_for_server(url, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get(f"{url}/health")
            if r.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
        raise RuntimeError("Le serveur Gamestore ne répond pas dans le temps imparti")



@pytest.fixture(scope="module")
def api_url():
    """
    Démarre le serveur Flask en sous-processus réel pour les tests d'intégration.
    """

    env = os.environ.copy()

    proc = subprocess.Popen(
        ["python", "app_gamestore.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    # attendre que le serveur soit prêt
    url = "http://localhost:5000"
    timeout = 10
    start = time.time()

    while True:
        try:
            requests.get(f"{url}/health")
            break
        except Exception:
            if time.time() - start > timeout:
                proc.kill()
                raise RuntimeError("Serveur GameStore ne démarre pas")
            time.sleep(0.3)

    yield url

    # teardown
    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=5)


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Scénarios de bout en bout
# ════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestScenariosCatalogueComplet:
    """
    Scénarios E2E sur le catalogue de jeux.
    Ces tests utilisent requests (HTTP réel) — pas le client Flask.
    """

    def test_catalogue_initial_non_vide(self, api_url):
        """
        TODO — GET /games retourne 200 et une liste non vide.
        Utiliser requests.get(), pas client.get().
        """
        # À compléter
        r = requests.get(f"{api_url}/games")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_cycle_complet_creation_lecture_suppression(self, api_url):
        """
        TODO — Scénario complet :
        1. POST /games → créer un jeu, récupérer son id
        2. GET /games/{id} → vérifier qu'il existe
        3. DELETE /games/{id} → supprimer
        4. GET /games/{id} → vérifier 404

        """
        # À compléter
        payload = {
            "title" : "integration game",
            "genre" : "action",
            "price" : "19.99",
            "rating" : "4.3",
            "stock" : "15"
        }

        r = requests.post(f"{api_url}/games", json=payload)
        assert r.status_code == 201
        game_id = r.json()["id"]

        r = requests.get(f"{api_url}/games/{game_id}")
        assert r.status_code == 200
        assert r.json()["title"] == payload["title"]

        r = requests.delete(f"{api_url}/games/{game_id}")
        assert r.status_code == 204

        r = requests.get(f"{api_url}/games/{game_id}")
        assert r.status_code == 404

    def test_mise_a_jour_stock(self, api_url):
        """
        TODO — Créer un jeu avec stock=10, PUT pour passer à stock=0,
        vérifier que la valeur est bien persistée en base.
        """
        # À compléter
        payload = {
            "title": f"stock update game {time.time()}",
            "genre": "RPG",
            "price": 26.99,
            "rating": 2.3,
            "stock": 10,
        }

        r = requests.post(f"{api_url}/games", json=payload)
        assert r.status_code == 201
        game_id = r.json()["id"]

        r = requests.put(f"{api_url}/games/{game_id}", json={"stock": 0})
        assert r.status_code == 200
        assert r.json()["stock"] == 0

        r = requests.get(f"{api_url}/games/{game_id}")
        assert r.status_code == 200
        assert r.json()["stock"] == 0


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Tests de robustesse
# ════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestRobustesse:
    """
    Ces tests valident le comportement de l'API sous des conditions inhabituelles.
    """

    def test_requetes_concurrentes(self, api_url):
        """
        TODO — Envoyer 10 requêtes GET /games en parallèle avec threading.
        Vérifier que toutes retournent 200.

        Indice :
            import threading
            results = []
            def call(): results.append(requests.get(f"{api_url}/games").status_code)
            threads = [threading.Thread(target=call) for _ in range(10)]
            ...
        """
        # À compléter
        results = []

        def call() :
            try:
                r = requests.get(f"{api_url}/games")
                results.append(r.status_code)
            except Exception :
                results.append(None)

        threads = [threading.Thread(target=call) for _ in range(10)]

        for t in threads :
            t.start()
        for t in threads :
            t.join()

        assert len(results) == 10
        assert all(status == 200 for status in results)

    def test_payload_json_malforme(self, api_url):
        """
        TODO — POST /games avec un body non-JSON (texte brut).
        L'API doit retourner 400 sans crasher.
        """
        # À compléter
        headers = {"Content-Type": "application/json"}
        r = requests.post(
            f"{api_url}/games",
            data="ceci n'est pas un json valide",
            headers=headers,
        )
        assert r.status_code == 400


# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Choix libres (à justifier dans le README)
# ════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestChoixLibresIntegration:
    """
    Ajoutez ici les scénarios d'intégration que VOUS jugez critiques.

    Pensez aux questions suivantes :
    - Quels enchaînements d'appels représentent un vrai usage de l'API ?
    - Qu'est-ce qui ne peut être testé qu'avec un serveur réel (pas un client Flask) ?
    - Y a-t-il des conditions de bord qui ne se voient qu'en intégration ?

    Documentez vos choix dans le README.
    """

    def test_featured_endpoint_filtrage_et_tri(self, api_url):
        """
        Vérifie que l'endpoint /games/featured :
        - Retourne uniquement des jeux payants (price > 0)
        - Retourne uniquement des jeux en stock (stock > 0)
        - Trie les jeux par rating décroissant
        """
        payloads = [
            {"title": "Featured High", "genre": "Action", "price": 20, "rating": 4.9, "stock": 10},
            {"title": "Featured Mid", "genre": "Action", "price": 15, "rating": 3.5, "stock": 10},
            {"title": "Free Game", "genre": "Action", "price": 0, "rating": 5.0, "stock": 10},
            {"title": "Out Of Stock", "genre": "Action", "price": 25, "rating": 4.8, "stock": 0},
        ]

        for payload in payloads:
            requests.post(f"{api_url}/games", json=payload)

        r = requests.get(f"{api_url}/games/featured?limit=3")
        assert r.status_code == 200
        data = r.json()

        assert "featured" in data
        featured = data["featured"]

        assert len(featured) <= 3
        assert all(g["price"] > 0 for g in featured)
        assert all(g["stock"] > 0 for g in featured)

        ratings = [g["rating"] for g in featured]
        assert ratings == sorted(ratings, reverse=True)
