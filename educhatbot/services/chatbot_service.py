import logging
from .feedback_service import FeedbackService
from .educational_content_service import EducationalContentService
from .generative_service import GenerativeService
from .nlu_service import NLUService

# Configuração básica de log
logger = logging.getLogger(__name__)

class ChatbotService:
    """
    Serviço orquestrador que utiliza o NLUService e o GenerativeService
    para fornecer uma resposta completa ao usuário.
    """

    def __init__(self):
        self.nlu_service = NLUService()
        self.generative_service = GenerativeService()
        self.content_service = EducationalContentService()
        self.feedback_service = FeedbackService()
        logger.info("ChatbotService inicializado, pronto para orquestrar.")

    def get_response(self, user_input: str, session_id: int | None = None,
                     simplify: bool = False, last_messages: list = None) -> dict:

        # Garante que last_messages seja uma lista, mesmo que venha None
        if last_messages is None:
            last_messages = []

        # 0. Simplificação direta (Prioridade máxima)
        if simplify:
            prompt_simplificado = (
                f"O usuário pediu: '{user_input}'.\n"
                "Instrução obrigatória: Explique de forma MUITO RESUMIDA, "
                "usando linguagem simples, sem jargões técnicos e, se possível, com uma analogia do dia a dia."
            )
            answer = self.generative_service.generate_free_response(prompt_simplificado)
            return {"answer": answer, "intent": "generativo_simplificado"}

        # ---------------------------------------------------------------------
        # 1. Preparação do Contexto para NLU
        # ---------------------------------------------------------------------

        history_text = ""
        for msg in last_messages:
            role_label = "Usuário" if msg.get('role') == 'user' else "Bot"
            content = msg.get('text', '')
            if content:
                history_text += f"{role_label}: {content}\n"

        if history_text:
            nlu_input = (
                f"Histórico recente da conversa:\n{history_text}\n"
                f"--- Fim do Histórico ---\n\n"
                f"Mensagem ATUAL do Usuário: {user_input}"
            )
            logger.info(f"Enviando NLU com contexto. Histórico de {len(last_messages)} mensagens.")
        else:
            nlu_input = user_input

        # Chama o NLU
        nlu_result = self.nlu_service.analyze_text(nlu_input)
        intent = nlu_result.get('intent')
        entities = nlu_result.get('entities', {})

        # ---------------------------------------------------------------------

        # 2. Verifica feedback negativo
        fb = self.feedback_service.get_last_unconsumed_negative(session_id)
        if fb:
            answer = self._answer_with_feedback(user_input, session_id)
            self.feedback_service.mark_consumed(fb)
            return {"answer": answer, "intent": "feedback_recovery"}

        # 3. Tenta resolver via Intents Estruturadas
        ignored_intents = ['saudacao', 'desconhecido', 'modo_generativo', 'erro_processamento']

        if intent and intent not in ignored_intents:
            answer = self._handle_structured_intent(intent, entities)
            if answer:
                return {"answer": answer, "intent": intent}

        # 4. Resposta Generativa (Fallback)
        answer = self.generative_service.generate_free_response(user_input)
        return {"answer": answer, "intent": "generativo"}

    def _handle_structured_intent(self, intent: str, entities: dict) -> str | None:
        if intent == 'buscar_conteudo_disciplina':
            return self._handle_buscar_conteudo_disciplina(entities)

        elif intent == "aprofundar_topico":
            return self._handle_aprofundar_topico(entities)

        elif intent == 'consultar_informacao_institucional':
            return self._handle_institucional(entities)

        elif intent == 'buscar_video_educacional':
            return self._handle_videos(entities)

        elif intent == 'explicar_funcionalidades':
            return """Eu sou o ED, seu assistente educacional acessível. Minhas principais funções são:
                    - Buscar materiais e informações de disciplinas.
                    - Responder perguntas sobre a universidade.
                    - Recomendar vídeos educativos para seus estudos.
                    Além disso, posso conversar sobre outros assuntos para te ajudar no que for preciso!"""

        return None

    def _answer_with_feedback(self, user_input: str, session_id: int | None) -> str:
        extra_instructions = []

        if session_id and self.feedback_service.session_needs_simplify(session_id):
            extra_instructions.append(
                "A resposta anterior NÃO ajudou este aluno. Agora explique de forma BEM mais simples, "
                "em passos curtos, sem termos técnicos e com um exemplo do dia a dia."
            )

        similar_neg = self.feedback_service.find_similar_negative_feedbacks(user_input)
        if similar_neg:
            extra_instructions.append(
                "Outros alunos também tiveram dificuldade com esse mesmo assunto. "
                "Seja ainda mais didático e ofereça uma segunda forma de explicar."
            )

        if extra_instructions:
            prompt = (
                    f"Aluno perguntou: {user_input}\n" +
                    "\n".join(extra_instructions) +
                    "\nResponda em português claro e no final pergunte se ele quer outro exemplo."
            )
            return self.generative_service.generate_free_response(prompt)

        return self.generative_service.generate_free_response(user_input)

    def _handle_buscar_conteudo_disciplina(self, entities: dict) -> str:
        disciplina = (entities.get('disciplina') or "").strip().lower()
        if not disciplina:
            discs = self.content_service.list_disciplinas()
            nomes = "\n".join(f"- {d.get('nome', '')}" for d in discs)
            return f"Posso trazer conteúdos de:\n{nomes}\nQual disciplina você quer?"

        payload = self.content_service.get_conteudos(disciplina)
        if not payload:
            return f"Não encontrei a disciplina **{disciplina}**."

        resumo = self.content_service.normalizar_topicos(payload)
        if not resumo:
            return f"Não encontrei tópicos para **{disciplina}** agora. Quer tentar outra disciplina?"

        return (
            f"Aqui estão alguns tópicos de **{payload.get('disciplina', disciplina)}**:\n"
            f"{resumo}\n"
            f"Quer que eu aprofunde algum deles ou prefere fazer um quiz?"
        )

    def _handle_aprofundar_topico(self, entities: dict) -> str | None:
        topico = entities.get("topico", "").strip().lower()
        if not topico:
            return "Certo! Sobre qual tópico você gostaria de se aprofundar?"

        logger.info(f"...Buscando tópico: {topico}")
        data = self.content_service.get_aprofundamento(topico)

        if not data or "erro" in data:
            return None

        detalhamento = data.get("detalhamento", {})
        descricao = data.get("descricao", "")
        etapas = detalhamento.get("etapas", [])
        curiosidades = detalhamento.get("curiosidades", [])
        refs = detalhamento.get("referencias", [])

        resposta = f"🔎 **Aprofundamento em {data.get('topico', '')}**\n\n{descricao}\n\n"

        if etapas:
            resposta += "**Etapas principais:**\n" + "\n".join(f"• {e}" for e in etapas) + "\n\n"

        if curiosidades:
            resposta += "**Curiosidades:**\n" + "\n".join(f"• {c}" for c in curiosidades) + "\n\n"

        if refs:
            resposta += "**Referências:**\n" + "\n".join(f"- {r.get('titulo')}: {r.get('url')}" for r in refs)

        return resposta

    def _handle_institucional(self, entities: dict) -> str:
        local = (entities.get("local") or "").strip().lower()
        campus = (entities.get("campus") or "").strip()
        info = (entities.get("info") or "").strip().lower()

        logger.info(f"...Buscando entities: {local}, {campus}, {info}")

        # Verifica se deve retornar a lista genérica de locais
        if not local and not campus and (not info or info == "horarios"):
            locs = self.content_service.locais()
            return self._formatar_locais(locs)

        # Validações de contexto para pedir mais informações
        if not local and not campus and info:
            return f"Para acessar **{info.upper()}**, preciso que você informe o **campus** ou o **local**."

        if local and not campus:
            return f"Qual campus você deseja consultar para **{local}**? (Ex.: São Leopoldo, Porto Alegre)"

        if not local and campus:
            tipo_info = f"ver {info} de" if info else "consultar"
            return f"Certo! Em **{campus}**, qual local você deseja {tipo_info}? (Ex.: biblioteca, secretaria)"

        # Lógica de busca específica
        data = None
        if info == "horarios":
            data = self.content_service.horarios(local=local, campus=campus)
            if not data or "erro" in data:
                return f"Não encontrei horários para **{local}** em **{campus}**."
            return self._formatar_horarios(data)

        elif info == "faq":
            data = self.content_service.faq(local=local, campus=campus)
            if not data:
                return f"Não encontrei FAQ para **{local}** em **{campus}**."
            return self._formatar_faq(data)

        elif info == "contatos":
            data = self.content_service.contatos(local=local, campus=campus)
            if not data:
                return f"Não encontrei contatos para **{local}** em **{campus}**."
            return self._formatar_contatos(data)

        # Default: Horários (caso info seja vazio, mas tenha local/campus)
        data = self.content_service.horarios(local=local, campus=campus)
        return self._formatar_horarios(data) if data else f"Não encontrei dados para **{local}** em **{campus}**."

    def _handle_videos(self, data: dict) -> str:
        assunto = data.get('assunto', '').strip()
        if not assunto:
            return "Sobre qual assunto você quer ver vídeos? (Ex: Matemática, História)"

        videos = self.content_service.buscar_videos(assunto=assunto)

        if not videos:
            return f"Poxa, não encontrei vídeos sobre **{assunto}** na minha base agora."

        resposta = f"🎬 **Vídeos sugeridos sobre {assunto}:**\n"
        for v in videos:
            titulo = v.get('titulo', 'Vídeo')
            url = v.get('url', '#')
            desc = v.get('descricao', '')
            resposta += f"\n• [{titulo}]({url})"
            if desc:
                resposta += f" - {desc}"

        return resposta

    def _formatar_locais(self, data: dict) -> str:
        campi = data.get("campi", []) or []
        if not campi:
            return "No momento não encontrei a lista de locais por campus."
        linhas = ["Posso consultar estes locais por campus:"]
        for c in campi:
            campus_nome = c.get("campus", "Campus")
            locais_lista = c.get("locais") or []
            nomes = ", ".join(l.get("nome", "") for l in locais_lista)
            linhas.append(f"• **{campus_nome}**: {nomes}")
        linhas.append("Diga: 'horários da biblioteca em São Leopoldo', por exemplo.")
        return "\n".join(linhas)

    def _formatar_horarios(self, data: dict) -> str:
        h = (data.get("horarios") or {})
        obs = data.get("observacoes_acessibilidade") or []
        linhas = [
            f"**{data.get('local', 'Local')} – {data.get('campus', 'Campus')}**",
        ]
        if data.get("descricao_curta"):
            linhas.append(data["descricao_curta"])
        if h:
            linhas.append(
                f"🕒 Horários: Seg-Sex {h.get('segunda_sexta', '-')}; "
                f"Sáb {h.get('sabado', '-')}; Dom {h.get('domingo', '-')}."
            )
        if obs:
            linhas.append("Acessibilidade:")
            linhas += [f"• {o}" for o in obs]
        return "\n".join(linhas)

    def _formatar_faq(self, data: dict) -> str:
        faq = data.get("faq") or []
        if not faq:
            return "Não há itens de FAQ disponíveis."
        linhas = [f"**FAQ – {data.get('local', 'Local')} – {data.get('campus', 'Campus')}**"]
        for i, item in enumerate(faq, start=1):
            pgt = item.get('pergunta', '')
            resp = item.get('resposta_simplificada', '')
            linhas.append(f"{i}. {pgt}")
            linhas.append(f"   → {resp}")
        return "\n".join(linhas)

    def _formatar_contatos(self, data: dict) -> str:
        linhas = [f"**Contatos – {data.get('local', 'Local')} – {data.get('campus', 'Campus')}**"]
        campos = [
            ("email", "E-mail"), ("telefone", "Telefone"),
            ("site", "Site"), ("endereco", "Endereço"), ("mapa_url", "Mapa")
        ]
        for key, label in campos:
            if data.get(key):
                linhas.append(f"• {label}: {data[key]}")

        if data.get("acessibilidade"):
            linhas.append("Acessibilidade:")
            linhas += [f"• {o}" for o in (data.get("acessibilidade") or [])]
        return "\n".join(linhas)