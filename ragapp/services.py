import json
from typing import Dict, List, Optional

from django.conf import settings

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage

# ✅ UPDATED: import LOCKED_DAILY_PROMPT
from ragapp.prompts import ROLE_AND_CONSTRAINTS, OUTPUT_FORMAT, LOCKED_DAILY_PROMPT


_VECTORSTORE: Optional[FAISS] = None


def _load_vectorstore() -> FAISS:
    global _VECTORSTORE

    if _VECTORSTORE is not None:
        return _VECTORSTORE

    index_dir = settings.RAG_INDEX_DIR
    if not index_dir.exists():
        raise RuntimeError("FAISS index not found. Run: python manage.py build_index")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    _VECTORSTORE = FAISS.load_local(
        str(index_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return _VECTORSTORE


def _load_metadata() -> Dict:
    meta_dir = settings.TRADING_KNOWLEDGE_DIR / "metadata"
    meta: Dict = {}
    if not meta_dir.exists():
        return meta

    for jf in sorted(meta_dir.glob("journal_metadata_*.json")):
        try:
            meta.update(json.loads(jf.read_text(encoding="utf-8")))
        except Exception:
            continue

    return meta


def _load_journal(date_iso: str) -> Optional[Document]:
    journals_dir = settings.TRADING_KNOWLEDGE_DIR / "journals"
    f = journals_dir / f"{date_iso}_NIFTY_Journal.md"
    if not f.exists():
        return None

    return Document(
        page_content=f.read_text(encoding="utf-8", errors="ignore"),
        metadata={"source": "journals", "filename": f.name, "path": str(f)},
    )


def _filter_journal_dates(meta: Dict, market_type_any: List[str], limit: int = 3) -> List[str]:
    dates: List[str] = []

    # Most recent first
    for date_iso, info in sorted(meta.items(), reverse=True):
        if not isinstance(info, dict):
            continue

        mt = info.get("market_type", [])
        if any(tag in mt for tag in market_type_any):
            dates.append(date_iso)

        if len(dates) >= limit:
            break

    return dates


def _format_context(docs: List[Document]) -> str:
    blocks: List[str] = []
    for d in docs:
        title = f"[{d.metadata.get('source')}] {d.metadata.get('filename')}"
        blocks.append(f"{title}\n{d.page_content}".strip())
    return "\n\n---\n\n".join(blocks)


def _build_final_user_request(user_query: str) -> str:
    """
    ✅ This makes your RAG app ALWAYS use the locked daily prompt.
    The textbox query becomes "extra instruction" (optional).
    """
    user_query = (user_query or "").strip()

    if user_query:
        return (
            f"{LOCKED_DAILY_PROMPT}\n\n"
            f"User extra instruction (apply this without breaking the A–F format):\n"
            f"{user_query}"
        )

    # If user gives nothing, run the locked prompt only
    return LOCKED_DAILY_PROMPT


def _stable_retrieval_query(user_query: str) -> str:
    """
    ✅ Retrieval query should be simple & broad so it fetches correct rules/playbooks.
    We do NOT want the full locked prompt text to drive similarity search.
    """
    user_query = (user_query or "").strip()

    base = "NIFTY 50 daily outlook, global cues, geopolitics, risk-off, earnings, FII DII, support resistance, VWAP, volume, trading stance"
    if user_query:
        return f"{base}. Extra focus: {user_query}"
    return base


def generate_outlook(query: str) -> str:
    if not settings.OPENAI_API_KEY:
        return (
            "OPENAI_API_KEY is missing.\n\n"
            "1) Copy .env.example to .env\n"
            "2) Add your OpenAI API key\n"
            "3) Restart the server\n"
        )

    vectorstore = _load_vectorstore()
    meta = _load_metadata()

    # ✅ Build final user request (locked prompt + optional extra instruction)
    final_user_request = _build_final_user_request(query)

    # ✅ Use a clean retrieval query so similarity search is accurate
    retrieval_query = _stable_retrieval_query(query)

    # Retrieve stable docs (rules + playbooks)
    stable_docs = vectorstore.similarity_search(retrieval_query, k=7)

    # Retrieve journal context using metadata tags (recent breakdown/slow days)
    dates = _filter_journal_dates(
        meta,
        market_type_any=["breakdown", "slow_grind", "weak_trend"],
        limit=3,
    )
    journal_docs = [d for d in (_load_journal(dt) for dt in dates) if d is not None]

    context = _format_context(stable_docs + journal_docs)

    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.2)

    system = SystemMessage(content=ROLE_AND_CONSTRAINTS)

    human = HumanMessage(
        content=(
            f"User request:\n{final_user_request}\n\n"
            f"Retrieved context (use this; do not hallucinate):\n{context}"
        )
    )

    resp = llm.invoke([system, human])
    return resp.content
