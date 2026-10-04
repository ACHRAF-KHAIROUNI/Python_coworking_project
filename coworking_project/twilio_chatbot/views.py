# twilio_chatbot/views.py

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import traceback

from chatAI import services as ai_services
from chatAI import tools

@csrf_exempt
def twilio_webhook(request):
    """
    Reçoit les messages entrants de WhatsApp via Twilio,
    les traite avec l'IA, et renvoie une réponse.
    """
    if request.method != 'POST':
        return HttpResponse("Requête non autorisée.", status=405)

    # 1. Extraire les informations de la requête de Twilio
    incoming_msg = request.POST.get('Body', '').strip()
    from_number = request.POST.get('From', '')

    if not incoming_msg or not from_number:
        return HttpResponse("Requête invalide.", status=400)
    
    print(f"Message reçu de {from_number} sur WhatsApp: {incoming_msg}")

    try:
        # 2. Obtenir le modèle IA (version publique, sans utilisateur)
        model = ai_services.get_model_for_user(user=None)
        if model is None:
            raise ConnectionError("Le modèle IA n'est pas initialisé.")

        # 3. Gérer l'historique de conversation par numéro de téléphone
        session_key = f"whatsapp_history_{from_number}"
        chat_history = request.session.get(session_key, [])
        chat_session = ai_services.start_chat_session(model, history=chat_history)

        # 4. Envoyer le message à l'IA et traiter la réponse (logique des outils)
        response = chat_session.send_message(incoming_msg)

        function_call = None
        for part in response.parts:
            if part.function_call:
                function_call = part.function_call
                break

        ai_response_text = ""
        if function_call:
            tool_name = function_call.name
            tool_args = {key: value for key, value in function_call.args.items()}
            
            if hasattr(tools, tool_name):
                # Les outils privés ne seront pas disponibles, donc pas de risque ici
                tool_function = getattr(tools, tool_name)
                tool_response_data = tool_function(**tool_args)
                
                response_with_tool_result = chat_session.send_message(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=tool_name, response={"result": tool_response_data}
                        )
                    )
                )
                ai_response_text = response_with_tool_result.text
            else:
                ai_response_text = f"Erreur : L'outil '{tool_name}' n'est pas implémenté."
        else:
            ai_response_text = response.text

        # 5. Mettre à jour l'historique dans la session
        chat_history.append({'role': 'user', 'parts': [{'text': incoming_msg}]})
        chat_history.append({'role': 'model', 'parts': [{'text': ai_response_text}]})
        request.session[session_key] = chat_history[-10:]

        # 6. Préparer et renvoyer la réponse TwiML
        twilio_response = MessagingResponse()
        twilio_response.message(ai_response_text)

        return HttpResponse(str(twilio_response), content_type='application/xml')

    except Exception as e:
        traceback.print_exc()
        # En cas d'erreur, on envoie une réponse d'erreur à l'utilisateur
        twilio_response_error = MessagingResponse()
        twilio_response_error.message("Désolé, une erreur technique est survenue. Veuillez réessayer plus tard.")
        return HttpResponse(str(twilio_response_error), content_type='application/xml')