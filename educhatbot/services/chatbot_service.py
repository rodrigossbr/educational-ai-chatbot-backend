# services/chatbot_service.py
from .educational_content_service import EducationalContentService
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
        self.content_service = EducationalContentService()
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
        if intent and intent not in ['saudacao', 'desconhecido', 'erro_processamento']:
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
            return self._handle_buscar_conteudo_disciplina(entities)
        elif intent == "aprofundar_topico":
            return self._handle_aprofundar_topico(entities)
        elif intent == 'consultar_informacao_institucional':
            return self._handle_institucional(entities)

        elif intent == 'buscar_video_educacional':
            assunto = entities.get('assunto', 'não especificado')
            return f"Perfeito! Procurando um vídeo educativo sobre: '{assunto}'."

        elif intent == 'explicar_funcionalidades':
            return """Eu sou o ED, seu assistente educacional acessível. Minhas principais funções são:
                    - Buscar materiais e informações de disciplinas.
                    - Responder perguntas sobre a universidade.
                    - Recomendar vídeos educativos para seus estudos.
                    Além disso, posso conversar sobre outros assuntos para te ajudar no que for preciso!"""

        return "Não consegui definir uma ação para sua solicitação."

    def _handle_buscar_conteudo_disciplina(self, entities: dict) -> str:
        disciplina = (entities.get('disciplina') or "").strip().lower()
        if not disciplina:
            discs = self.content_service.list_disciplinas()
            nomes = "\n".join(f"\\- {d.get('nome', '')}" for d in discs)
            return f"Posso trazer conteúdos de:\n{nomes}\nQual disciplina você quer?"

        payload = self.content_service.get_conteudos(disciplina)
        resumo = self.content_service.normalizar_topicos(payload)
        if not resumo:
            return f"Não encontrei tópicos para **{disciplina}** agora. Quer tentar outra disciplina?"

        return (
            f"Aqui estão alguns tópicos de **{payload.get('disciplina', disciplina)}**:\n"
            f"{resumo}\n"
            f"Quer que eu aprofunde algum deles ou prefere fazer um quiz?"
        )

    def _handle_aprofundar_topico(self, entities: dict) -> str:
        topico = entities.get("topico", "").strip().lower()

        if not topico:
            return "Certo! Sobre qual tópico você gostaria de se aprofundar?"

        print("...Buscando tópico...", topico)

        data = self.content_service.get_aprofundamento(topico)

        if "erro" in data:
            return f"Não consegui encontrar mais detalhes sobre '{topico}'."

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
            resposta += "**Referências:**\n" + "\n".join(f"- {r['titulo']}: {r['url']}" for r in refs)

        return resposta

    def _handle_institucional(self, entities: dict) -> str:
        """
        Entities esperadas:
          - local: ex. 'biblioteca', 'secretaria', 'financeiro', 'acessibilidade'
          - campus: ex. 'São Leopoldo', 'Porto Alegre'
          - info (opcional): 'horarios' | 'faq' | 'contatos' (se ausente, traga horários por padrão)
        """
        local = (entities.get("local") or "").strip().lower()
        campus = (entities.get("campus") or "").strip()
        info = (entities.get("info") or "horarios").strip().lower()

        if not local and not campus:
            locs = self.content_service.locais()
            return self._formatar_locais(locs)

        if local and not campus:
            return f"Qual campus você deseja consultar para **{local}**? (Ex.: São Leopoldo, Porto Alegre)"

        if not local and campus:
            return f"Certo! Em **{campus}**, qual local você deseja consultar? (Ex.: biblioteca, secretaria)"

        # Temos local + campus
        if info == "horarios":
            data = self.content_service.horarios(local=local, campus=campus)
            if "erro" in data:
                return f"Não encontrei horários para **{local}** em **{campus}**."
            return self._formatar_horarios(data)

        if info == "faq":
            data = self.content_service.faq(local=local, campus=campus)
            if not data:
                return f"Não encontrei FAQ para **{local}** em **{campus}**."
            return self._formatar_faq(data)

        if info == "contatos":
            data = self.content_service.contatos(local=local, campus=campus)
            if not data:
                return f"Não encontrei contatos para **{local}** em **{campus}**."
            return self._formatar_contatos(data)

        # padrão
        data = self.content_service.horarios(local=local, campus=campus)
        return self._formatar_horarios(data) if data else f"Não encontrei dados para **{local}** em **{campus}**."

    def _formatar_locais(self, data: dict) -> str:
        # data: { "campi": [ { "campus": "...", "locais": [ {"id","nome"}, ... ] }, ... ] }
        campi = data.get("campi", []) or []
        if not campi:
            return "No momento não encontrei a lista de locais por campus."
        linhas = ["Posso consultar estes locais por campus:"]
        for c in campi:
            campus = c.get("campus", "Campus")
            nomes = ", ".join(l.get("nome", "") for l in (c.get("locais") or []))
            linhas.append(f"• **{campus}**: {nomes}")
        linhas.append("Diga: 'horários da biblioteca em São Leopoldo', por exemplo.")
        return "\n".join(linhas)

    def _formatar_horarios(self, data: dict) -> str:
        # data: { local, campus, descricao_curta, horarios: {segunda_sexta, sabado, domingo}, observacoes_acessibilidade: [] }
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
            linhas.append(f"{i}. {item.get('pergunta', '')}")
            linhas.append(f"   → {item.get('resposta_simplificada', '')}")
        return "\n".join(linhas)

    def _formatar_contatos(self, data: dict) -> str:
        linhas = [f"**Contatos – {data.get('local', 'Local')} – {data.get('campus', 'Campus')}**"]
        if data.get("email"):
            linhas.append(f"• E-mail: {data['email']}")
        if data.get("telefone"):
            linhas.append(f"• Telefone: {data['telefone']}")
        if data.get("site"):
            linhas.append(f"• Site: {data['site']}")
        if data.get("endereco"):
            linhas.append(f"• Endereço: {data['endereco']}")
        if data.get("mapa_url"):
            linhas.append(f"• Mapa: {data['mapa_url']}")
        if data.get("acessibilidade"):
            linhas.append("Acessibilidade:")
            linhas += [f"• {o}" for o in (data.get("acessibilidade") or [])]
        return "\n".join(linhas)