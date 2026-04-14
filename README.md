# NexusGame — Suite de Tests

> Projet final 2TES3 — Tests Avancés & Automatisation

## Présentation du projet

<!-- Décrivez le contexte du projet et l'API GameStore. -->

---

## Structure du repo

```
NexusGame/
├── app_gamestore.py
├── requirements.txt
├── tests/
│   ├── conftest.py
│   ├── test_unit.py
│   ├── test_integration.py
│   ├── test_ui.py
│   ├── gamestore_collection.json
│   ├── locust_gamestore.py
│   └── pages/
│       ├── home_page.py
│       └── add_game_modal.py
└── .github/
    └── workflows/
        └── tests.yml
```

---

## Lancer les tests

```bash
# Installation
pip install -r requirements.txt
playwright install chromium
npm install -g newman newman-reporter-htmlextra
pip install locust

# Démarrer l'API
python app_gamestore.py

# Tests unitaires
pytest tests/test_unit.py -v --cov=app_gamestore --cov-report=html

# Tests d'intégration
pytest tests/test_integration.py -v -m integration

# Tests UI
pytest tests/test_ui.py -v --headed

# Collection Newman
newman run tests/gamestore_collection.json --env-var "base_url=http://localhost:5000" --reporters cli,htmlextra

# Tests de charge
locust -f tests/locust_gamestore.py --host=http://localhost:5000 --headless -u 20 -r 2 --run-time 30s
```

---

## Mes choix techniques

### Pyramide de tests adoptée

<!-- Quelle pyramide avez-vous choisie et pourquoi ? -->
La stratégie de tests mise en place pour le projet NexusGame – GameStore API suit la pyramide de tests classique, qui privilégie un grand nombre de tests rapides et fiables à la base, et un nombre plus limité de tests coûteux en ressources au sommet.

 Structure de la pyramide
Tests unitaires (majoritaires)
Objectif : Vérifier le comportement des endpoints et de la logique métier de manière isolée.
Implémentation : Utilisation de pytest avec le FlaskClient et une base de données temporaire réinitialisée à chaque test (fixture avec un scope function).

Tests d’intégration (quantité modérée)

Objectif : Vérifier l’interaction entre les différentes couches de l’application (API Flask, logique métier et base de données SQLite).
Implémentation : Les tests utilisent une base de données temporaire, ce qui permet de tester le comportement réel du système sans dépendances externes.

Tests end-to-end (E2E) – non inclus

### Pipeline CI vs local

<!-- Qu'est-ce qui tourne en CI, qu'est-ce qui reste en local, et pourquoi ? -->

La stratégie de répartition entre les exécutions locales et celles réalisées dans le pipeline d’Intégration Continue (CI) vise à garantir la qualité du code tout en optimisant le temps de développement.
Tests unitaires et d’intégration et Couverture de code

Le pipeline CI (par exemple avec GitHub Actions, GitLab CI ou Jenkins) exécute automatiquement les étapes suivantes à chaque push ou pull request :

Installation des dépendances, Exécution des tests , Analyse statique du code et la Vérification de la couverture

### Mes choix libres

<!-- Pour chaque test libre : ce qu'il teste et pourquoi vous l'avez choisi. -->

j'ai fais deux tests principalement pour tester le rating pour observer si l'api détecte bien que l'on peut avoir une note = 0 ou égal à 5 pour voir si les bornes sont acceptées.
De plus j'ai fais un test avec un prix égal à 0, le prix négatif est testé mais il est possible qu'un jeu coûte 0 et qu'il soit gratuit
Enfin j'ai fais un test avec un body vide pour observer si une potentielle erreur arrive si on ne remplit rien 


Ce test d’intégration vérifie le comportement réel de l’endpoint /games/featured dans des conditions proches de la production.


# test_featured_endpoint_filtrage_et_tri
Objectifs du test

Le test valide trois règles métier essentielles :

Les jeux affichés dans la section “featured” doivent être payants (price > 0)
Les jeux doivent être disponibles en stock (stock > 0)
Les jeux doivent être triés par note (rating) décroissante


# différence entre test unitaire et intégration

