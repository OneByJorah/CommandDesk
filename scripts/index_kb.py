#!/usr/bin/env python3
"""
Knowledge Base Indexer
Loads documents from knowledge-base/ into ChromaDB.
"""
from __future__ import annotations

import hashlib
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger("index-kb")

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    logger.error("chromadb not installed. Run: pip install chromadb")
    sys.exit(1)

CHROMA_URL = os.getenv("CHROMA_URL", "http://chroma:8000")
KB_DIR = os.getenv("KB_DIR", "./knowledge-base")
COLLECTION_NAME = os.getenv("KB_COLLECTION", "helpdesk-kb")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    client = chromadb.HttpClient(url=CHROMA_URL)

    # Get or create collection
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2",
    )

    try:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    kb_path = Path(KB_DIR)
    if not kb_path.exists():
        logger.error("Knowledge base directory not found: %s", KB_DIR)
        sys.exit(1)

    files = list(kb_path.glob("*.md")) + list(kb_path.glob("*.txt"))
    logger.info("Found %d knowledge base files", len(files))

    total_chunks = 0
    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        content_hash = compute_hash(content)

        # Check if already indexed
        source_str = str(file_path)
        existing = collection.get(
            where={"source": source_str},
            limit=1,
        )
        if existing.get("ids"):
            # Check if content changed
            for meta in existing.get("metadatas", []):
                if meta and meta.get("hash") == content_hash:
                    logger.info("  [skip] %s (unchanged)", file_path.name)
                    break
            else:
                # Content changed, re-index
                collection.delete(where={"source": source_str})
            continue

        # Chunk and index
        chunks = chunk_text(content)
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_path.stem}_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": source_str,
                "file": file_path.name,
                "chunk_index": i,
                "hash": content_hash,
            })

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        total_chunks += len(chunks)
        logger.info("  [indexed] %s: %d chunks", file_path.name, len(chunks))

    # Get final count
    count = collection.count()
    logger.info("\nDone! Indexed %d new chunks. Total in collection: %d", total_chunks, count)


if __name__ == "__main__":
    main()
