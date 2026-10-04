# chatAI/services.py

import os
from datetime import datetime
import google.generativeai as genai
from company.models import Salle
from . import tools

def get_system_instruction():
    """Construit l'instruction système dynamiquement."""
    try:
        noms_salles = list(Salle.objects.filter(societer__etat='ACTIVE').values_list('nom', flat=True))
        salles_list_str = ", ".join(noms_salles) if noms_salles else "Aucune n'est listée."
    except Exception:
        salles_list_str = "Information non disponible."

    instruction = (
        "Tu es un assistant virtuel pour une plateforme de réservation d'espaces de coworking. "
        "Réponds en français, de manière amicale et concise.\n\n"
        "INFORMATIONS IMPORTANTES:\n"
        f"- Date d'aujourd'hui: {datetime.now().strftime('%Y-%m-%d')}.\n"
        f"- Salles existantes: {salles_list_str}.\n"
        "- Pour les outils privés comme 'get_user_reservations' ou 'get_user_balance', tu ne dois PAS demander l'ID de l'utilisateur. Appelle la fonction sans argument, le système le fournira.\n"
        "- Ne propose jamais de réserver ou d'annuler. Guide l'utilisateur vers les pages du site pour ces actions."
    )
    return instruction

def get_model_for_user(user=None):
    """Configure et retourne un modèle Gemini avec les outils appropriés."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: raise ValueError("Clé d'API Google non définie.")
        genai.configure(api_key=api_key)

        public_tools = [tools.list_salles, tools.check_salle_availability]
        private_tools = []
        if user and user.is_authenticated:
            private_tools = [tools.get_user_reservations, tools.get_user_balance]
        
        available_tools = public_tools + private_tools
        
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            #model_name='gemini-2.5-flash-lite-preview-06-17',
            system_instruction=get_system_instruction(),
            tools=available_tools
        )
        return model
    except Exception as e:
        print(f"ERREUR CRITIQUE: Impossible de configurer le modèle Google AI: {e}")
        import traceback
        traceback.print_exc()
        return None

def start_chat_session(model, history=None):
    """Démarre une session de chat."""
    if model is None: raise ConnectionError("Le modèle Google AI n'est pas disponible.")
    
    rebuilt_history = []
    if history:
        for item in history:
            try:
                rebuilt_history.append({'role': item['role'], 'parts': item['parts']})
            except KeyError:
                print(f"Avertissement: entrée d'historique ignorée: {item}")
    return model.start_chat(history=rebuilt_history)