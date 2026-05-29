def build_analysis_prompt(raw_content: str) -> str:
    """Construit le prompt envoyé à Mistral."""

    return f"""
Tu es un assistant SOC.

SOC signifie Security Operations Center.
C'est l'équipe qui surveille les alertes de cybersécurité.

Tu dois analyser le contenu suivant.
Il est organisé par blocs :
--- TICKET: ticket_id | SOURCE: type ---

Chaque ticket peut avoir plusieurs sources :
- text
- logs
- pdf
- image

CONTENU :
\"\"\"
{raw_content}
\"\"\"

Réponds uniquement en JSON valide.
Ne mets pas de markdown.
Ne mets aucun texte avant ou après le JSON.

Format obligatoire :
{{
  "analyses": [
    {{
      "ticket_id": "string",
      "resume": "string",
      "type_incident": "string",
      "utilisateur": "string ou null",
      "application": "string ou null",
      "criticite": "faible | moyenne | elevee | critique",
      "score_risque": 0,
      "signaux_detectes": ["string"],
      "elements_suspects": ["string"],
      "donnees_manquantes": ["string"],
      "actions_recommandees": ["string"],
      "validation_humaine": true,
      "justification": "string"
    }}
  ],
  "synthese_globale": "string",
  "tickets_prioritaires": ["ticket_id"]
}}

Règles importantes :
- Crée une analyse séparée pour chaque ticket_id.
- Si un ticket a plusieurs sources, fusionne ses informations.
- Ne mélange jamais les informations de deux tickets différents.
- Si le contenu contient plus de 5 tickets, analyse seulement les 5 plus risqués.
- Les réponses doivent être courtes.
- Maximum 3 signaux_detectes par ticket.
- Maximum 3 elements_suspects par ticket.
- Maximum 3 donnees_manquantes par ticket.
- Maximum 3 actions_recommandees par ticket.
- tickets_prioritaires doit contenir les ticket_id triés du plus grave au moins grave.
- Ne pas inventer d'information absente du contenu.

Grille de scoring :
- connexion réussie suspecte : +30
- pays inhabituel : +20
- plusieurs échecs de connexion : +15
- MFA non demandé ou MFA bombing : +25
- compte admin ou compte sensible : +25
- export massif de données : +40
- malware actif ou ransomware : +50
- utilisateur nie être à l'origine de l'action : +20
- utilisateur confirme que l'action est légitime : -30
- phishing reçu mais lien non cliqué : -15
- contexte professionnel cohérent : -30

Criticité :
- 0 à 24 : faible
- 25 à 49 : moyenne
- 50 à 79 : elevee
- 80 à 100 : critique

Le score final doit rester entre 0 et 100.
La justification doit expliquer brièvement les critères utilisés.
"""
