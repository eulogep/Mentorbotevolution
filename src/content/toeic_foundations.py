"""Paquet éditorial initial pour le parcours TOEIC.

Les cartes sont des formulations originales consacrées à la communication
professionnelle. Elles ne reproduisent ni questions, ni passages, ni audio
d'un examen TOEIC. Elles servent de point de départ au rappel actif et non de
prédiction de score.
"""

from copy import deepcopy


TOEIC_FOUNDATIONS_PACK_ID = "toeic-business-vocabulary-foundations-v1"

TOEIC_FOUNDATIONS_PACK = {
    "id": TOEIC_FOUNDATIONS_PACK_ID,
    "title": "TOEIC — vocabulaire professionnel : socle initial",
    "template_id": "toeic-foundations",
    "learning_domain": "language",
    "description": (
        "36 cartes originales de vocabulaire et collocations pour les réunions, "
        "les courriels et projets, les ressources humaines, la relation client, "
        "la logistique et les rapports financiers."
    ),
    "source": "editorial_original",
    "license_note": "Contenu original du projet Mentor Evolution ; aucune question d’examen n’est reproduite.",
    "learning_design": {
        "method": "rappel actif avec correction concise, collocation et exemple original",
        "usage": "Répondre sans regarder, vérifier la correction, puis choisir une évaluation honnête.",
        "scope": "Socle lexical professionnel ; à compléter par écoute, lecture et production écrite.",
    },
    "cards": [
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Réunion — Complétez : ‘Please send the ___ before the meeting.’ (ordre des sujets à traiter)",
            "answer": "agenda — ordre des sujets d’une réunion. Collocation : set / send the agenda. Exemple : ‘The manager sent the agenda on Monday.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "meetings", "agenda"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Réunion — Quel mot anglais désigne le compte rendu officiel d’une réunion ?",
            "answer": "minutes — compte rendu de réunion. Collocation : take / approve the minutes. Exemple : ‘Nina took the minutes during the meeting.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "meetings", "minutes"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Réunion — Complétez : ‘All department heads will ___ the conference.’ (être présents)",
            "answer": "attend — assister à un événement. Collocation : attend a meeting / conference. Exemple : ‘All department heads will attend the conference.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "meetings", "attend"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Réunion — Quel verbe signifie reporter une réunion à une date ultérieure ?",
            "answer": "postpone — reporter. Collocation : postpone a meeting until Friday. Exemple : ‘We postponed the meeting until Friday.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "meetings", "postpone"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Réunion — Complétez : ‘Could you ___ your availability by noon?’ (confirmer)",
            "answer": "confirm — confirmer. Collocation : confirm availability / an appointment. Exemple : ‘Could you confirm your availability by noon?’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "meetings", "confirm"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Réunion — Quel nom désigne un accord général atteint par un groupe ?",
            "answer": "consensus — accord général. Collocation : reach a consensus. Exemple : ‘The team reached a consensus after a short discussion.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "meetings", "consensus"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Courriel et projets — Quel nom anglais désigne une échéance à respecter ?",
            "answer": "deadline — échéance. Collocation : meet / extend a deadline. Exemple : ‘The design team met the deadline.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "email-projects", "deadline"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Courriel et projets — Complétez : ‘The updated ___ is attached to this email.’ (planning)",
            "answer": "schedule — planning, calendrier. Collocation : update a schedule. Exemple : ‘The updated schedule is attached to this email.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "email-projects", "schedule"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Courriel et projets — Quel verbe signifie remettre officiellement un document ou une proposition ?",
            "answer": "submit — remettre, soumettre. Collocation : submit a report / proposal. Exemple : ‘Please submit the report by Thursday.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "email-projects", "submit"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Courriel et projets — Complétez : ‘The director must ___ the final budget.’ (donner son accord)",
            "answer": "approve — approuver. Collocation : approve a budget / request. Exemple : ‘The director approved the final budget.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "email-projects", "approve"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Courriel et projets — Quelle expression signifie relancer quelqu’un après un premier échange ?",
            "answer": "follow up — relancer, assurer le suivi. Collocation : follow up on a request. Exemple : ‘I will follow up on your request tomorrow.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "email-projects", "follow-up"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Courriel et projets — Quel nom désigne un document joint à un email ?",
            "answer": "attachment — pièce jointe. Collocation : add / open an attachment. Exemple : ‘Please review the attachment before the call.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "email-projects", "attachment"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Ressources humaines — Quel nom anglais désigne une personne qui postule à un emploi ?",
            "answer": "applicant — candidat à un emploi. Collocation : qualified applicant. Exemple : ‘Each applicant completed an online form.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "human-resources", "applicant"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Ressources humaines — Quel mot désigne un poste vacant à pourvoir ?",
            "answer": "vacancy — poste vacant. Collocation : fill a vacancy. Exemple : ‘The company plans to fill the vacancy quickly.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "human-resources", "vacancy"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Ressources humaines — Complétez : ‘The company plans to ___ two engineers this year.’ (recruter)",
            "answer": "recruit — recruter. Collocation : recruit staff / employees. Exemple : ‘The company plans to recruit two engineers this year.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "human-resources", "recruit"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Ressources humaines — Quel nom désigne le programme d’accueil et d’intégration d’un nouvel employé ?",
            "answer": "orientation — programme d’accueil et d’intégration. Collocation : attend an orientation session. Exemple : ‘New employees attend orientation on their first day.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "human-resources", "orientation"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Ressources humaines — Quel nom désigne des avantages offerts en plus du salaire ?",
            "answer": "benefits — avantages sociaux. Collocation : employee benefits. Exemple : ‘Health insurance is one of the employee benefits.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "human-resources", "benefits"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Ressources humaines — Quel nom désigne une période d’essai ?",
            "answer": "probation — période d’essai. Collocation : probation period. Exemple : ‘Her probation period ends in September.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "human-resources", "probation"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Relation client — Quel nom désigne une estimation de prix envoyée avant une vente ?",
            "answer": "quote — devis. Collocation : provide / request a quote. Exemple : ‘We provided a quote for the maintenance service.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "customer-service", "quote"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Relation client — Quel document demande le paiement de biens ou services fournis ?",
            "answer": "invoice — facture. Collocation : issue / pay an invoice. Exemple : ‘The supplier issued the invoice yesterday.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "customer-service", "invoice"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Relation client — Quel document officiel autorise l’achat auprès d’un fournisseur ?",
            "answer": "purchase order — bon de commande. Collocation : place / process a purchase order. Exemple : ‘The buyer placed a purchase order for new monitors.’",
            "difficulty": "hard",
            "tags": ["toeic", "starter", "customer-service", "purchase-order"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Relation client — Quel verbe signifie négocier des conditions ou un prix ?",
            "answer": "negotiate — négocier. Collocation : negotiate terms / a contract. Exemple : ‘Both companies negotiated the contract terms.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "customer-service", "negotiate"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Relation client — Quel nom désigne une réclamation d’un client ?",
            "answer": "complaint — réclamation. Collocation : handle / file a complaint. Exemple : ‘The service team handled the complaint promptly.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "customer-service", "complaint"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Relation client — Quel nom désigne le remboursement d’un client ?",
            "answer": "refund — remboursement. Collocation : issue / request a refund. Exemple : ‘The store issued a refund within two days.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "customer-service", "refund"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Logistique et déplacements — Quel nom désigne un envoi de marchandises ?",
            "answer": "shipment — expédition, envoi. Collocation : track a shipment. Exemple : ‘You can track the shipment online.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "logistics-travel", "shipment"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Logistique et déplacements — Quel nom désigne la remise effective d’un colis ou d’une commande ?",
            "answer": "delivery — livraison. Collocation : delivery date / confirm delivery. Exemple : ‘The customer confirmed the delivery this morning.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "logistics-travel", "delivery"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Logistique et déplacements — Quel nom désigne le stock de produits disponible ?",
            "answer": "inventory — stock, inventaire. Collocation : check / manage inventory. Exemple : ‘The warehouse team checks inventory weekly.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "logistics-travel", "inventory"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Logistique et déplacements — Quel nom désigne le lieu où les marchandises sont entreposées ?",
            "answer": "warehouse — entrepôt. Collocation : warehouse manager. Exemple : ‘The warehouse is close to the airport.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "logistics-travel", "warehouse"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Logistique et déplacements — Quel nom désigne un programme détaillé de voyage ou de visite ?",
            "answer": "itinerary — itinéraire, programme de voyage. Collocation : travel itinerary. Exemple : ‘Your travel itinerary includes two client visits.’",
            "difficulty": "hard",
            "tags": ["toeic", "starter", "logistics-travel", "itinerary"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Logistique et déplacements — Quel verbe signifie fournir un hébergement ou s’adapter à un besoin ?",
            "answer": "accommodate — héberger, répondre à un besoin. Collocation : accommodate a request. Exemple : ‘The hotel can accommodate late arrivals.’",
            "difficulty": "hard",
            "tags": ["toeic", "starter", "logistics-travel", "accommodate"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Finances et rapports — Quel nom désigne le budget prévu pour une activité ?",
            "answer": "budget — budget. Collocation : stay within / approve a budget. Exemple : ‘The project stayed within its budget.’",
            "difficulty": "easy",
            "tags": ["toeic", "starter", "finance-reporting", "budget"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Finances et rapports — Quel nom désigne les revenus d’une entreprise issus de ses ventes ?",
            "answer": "revenue — chiffre d’affaires, recettes. Collocation : increase revenue. Exemple : ‘Online sales increased revenue last quarter.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "finance-reporting", "revenue"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Finances et rapports — Quel nom désigne une dépense engagée par l’entreprise ?",
            "answer": "expense — dépense. Collocation : reduce operating expenses. Exemple : ‘The team reduced travel expenses this year.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "finance-reporting", "expense"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Finances et rapports — Quel nom désigne une estimation de résultats futurs ?",
            "answer": "forecast — prévision. Collocation : sales forecast. Exemple : ‘The sales forecast was revised in April.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "finance-reporting", "forecast"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Finances et rapports — Quel adjectif signifie trimestriel ?",
            "answer": "quarterly — trimestriel. Collocation : quarterly report. Exemple : ‘The quarterly report is ready for review.’",
            "difficulty": "medium",
            "tags": ["toeic", "starter", "finance-reporting", "quarterly"],
        },
        {
            "concept_name": "Vocabulaire professionnel",
            "question": "Finances et rapports — Quel verbe signifie attribuer des ressources ou un budget ?",
            "answer": "allocate — attribuer, allouer. Collocation : allocate funds / resources. Exemple : ‘The board allocated funds to staff training.’",
            "difficulty": "hard",
            "tags": ["toeic", "starter", "finance-reporting", "allocate"],
        },
    ],
}


def get_starter_pack(template_id: str) -> dict | None:
    """Return a defensive copy of the starter pack associated with a template."""
    if template_id != TOEIC_FOUNDATIONS_PACK["template_id"]:
        return None
    return deepcopy(TOEIC_FOUNDATIONS_PACK)
