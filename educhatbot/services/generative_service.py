# generative_service.py

import os
import google.generativeai as genai
from dotenv import load_dotenv


class GenerativeService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL")
        if not api_key:
            raise ValueError("A chave GEMINI_API_KEY não foi encontrada.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        print("GenerativeService inicializado.")

    def generate_free_response(self, prompt_usuario: str) -> str:
        """
        Gera uma resposta conversacional e aberta para um prompt do usuário.
        """
        # Prompt focado em ser um assistente prestativo
        prompt_completo = f"""
        Você é um chatbot educacional acessível e amigável chamado ED, criado para um TCC da UNISINOS.
        Seu objetivo é ajudar os estudantes. Responda à pergunta do usuário de forma clara, prestativa e concisa.

        Pergunta do usuário: "{prompt_usuario}"
        Sua resposta:
        """
        try:
            response = self.model.generate_content(prompt_completo)
            return response.text
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao tentar gerar uma resposta: {e}"