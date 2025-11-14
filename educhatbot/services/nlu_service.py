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
    Mantém o estilo original: prompt exemplificado e limpeza de JSON via regex.
    """

    def __init__(self):
        """
        Inicializa o serviço, carrega a API key e configura o modelo Gemini.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        if not api_key:
            raise ValueError("A chave GEMINI_API_KEY não foi encontrada. Verifique seu arquivo .env")

        genai.configure(api_key=api_key)

        # Configuração tipada (evita o warning de type checker no VS Code/Pylance)
        gen_cfg: GenerationConfigDict = {
            "response_mime_type": "application/json",
            "temperature": 0.2,
        }

        self.model = genai.GenerativeModel(
            model_name,
            generation_config=gen_cfg,
            system_instruction="Retorne APENAS JSON válido com 'intent' e 'entities'.",
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
        Analisa um texto para extrair a intenção e as entidades, com um prompt
        especializado para o contexto educacional do TCC.
        Mantém a estratégia original de exemplos e limpeza de JSON.
        """
        user_text = (text or "").strip()

        bad_intents: List[str] = self.feedback_service.get_negative_intents_for_similar_text(
            user_text, min_score=0.70
        )

        avoid_clause = ""
        if bad_intents:
            lista = ", ".join(f"'{i}'" for i in bad_intents)
            avoid_clause = (
                "Atenção: Para textos semelhantes a este, usuários reprovaram as intenções "
                f"{lista}. EVITE classificá-lo como {lista}. Se houver dúvida, retorne 'desconhecido'.\n"
            )

        prompt = f"""
        Você é o cérebro de um chatbot educacional da universidade UNISINOS.
        Seu objetivo é ajudar estudantes, incluindo aqueles com deficiência visual e auditiva, a encontrar informações acadêmicas e educacionais.
        Analise o texto do usuário e retorne um objeto JSON com a "intent" (intenção) e as "entities" (entidades) extraídas.

        As intenções possíveis são:
        - 'buscar_conteudo_disciplina': O usuário quer disciplinas, materiais, links ou informações sobre uma disciplina ou curso.
        - 'aprofundar_topico': O usuário quer se aprofundar em um tema ou tópico de estudo.
        - 'consultar_informacao_institucional': O usuário pergunta sobre locais (biblioteca, secretarias), horários ou FAQs da universidade.
        - 'buscar_video_educacional': O usuário pede por um vídeo sobre um assunto de estudo.
        - 'explicar_funcionalidades': O usuário pergunta sobre o que o chatbot pode fazer ou como pode ajudar.
        - 'saudacao': O usuário está apenas cumprimentando.
        - 'modo_generativo': O usuário quer usar diretamente a IA generativa, sem intenções específicas.
        - 'desconhecido': A intenção não se encaixa em nenhuma das anteriores.

        {avoid_clause}
        Siga rigorosamente os exemplos abaixo para formatar sua resposta.
        Retorne APENAS JSON. Não inclua comentários, markdown ou texto fora do JSON.

        ---
        Exemplo 1:
        Texto: "Quais disciplinas tem?"
        JSON: {{"intent": "buscar_conteudo_disciplina", "entities": {{ "disciplina": "" }}}}

        Exemplo 1.1:
        Texto: "Sobre quais disciplinas vc pode me ajudar?"
        JSON: {{"intent": "buscar_conteudo_disciplina", "entities": {{ "disciplina": "" }}}}

        Exemplo 1.2:
        Texto: "Me de o conteúdo de matemática?"
        JSON: {{"intent": "buscar_conteudo_disciplina", "entities": {{ "disciplina": "matematica" }}}}

        Exemplo 1.3:
        Texto: "Me de informações sobre Ciências?"
        JSON: {{"intent": "buscar_conteudo_disciplina", "entities": {{ "disciplina": "ciencias" }}}}

        Exemplo 2:
        Texto: "Onde eu acho o material de TCC2?"
        JSON: {{"intent": "buscar_conteudo_disciplina", "entities": {{"disciplina": "tcc2"}}}}

        Exemplo 3:
        Texto: "Qual o horário de funcionamento da biblioteca do campus São Leopoldo?"
        JSON: {{"intent": "consultar_informacao_institucional", "entities": {{"local": "biblioteca", "campus": "São Leopoldo"}}}}

        Exemplo 4:
        Texto: "preciso de um vídeo sobre a história do Brasil colonial"
        JSON: {{"intent": "buscar_video_educacional", "entities": {{"assunto": "história do Brasil colonial"}}}}

        Exemplo 5:
        Texto: "como você pode me ajudar?"
        JSON: {{"intent": "explicar_funcionalidades", "entities": {{}}}}

        Exemplo 6:
        Texto: "Oi, tudo bem?"
        JSON: {{"intent": "saudacao", "entities": {{}}}}
        ---
        
        Exemplo 7:
        Texto: "Quero falar direto com a IA"
        JSON: {{"intent": "modo_generativo", "entities": {{}}}}
        
        Exemplo 8:
        Texto: "Pesquisar na internet"
        JSON: {{"intent": "modo_generativo", "entities": {{}}}}

        Exemplo 9:
        Texto: "Quero saber mais sobre fotossíntese"
        JSON: {{"intent": "aprofundar_topico", "entities": {{"topico": "fotossintese"}}}}
        
        Exemplo 9.1:
        Texto: "Quero saber mais sobre equações"
        JSON: {{"intent": "aprofundar_topico", "entities": {{"topico": "fotossintese"}}}}
        
        Exemplo 10:
        Texto: "Aprofunda esse tópico pra mim"
        JSON: {{"intent": "aprofundar_topico", "entities": {{"topico": ""}}}}

        Agora, analise o seguinte texto:
        Texto: "{user_text}"
        JSON:
        """

        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text or ""

            # Mantém a limpeza via regex (compatível com saídas envoltas em ```json ... ```)
            cleaned_response = self._clean_json_response(raw_text)

            # Parse do JSON
            result: Dict[str, Any] = json.loads(cleaned_response)

            # Normalização da entidade de disciplina via aliases vindos da API
            entities = result.get("entities") or {}
            if "disciplina" in entities:
                entities["disciplina"] = self.content_service.normalize(entities.get("disciplina"))
                result["entities"] = entities

            # Sanitiza intent inesperada
            intent = result.get("intent", "desconhecido")
            if intent not in self._intents_validas:
                result["intent"] = "desconhecido"
            result["intent"] = intent

            if not isinstance(result.get("entities"), dict):
                result["entities"] = {}

            return result

        except Exception as e:
            print(f"Erro ao analisar o texto: {e}")
            return {
                "intent": "erro_processamento",
                "entities": {"details": str(e)}
            }

    def _clean_json_response(self, text: str) -> str:
        """
        Se a resposta vier em bloco markdown ```json ... ```, extrai apenas o objeto JSON.
        Caso contrário, retorna o texto com strip().
        """
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        return text.strip()
