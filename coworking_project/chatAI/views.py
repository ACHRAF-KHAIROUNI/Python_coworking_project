# chatAI/views.py

import json
import traceback
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai

from . import services
from . import tools

def chat_page(request):
    """Affiche la page de chat HTML."""
    return render(request, 'chatAI/chat_page.html')

@csrf_exempt
def chat_api(request):
    """Gère la conversation, les outils, et l'historique de session."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        if not user_message: return JsonResponse({'error': 'Message vide'}, status=400)
        
        model = services.get_model_for_user(request.user)
        if model is None: raise ConnectionError("Le modèle IA n'est pas initialisé.")
        
        chat_history = request.session.get('chat_history', [])
        chat_session = services.start_chat_session(model, history=chat_history)

        response = chat_session.send_message(user_message)

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
                tool_function = getattr(tools, tool_name)
                
                # INJECTION DE L'ID UTILISATEUR POUR LES OUTILS PRIVÉS
                if tool_name in ['get_user_reservations', 'get_user_balance']:
                    if request.user.is_authenticated:
                        tool_args['user_id'] = request.user.pk
                    else:
                        ai_response_text = "Désolé, vous devez être connecté pour utiliser cette fonctionnalité."
                
                if not ai_response_text: # Si pas d'erreur de permission
                    tool_response_data = tool_function(**tool_args)
                    
                    response_with_tool_result = chat_session.send_message(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=tool_name,
                                response={"result": tool_response_data},
                            )
                        )
                    )
                    ai_response_text = response_with_tool_result.text
            else:
                ai_response_text = f"Erreur : L'outil '{tool_name}' n'est pas implémenté."
        else:
            ai_response_text = response.text

        # Mise à jour de l'historique de la session
        chat_history.append({'role': 'user', 'parts': [{'text': user_message}]})
        chat_history.append({'role': 'model', 'parts': [{'text': ai_response_text}]})
        request.session['chat_history'] = chat_history[-10:]

        return JsonResponse({'response': ai_response_text})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': f"Une erreur interne est survenue: {str(e)}"}, status=500)