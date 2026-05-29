# Cyber Ticket & TPRM — Projet Mistral AI Workflows

Guide simple pour comprendre, lancer et présenter le projet pendant le hackathon.

## 1. Objectif du projet

Ce projet contient deux workflows Mistral AI Studio :

1. **Cyber Ticket Analysis**  
   Analyse des tickets cybersécurité à partir de plusieurs sources :
   - texte libre ;
   - logs techniques ;
   - PDF ;
   - images.

2. **Third Party Risk Analysis / TPRM**  
   Analyse des risques fournisseurs à partir de :
   - descriptions fournisseurs ;
   - questionnaires sécurité ;
   - emails ;
   - PDF ;
   - images.

L’objectif est de montrer qu’on peut construire un assistant capable de lire plusieurs formats, extraire les informations utiles, calculer un niveau de risque, puis retourner une réponse structurée en JSON.

---

## 2. Définitions simples

### Mistral AI

Mistral AI fournit des modèles d’intelligence artificielle capables de comprendre du texte, générer du texte, analyser du code, extraire des informations, traiter des documents, etc.

### Mistral AI Studio

Studio est l’espace où on peut créer, enregistrer, tester et exécuter des workflows IA.

### Workflow

Un **workflow** est une suite d’étapes.  
Il décrit **quoi faire et dans quel ordre**.

Exemple :

```text
input utilisateur
→ parser les données
→ lire les PDF avec OCR
→ construire un texte propre
→ appeler Mistral
→ retourner un JSON structuré
```

### Activity

Une **activity** est une étape concrète qui fait du travail.

Exemples :

- lire un PDF avec OCR ;
- appeler un modèle Mistral ;
- parser un input ;
- extraire un JSON.

Une bonne règle mentale :

```text
Workflow = chef d’orchestre
Activity = tâche concrète
```

### Worker

Un **worker** est ton programme local qui se connecte à Mistral Studio.  
Il dit à Mistral : “je suis disponible pour exécuter ces workflows”.

Quand tu fais :

```bash
make start-worker
```

ton worker démarre et enregistre tes workflows dans Studio.

### OCR

OCR signifie **Optical Character Recognition**.  
En français : reconnaissance optique de caractères.

Ça sert à lire du texte dans :

- un PDF ;
- une image ;
- un screenshot ;
- un scan.

### JSON

JSON est un format structuré très utilisé pour échanger des données.

Exemple :

```json
{
  "ticket_id": "TICKET-001",
  "criticite": "elevee",
  "score_risque": 75
}
```

Dans ce projet, on force le modèle à répondre en JSON pour pouvoir exploiter automatiquement la réponse.

---

## 3. Architecture du projet

Structure recommandée :

```text
cyber_ticket/
├── Makefile
├── pyproject.toml
├── .env
├── .gitignore
├── entrypoints/
│   ├── __init__.py
│   └── dev.py
└── src/
    ├── discover.py
    └── workflows/
        ├── __init__.py
        ├── common/
        │   ├── __init__.py
        │   ├── models.py
        │   └── ocr.py
        ├── cyber_ticket/
        │   ├── __init__.py
        │   ├── workflow.py
        │   ├── models.py
        │   ├── parser.py
        │   ├── prompt.py
        │   ├── analysis.py
        │   └── utils.py
        └── tprm/
            ├── __init__.py
            ├── workflow.py
            ├── models.py
            ├── parser.py
            ├── prompt.py
            └── analysis.py
```

---

## 4. Fichiers importants

### `src/discover.py`

Ce fichier dit au worker quels workflows charger.

```python
"""Discover and run local Mistral workflows."""

import mistralai.workflows as workflows

from src.workflows.cyber_ticket.workflow import CyberTicketWorkflow
from src.workflows.tprm.workflow import TPRMWorkflow


async def main() -> None:
    """Start the local worker with all available workflows."""

    workflows_to_run = [
        CyberTicketWorkflow,
        TPRMWorkflow,
    ]

    print(
        "Discovered workflow(s): "
        + ", ".join(workflow.__name__ for workflow in workflows_to_run)
    )

    await workflows.run_worker(workflows_to_run)
```

### `entrypoints/dev.py`

Ce fichier lance le worker en local.

```python
"""Dev entrypoint for the local Mistral Workflows worker."""

import asyncio

from src.discover import main


if __name__ == "__main__":
    asyncio.run(main())
```

### `src/workflows/common/ocr.py`

Ce fichier contient l’OCR partagé par les deux workflows.

Il est dans `common/` parce que le cas cyber et le cas TPRM ont tous les deux besoin de lire des PDF ou des images.

### `src/workflows/cyber_ticket/`

Dossier du cas 1 : analyse de tickets cyber.

