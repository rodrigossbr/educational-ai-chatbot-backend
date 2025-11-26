import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class GenerativeService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Fallback seguro

        if not api_key:
            raise ValueError("A chave GEMINI_API_KEY não foi encontrada.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info("GenerativeService inicializado.")

    def generate_free_response(self, prompt_usuario: str) -> str:
        """
        Gera uma resposta conversacional com links de busca seguros contra alucinação.
        """
        prompt_completo = f"""
        Você é o ED, chatbot da UNISINOS.

        REGRA DE OURO PARA LINKS (Anti-Alucinação):
        1. **NUNCA** invente URLs diretas para artigos ou notícias (ex: não use 'unisinos.br/noticia/xyz').
        2. Se precisar recomendar leitura, crie um **Link de Busca no Google** restrito ao site da universidade.
           Padrão: [Buscar sobre TEMA no site da Unisinos](https://www.google.com/search?q=site:unisinos.br+TEMA)
        3. Você pode usar links oficiais seguros que você tem certeza absoluta, como:
           - https://www.unisinos.br
           - https://www.unisinos.br/graduacao
           - https://www.unisinos.br/biblioteca

        Pergunta: "{prompt_usuario}"

        Responda de forma útil, curta e inclua 1 link de busca no final se o assunto pedir aprofundamento.
        """

        try:
            response = self.model.generate_content(prompt_completo)
            return response.text
        except Exception as e:
            return "Desculpe, não consegui gerar a resposta agora."