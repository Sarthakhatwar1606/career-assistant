import streamlit as st
import ollama
import numpy as np
import pypdf
import requests
import json
import io
import re
import uuid
import csv
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Career Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Base ───────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, .stDeployButton { visibility: hidden; }
.stApp { background: #F1F5F9; }
.main .block-container { padding-top: 1.2rem; max-width: 1100px; }

/* ── Sidebar ────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0F172A 0%, #1E293B 100%) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #F1F5F9 !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #CBD5E1 !important;
    border-radius: 8px !important;
    transition: all 0.15s ease;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.25) !important;
    border-color: #6366F1 !important;
    color: #fff !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    border: none !important;
    color: #fff !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #F1F5F9 !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    color: #F1F5F9 !important;
}

/* ── Tabs ───────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: transparent;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 10px 22px;
    font-weight: 500;
    font-size: 0.9rem;
    color: #64748B;
    border: none;
    background: transparent;
    transition: all 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: #6366F1; background: #EEF2FF; }
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #6366F1 !important;
    border-top: 3px solid #6366F1 !important;
    font-weight: 600 !important;
}

/* ── Cards (st.container border=True) ──────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important;
    border-radius: 14px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04) !important;
    padding: 4px 4px !important;
    transition: box-shadow 0.2s ease, transform 0.15s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 4px 20px rgba(99,102,241,0.12) !important;
    transform: translateY(-1px);
}

/* ── Primary buttons ────────────────────────────────── */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px;
    color: white !important;
    transition: all 0.2s ease;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.45) !important;
    transform: translateY(-1px);
}

/* ── Secondary buttons ──────────────────────────────── */
.stButton > button[kind="secondary"] {
    border-radius: 8px !important;
    border-color: #CBD5E1 !important;
    color: #475569 !important;
    font-weight: 500 !important;
    transition: all 0.15s ease;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #6366F1 !important;
    color: #6366F1 !important;
    background: #EEF2FF !important;
}

/* ── Link buttons ───────────────────────────────────── */
.stLinkButton a {
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}

/* ── Inputs ─────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > textarea {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}

/* ── Select boxes ───────────────────────────────────── */
[data-baseweb="select"] > div { border-radius: 8px !important; }

/* ── Expander ───────────────────────────────────────── */
details { border-radius: 10px !important; border-color: #E2E8F0 !important; }
details summary {
    font-weight: 600;
    color: #475569;
    border-radius: 10px;
}

/* ── Chat messages ──────────────────────────────────── */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 4px !important;
    background: white !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] code,
[data-testid="stChatMessage"] pre {
    color: #1E293B !important;
}

