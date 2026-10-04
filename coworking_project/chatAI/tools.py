# chatAI/tools.py

from company.models import Salle
from reservations.models import Reservation
from users.models import User
from datetime import date, datetime, timedelta
import json
from decimal import Decimal

def convert_relative_date(date_str: str) -> date:
    """Convertit 'aujourd'hui', 'demain', 'après-demain' en objet date."""
    today = date.today()
    date_str_lower = date_str.lower()
    if date_str_lower in ["aujourd'hui", "today"]:
        return today
    if date_str_lower in ["demain", "tomorrow"]:
        return today + timedelta(days=1)
    if date_str_lower == "après-demain":
        return today + timedelta(days=2)
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def list_salles(ville: str = None, capacite_min: int = None):
    """
    Obtient une liste de salles de coworking disponibles, avec des filtres optionnels.

    Args:
        ville (str, optional): Filtre les salles par ville (basé sur le champ localisation).
        capacite_min (int, optional): Filtre les salles ayant une capacité minimale.
    """
    salles = Salle.objects.filter(societer__etat='ACTIVE')
    if ville:
        salles = salles.filter(societer__localisation__icontains=ville)
    if capacite_min:
        salles = salles.filter(capacite__gte=capacite_min)

    if not salles.exists():
        return json.dumps({"salles": [], "message": "Désolé, aucune salle ne correspond à vos critères."})
    
    salles_data = [
        {"nom": s.nom, "capacite": s.capacite, "prix_par_heure": float(s.prix_par_heure), "ville": s.societer.localisation}
        for s in salles
    ]
    return json.dumps({"salles": salles_data})

def check_salle_availability(nom_salle: str, date_str: str, heure_debut_str: str, duree_heures: int = 1):
    """
    Vérifie la disponibilité d'une salle spécifique pour un créneau donné.

    Args:
        nom_salle (str): Le nom exact de la salle.
        date_str (str): La date souhaitée au format AAAA-MM-JJ ou un mot-clé comme 'demain'.
        heure_debut_str (str): L'heure de début au format HH:MM.
        duree_heures (int, optional): La durée en heures. Par défaut 1.
    """
    try:
        salle = Salle.objects.get(nom__iexact=nom_salle)
        date_reserv = convert_relative_date(date_str)
        heure_debut = datetime.strptime(heure_debut_str, "%H:%M").time()
    except Salle.DoesNotExist:
        return json.dumps({"disponible": False, "raison": f"Désolé, je ne trouve pas de salle nommée '{nom_salle}'."})
    except ValueError:
        return json.dumps({"disponible": False, "raison": f"Le format de la date '{date_str}' ou de l'heure '{heure_debut_str}' est incorrect."})

    heure_fin = (datetime.combine(date_reserv, heure_debut) + timedelta(hours=duree_heures)).time()

    if not (salle.heurD <= heure_debut < salle.heurF and salle.heurD < heure_fin <= salle.heurF):
        return json.dumps({"disponible": False, "raison": "Le créneau est en dehors des heures d'ouverture."})

    reservations_ce_jour = Reservation.objects.filter(salle=salle, date_reservation=date_reserv, etat='CONFIRMED')
    creneau_debut_dt = datetime.combine(date_reserv, heure_debut)
    creneau_fin_dt = datetime.combine(date_reserv, heure_fin)

    for res in reservations_ce_jour:
        res_debut_dt = datetime.combine(date_reserv, res.heure_debut)
        res_fin_occupation_dt = (datetime.combine(date_reserv, res.heure_fin) + timedelta(minutes=30))
        if creneau_debut_dt < res_fin_occupation_dt and creneau_fin_dt > res_debut_dt:
            return json.dumps({"disponible": False, "raison": "Ce créneau est déjà réservé."})

    prix_total = salle.prix_par_heure * Decimal(duree_heures)
    return json.dumps({
        "disponible": True, "salle": salle.nom,
        "creneau": f"Le {date_reserv.strftime('%d/%m/%Y')} de {heure_debut_str} à {heure_fin.strftime('%H:%M')}",
        "prix_estime": float(prix_total)
    })

def get_user_reservations(user_id: int):
    """
    Obtient la liste des réservations futures d'un utilisateur via son ID.
    L'IA doit appeler cette fonction sans argument si l'utilisateur demande 'mes réservations'.
    """
    try:
        user = User.objects.get(pk=user_id)
        reservations = Reservation.objects.filter(
            user=user, date_reservation__gte=date.today(), etat__in=['CONFIRMED', 'PENDING']
        ).order_by('date_reservation', 'heure_debut')
        if not reservations.exists():
            return json.dumps({"reservations": [], "message": "Vous n'avez aucune réservation à venir."})
        reservations_data = [
            {"salle": r.salle.nom, "date": r.date_reservation.strftime('%d/%m/%Y'), "creneau": f"{r.heure_debut.strftime('%H:%M')}-{r.heure_fin.strftime('%H:%M')}", "etat": r.get_etat_display()}
            for r in reservations
        ]
        return json.dumps({"reservations": reservations_data})
    except User.DoesNotExist:
        return json.dumps({"error": "Utilisateur non trouvé."})

def get_user_balance(user_id: int):
    """
    Obtient le solde actuel de l'utilisateur connecté via son ID.
    L'IA doit appeler cette fonction sans argument si l'utilisateur demande 'mon solde'.
    """
    try:
        user = User.objects.get(pk=user_id)
        return json.dumps({"solde": float(user.solde)})
    except User.DoesNotExist:
        return json.dumps({"error": "Utilisateur non trouvé."})