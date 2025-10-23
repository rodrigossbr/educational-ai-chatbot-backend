from typing import Any, Dict, List

from educhatbot.core import HttpClientService, _env

API_BASE = _env("EXTERNAL_API_BASE", "http://localhost:3001/api")
TIMEOUT = float(_env("EXTERNAL_TIMEOUT_SECS", "6"))
RETRIES = int(_env("EXTERNAL_RETRY_TOTAL", "3"))


class EducationalContentService:
    """
    Camada de integração com a API simulada (Mockoon)
    para conteúdos, busca e quiz.
    """

    def __init__(self):
        self.http = HttpClientService(base_url=API_BASE, timeout=TIMEOUT, retries=RETRIES)
        self.aliases_map: Dict[str, str] = {}
        self.aliases_loaded = False

    def list_disciplinas(self) -> List[Dict[str, Any]]:
        resp = self.http.get("/disciplinas")
        resp.raise_for_status()
        return resp.json().get("disciplinas", [])

    def get_conteudos(self, disciplina: str) -> Dict[str, Any]:
        resp = self.http.get("/disciplinas/conteudos", params={"disciplina": disciplina})
        resp.raise_for_status()
        data = resp.json() or {}
        topicos = []
        for t in data.get("topicos", []):
            topicos.append({
                "id": t.get("id", ""),
                "titulo": t.get("titulo", ""),
                "texto_simplificado": t.get("resumo_simplificado") or t.get("resumo") or "",
                "exemplo": t.get("exemplo", ""),
            })
        return {
            "disciplina": data.get("disciplina", disciplina),
            "topicos": topicos
        }

    def get_aprofundamento(self, topico: str) -> dict:
        if not topico:
            return {"erro": "Tópico não informado."}

        try:
            r = self.http.get("/disciplinas/conteudos/aprofundamento", params={"topico": topico})
            return r.json()
        except Exception as e:
            print(f"[EducationalContentService] Erro em get_aprofundamento: {e}")
            return {"erro": str(e)}

    def locais(self) -> dict:
        return self.http.get("/institucional/locais").json()

    def horarios(self, local: str, campus: str) -> dict:
        return self.http.get("/institucional/horarios", params={"local": local, "campus": campus}).json()

    def faq(self, local: str, campus: str) -> dict:
        return self.http.get("/institucional/faq", params={"local": local, "campus": campus}).json()

    def contatos(self, local: str, campus: str) -> dict:
        return self.http.get("/institucional/contatos", params={"local": local, "campus": campus}).json()






    def buscar(self, termo: str) -> Dict[str, Any]:
        resp = self.http.get("/busca", params={"q": termo})
        resp.raise_for_status()
        return resp.json() or {"q": termo, "resultados": []}

    def quiz(self, disciplina: str, n: int = 3) -> Dict[str, Any]:
        resp = self.http.get("/quiz", params={"disciplina": disciplina, "n": n})
        resp.raise_for_status()
        return resp.json() or {"disciplina": disciplina, "quantidade": 0, "perguntas": []}

    def load_aliases(self):
        if self.aliases_loaded:
            return self.aliases_map
        r = self.http.get("/disciplinas")
        r.raise_for_status()
        for d in r.json().get("disciplinas", []):
            did = d.get("id", "").strip().lower()
            nome = d.get("nome", "").strip().lower()
            aliases: List[str] = [a.strip().lower() for a in (d.get("aliases") or [])]
            for k in {did, nome, *aliases}:
                if k:
                    self.aliases_map[k] = did
        self.aliases_loaded = True
        return self.aliases_map

    def normalize(self, raw: str | None) -> str:
        if not raw:
            return ""
        self.load_aliases()
        key = raw.strip().lower()
        return self.aliases_map.get(key, key)

    @staticmethod
    def normalizar_topicos(conteudos: Dict[str, Any]) -> str:
        topicos = conteudos.get("topicos", [])
        out: List[Dict[str, str]] = []
        for t in topicos:
            out.append({
                "id": t.get("id", ""),
                "titulo": t.get("titulo", ""),
                "texto_simplificado": t.get("texto_simplificado") or t.get("resumo") or "",
                "exemplo": t.get("exemplo", ""),
            })
        return EducationalContentService.resumir_topicos_para_resposta(out)

    @staticmethod
    def resumir_topicos_para_resposta(topicos: List[Dict[str, str]], limite: int = 3) -> str:
        """
        Gera um texto breve (bom para TTS e Libras) com até N tópicos.
        """
        itens = []
        for t in topicos[:limite]:
            base = f"\\- {t['titulo']}: {t['texto_simplificado']}".strip()
            if t.get("exemplo"):
                base += f" Ex.: {t['exemplo']}"
            itens.append(base)
        return "\n".join(itens)
