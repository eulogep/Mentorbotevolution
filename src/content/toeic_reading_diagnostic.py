"""Diagnostic lecture original pour Mentor Evolution.

Les textes, questions, choix et corrections sont éditoriaux et originaux. Ce
paquet s’inspire de tâches de communication professionnelle, mais ne reproduit
aucun document, item ni corrigé d’ETS.
"""

from copy import deepcopy


TOEIC_READING_DIAGNOSTIC_ID = "toeic-reading-diagnostic-v1"

TOEIC_READING_DIAGNOSTIC = {
    "id": TOEIC_READING_DIAGNOSTIC_ID,
    "title": "Diagnostic lecture — anglais professionnel",
    "description": (
        "Diagnostic original de 19 items courts portant sur la grammaire, le vocabulaire, "
        "la cohésion et la compréhension de documents professionnels."
    ),
    "learning_domain": "language",
    "source": "editorial_original",
    "disclaimer": (
        "Ce diagnostic est une activité formative originale. Il ne constitue pas un test TOEIC officiel "
        "et ne fournit aucune estimation de score."
    ),
    "items": [
        {
            "id": "rd-01",
            "task_type": "sentence_completion",
            "target": "grammar",
            "scenario": "contract",
            "prompt": "The sales director ___ the contract yesterday.",
            "choices": ["approve", "approved", "approving", "has approve"],
            "correct_index": 1,
            "explanation": "‘Yesterday’ appelle ici le prétérit : ‘approved’.",
            "remediation": {
                "front": "Complétez : ‘The director ___ the contract yesterday.’",
                "back": "approved — prétérit de approve. Exemple : ‘The director approved the contract yesterday.’",
                "concept_name": "Prétérit en contexte professionnel",
                "tags": ["toeic", "diagnostic", "reading", "grammar", "past-simple"],
            },
        },
        {
            "id": "rd-02",
            "task_type": "sentence_completion",
            "target": "lexis",
            "scenario": "meeting",
            "prompt": "All participants ___ their availability before the meeting.",
            "choices": ["confirmed", "invented", "delivered", "borrowed"],
            "correct_index": 0,
            "explanation": "‘Confirm availability’ est une collocation professionnelle courante.",
            "remediation": {
                "front": "Quelle expression signifie confirmer ses disponibilités pour une réunion ?",
                "back": "confirm availability — confirmer ses disponibilités. Exemple : ‘Please confirm your availability by noon.’",
                "concept_name": "Collocations de réunion",
                "tags": ["toeic", "diagnostic", "reading", "lexis", "meetings"],
            },
        },
        {
            "id": "rd-03",
            "task_type": "sentence_completion",
            "target": "grammar",
            "scenario": "email",
            "prompt": "Please send the revised budget ___ noon on Friday.",
            "choices": ["by", "for", "during", "since"],
            "correct_index": 0,
            "explanation": "‘By noon’ exprime une échéance, au plus tard à midi.",
            "remediation": {
                "front": "Quelle préposition indique une échéance : ‘Please reply ___ Friday’ ?",
                "back": "by — au plus tard. Exemple : ‘Please reply by Friday.’",
                "concept_name": "Échéances et prépositions",
                "tags": ["toeic", "diagnostic", "reading", "grammar", "deadlines"],
            },
        },
        {
            "id": "rd-04",
            "task_type": "sentence_completion",
            "target": "grammar",
            "scenario": "maintenance",
            "prompt": "The equipment is ___ inspection until Thursday.",
            "choices": ["under", "between", "across", "toward"],
            "correct_index": 0,
            "explanation": "L’expression fixe est ‘under inspection’ : en cours d’inspection.",
            "remediation": {
                "front": "Complétez : ‘The equipment is ___ inspection.’",
                "back": "under — ‘under inspection’ signifie en cours d’inspection.",
                "concept_name": "Expressions professionnelles fixes",
                "tags": ["toeic", "diagnostic", "reading", "grammar", "fixed-expression"],
            },
        },
        {
            "id": "rd-05",
            "task_type": "sentence_completion",
            "target": "grammar",
            "scenario": "product-launch",
            "prompt": "The new service will be ___ next month.",
            "choices": ["launch", "launched", "launching", "launches"],
            "correct_index": 1,
            "explanation": "Après ‘will be’, la voix passive utilise le participe passé : ‘launched’.",
            "remediation": {
                "front": "Complétez : ‘The new service will be ___.’",
                "back": "launched — participe passé dans la forme passive. Exemple : ‘The service will be launched next month.’",
                "concept_name": "Voix passive en contexte professionnel",
                "tags": ["toeic", "diagnostic", "reading", "grammar", "passive"],
            },
        },
        {
            "id": "rd-06",
            "task_type": "sentence_completion",
            "target": "grammar",
            "scenario": "training",
            "prompt": "Employees ___ complete the safety training before Monday.",
            "choices": ["must", "must to", "are must", "musts"],
            "correct_index": 0,
            "explanation": "Le modal ‘must’ est suivi directement de la base verbale : ‘must complete’.",
            "remediation": {
                "front": "Quelle structure exprime une obligation : ‘Employees ___ complete the training’ ?",
                "back": "must complete — ‘must’ est suivi de la base verbale, sans ‘to’.",
                "concept_name": "Modaux et obligations",
                "tags": ["toeic", "diagnostic", "reading", "grammar", "modals"],
            },
        },
        {
            "id": "rd-07",
            "task_type": "sentence_completion",
            "target": "lexis",
            "scenario": "finance",
            "prompt": "Online sales increased the company’s ___ during the last quarter.",
            "choices": ["revenue", "vacancy", "itinerary", "warehouse"],
            "correct_index": 0,
            "explanation": "‘Revenue’ désigne les recettes ou le chiffre d’affaires d’une entreprise.",
            "remediation": {
                "front": "Quel mot anglais désigne les recettes ou le chiffre d’affaires ?",
                "back": "revenue — recettes, chiffre d’affaires. Collocation : increase revenue.",
                "concept_name": "Vocabulaire financier professionnel",
                "tags": ["toeic", "diagnostic", "reading", "lexis", "finance"],
            },
        },
        {
            "id": "rd-08",
            "task_type": "sentence_completion",
            "target": "lexis",
            "scenario": "logistics",
            "prompt": "You can track the ___ online with the reference number.",
            "choices": ["shipment", "orientation", "consensus", "benefit"],
            "correct_index": 0,
            "explanation": "Une ‘shipment’ est une expédition ; elle peut être suivie par un numéro de référence.",
            "remediation": {
                "front": "Quel mot anglais désigne une expédition de marchandises ?",
                "back": "shipment — expédition. Collocation : track a shipment.",
                "concept_name": "Vocabulaire logistique professionnel",
                "tags": ["toeic", "diagnostic", "reading", "lexis", "logistics"],
            },
        },
        {
            "id": "rd-09",
            "task_type": "sentence_completion",
            "target": "lexis",
            "scenario": "customer-service",
            "prompt": "The client requested a ___ after receiving the damaged item.",
            "choices": ["refund", "forecast", "minute", "agenda"],
            "correct_index": 0,
            "explanation": "Un ‘refund’ est un remboursement demandé après un problème de livraison ou de produit.",
            "remediation": {
                "front": "Quel mot anglais désigne un remboursement ?",
                "back": "refund — remboursement. Collocation : request / issue a refund.",
                "concept_name": "Vocabulaire de la relation client",
                "tags": ["toeic", "diagnostic", "reading", "lexis", "customer-service"],
            },
        },
        {
            "id": "rd-10",
            "task_type": "text_completion",
            "target": "cohesion",
            "scenario": "project-email",
            "passage": "Subject: Updated delivery date\n\nThe supplier has completed the quality checks. ___, the delivery can leave the warehouse on Wednesday.",
            "prompt": "Which phrase best completes the email?",
            "choices": ["As a result", "For example", "In contrast", "Meanwhile yesterday"],
            "correct_index": 0,
            "explanation": "La seconde phrase est une conséquence des contrôles terminés ; ‘As a result’ relie correctement les idées.",
            "remediation": None,
        },
        {
            "id": "rd-11",
            "task_type": "text_completion",
            "target": "cohesion",
            "scenario": "office-notice",
            "passage": "The main meeting room is unavailable this morning. ___, the training session will take place in Room 204.",
            "prompt": "Which connector is most appropriate?",
            "choices": ["Therefore", "Although", "Unless", "Before"],
            "correct_index": 0,
            "explanation": "Le changement de salle est la conséquence de l’indisponibilité ; ‘Therefore’ convient.",
            "remediation": None,
        },
        {
            "id": "rd-12",
            "task_type": "text_completion",
            "target": "cohesion",
            "scenario": "job-posting",
            "passage": "Applicants need two years of customer-service experience. ___, they should be comfortable using spreadsheet software.",
            "prompt": "Which addition completes the list of requirements?",
            "choices": ["In addition", "Instead", "Otherwise", "Previously"],
            "correct_index": 0,
            "explanation": "‘In addition’ ajoute une seconde exigence sans marquer d’opposition.",
            "remediation": None,
        },
        {
            "id": "rd-13",
            "task_type": "text_completion",
            "target": "cohesion",
            "scenario": "client-update",
            "passage": "Our technician will visit the site on Tuesday. ___ the repair takes longer than expected, we will provide a temporary replacement unit.",
            "prompt": "Which word best completes the condition?",
            "choices": ["If", "Because", "Since", "After"],
            "correct_index": 0,
            "explanation": "La phrase exprime une condition éventuelle : ‘If the repair takes longer…’.",
            "remediation": None,
        },
        {
            "id": "rd-14",
            "task_type": "reading_comprehension",
            "target": "detail",
            "scenario": "office-notice",
            "passage": "Notice to staff\nThe north entrance will remain closed from 8:00 a.m. to 1:00 p.m. on 14 May while a security gate is replaced. Visitors should use the reception entrance on Oak Street. Employee parking will not be affected.",
            "prompt": "What should visitors do on 14 May?",
            "choices": ["Use the reception entrance", "Park on Oak Street", "Arrive after 1:00 p.m.", "Call the security company"],
            "correct_index": 0,
            "explanation": "Le texte indique explicitement que les visiteurs doivent utiliser l’entrée de réception située Oak Street.",
            "remediation": None,
        },
        {
            "id": "rd-15",
            "task_type": "reading_comprehension",
            "target": "detail",
            "scenario": "meeting-minutes",
            "passage": "Project meeting summary\nThe design team will deliver the first mock-ups on 6 June. The client review is scheduled for 9 June. Because the marketing manager will be travelling that week, Jordan Lee will collect comments from the marketing team before the review.",
            "prompt": "What is Jordan Lee expected to do?",
            "choices": ["Gather marketing comments", "Create the mock-ups", "Travel with the manager", "Lead the client review"],
            "correct_index": 0,
            "explanation": "Le résumé précise que Jordan Lee collectera les commentaires marketing avant la revue.",
            "remediation": None,
        },
        {
            "id": "rd-16",
            "task_type": "reading_comprehension",
            "target": "detail",
            "scenario": "shipment-update",
            "passage": "Delivery update\nOrder 4582 left our Lyon warehouse on Monday. The carrier expects to deliver it to Marseille on Thursday between 9:00 a.m. and noon. A signature will be required at delivery. Please contact us by Wednesday if a different person will receive the order.",
            "prompt": "Why should the customer contact the company by Wednesday?",
            "choices": ["To name another recipient", "To change the warehouse", "To cancel the order", "To request a morning delivery"],
            "correct_index": 0,
            "explanation": "Le client doit prévenir si une autre personne recevra la commande nécessitant une signature.",
            "remediation": None,
        },
        {
            "id": "rd-17",
            "task_type": "reading_comprehension",
            "target": "detail",
            "scenario": "job-posting",
            "passage": "Customer support assistant\nWe are seeking a full-time assistant for our support team. Applicants should write clearly in English and French and be available to work one Saturday each month. Training is provided during the first two weeks. Applications close on 18 September.",
            "prompt": "What does the company provide?",
            "choices": ["Initial training", "Remote work equipment", "A part-time schedule", "A language certificate"],
            "correct_index": 0,
            "explanation": "L’annonce indique que la formation est fournie pendant les deux premières semaines.",
            "remediation": None,
        },
        {
            "id": "rd-18",
            "task_type": "reading_comprehension",
            "target": "inference",
            "scenario": "return-policy",
            "passage": "Return policy\nItems purchased online may be returned within 30 days if they are unused and include the original receipt. Delivery charges are not refunded unless an item was sent in error. Refunds are issued to the payment method used for the purchase.",
            "prompt": "A customer returns an unused item because they changed their mind. What will most likely happen?",
            "choices": ["The item price is refunded but delivery charges are not", "Both the item and delivery charges are refunded", "The refund is sent by cheque", "The return is refused after seven days"],
            "correct_index": 0,
            "explanation": "Le retour est accepté sous 30 jours, mais les frais de livraison ne sont remboursés que si l’envoi était erroné.",
            "remediation": None,
        },
        {
            "id": "rd-19",
            "task_type": "reading_comprehension",
            "target": "inference",
            "scenario": "event-invitation",
            "passage": "Invitation: supplier briefing\nOur annual supplier briefing will be held on 3 October at the Riverside Conference Centre. Registration opens at 8:30 a.m. and the first presentation begins at 9:15 a.m. Please register by 20 September so that we can prepare name badges and dietary options for lunch.",
            "prompt": "Why does the organiser ask guests to register early?",
            "choices": ["To prepare badges and lunch options", "To reserve hotel rooms", "To send presentation slides", "To arrange transport from the airport"],
            "correct_index": 0,
            "explanation": "La date limite sert à préparer les badges et les options de restauration.",
            "remediation": None,
        },
    ],
}


def get_toeic_reading_diagnostic() -> dict:
    """Return a defensive copy of the original diagnostic package."""
    return deepcopy(TOEIC_READING_DIAGNOSTIC)


def get_diagnostic_item(item_id: str) -> dict | None:
    """Return one original item by identifier without sharing mutable state."""
    for item in TOEIC_READING_DIAGNOSTIC["items"]:
        if item["id"] == item_id:
            return deepcopy(item)
    return None