### `src/workflows/tprm/`

Dossier du cas 2 : analyse des risques fournisseurs.

---

## 5. Installer le projet

Depuis la racine du projet :

```bash
cd /home/egravagn/Documents/cyber_ticket
make installdeps
```

La commande lance :

```bash
uv sync
```

Elle installe les dépendances définies dans `pyproject.toml`.

---

## 6. Configurer la clé Mistral

Créer un fichier `.env` :

```env
MISTRAL_API_KEY=ta_cle_mistral_ici
DEPLOYMENT_NAME=cyber-ticket
```

Puis charger les variables :

```bash
set -a
source .env
set +a
```

Vérifier que la clé est chargée :

```bash
echo $MISTRAL_API_KEY
```

Important : il ne faut jamais push `.env`.

---

## 7. Lancer les workflows

Depuis la racine :

```bash
make start-worker
```

Tu dois voir un message du type :

```text
Discovered workflow(s): CyberTicketWorkflow, TPRMWorkflow
```

Dans Mistral Studio, tu verras ensuite deux workflows :

```text
Cyber Ticket Analysis
Third Party Risk Analysis
```

Le choix du workflow dans Studio vient du décorateur Python :

```python
@workflows.workflow.define(
    name="cyber-ticket-analysis",
    workflow_display_name="Cyber Ticket Analysis",
)
```

et :

```python
@workflows.workflow.define(
    name="third-party-risk-analysis",
    workflow_display_name="Third Party Risk Analysis",
)
```

---

# Partie 1 — Workflow Cyber Ticket Analysis

## 8. Objectif du workflow cyber

Le workflow cyber analyse plusieurs tickets de cybersécurité.

Chaque ticket peut contenir :

- du texte ;
- des logs ;
- un PDF ;
- une image.

Le workflow retourne :

- une analyse par ticket ;
- une synthèse globale ;
- une liste des tickets prioritaires.

---

## 9. Pipeline cyber

```text
CyberTicketInput
→ parse_cyber_input()
→ build_raw_content()
→ OCR si PDF/image
→ analyse_ticket()
→ BatchCyberAnalysis
```

### Étape 1 : input

Exemple d’entrée :

```json
{
  "tickets": [
    {
      "ticket_id": "TICKET-001",
      "ticket_text": "marie.dupont signale des notifications MFA non demandées.",
      "logs": [
        {
          "timestamp": "2026-05-25 03:19:02",
          "level": "ERROR",
          "event": "vpn_login_success",
          "user": "marie.dupont",
          "country": "Russia"
        }
      ]
    }
  ]
}
```

### Étape 2 : parsing

Le parser transforme chaque source en bloc texte :

```text
--- TICKET: TICKET-001 | SOURCE: text ---
...

--- TICKET: TICKET-001 | SOURCE: logs ---
...
```

### Étape 3 : OCR

Si le ticket contient un PDF ou une image, le workflow appelle `ocr_document()`.

### Étape 4 : analyse IA

Le prompt demande au modèle :

- d’analyser chaque ticket séparément ;
- de ne pas mélanger les tickets ;
- de calculer un score ;
- de retourner uniquement du JSON.

---

## 10. Sortie cyber attendue

```json
{
  "analyses": [
    {
      "ticket_id": "TICKET-001",
      "resume": "Suspicion de compromission du compte.",
      "type_incident": "compromission de compte",
      "utilisateur": "marie.dupont",
      "application": "VPN",
      "criticite": "elevee",
      "score_risque": 75,
      "signaux_detectes": [
        "MFA non demandé",
        "connexion réussie suspecte",
        "pays inhabituel"
      ],
      "elements_suspects": [
        "notifications MFA non demandées",
        "connexion depuis la Russie"
      ],
      "donnees_manquantes": [
        "confirmation utilisateur",
        "historique de connexion"
      ],
      "actions_recommandees": [
        "Révoquer les sessions",
        "Réinitialiser le mot de passe",
        "Analyser les logs VPN"
      ],
      "validation_humaine": true,
      "justification": "Plusieurs signaux indiquent une compromission possible."
    }
  ],
  "synthese_globale": "Un ticket prioritaire détecté.",
  "tickets_prioritaires": ["TICKET-001"]
}
```

---

## 11. Différence entre les champs cyber

### `signaux_detectes`

Ce sont les règles qui ont influencé le score.

Exemple :

```json
["MFA non demandé", "connexion réussie suspecte"]
```

### `elements_suspects`

Ce sont les faits observés dans les données.

Exemple :

```json
["12 notifications MFA", "connexion à 03:19"]
```

### `donnees_manquantes`

Ce sont les informations qui manquent pour confirmer l’analyse.

Exemple :

```json
["IP complète", "confirmation utilisateur"]
```

