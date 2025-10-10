# nlu_service.py

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv


class NLUService:
    """
    Um serviço para realizar tarefas de NLU (Natural Language Understanding)
    usando a API do Google Gemini, otimizado para um chatbot educacional.
    """

    def __init__(self):
        """
        Inicializa o serviço, carrega a API key e configura o modelo Gemini.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL")
        if not api_key:
            raise ValueError("A chave GEMINI_API_KEY não foi encontrada. Verifique seu arquivo .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        print("NLUService inicializado com sucesso.")

    def analyze_text(self, text: str) -> dict:
        """
        Analisa um texto para extrair a intenção e as entidades, com um prompt
        especializado para o contexto educacional do TCC.
        """
        prompt = f"""
        Você é o cérebro de um chatbot educacional da universidade UNISINOS.
        Seu objetivo é ajudar estudantes, incluindo aqueles com deficiência visual e auditiva, a encontrar informações acadêmicas e educacionais.
        Analise o texto do usuário e retorne um objeto JSON com a "intent" (intenção) e as "entities" (entidades) extraídas.

        As intenções possíveis são:
        - 'buscar_conteudo_disciplina': O usuário quer materiais, links ou informações sobre uma disciplina ou curso.
        - 'consultar_informacao_institucional': O usuário pergunta sobre locais (biblioteca, secretarias), horários ou FAQs da universidade.
        - 'buscar_video_educacional': O usuário pede por um vídeo sobre um assunto de estudo.
        - 'explicar_funcionalidades': O usuário pergunta sobre o que o chatbot pode fazer ou como pode ajudar.  <-- NOVA INTENÇÃO
        - 'saudacao': O usuário está apenas cumprimentando.
        - 'desconhecido': A intenção não se encaixa em nenhuma das anteriores.

        Siga rigorosamente os exemplos abaixo para formatar sua resposta.

        ---
        Exemplo 1:
        Texto: "Onde eu acho o material de TCC2?"
        JSON: {{"intent": "buscar_conteudo_disciplina", "entities": {{"disciplina": "TCC2"}}}}

        Exemplo 2:
        Texto: "Qual o horário de funcionamento da biblioteca do campus São Leopoldo?"
        JSON: {{"intent": "consultar_informacao_institucional", "entities": {{"local": "biblioteca", "campus": "São Leopoldo"}}}}

        Exemplo 3:
        Texto: "preciso de um vídeo sobre a história do Brasil colonial"
        JSON: {{"intent": "buscar_video_educacional", "entities": {{"assunto": "história do Brasil colonial"}}}}

        Exemplo 4:
        Texto: "como você pode me ajudar?"
        JSON: {{"intent": "explicar_funcionalidades", "entities": {{}}}}  <-- NOVO EXEMPLO

        Exemplo 5:
        Texto: "Oi, tudo bem?"
        JSON: {{"intent": "saudacao", "entities": {{}}}}
        ---

        Agora, analise o seguinte texto:
        Texto: "{text}"
        JSON:
        """

        try:
            response = self.model.generate_content(prompt)
            cleaned_response = self._clean_json_response(response.text)
            result = json.loads(cleaned_response)
            return result

        except Exception as e:
            print(f"Erro ao analisar o texto: {e}")
            return {
                "intent": "erro_processamento",
                "entities": {"details": str(e)}
            }

    def _clean_json_response(self, text: str) -> str:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        return text.strip()