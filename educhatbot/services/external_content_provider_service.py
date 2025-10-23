# services/external_content_provider.py
from __future__ import annotations
import urllib.parse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Optional

TIMEOUT = 6

def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=2, backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False
    )
    s.headers.update({
        "User-Agent": "EDUChatbot/1.0 (+https://example.local)",
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    })
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

class ExternalContentProviderService:
    _http = _session()

    @staticmethod
    def wiki_summary(term: str, lang: str = "pt") -> List[Dict]:
        if not term:
            return []
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(term)}"
        r = ExternalContentProviderService._http.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return []
        j = r.json()
        link = j.get("content_urls", {}).get("desktop", {}).get("page") or j.get("canonicalurl")
        return [{
            "title": j.get("title"),
            "type": "resumo",
            "source": f"Wikipedia ({lang})",
            "url": link,
            "snippet": j.get("extract"),
            "year": None,
            "authors": [],
        }]

    @staticmethod
    def openalex_search(term: str, limit: int = 5, lang_filter: str = "pt|en") -> List[Dict]:
        if not term:
            return []
        url = "https://api.openalex.org/works"
        params = {"search": term, "per_page": limit, "filter": f"language:{lang_filter}", "sort": "publication_year:desc"}
        r = ExternalContentProviderService._http.get(url, params=params, timeout=TIMEOUT)
        if r.status_code != 200:
            return []
        out: List[Dict] = []
        for w in r.json().get("results", []):
            out.append({
                "title": w.get("title"),
                "type": "artigo",
                "source": "OpenAlex",
                "url": w.get("primary_location", {}).get("landing_page_url")
                       or (w.get("open_access", {}) or {}).get("oa_url"),
                "snippet": "",
                "year": w.get("publication_year"),
                "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])],
            })
        return out

    @staticmethod
    def openlibrary_search(term: str, limit: int = 5, lang: str = "por") -> List[Dict]:
        if not term:
            return []
        url = "https://openlibrary.org/search.json"
        params = {"q": term, "limit": limit, "language": lang}
        r = ExternalContentProviderService._http.get(url, params=params, timeout=TIMEOUT)
        if r.status_code != 200:
            return []
        out: List[Dict] = []
        for b in r.json().get("docs", []):
            out.append({
                "title": b.get("title"),
                "type": "livro",
                "source": "Open Library",
                "url": f'https://openlibrary.org{b.get("key")}' if b.get("key") else None,
                "snippet": ", ".join(b.get("subject", [])[:6]) if b.get("subject") else "",
                "year": b.get("first_publish_year"),
                "authors": b.get("author_name", []) or [],
            })
        return out

    @staticmethod
    def openalex_by_university(ror_id: str, term: str, limit: int = 5) -> List[Dict]:
        if not ror_id or not term:
            return []
        url = "https://api.openalex.org/works"
        params = {
            "filter": f"institutions.ror:{ror_id},language:pt|en",
            "per_page": limit,
            "search": term,
            "sort": "publication_year:desc",
        }
        r = ExternalContentProviderService._http.get(url, params=params, timeout=TIMEOUT)
        if r.status_code != 200:
            return []
        out: List[Dict] = []
        for w in r.json().get("results", []):
            out.append({
                "title": w.get("title"),
                "type": "artigo",
                "source": "OpenAlex",
                "university_ror": ror_id,
                "url": w.get("primary_location", {}).get("landing_page_url")
                       or (w.get("open_access", {}) or {}).get("oa_url"),
                "snippet": "",
                "year": w.get("publication_year"),
                "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])],
            })
        return out

    @staticmethod
    def oai_search(base_url: str, term: str, limit: int = 5) -> List[Dict]:
        """Busca simples em OAI-PMH (Dublin Core). Requer 'sickle' instalado."""
        try:
            from sickle import Sickle
        except Exception:
            return []
        out: List[Dict] = []
        s = Sickle(base_url)
        recs = s.ListRecords(metadataPrefix="oai_dc")
        for r in recs:
            md = r.metadata or {}
            title = (md.get("title") or [""])[0]
            subjects = " ; ".join(md.get("subject", [])[:10])
            if term.lower() in (title + " " + subjects).lower():
                out.append({
                    "title": title,
                    "type": "tese/dissertacao",
                    "source": "OAI-PMH",
                    "url": (md.get("identifier") or [""])[0] or None,
                    "snippet": subjects,
                    "year": (md.get("date") or [""])[0][:4] or None,
                    "authors": md.get("creator", []) or [],
                })
            if len(out) >= limit:
                break
        return out

    # ---------- Agregador + Markdown ----------
    @staticmethod
    def aggregate_search(
        disciplina: Optional[str] = None,
        topico: Optional[str] = None,
        idioma: str = "pt",
        universidade_ror: Optional[str] = None,
        limit_total: int = 10,
    ) -> Dict[str, any]:
        term = " ".join(p for p in [disciplina or "", topico or ""] if p).strip()
        if not term:
            return {"items": [], "markdown": "Informe **disciplina** ou **tópico**."}

        items: List[Dict] = []
        items += ExternalContentProviderService.wiki_summary(term, "pt" if idioma == "pt" else "en")
        if universidade_ror:
            items += ExternalContentProviderService.openalex_by_university(universidade_ror, term, limit=5)
        else:
            items += ExternalContentProviderService.openalex_search(term, limit=5)
        items += ExternalContentProviderService.openlibrary_search(term, limit=5, lang="por" if idioma == "pt" else "eng")

        if not items:
            return {"items": [], "markdown": f"Não encontrei resultados para **{term}**."}

        # ordena: resumo > artigo (mais novo) > livro
        def score(x):
            base = {"resumo": 3, "artigo": 2, "livro": 1, "tese/dissertacao": 2}.get(x.get("type"), 0)
            yr = x.get("year") or 0
            try:
                yr = int(yr)
            except Exception:
                yr = 0
            return (base, yr)
        items.sort(key=score, reverse=True)
        items = items[:limit_total]

        # markdown
        header_uni = ""
        md_title = f"### Conteúdos sobre **{term}**{header_uni}\n\n"
        md_lines = [md_title]
        for i, x in enumerate(items, 1):
            title = x.get("title") or "(sem título)"
            url = x.get("url") or ""
            typ = (x.get("type") or "").capitalize()
            src = x.get("source") or ""
            year = x.get("year")
            year_txt = f" • {year}" if year else ""
            snippet = (x.get("snippet") or "").strip()
            md_lines.append(f"{i}. [{title}]({url}) — _{typ} • {src}{year_txt}_")
            if snippet:
                md_lines.append(f"   {snippet}")
        md_lines.append("")
        return {"items": items, "markdown": "\n".join(md_lines)}