### `actions_recommandees`

Ce sont les prochaines actions concrètes.

Exemple :

```json
["Bloquer l'IP", "Contacter l'utilisateur"]
```

---

## 12. Grille de scoring cyber

Le prompt utilise une grille simple :

```text
connexion réussie suspecte : +30
pays inhabituel : +20
plusieurs échecs de connexion : +15
MFA non demandé ou MFA bombing : +25
compte admin ou compte sensible : +25
export massif de données : +40
malware actif ou ransomware : +50
utilisateur nie être à l'origine de l'action : +20
utilisateur confirme que l'action est légitime : -30
phishing reçu mais lien non cliqué : -15
contexte professionnel cohérent : -30
```

Criticité :

```text
0 à 24 : faible
25 à 49 : moyenne
50 à 79 : elevee
80 à 100 : critique
```

---

# Partie 2 — Workflow Third Party Risk Analysis / TPRM

## 13. Objectif du workflow TPRM

TPRM signifie **Third Party Risk Management**.

En français : gestion des risques liés aux fournisseurs externes.

Le workflow sert à analyser le risque cybersécurité d’un fournisseur.

Il peut lire :

- une description fournisseur ;
- un questionnaire ;
- un email ;
- un PDF ;
- une image.

Il retourne :

- une analyse par fournisseur ;
- un score de risque ;
- les risques détectés ;
- les informations manquantes ;
- les exceptions ;
- les recommandations ;
- une synthèse globale.

---

## 14. Pipeline TPRM

```text
TPRMInput
→ parse_tprm_input()
→ build_raw_content()
→ OCR si PDF/image
→ analyse_supplier_risk()
→ BatchTPRMAnalysis
```

---

## 15. Exemple input TPRM

```json
{
  "suppliers": [
    {
      "supplier_id": "SUP-001",
      "supplier_name": "CloudPay Europe",
      "description": "Fournisseur SaaS de paiement qui traitera des données clients.",
      "documents": [
        {
          "document_id": "DOC-001",
          "document_type": "questionnaire",
          "content": "Le fournisseur héberge les données en Allemagne. TLS est activé. Le chiffrement au repos n'est pas précisé. Un DPA est fourni. Deux sous-traitants cloud sont mentionnés mais non détaillés."
        }
      ]
    }
  ]
}
```

---

## 16. Sortie TPRM attendue

```json
{
  "analyses": [
    {
      "supplier_id": "SUP-001",
      "supplier_name": "CloudPay Europe",
      "summary": "Fournisseur SaaS traitant des données clients.",
      "risk_level": "moyen",
      "risk_score": 45,
      "risks_detected": [
        "données clients traitées",
        "chiffrement au repos non précisé",
        "sous-traitants non détaillés"
      ],
      "missing_information": [
        "preuve du chiffrement au repos",
        "liste détaillée des sous-traitants"
      ],
      "exceptions": ["certification sécurité non fournie"],
      "recommendations": [
        "Demander la preuve du chiffrement au repos",
        "Demander la liste des sous-traitants",
        "Faire valider par l'équipe sécurité"
      ],
      "human_validation_required": true,
      "justification": "Le fournisseur traite des données clients et certaines garanties sont manquantes."
    }
  ],
  "global_summary": "Un fournisseur nécessite une validation humaine.",
  "priority_suppliers": ["SUP-001"]
}
```

---

## 17. Grille de scoring TPRM

```text
données sensibles traitées : +25
accès à des données clients : +25
accès administrateur ou API sensible : +30
chiffrement non mentionné : +30
absence de certification sécurité : +15
absence de plan de réponse à incident : +20
hébergement hors Union Européenne : +20
sous-traitants non déclarés ou non détaillés : +20
RGPD/DPA manquant : +35
absence de sauvegarde ou de plan de reprise d’activité : +20
```

Points rassurants :

```text
certification ISO 27001 ou SOC 2 valide : -20
chiffrement au repos et en transit documenté : -20
hébergement dans l’Union Européenne : -10
DPA ou contrat RGPD fourni : -15
plan de réponse à incident documenté : -10
plan de sauvegarde documenté : -10
```

Niveau de risque :

```text
0 à 24 : faible
25 à 49 : moyen
50 à 79 : eleve
80 à 100 : critique
```

---

# Partie 3 — Fonctionnalités Mistral AI Studio vues dans le projet

## 18. Fonctionnalités utilisées

### Workflows

Utilisés pour orchestrer plusieurs étapes.

Dans le projet :

- `CyberTicketWorkflow`
- `TPRMWorkflow`

### Activities

Utilisées pour les actions concrètes :

- parsing de l’input ;
- OCR ;
- appel au modèle.

### Worker local

