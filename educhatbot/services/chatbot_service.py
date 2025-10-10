# services/chatbot_service.py

from .generative_service import GenerativeService
from .nlu_service import NLUService


class ChatbotService:
    """
    Serviço orquestrador que utiliza o NLUService e o GenerativeService
    para fornecer uma resposta completa ao usuário.
    """

    def __init__(self):
        """
        Inicializa todos os serviços necessários para o funcionamento do chatbot.
        """
        self.nlu_service = NLUService()
        self.generative_service = GenerativeService()
        print("ChatbotService inicializado, pronto para orquestrar.")

    def get_response(self, user_input: str) -> str:
        """
        Processa a entrada do usuário e retorna a melhor resposta possível,
        utilizando o modelo híbrido (NLU + Generativo).
        """
        # 1. Primeiro, tentamos entender a entrada com o NLU Service
        nlu_result = self.nlu_service.analyze_text(user_input)
        intent = nlu_result.get('intent')
        entities = nlu_result.get('entities', {})

        # 2. Se a intenção for estruturada e conhecida, geramos uma resposta específica
        if intent and intent not in ['desconhecido', 'erro_processamento']:
            return self._handle_structured_intent(intent, entities)

        # 3. Se a intenção for desconhecida, usamos o modo generativo para uma resposta aberta
        else:
            print("...(Intenção não reconhecida. Acionando modo generativo)...")
            return self.generative_service.generate_free_response(user_input)

    def _handle_structured_intent(self, intent: str, entities: dict) -> str:
        """
        Método privado para gerar as respostas para as intenções conhecidas.
        """
        if intent == 'buscar_conteudo_disciplina':
            disciplina = entities.get('disciplina', 'não especificada')
            return f"Entendido. Vou iniciar a busca por materiais da disciplina: '{disciplina}'."

        elif intent == 'consultar_informacao_institucional':
            local = entities.get('local', 'local não especificado')
            return f"Certo. Consultando informações sobre: '{local}'."

        elif intent == 'buscar_video_educacional':
            assunto = entities.get('assunto', 'não especificado')
            return f"Perfeito! Procurando um vídeo educativo sobre: '{assunto}'."

        elif intent == 'explicar_funcionalidades':
            return """Eu sou o ED, seu assistente educacional acessível. Minhas principais funções são:
                    - Buscar materiais e informações de disciplinas.
                    - Responder perguntas sobre a universidade.
                    - Recomendar vídeos educativos para seus estudos.
                    Além disso, posso conversar sobre outros assuntos para te ajudar no que for preciso!"""

        elif intent == 'saudacao':
            return "Olá! Como posso te ajudar hoje?"

        # Fallback, embora o `get_response` já lide com isso
        return "Não consegui definir uma ação para sua solicitação."