Les tests unitaires vérifient le comportement de fonctions ou composants isolés, sans dépendre d’un serveur réel ni d’une base de données en conditions réelles.
Les tests d’intégration vérifient le comportement de l’API dans un environnement proche de la réalité, en utilisant un serveur Flask réellement lancé.


# Postman
Dans postman j'ai rajouté comme scénario d'un get avec un ID inexistant afin de vérifier que l'api ne renvoie pas une 200 vide , qu'elle gère correctement les erreurs et ne crash pas en renvoyant un message d'erreur clair et compréhensible 


# Playwright
J'ai ajouté un test qui permet de mettre plus de filtres afin d'avoir une recherche plus poussée .


##  NGS-105 — Test de charge avec Locust

### Objectif
Valider le comportement de l’API GameStore sous charge à l’aide de Locust, en simulant des utilisateurs naviguant sur les principaux endpoints.


### Représentation du test locust

| Endpoint | p50 (ms) | p95 (ms) | Nombre de requêtes |
|---------|----------|----------|-------------------|
| /games | 2000 | 2100 | 196 |
| /games/[id] | 2000 | 2100 | 85 |
| /games?genre=[genre] | 2000 | 2100 | 129 |
| /games/featured | 2000 | 2100 | 53 |
| /games/stats | 2000 | 2100 | 48 |
| /health | 2000 | 2100 | 78 |
| POST /games | 2000 | 2100 | 54 |
| DELETE /games/[id] | 2000 | 2100 | 54 |

### Analyse
Les temps de réponse sont stables mais relativement élevés (~2 secondes) pour l’ensemble des endpoints

Le rapport HTML généré par Locust est disponible dans : `reports/locust_report.html`.
---

## Investigation de l'API

<!-- Ce que vous avez observé en testant l'API.
     Comportements inattendus, hypothèses, ce que vos tests révèlent. -->

Lors de l'exécution de la suite de tests unitaires, plusieurs comportements inattendus ont été identifiés. Ces échecs sont intentionnels et permettent de mettre en évidence des défauts dans l’implémentation de l’API `GameStore`.

### 1. Suppression d’un jeu – Code de statut incorrect

- **Test concerné :** `TestGameCRUD::test_delete_jeu`
- **Comportement attendu :** L’endpoint `DELETE /games/{id}` doit retourner un code **204 No Content** après une suppression réussie.
- **Comportement observé :** L’API retourne un code **200 OK**.
- **Hypothèse :** L’implémentation renvoie une réponse JSON avec un message, au lieu d’une réponse vide conforme aux bonnes pratiques REST.
- **Correction proposée :** Modifier l’endpoint pour retourner `Response(status=204)`.

### 2. Endpoint `/games/featured` – Tri incorrect

- Test concerné : `TestFeatured::test_featured_tries_par_rating_decroissant`
- Comportement attendu : Les jeux doivent être triés par **rating décroissant**.
- Comportement observé : Les jeux sont retournés dans un ordre non trié ou croissant.
- Hypothèse : La requête SQL ne contient pas de clause `ORDER BY rating DESC`.
- Correction proposée : Ajouter `ORDER BY rating DESC` dans la requête.

### 3. Présence de jeux gratuits dans `/games/featured`

- Test concerné : `TestFeatured::test_featured_sans_jeux_gratuits`
- Comportement attendu : Les jeux gratuits (`price = 0`) ne doivent pas apparaître dans la liste des jeux mis en avant.
- Comportement observé : Des jeux gratuits sont inclus dans la réponse.
- Hypothèse : L’endpoint ne filtre pas correctement les jeux avec `price = 0`.
- Correction proposée : Ajouter la condition `WHERE price > 0` dans la requête SQL.

---

## Pipeline CI/CD

Le projet utilise **GitHub Actions** pour automatiser les tests et l’intégration continue.

À chaque push ou pull request sur la branche principale :
- Installation des dépendances
- Exécution des tests automatisés
- Analyse de qualité du code (si configurée)
- Vérification du bon fonctionnement de l’application

Le pipeline permet de détecter rapidement les erreurs et d’assurer la stabilité du projet.

## Ce que j'ai appris

- Mise en place d’un pipeline CI/CD avec GitHub Actions
- Utilisation de Docker pour exécuter des outils de sécurité (ZAP)
- Importance des bonnes pratiques de sécurité dans une application web