Le worker exécute le code localement et se connecte à Studio.

### Workflow display name

Permet d’afficher un nom lisible dans Studio.

### OCR

Utilisé pour lire les PDF et images.

### Chat completion

Utilisé pour demander au modèle de produire l’analyse.

### JSON structuré

Le prompt impose une réponse JSON.

### Déploiements

`DEPLOYMENT_NAME` permet d’isoler les workers et leurs workflows dans un workspace.

---

## 19. Fonctionnalités Mistral Studio utiles à connaître

Selon la documentation Mistral, les workflows sont utiles pour :

- pipelines LLM multi-étapes ;
- processus human-in-the-loop ;
- tâches planifiées ;
- orchestration multi-agents ;
- workflows résistants aux crashs et redémarrages.

Les workflows peuvent coordonner des activités, attendre des événements externes, gérer des timers et décider de la suite selon les résultats.

Les activités peuvent faire des appels API, du traitement de fichiers, des appels LLM ou tout autre travail concret.

Le plugin Mistral donne accès aux appels LLM, agents, embeddings, OCR et autres intégrations.

---

# Partie 4 — Erreurs rencontrées et solutions

## 20. `401 Unauthorized`

Signifie que la clé Mistral est absente ou invalide.

À vérifier :

```bash
echo $MISTRAL_API_KEY
```

Puis :

```bash
set -a
source .env
set +a
```

## 21. `More than one activity named parse_input`

Tu avais deux activities avec le même nom.

Solution :

- `parse_cyber_input` pour le cas cyber ;
- `parse_tprm_input` pour le cas TPRM.

Dans un même worker, les activity names doivent être uniques.

## 22. JSON tronqué

Le modèle avait commencé à répondre mais n’avait pas fermé le JSON.

Solutions :

- `max_tokens=4096` ;
- `temperature=0` ;
- prompt compact ;
- limiter le nombre de tickets ;
- limiter `raw_content`.

## 23. OCR avec mauvais argument

`mistralai_ocr(document_url=...)` ne marchait pas.

La bonne logique dans ce projet :

```python
request = mistralai_models.OCRRequest(
    model="mistral-ocr-latest",
    document=document,
)

ocr_result = await mistralai_ocr(request)
```

## 24. `localhost` pour les PDF

Un PDF en `localhost` n’est pas accessible par l’API Mistral.

Il faut une URL publique :

- GitHub raw ;
- serveur public ;
- ngrok ;
- Cloudflare tunnel.

---

# Partie 5 — Commandes utiles

## Installer

```bash
make installdeps
```

## Charger l’environnement

```bash
set -a
source .env
set +a
```

## Lancer le worker

```bash
make start-worker
```

## Nettoyer

Dans le Makefile :

```makefile
clean:
	find . -type f -name "*.bak" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
```

Puis :

```bash
make clean
```

## Vérifier avant push

```bash
git status
```

Ne jamais push :

- `.env`
- `.venv/`
- `__pycache__/`
- `.ruff_cache/`
- `*.pyc`
- `*.bak`

---

# Partie 6 — Démo hackathon

## 25. Pitch court

Ce projet montre deux assistants IA basés sur Mistral Workflows.

Le premier analyse des tickets cybersécurité multi-sources : texte, logs, PDF ou image. Il détecte les risques, calcule une criticité et propose des actions.

Le second analyse des fournisseurs externes dans une logique TPRM. Il lit les documents fournisseur, détecte les risques, signale les informations manquantes et produit un score de risque.

Dans les deux cas, le workflow garde une validation humaine quand le risque est important ou quand les informations sont insuffisantes.

## 26. Ce que tu peux montrer

1. Lancer le worker avec `make start-worker`.
2. Ouvrir Mistral Studio.
3. Choisir `Cyber Ticket Analysis`.
4. Envoyer un JSON avec plusieurs tickets.
5. Montrer le JSON de sortie.
6. Choisir `Third Party Risk Analysis`.
7. Envoyer un JSON fournisseur.
8. Montrer le score et les recommandations.

## 27. Phrase simple pour expliquer l’architecture

> Le workflow reçoit des données hétérogènes, les normalise, lit les documents avec OCR si nécessaire, construit un contexte propre, appelle un modèle Mistral, puis retourne une réponse JSON exploitable par une équipe sécurité.

---

## 28. Prochaines améliorations possibles

- Ajouter une vraie validation humaine dans le workflow.
- Ajouter une base de connaissances interne.
- Ajouter un export PDF du rapport final.
- Ajouter un calcul de score en Python au lieu de tout laisser au modèle.
- Ajouter un frontend simple.
- Ajouter des tests unitaires.
- Ajouter un mode “expliquer la décision”.
- Ajouter des logs plus propres.
