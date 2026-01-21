from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def load_md_docs(folder: Path, source: str) -> List[Document]:
    docs: List[Document] = []
    if not folder.exists():
        return docs

    for p in sorted(folder.glob('*.md')):
        docs.append(
            Document(
                page_content=p.read_text(encoding='utf-8', errors='ignore'),
                metadata={'source': source, 'filename': p.name, 'path': str(p)},
            )
        )
    return docs


def build_and_save_index(trading_knowledge_dir: Path, index_dir: Path) -> None:
    playbooks = load_md_docs(trading_knowledge_dir / 'playbooks', 'playbooks')
    rules = load_md_docs(trading_knowledge_dir / 'rules', 'rules')
    summaries = load_md_docs(trading_knowledge_dir / 'summaries', 'summaries')

    stable_docs = playbooks + rules + summaries
    if not stable_docs:
        raise RuntimeError('No stable docs found (playbooks/rules/summaries).')

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_documents(stable_docs)

    embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
    vs = FAISS.from_documents(chunks, embeddings)

    index_dir.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(index_dir))