/* ── Metric override ────────────────────────────────── */
[data-testid="stMetric"] {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border: 1px solid #F1F5F9;
}
[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700 !important; color: #1E293B !important; }
[data-testid="stMetricLabel"] { font-size: 0.78rem !important; font-weight: 500 !important; color: #64748B !important; text-transform: uppercase; letter-spacing: 0.6px; }

/* ── Dividers ───────────────────────────────────────── */
hr { border-color: #E2E8F0 !important; margin: 1.2rem 0 !important; }

/* ── Alerts / info ──────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Main content headings — force visible dark color ── */
.main h1, .main h2, .main h3,
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3 {
    color: #1E293B !important;
    opacity: 1 !important;
}

/* ── Sidebar toggle button — make it visible ─────────── */
[data-testid="collapsedControl"] {
    background: #6366F1 !important;
    border-radius: 0 8px 8px 0 !important;
    color: white !important;
    width: 24px !important;
    opacity: 1 !important;
}
button[kind="header"] {
    color: #CBD5E1 !important;
    opacity: 1 !important;
}

/* ── Hide only GitHub/Fork — NOT the sidebar toggle ──── */
.viewerBadge_container__r5tak,
#GithubIcon { visibility: hidden !important; display: none !important; }

/* ── Sidebar collapse/expand toggle — always visible ─── */
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: flex !important;
    background: #6366F1 !important;
    border-radius: 0 8px 8px 0 !important;
    color: white !important;
    opacity: 1 !important;
}
[data-testid="collapsedControl"] svg { fill: white !important; }

/* ── Applied (disabled) button — green ──────────────── */
.stButton > button[disabled] {
    background: #10B981 !important;
    border: none !important;
    color: white !important;
    opacity: 1 !important;
    cursor: default !important;
    font-weight: 600 !important;
}

/* ── File uploader — dark sidebar version ───────────── */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1.5px dashed rgba(255,255,255,0.35) !important;
    border-radius: 10px !important;
    padding: 8px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: #6366F1 !important;
    border: none !important;
    color: #ffffff !important;
    border-radius: 7px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.3px !important;
    padding: 6px 16px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
    background: #4F46E5 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.5) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span {
    color: #94A3B8 !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

EMBED_MODEL    = "nomic-embed-text"
COLLECTION     = "resume_chunks"
APP_COLLECTION = "job_applications"
CHUNK_SIZE     = 400
CHUNK_OVERLAP  = 80
DATA_DIR       = "./data"

# ── Cloud / local mode detection ───────────────────────────────────────────────
def _groq_key() -> str:
    # Try every possible way to get the key
    try:
        k = st.secrets["GROQ_API_KEY"]
        if k:
            return k
    except Exception:
        pass
    try:
        k = st.secrets.get("GROQ_API_KEY", "")
        if k:
            return k
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")

def IS_CLOUD() -> bool:
    return bool(_groq_key())

# Local models (Ollama)
AVAILABLE_MODELS = {
    "llama3.2:3b  (~2 GB)  ← recommended": "llama3.2:3b",
    "phi3.5:mini  (~2.2 GB)":               "phi3.5:mini",
    "llama3.2:1b  (~1.3 GB)  ← smallest":  "llama3.2:1b",
    "llama3.1     (4.9 GB)  ← original":   "llama3.1",
}

# Cloud models (Groq)
GROQ_MODELS = {
    "Llama 3.1 8B  — fast":   "llama-3.1-8b-instant",
    "Llama 3.3 70B — smart":  "llama-3.3-70b-versatile",
    "Gemma 2 9B":             "gemma2-9b-it",
    "Mixtral 8x7B":           "mixtral-8x7b-32768",
}

APP_STATUSES = ["Applied", "Phone Screen", "Interview", "Technical", "Offer", "Rejected", "Withdrawn"]
STATUS_COLORS = {
    "Applied":      "#4A90D9",
    "Phone Screen": "#9B59B6",
    "Interview":    "#F39C12",
    "Technical":    "#E67E22",
    "Offer":        "#27AE60",
    "Rejected":     "#E74C3C",
    "Withdrawn":    "#95A5A6",
}

COUNTRY_URL_LABEL = {
    "Any location":       "",
    "Remote / Worldwide": "Remote",
    "USA":                "United States",
    "India":              "India",
    "United Kingdom":     "United Kingdom",
    "Canada":             "Canada",
    "Australia":          "Australia",
    "Germany":            "Germany",
    "Europe":             "Europe",
}

COUNTRY_FILTERS = {
    "Any location":       None,
    "Remote / Worldwide": ["remote", "worldwide", "anywhere", "global", ""],
    "USA":                ["united states", "usa", "us ", "u.s.", "america", "remote", "worldwide", "anywhere"],
    "India":              ["india", "remote", "worldwide", "anywhere"],
    "United Kingdom":     ["united kingdom", "uk", " gb", "britain", "england", "remote", "worldwide"],
    "Canada":             ["canada", "remote", "worldwide", "anywhere"],
    "Australia":          ["australia", "remote", "worldwide", "anywhere"],
    "Germany":            ["germany", "deutschland", "remote", "worldwide", "anywhere"],
    "Europe":             ["europe", "eu", "remote", "worldwide", "anywhere"],
}

# ── Lightweight numpy vector store (replaces ChromaDB) ────────────────────────
class VectorStore:
    def __init__(self, persist_path: str | None = None):
        self.docs:  list[str]        = []
        self.embs:  list[list[float]] = []
        self.metas: list[dict]       = []
        self.ids:   list[str]        = []
        self.path = persist_path
        if persist_path and os.path.exists(persist_path):
            self._load()

    def add(self, documents, embeddings, ids, metadatas=None):
        for i, (doc, emb, id_) in enumerate(zip(documents, embeddings, ids)):
            self.docs.append(doc)
            self.embs.append(emb)
            self.ids.append(id_)
            self.metas.append((metadatas or [{}] * len(documents))[i])
        self._save()

    def count(self) -> int:
        return len(self.docs)

    def query(self, query_embeddings, n_results=4, **_):
        if not self.embs:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
        q   = np.array(query_embeddings[0], dtype=np.float32)
        emb = np.array(self.embs,           dtype=np.float32)
        q   /= np.linalg.norm(q)   + 1e-10
        emb /= np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10
        scores  = emb @ q
        n       = min(n_results, len(self.docs))
        top_idx = np.argsort(scores)[::-1][:n].tolist()
        return {
            "documents": [[self.docs[i]  for i in top_idx]],
            "metadatas": [[self.metas[i] for i in top_idx]],
            "distances": [[float(1 - scores[i]) for i in top_idx]],
            "ids":       [[self.ids[i]   for i in top_idx]],
        }

    def get(self, **_):
        return {"ids": self.ids, "documents": self.docs, "metadatas": self.metas}

    def update(self, ids, metadatas):
        for id_, meta in zip(ids, metadatas):
            if id_ in self.ids:
                self.metas[self.ids.index(id_)].update(meta)
        self._save()

    def delete(self, ids):
        for id_ in ids:
            if id_ in self.ids:
                i = self.ids.index(id_)
                self.docs.pop(i); self.embs.pop(i)
                self.metas.pop(i); self.ids.pop(i)
        self._save()

    def clear(self):
        self.docs.clear(); self.embs.clear()
        self.metas.clear(); self.ids.clear()
        if self.path and os.path.exists(self.path):
            os.remove(self.path)

    def _save(self):
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump({"docs": self.docs, "embs": self.embs,
                       "metas": self.metas, "ids": self.ids}, f)

    def _load(self):
        with open(self.path) as f:
            d = json.load(f)
        self.docs  = d["docs"];  self.embs  = d["embs"]
        self.metas = d["metas"]; self.ids   = d["ids"]

@st.cache_resource
def _resume_store() -> VectorStore:
    return VectorStore(None if IS_CLOUD() else f"{DATA_DIR}/resume.json")

@st.cache_resource
def _app_store() -> VectorStore:
    return VectorStore(None if IS_CLOUD() else f"{DATA_DIR}/apps.json")

# ── Sentence-transformers embedder (cloud only, cached) ────────────────────────
@st.cache_resource
def _st_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

# ── RAG helpers ────────────────────────────────────────────────────────────────
def chunk_text(text: str) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if c.strip()]

def embed(texts: list[str]) -> list[list[float]]:
    try:
        if IS_CLOUD():
            return _st_embedder().encode(texts).tolist()
        return ollama.embed(model=EMBED_MODEL, input=texts)["embeddings"]
    except Exception:
        # Graceful fallback — zero vectors so nothing crashes
        return [[0.0] * 384] * len(texts)

def index_resume(text: str) -> int:
    store  = _resume_store()
    store.clear()
    chunks = chunk_text(text)
    store.add(documents=chunks, embeddings=embed(chunks),
              ids=[f"chunk_{i}" for i in range(len(chunks))])
    return len(chunks)

def retrieve(query: str, n: int = 4) -> list[str]:
    store = _resume_store()
    if store.count() == 0:
        return []
    res = store.query(query_embeddings=[embed([query])[0]],
                      n_results=min(n, store.count()))
    return res["documents"][0] if res["documents"] else []

def build_prompt(query: str, context_chunks: list[str], history: list[dict]) -> list[dict]:
    system = (
        "You are an expert career coach and resume advisor. "
        "You have access to the user's resume content shown below. "
        "Give concise, actionable, and encouraging advice. "
        "When relevant, reference specific details from the resume.\n\n"
        "=== RESUME CONTEXT ===\n"
        + "\n---\n".join(context_chunks)
        + "\n=== END CONTEXT ==="
    )
    messages = [{"role": "system", "content": system}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": query})
    return messages

def stream_response(messages: list[dict], model: str):
    if IS_CLOUD():
        from groq import Groq
        client = Groq(api_key=_groq_key())
        stream = client.chat.completions.create(
            messages=messages, model=model, stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    else:
        for chunk in ollama.chat(model=model, messages=messages, stream=True):
            yield chunk["message"]["content"]

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# ── Application tracker (VectorStore) ─────────────────────────────────────────
def tracker_add(company: str, role: str, location: str, url: str,
                salary: str, status: str, notes: str) -> str:
    store  = _app_store()
    app_id = str(uuid.uuid4())
    store.add(
        documents=[f"{role} at {company}"],
        embeddings=embed([f"{role} at {company}"]),
        ids=[app_id],
        metadatas=[{
            "company": company, "role": role, "location": location,
            "url": url, "salary": salary, "status": status, "notes": notes,
            "applied_date": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        }],
    )
    return app_id

def tracker_all() -> list[dict]:
    store = _app_store()
    if store.count() == 0:
        return []
    res  = store.get()
    apps = [{"id": res["ids"][i], **res["metadatas"][i]}
            for i in range(len(res["ids"]))]
    return sorted(apps, key=lambda x: x.get("applied_date", ""), reverse=True)

def tracker_update_status(app_id: str, status: str, notes: str):
    _app_store().update(ids=[app_id], metadatas=[{"status": status, "notes": notes}])

def tracker_delete(app_id: str):
    _app_store().delete(ids=[app_id])

def tracker_similar(query: str, n: int = 5) -> list[dict]:
    store = _app_store()
    if store.count() == 0:
        return []
    res = store.query(query_embeddings=embed([query]),
                      n_results=min(n, store.count()))
    results = []
    for i, app_id in enumerate(res["ids"][0]):
        results.append({"id": app_id,
                        "similarity": round(1 - res["distances"][0][i], 3),
                        **res["metadatas"][0][i]})
    return results

def tracker_export_csv(apps: list[dict]) -> str:
    fields = ["company", "role", "location", "status", "applied_date", "salary", "url", "notes"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(apps)
    return buf.getvalue()

# ── Job search helpers ─────────────────────────────────────────────────────────
def suggest_job_titles(resume_text: str, model: str) -> list[str]:
    prompt = (
        "Based on this resume extract, return ONLY a JSON array of 4 short job search "
        "keywords (titles or roles), e.g. [\"Data Engineer\",\"Python Developer\"]. "
        "No explanation, just the JSON array.\n\nResume:\n" + resume_text[:2000]
    )
    resp = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    raw = resp["message"]["content"].strip()
    match = re.search(r"\[.*?\]", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return [t.strip().strip('"') for t in raw.strip("[]").split(",")][:4]

def _parse_date(raw) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromtimestamp(int(raw), tz=timezone.utc)
    except (ValueError, TypeError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(raw)[:19], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None

def _age_label(dt: datetime | None) -> str:
    if dt is None:
        return ""
    delta = datetime.now(tz=timezone.utc) - dt
    if delta.days == 0:
        hours = delta.seconds // 3600
        return f"{hours}h ago" if hours > 0 else "just now"
    if delta.days == 1:
        return "1 day ago"
    return f"{delta.days} days ago"

def _external_search_links(keywords: list[str], country_label: str) -> dict[str, str]:
    q    = quote_plus(" ".join(keywords))
    loc  = COUNTRY_URL_LABEL.get(country_label, "")
    qloc = quote_plus(loc) if loc else ""
    return {
        "Google Jobs":     f"https://www.google.com/search?q={q}+jobs{'+'+qloc if qloc else ''}&ibp=htl;jobs",
        "LinkedIn":        f"https://www.linkedin.com/jobs/search/?keywords={q}&location={qloc}",
        "Indeed":          f"https://www.indeed.com/jobs?q={q}&l={qloc}",
        "Glassdoor":       f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={q}&locT=N&locId=1",
        "Naukri (India)":  f"https://www.naukri.com/{'-'.join(keywords[0].lower().split()) if keywords else 'jobs'}-jobs",
    }

def _flat_tags(tags) -> list[str]:
    """Flatten tags that may contain nested lists (e.g. Jobicy jobIndustry)."""
    result = []
    for t in (tags or []):
        if isinstance(t, list):
            result.extend(str(x) for x in t)
        elif t:
            result.append(str(t))
    return result

def _matches_location(job: dict, country_terms: list[str] | None) -> bool:
    if country_terms is None:
        return True
    haystack = (job.get("location") or "").lower() + " " + " ".join(_flat_tags(job.get("tags", []))).lower()
    return any(term in haystack for term in country_terms)

def _relevance_score(job: dict, keywords: list[str]) -> int:
    title    = job.get("title", "").lower()
    tag_str  = " ".join(_flat_tags(job.get("tags", []))).lower()
    return sum(1 for kw in keywords if kw.lower() in title or kw.lower() in tag_str)

SOURCE_COLORS = {
    "Remotive":      "#0EA5E9",
    "RemoteOK":      "#10B981",
    "Arbeitnow":     "#F59E0B",
    "Jobicy":        "#8B5CF6",
    "HN Jobs":       "#FF6314",
    "Findwork.dev":  "#EC4899",
    "Adzuna":        "#14B8A6",
}

ADZUNA_COUNTRY = {
    "USA":                "us",
    "India":              "in",
    "United Kingdom":     "gb",
    "Canada":             "ca",
    "Australia":          "au",
    "Germany":            "de",
    "Europe":             "gb",
    "Remote / Worldwide": "us",
    "Any location":       "us",
}

API_KEYS_FILE = os.path.join("data", "api_keys.json")

def load_api_keys() -> dict:
    try:
        with open(API_KEYS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_api_keys(keys: dict):
    os.makedirs("data", exist_ok=True)
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def _job_card(job: dict) -> None:
    title   = job.get("title", "Untitled")
    company = job.get("company", "")
    loc     = job.get("location", "Remote")
    salary  = job.get("salary", "")
    url     = job.get("url", "")
    tags    = job.get("tags", [])[:5]
    posted  = _age_label(_parse_date(job.get("posted_at")))
    source  = job.get("source", "")
    src_color = SOURCE_COLORS.get(source, "#6366F1")

    tag_html = "".join(
        f"<span style='background:#F1F5F9;color:#475569;padding:2px 9px;"
        f"border-radius:20px;font-size:0.75rem;font-weight:500;margin-right:4px'>{t}</span>"
        for t in _flat_tags(tags)
    )
    meta_parts = [p for p in [company, loc, salary, posted] if p]
    meta_html = "  ·  ".join(meta_parts)

    st.markdown(
        f"""
        <div style='background:white;border-radius:14px;padding:18px 20px;
                    border-left:4px solid {src_color};
                    box-shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 16px rgba(0,0,0,0.04);
                    margin-bottom:10px;transition:box-shadow 0.2s ease'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                <div style='flex:1'>
                    <div style='font-size:1.05rem;font-weight:600;color:#1E293B;margin-bottom:4px'>{title}</div>
                    <div style='font-size:0.83rem;color:#64748B;margin-bottom:10px'>{meta_html}</div>
                    <div style='margin-bottom:8px'>{tag_html}</div>
                    {"<a href='"+url+"' target='_blank' style='font-size:0.78rem;color:#94A3B8;word-break:break-all'>"+url+"</a>" if url else ""}
                </div>
                <span style='background:{src_color}22;color:{src_color};padding:3px 10px;
                             border-radius:20px;font-size:0.72rem;font-weight:600;
                             margin-left:12px;white-space:nowrap'>{source}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    already_applied = url in st.session_state.get("applied_urls", set())
    btn1, btn2 = st.columns([1, 1])
    with btn1:
        if url:
            apply_key = f"apply_{hash(title + company)}"
            if already_applied:
                st.button("✓ Applied", key=apply_key, use_container_width=True,
                          disabled=True, type="primary")
            else:
                if st.button("Apply Now →", key=apply_key, use_container_width=True, type="primary"):
                    try:
                        tracker_add(company, title, loc, url, salary, "Applied",
                                    "Auto-logged via Apply Now button.")
                    except Exception:
                        pass  # log failure silently — never crash the page
                    st.session_state["applied_urls"].add(url)
                    import streamlit.components.v1 as components
                    components.html(
                        f'<script>window.open("{url}", "_blank");</script>',
                        height=0,
                    )
                    st.toast(f"Applied & logged: {title} at {company}", icon="🎉")
                    st.rerun()
    with btn2:
        if st.button("+ Log Manually", key=f"log_{hash(title+company)}", use_container_width=True):
            st.session_state["log_app_prefill"] = {
                "company":  company,
                "role":     title,
                "location": loc,
                "url":      url,
                "salary":   salary,
            }
            st.session_state["active_tab"] = 2

def search_remotive(keyword: str, limit: int = 6) -> list[dict]:
    try:
        r = requests.get("https://remotive.com/api/remote-jobs",
                         params={"search": keyword, "limit": limit}, timeout=10)
        return [{"title": j.get("title",""), "company": j.get("company_name",""),
                 "location": j.get("candidate_required_location","Remote"),
                 "salary": j.get("salary",""), "url": j.get("url",""),
                 "tags": j.get("tags",[]), "posted_at": j.get("publication_date",""),
                 "source": "Remotive"} for j in r.json().get("jobs",[])[:limit]]
    except Exception:
        return []

def search_remoteok(keyword: str, limit: int = 6) -> list[dict]:
    try:
        tag = keyword.lower().replace(" ", "-")
        r = requests.get(f"https://remoteok.com/api?tag={tag}",
                         headers={"User-Agent": "career-assistant/1.0"}, timeout=10)
        jobs = [j for j in r.json() if isinstance(j, dict) and "position" in j][:limit]
        return [{"title": j.get("position",""), "company": j.get("company",""),
                 "location": "Remote",
                 "salary": f"${j['salary_min']}–${j['salary_max']}" if j.get("salary_min") else "",
                 "url": j.get("url",""), "tags": j.get("tags",[]),
                 "posted_at": j.get("date",""), "source": "RemoteOK"} for j in jobs]
    except Exception:
        return []

def search_arbeitnow(keyword: str, limit: int = 6) -> list[dict]:
    try:
        r = requests.get("https://arbeitnow.com/api/job-board-api", timeout=10)
        kw = keyword.lower()
        filtered = [j for j in r.json().get("data",[])
                    if kw in j.get("title","").lower()
                    or any(kw in t.lower() for t in j.get("tags",[]))][:limit]
        return [{"title": j.get("title",""), "company": j.get("company_name",""),
                 "location": j.get("location",""), "salary": "",
                 "url": j.get("url",""), "tags": j.get("tags",[]),
                 "posted_at": j.get("created_at",""), "source": "Arbeitnow"} for j in filtered]
    except Exception:
        return []

def search_jobicy(keyword: str, limit: int = 8) -> list[dict]:
    try:
        r = requests.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"count": limit, "tag": keyword},
            timeout=10,
        )
        jobs = r.json().get("jobs", [])
        results = []
        for j in jobs:
            sal_min = j.get("jobSalaryMin")
            sal_max = j.get("jobSalaryMax")
            sal_cur = j.get("jobSalaryCurrency", "")
            salary  = f"{sal_cur}{sal_min}–{sal_max}" if sal_min and sal_max else ""
            industry = j.get("jobIndustry", "")
            if isinstance(industry, list):
                industry = ", ".join(str(x) for x in industry)
            results.append({
                "title":     j.get("jobTitle", ""),
                "company":   j.get("companyName", ""),
                "location":  j.get("jobGeo", "Remote"),
                "salary":    salary,
                "url":       j.get("url", ""),
                "tags":      [t for t in [j.get("jobType", ""), industry] if t],
                "posted_at": j.get("publishedAt", ""),
                "source":    "Jobicy",
            })
        return results
    except Exception:
        return []

def search_hn_jobs(keyword: str, limit: int = 8) -> list[dict]:
    """Search HN Who's Hiring via Algolia — YC company job postings."""
    try:
        r = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": keyword, "tags": "job", "hitsPerPage": limit},
            timeout=10,
        )
        results = []
        for h in r.json().get("hits", []):
            title = h.get("title", "")
            url   = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID','')}"
            # Parse "Company | Role | Details" style HN titles
            parts = [p.strip() for p in title.split("|")]
            role    = parts[1] if len(parts) > 1 else title
            company = parts[0] if len(parts) > 1 else h.get("author", "")
            results.append({
                "title":     role,
                "company":   company,
                "location":  "Remote / Various",
                "salary":    "",
                "url":       url,
                "tags":      ["YC", "startup"],
                "posted_at": h.get("created_at", ""),
                "source":    "HN Jobs",
            })
        return results
    except Exception:
        return []

def search_findwork(keyword: str, api_key: str, limit: int = 8) -> list[dict]:
    try:
        r = requests.get(
            "https://findwork.dev/api/jobs/",
            params={"search": keyword, "sort_by": "date"},
            headers={"Authorization": f"Token {api_key}"},
            timeout=10,
        )
        results = []
        for j in r.json().get("results", [])[:limit]:
            results.append({
                "title":     j.get("role", ""),
                "company":   j.get("company_name", ""),
                "location":  "Remote" if j.get("remote") else j.get("location", ""),
                "salary":    "",
                "url":       j.get("url", ""),
                "tags":      j.get("keywords", [])[:5],
                "posted_at": j.get("date_posted", ""),
                "source":    "Findwork.dev",
            })
        return results
    except Exception:
        return []

def search_adzuna(keyword: str, country_label: str,
                  app_id: str, app_key: str, limit: int = 8) -> list[dict]:
    country = ADZUNA_COUNTRY.get(country_label, "us")
    try:
        r = requests.get(
            f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
            params={
                "app_id":           app_id,
                "app_key":          app_key,
                "results_per_page": limit,
                "what":             keyword,
                "content-type":     "application/json",
            },
            timeout=10,
        )
        results = []
        for j in r.json().get("results", []):
            sal_min = j.get("salary_min")
            sal_max = j.get("salary_max")
            salary  = f"${sal_min:.0f}–${sal_max:.0f}" if sal_min and sal_max else ""
            results.append({
                "title":     j.get("title", ""),
                "company":   j.get("company", {}).get("display_name", ""),
                "location":  j.get("location", {}).get("display_name", ""),
                "salary":    salary,
                "url":       j.get("redirect_url", ""),
                "tags":      [j.get("category", {}).get("label", "")],
                "posted_at": j.get("created", ""),
                "source":    "Adzuna",
            })
        return results
    except Exception:
        return []

# ── Pre-warm embedder on cloud (all functions defined above by this point) ─────
if IS_CLOUD():
    try:
        _st_embedder()
    except Exception:
        pass

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    "messages":        [],
    "resume_indexed":  False,
    "resume_preview":  "",
    "resume_text":     "",
    "chat_model":      "llama3.2:3b",
    "job_results":     [],
    "job_keywords":    [],
    "log_app_prefill": None,
    "active_tab":      0,
    "applied_urls":    set(),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💼 Career Assistant")
    if IS_CLOUD():
        st.caption("Cloud mode · Groq API · Free")
    else:
        st.caption("Local mode · Ollama · 100% private")
        # Warn on cloud if key missing
        if not _groq_key() and os.environ.get("HOME", "").startswith("/home"):
            st.warning("⚠️ GROQ_API_KEY missing in Streamlit secrets. Chat won't work.", icon="🔑")
    st.divider()

    st.subheader("0 · Chat Model")
    _model_options = GROQ_MODELS if IS_CLOUD() else AVAILABLE_MODELS
    selected_label = st.selectbox(
        "Model (switch anytime)",
        options=list(_model_options.keys()),
        index=0,
    )
    st.session_state.chat_model = _model_options[selected_label]
    st.caption(f"Active: `{st.session_state.chat_model}`")
    st.divider()

    st.subheader("1 · Upload Your Resume")
    uploaded = st.file_uploader(
        "PDF or plain-text (.txt)",
        type=["pdf", "txt"],
        help="Your resume stays on your machine — nothing is sent to the cloud.",
    )
    if uploaded:
        raw = uploaded.read()
        resume_text = (
            extract_text_from_pdf(raw)
            if uploaded.name.endswith(".pdf")
            else raw.decode("utf-8", errors="ignore")
        )
        resume_text = re.sub(r"\n{3,}", "\n\n", resume_text).strip()
        if st.button("Index Resume", type="primary"):
            with st.spinner("Embedding resume chunks… (first run may take ~30s on cloud)"):
                try:
                    n = index_resume(resume_text)
                    msg = f"Indexed {n} chunks. Ready to chat!"
                except Exception as e:
                    n = 0
                    msg = f"⚠️ Indexing failed: {e}"
            st.session_state.resume_indexed = True
            st.session_state.resume_preview = resume_text[:600]
            st.session_state.resume_text    = resume_text
            st.session_state.messages       = []
            st.session_state.job_results    = []
            st.session_state.job_keywords   = []
            st.success(msg) if n else st.error(msg)

    if st.session_state.resume_indexed:
        with st.expander("Resume preview"):
            st.text(st.session_state.resume_preview + " …")

    st.divider()
    st.subheader("2 · Ask a Question")
    custom_q = st.text_area(
        "Type any career question",
        placeholder="e.g. Am I ready for a senior role? What salary should I ask for?",
        height=100,
        key="custom_question_input",
    )
    if st.button("Ask", type="primary", use_container_width=True, disabled=not custom_q.strip()):
        st.session_state["prefill"] = custom_q.strip()
        st.session_state["active_tab"] = 0
        st.rerun()

    st.caption("Quick suggestions:")
    for s in ["What are my strongest skills?", "Improve my resume for data engineering.",
              "Write a cover letter intro.", "What gaps should I address?",
              "Suggest 5 matching job titles."]:
        if st.button(s, use_container_width=True):
            st.session_state["prefill"] = s
            st.session_state["active_tab"] = 0

    st.divider()
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # ── API Keys (optional sources) ────────────────────────────────────────────
    st.divider()
    st.subheader("3 · API Keys (Optional)")
    st.caption("Unlocks Findwork.dev and Adzuna. Keys saved locally — never sent anywhere.")
    _keys = load_api_keys()
    with st.expander("Enter API Keys"):
        fw_key = st.text_input(
            "Findwork.dev Token",
            value=_keys.get("findwork", ""),
            type="password",
            placeholder="Get free key at findwork.dev/api-token",
        )
        az_id = st.text_input(
            "Adzuna App ID",
            value=_keys.get("adzuna_id", ""),
            placeholder="developer.adzuna.com",
        )
        az_key = st.text_input(
            "Adzuna App Key",
            value=_keys.get("adzuna_key", ""),
            type="password",
        )
        if st.button("Save Keys", type="primary", use_container_width=True):
            save_api_keys({"findwork": fw_key, "adzuna_id": az_id, "adzuna_key": az_key})
            st.success("Keys saved!")
            st.rerun()
    # expose keys to the rest of the app via session state
    if IS_CLOUD():
        # On Streamlit Cloud, pull optional keys from st.secrets
        try:
            cloud_keys = {
                "findwork":   st.secrets.get("FINDWORK_KEY", ""),
                "adzuna_id":  st.secrets.get("ADZUNA_ID", ""),
                "adzuna_key": st.secrets.get("ADZUNA_KEY", ""),
            }
        except Exception:
            cloud_keys = {}
        st.session_state["_api_keys"] = cloud_keys
    else:
        st.session_state["_api_keys"] = load_api_keys()

    # ── Tracker quick stats ────────────────────────────────────────────────────
    st.divider()
    apps = tracker_all()
    if apps:
        st.subheader("Application Stats")
        _t = len(apps)
        _a = sum(1 for a in apps if a["status"] in ("Applied","Phone Screen","Interview","Technical"))
        _o = sum(1 for a in apps if a["status"] == "Offer")
        _r = sum(1 for a in apps if a["status"] == "Rejected")
        def _mini_tile(label, val, color):
            return (f"<div style='background:rgba(255,255,255,0.07);border-radius:8px;"
                    f"padding:10px;text-align:center;border-left:3px solid {color}'>"
                    f"<div style='font-size:1.4rem;font-weight:700;color:#F1F5F9'>{val}</div>"
                    f"<div style='font-size:0.7rem;color:#94A3B8;text-transform:uppercase;"
                    f"letter-spacing:0.5px'>{label}</div></div>")
        c1, c2 = st.columns(2)
        c1.markdown(_mini_tile("Total",    _t, "#6366F1"), unsafe_allow_html=True)
        c2.markdown(_mini_tile("Active",   _a, "#F59E0B"), unsafe_allow_html=True)
        c1.markdown(_mini_tile("Offers",   _o, "#10B981"), unsafe_allow_html=True)
        c2.markdown(_mini_tile("Rejected", _r, "#EF4444"), unsafe_allow_html=True)

# ── Main tabs ──────────────────────────────────────────────────────────────────
tab_chat, tab_jobs, tab_tracker = st.tabs([
    "💬 Career Chat",
    "🔍 Find Jobs",
    "📊 My Applications",
])

# ── Tab 1: Chat ────────────────────────────────────────────────────────────────
with tab_chat:
    st.header("Chat with your Career Assistant")
    if not st.session_state.resume_indexed:
        st.info("👈  Upload and index your resume in the sidebar to get started.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prefill    = st.session_state.pop("prefill", None)
    user_input = st.chat_input("Ask me anything about your career…") or prefill

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        context  = retrieve(user_input) if st.session_state.resume_indexed else []
        messages = build_prompt(user_input, context, st.session_state.messages[:-1])
        with st.chat_message("assistant"):
            response_text = st.write_stream(stream_response(messages, st.session_state.chat_model))
        st.session_state.messages.append({"role": "assistant", "content": response_text})

# ── Tab 2: Job Search ──────────────────────────────────────────────────────────
with tab_jobs:
    st.header("Find Relevant Jobs")
    st.caption("Searches Remotive, RemoteOK, and Arbeitnow — free APIs, no key needed.")

    col_kw, col_btn = st.columns([3, 1])
    with col_kw:
        keyword_input = st.text_input(
            "Search keywords",
            value=", ".join(st.session_state.job_keywords) if st.session_state.job_keywords else "",
            placeholder="e.g. Data Engineer, Python, AWS",
        )
    with col_btn:
        st.write("")
        auto_suggest = st.button("Auto-suggest from resume",
                                 disabled=not st.session_state.resume_indexed,
                                 use_container_width=True)

    if auto_suggest:
        with st.spinner("Analysing your resume for job titles…"):
            titles = suggest_job_titles(st.session_state.resume_text, st.session_state.chat_model)
        st.session_state.job_keywords = titles
        st.rerun()

    search_btn = st.button("Search Jobs", type="primary")

    if search_btn and keyword_input.strip():
        keywords  = [k.strip() for k in keyword_input.split(",") if k.strip()]
        _ak       = st.session_state.get("_api_keys", {})
        fw_key    = _ak.get("findwork", "")
        az_id     = _ak.get("adzuna_id", "")
        az_key    = _ak.get("adzuna_key", "")

        # show which sources will be searched
        active_srcs = ["Remotive", "RemoteOK", "Arbeitnow", "Jobicy", "HN Jobs"]
        if fw_key:
            active_srcs.append("Findwork.dev")
        if az_id and az_key:
            active_srcs.append("Adzuna")

        all_jobs = []
        with st.spinner(f"Searching {len(active_srcs)} sources for: {', '.join(keywords)}…"):
            for kw in keywords[:3]:
                all_jobs.extend(search_remotive(kw))
                all_jobs.extend(search_remoteok(kw))
                all_jobs.extend(search_arbeitnow(kw))
                all_jobs.extend(search_jobicy(kw))
                all_jobs.extend(search_hn_jobs(kw))
                if fw_key:
                    all_jobs.extend(search_findwork(kw, fw_key))
                if az_id and az_key:
                    # get country from current filter selection (use "Any location" as fallback)
                    _country = st.session_state.get("_last_country", "Any location")
                    all_jobs.extend(search_adzuna(kw, _country, az_id, az_key))

        seen, unique = set(), []
        for j in all_jobs:
            key = (j["title"].lower(), j["company"].lower())
            if key not in seen:
                seen.add(key)
                unique.append(j)
        st.session_state.job_results  = unique
        st.session_state.job_keywords = [k.strip() for k in keyword_input.split(",")]
        st.session_state["_active_srcs"] = active_srcs

    if st.session_state.job_results:
        jobs = st.session_state.job_results
        st.divider()
        fc1, fc2, fc3 = st.columns(3)

        with fc1:
            TIMEFRAME_OPTIONS = {"Last 24 hours":1,"Last 3 days":3,"Last 7 days":7,"Last 14 days":14,"Last 30 days":30}
            selected_timeframe = st.selectbox("Posted within", list(TIMEFRAME_OPTIONS.keys()), index=4)
            cutoff = datetime.now(tz=timezone.utc) - timedelta(days=TIMEFRAME_OPTIONS[selected_timeframe])

        with fc2:
            selected_country = st.selectbox("Country / Location", list(COUNTRY_FILTERS.keys()), index=0)
            country_terms = COUNTRY_FILTERS[selected_country]
            st.session_state["_last_country"] = selected_country

        with fc3:
            sources = sorted({j["source"] for j in jobs})
            selected_sources = st.multiselect("Source", sources, default=sources)

        active_kws = [k.strip() for k in ", ".join(st.session_state.job_keywords).split(",") if k.strip()]

        filtered = []
        for j in jobs:
            if j["source"] not in selected_sources:
                continue
            dt = _parse_date(j.get("posted_at"))
            if dt is not None and dt < cutoff:
                continue
            if not _matches_location(j, country_terms):
                continue
            if active_kws and _relevance_score(j, active_kws) == 0:
                haystack = (j.get("title","") + " " + " ".join(_flat_tags(j.get("tags",[])))).lower()
                if not any(kw.lower() in haystack for kw in active_kws):
                    continue
            filtered.append(j)

        filtered.sort(key=lambda j: (
            -_relevance_score(j, active_kws),
            -(_parse_date(j.get("posted_at")) or datetime(1970,1,1,tzinfo=timezone.utc)).timestamp(),
        ))

        without_date = sum(1 for j in filtered if not _parse_date(j.get("posted_at")))
        srcs_used = st.session_state.get("_active_srcs", [])
        src_badges = " ".join(
            f"<span style='background:{SOURCE_COLORS.get(s,'#888')}22;color:{SOURCE_COLORS.get(s,'#888')};"
            f"padding:2px 8px;border-radius:12px;font-size:0.72rem;font-weight:600'>{s}</span>"
            for s in srcs_used
        )
        if src_badges:
            st.markdown(f"Searched: {src_badges}", unsafe_allow_html=True)
        note = f"**{len(filtered)} relevant jobs** match your filters"
        if without_date:
            note += f"  _(includes {without_date} with no posting date)_"
        st.markdown(note)

        if not filtered:
            st.warning("No jobs match all filters. Try widening the timeframe, location, or keywords.")
        else:
            for src in selected_sources:
                src_jobs = [j for j in filtered if j["source"] == src]
                if not src_jobs:
                    continue
                st.subheader(f"{src}  ({len(src_jobs)})")
                for job in src_jobs:
                    _job_card(job)

        st.divider()
        st.subheader("Search on Other Platforms")
        st.caption("Opens in a new tab — uses your current keywords and location filter.")
        ext_links = _external_search_links(active_kws or ["jobs"], selected_country)
        ICONS = {"Google Jobs":"🔍","LinkedIn":"💼","Indeed":"📋","Glassdoor":"🪟","Naukri (India)":"🇮🇳"}
        for col, (name, url) in zip(st.columns(len(ext_links)), ext_links.items()):
            with col:
                st.link_button(f"{ICONS[name]} {name}", url, use_container_width=True)

    elif not search_btn:
        if not st.session_state.resume_indexed:
            st.info("Upload and index your resume first, then click **Auto-suggest from resume**.")
        else:
            st.info("Type keywords or click **Auto-suggest from resume**, then hit **Search Jobs**.")

# ── Tab 3: Application Tracker ─────────────────────────────────────────────────
with tab_tracker:
    st.header("My Applications")

    # ── Metrics row ───────────────────────────────────────────────────────────
    apps = tracker_all()
    total    = len(apps)
    active   = sum(1 for a in apps if a["status"] in ("Applied","Phone Screen","Interview","Technical"))
    offers   = sum(1 for a in apps if a["status"] == "Offer")
    rejected = sum(1 for a in apps if a["status"] == "Rejected")

    def _stat_tile(label, value, color, icon):
        return (
            f"<div style='background:white;border-radius:14px;padding:20px 24px;"
            f"border-top:4px solid {color};"
            f"box-shadow:0 1px 3px rgba(0,0,0,0.05),0 4px 12px rgba(0,0,0,0.04);"
            f"text-align:center'>"
            f"<div style='font-size:1.6rem;margin-bottom:4px'>{icon}</div>"
            f"<div style='font-size:2rem;font-weight:700;color:#1E293B;line-height:1'>{value}</div>"
            f"<div style='font-size:0.72rem;font-weight:600;color:#94A3B8;"
            f"text-transform:uppercase;letter-spacing:0.8px;margin-top:6px'>{label}</div>"
            f"</div>"
        )

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(_stat_tile("Total Applied", total,    "#6366F1", "📋"), unsafe_allow_html=True)
    m2.markdown(_stat_tile("Active",        active,   "#F59E0B", "⚡"), unsafe_allow_html=True)
    m3.markdown(_stat_tile("Offers",        offers,   "#10B981", "🎉"), unsafe_allow_html=True)
    m4.markdown(_stat_tile("Rejected",      rejected, "#EF4444", "✕"), unsafe_allow_html=True)

    st.divider()

    # ── Log new application form ───────────────────────────────────────────────
    prefill_data = st.session_state.pop("log_app_prefill", None)
    with st.expander("➕  Log New Application", expanded=bool(prefill_data)):
        with st.form("log_app_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            company  = fc1.text_input("Company *",  value=prefill_data.get("company","")  if prefill_data else "")
            role     = fc2.text_input("Job Title *", value=prefill_data.get("role","")     if prefill_data else "")
            location = fc1.text_input("Location",   value=prefill_data.get("location","") if prefill_data else "")
            url      = fc2.text_input("Job URL",     value=prefill_data.get("url","")      if prefill_data else "")
            salary   = fc1.text_input("Salary / Range", value=prefill_data.get("salary","") if prefill_data else "")
            status   = fc2.selectbox("Status", APP_STATUSES)
            notes    = st.text_area("Notes", placeholder="Interview date, contact name, impressions…", height=80)
            submitted = st.form_submit_button("Save Application", type="primary")
            if submitted:
                if company.strip() and role.strip():
                    tracker_add(company.strip(), role.strip(), location, url, salary, status, notes)
                    st.success(f"Logged: **{role}** at **{company}**")
                    st.rerun()
                else:
                    st.error("Company and Job Title are required.")

    st.divider()

    # ── Filter + table ─────────────────────────────────────────────────────────
    if not apps:
        st.info("No applications yet. Hit an **Apply Now** button in the Jobs tab, then click **Log App**, or use the form above.")
    else:
        fa1, fa2 = st.columns([2, 2])
        with fa1:
            status_filter = st.multiselect(
                "Filter by status", APP_STATUSES, default=APP_STATUSES,
                key="tracker_status_filter",
            )
        with fa2:
            search_company = st.text_input("Search company / role", placeholder="Type to filter…")

        visible = [
            a for a in apps
            if a["status"] in status_filter
            and (not search_company or
                 search_company.lower() in a.get("company","").lower() or
                 search_company.lower() in a.get("role","").lower())
        ]

        st.markdown(f"**{len(visible)}** of {total} applications")

        for app in visible:
            color   = STATUS_COLORS.get(app["status"], "#888")
            role    = app.get("role", "")
            company = app.get("company", "")
            loc_sal = "  ·  ".join(filter(None, [app.get("location"), app.get("salary")]))
            date    = app.get("applied_date", "")
            notes   = app.get("notes", "")
            url     = app.get("url", "")

            st.markdown(
                f"""
                <div style='background:white;border-radius:14px;padding:18px 20px 10px 20px;
                            border-left:5px solid {color};
                            box-shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 16px rgba(0,0,0,0.04);
                            margin-bottom:8px'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                        <div>
                            <div style='font-size:1.05rem;font-weight:600;color:#1E293B'>{role}</div>
                            <div style='font-size:0.85rem;color:#475569;margin-top:2px'>{company}{"  ·  "+loc_sal if loc_sal else ""}</div>
                            <div style='font-size:0.78rem;color:#94A3B8;margin-top:4px'>Applied {date}</div>
                            {"<div style='font-size:0.82rem;color:#64748B;margin-top:6px;font-style:italic'>"+notes+"</div>" if notes else ""}
                        </div>
                        <span style='background:{color}22;color:{color};padding:4px 12px;
                                     border-radius:20px;font-size:0.78rem;font-weight:600;
                                     white-space:nowrap;margin-left:12px'>{app["status"]}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            ac1, ac2, ac3 = st.columns([2, 1, 1])
            if url:
                ac1.link_button("View Posting", url, use_container_width=True)
            with ac2.popover("Edit Status / Notes"):
                new_status = st.selectbox("Status", APP_STATUSES,
                                          index=APP_STATUSES.index(app["status"]),
                                          key=f"st_{app['id']}")
                new_notes  = st.text_area("Notes", value=notes,
                                          key=f"nt_{app['id']}", height=80)
                if st.button("Save", key=f"sv_{app['id']}", type="primary"):
                    tracker_update_status(app["id"], new_status, new_notes)
                    st.rerun()
            if ac3.button("Delete", key=f"dl_{app['id']}"):
                tracker_delete(app["id"])
                st.rerun()

        # ── Export CSV ─────────────────────────────────────────────────────────
        st.divider()
        ec1, ec2 = st.columns([3, 1])
        with ec1:
            st.subheader("Find Similar Past Applications")
            sim_query = st.text_input("Describe a role", placeholder="e.g. Senior data engineer at a fintech startup")
        with ec2:
            st.write("")
            st.write("")
            find_sim = st.button("Search", use_container_width=True)

        if find_sim and sim_query.strip():
            sim_results = tracker_similar(sim_query.strip())
            if sim_results:
                st.markdown("**Most similar applications you've logged:**")
                for r in sim_results:
                    st.markdown(
                        f"- **{r['role']}** at {r['company']} — "
                        f"_{r['status']}_ — similarity: `{r['similarity']}`"
                    )
            else:
                st.info("No similar applications found.")

        st.divider()
        csv_data = tracker_export_csv(apps)
        st.download_button(
            "⬇️  Export all to CSV",
            data=csv_data,
            file_name=f"applications_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
