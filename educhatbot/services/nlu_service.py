# nlu_service.py

import os
import json
import re
from typing import Any, Dict, List

import google.generativeai as genai
from google.generativeai.types import GenerationConfigDict
from dotenv import load_dotenv
from .educational_content_service import EducationalContentService
from .feedback_service import FeedbackService


class NLUService:
    """
    Um serviço para realizar tarefas de NLU (Natural Language Understanding)
    usando a API do Google Gemini, otimizado para um chatbot educacional.
    """

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        print(f"TESTE: {model_name}")
        if not api_key:
            raise ValueError("A chave GEMINI_API_KEY não foi encontrada. Verifique seu arquivo .env")

        genai.configure(api_key=api_key)

        # Configuração para garantir saída JSON
        gen_cfg: GenerationConfigDict = {
            "response_mime_type": "application/json",
            "temperature": 0.2,  # Temperatura baixa para ser mais determinístico
        }

        self.model = genai.GenerativeModel(
            model_name,
            generation_config=gen_cfg,
            system_instruction="Você é um assistente de NLU. Retorne APENAS um objeto JSON válido contendo as chaves 'intent' e 'entities'.",
        )

        self.content_service = EducationalContentService()
        self.feedback_service = FeedbackService()
        print("NLUService inicializado com sucesso.")

        self._intents_validas = {
            "buscar_conteudo_disciplina",
            "aprofundar_topico",
            "consultar_informacao_institucional",
            "buscar_video_educacional",
            "explicar_funcionalidades",
            "saudacao",
            "modo_generativo",
            "desconhecido",
            "erro_processamento",
        }

    def analyze_text(self, text: str) -> dict:
        """
        Analisa o texto para extrair intenção e entidades.
        """
        user_text = (text or "").strip()

        # Verifica feedbacks negativos anteriores para evitar repetir erros
        bad_intents: List[str] = self.feedback_service.get_negative_intents_for_similar_text(
            user_text, min_score=0.70
        )

        avoid_clause = ""
        if bad_intents:
            lista = ", ".join(f"'{i}'" for i in bad_intents)
            avoid_clause = (
                f"OBSERVAÇÃO CRÍTICA: Usuários já indicaram que este texto NÃO deve ser classificado como: {lista}. "
                "Se estiver em dúvida, prefira 'desconhecido' ou 'modo_generativo'.\n"
            )

        # Prompt ajustado (Correção do Exemplo 9.1 aplicada)
        prompt = f"""
        Analise o texto do usuário para um chatbot da universidade UNISINOS.
        Objetivo: Identificar a 'intent' (intenção) e extrair 'entities' (entidades).

        INTENÇÕES DISPONÍVEIS:
        - 'buscar_conteudo_disciplina': Materiais, ementas, links de disciplinas.
        - 'aprofundar_topico': Explicações conceituais sobre um tema.
        - 'consultar_informacao_institucional': Locais, horários, contatos, secretaria.
        - 'buscar_video_educacional': Solicitação explícita de vídeos.
        - 'explicar_funcionalidades': O que o bot faz.
        - 'saudacao': Oi, olá, tudo bem.
        - 'modo_generativo': Conversa livre, perguntas gerais fora do contexto acadêmico estrito ou pedido para falar com a IA.
        - 'desconhecido': Não se encaixa nas anteriores.

        {avoid_clause}

        EXEMPLOS (Few-Shot Learning):

        Texto: "Quais disciplinas tem?"
        JSON: {{"intent": "buscar_conteudo_disciplina", "entities": {{ "disciplina": "" }}}}

        Texto: "Me de o conteúdo de matemática?"
        JSON: {{"intent": "buscar_conteudo_disciplina", "entities": {{ "disciplina": "matematica" }}}}

        Texto: "Qual o horário da biblioteca em São Leopoldo?"
        JSON: {{"intent": "consultar_informacao_institucional", "entities": {{"local": "biblioteca", "campus": "São Leopoldo"}}}}

        Texto: "preciso de um vídeo sobre história do Brasil"
        JSON: {{"intent": "buscar_video_educacional", "entities": {{"assunto": "história do Brasil"}}}}

        Texto: "como você funciona?"
        JSON: {{"intent": "explicar_funcionalidades", "entities": {{}}}}

        Texto: "Oi"
        JSON: {{"intent": "saudacao", "entities": {{}}}}

        Texto: "Quero falar direto com a IA"
        JSON: {{"intent": "modo_generativo", "entities": {{}}}}

        Texto: "Quero saber mais sobre fotossíntese"
        JSON: {{"intent": "aprofundar_topico", "entities": {{"topico": "fotossintese"}}}}

        Texto: "Me explica equações de segundo grau"
        JSON: {{"intent": "aprofundar_topico", "entities": {{"topico": "equações de segundo grau"}}}}

        Texto: "Aprofunda isso"
        JSON: {{"intent": "aprofundar_topico", "entities": {{"topico": ""}}}}

        ---
        INPUT DO USUÁRIO:
        Texto: "{user_text}"

        RESPOSTA JSON:
        """

        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text or ""

            # Limpeza robusta
            cleaned_response = self._clean_json_response(raw_text)

            # Parse
            result: Dict[str, Any] = json.loads(cleaned_response)

            # Normalização de disciplina (se houver)
            entities = result.get("entities") or {}
            if "disciplina" in entities and entities["disciplina"]:
                entities["disciplina"] = self.content_service.normalize(entities.get("disciplina"))
                result["entities"] = entities

            # Validação da intenção
            intent = result.get("intent", "desconhecido")
            if intent not in self._intents_validas:
                result["intent"] = "desconhecido"
            result["intent"] = intent

            if not isinstance(result.get("entities"), dict):
                result["entities"] = {}

            return result

        except Exception as e:
            print(f"Erro ao analisar o texto (NLU): {e}")
            # Fallback seguro
            return {
                "intent": "erro_processamento",
                "entities": {"error": str(e)}
            }

    def _clean_json_response(self, text: str) -> str:
        """
        Remove blocos de código Markdown (```json ... ```) se existirem.
        O regex agora é mais permissivo, aceitando ```json, ``` ou sem nada.
        """
        # Tenta encontrar o bloco de código
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return match.group(1)

        # Se não tiver bloco de código, tenta encontrar o primeiro objeto JSON válido { ... }
        # Isso ajuda se o modelo responder algo como "Aqui está o JSON: { ... }"
        match_simple = re.search(r'(\{.*\})', text, re.DOTALL)
        if match_simple:
            return match_simple.group(1)

        return text.strip()