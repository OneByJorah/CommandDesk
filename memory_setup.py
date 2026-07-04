"""
Hermes memory setup for self-hosted llama.cpp.
Assumes llama-server is running on 127.0.0.1:8080 with --embedding enabled.
"""

import os
import sqlite3

import requests

LLAMA_HOST = os.environ.get("LLAMA_HOST", "http://127.0.0.1:8080")
EMBED_MODEL = os.environ.get("LLAMA_EMBED_MODEL", "qwen2.5-7b-instruct-q4_k_m")
DB_PATH = os.environ.get("MEMORY_DB", "/opt/hermes/data/memory.sqlite3")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            user_id TEXT,
            status TEXT,
            subject TEXT,
            body TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_message(user_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages(user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content),
    )
    conn.commit()
    conn.close()


def get_recent_messages(user_id: str, limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT role, content, created_at FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return list(reversed(rows))


def embed(text: str) -> list[float]:
    try:
        r = requests.post(
            f"{LLAMA_HOST}/embedding",
            json={"content": text, "model": EMBED_MODEL},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        if "embedding" in data:
            return data["embedding"]
        if "data" in data and data["data"]:
            return data["data"][0]["embedding"]
        raise ValueError(f"Unexpected embedding response: {data}")
    except Exception as e:
        raise RuntimeError(f"Embedding failed: {e}")


def create_ticket(ticket_id: str, user_id: str, subject: str, body: str, status: str = "open"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO tickets(ticket_id, user_id, status, subject, body) VALUES (?, ?, ?, ?, ?)",
        (ticket_id, user_id, status, subject, body),
    )
    conn.commit()
    conn.close()


def update_ticket_status(ticket_id: str, status: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?",
        (status, ticket_id),
    )
    conn.commit()
    conn.close()


def search_tickets(user_id: str, query: str, limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        """
        SELECT ticket_id, subject, body, status, created_at
        FROM tickets
        WHERE user_id = ? AND (subject LIKE ? OR body LIKE ?)
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, f"%{query}%", f"%{query}%", limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print("memory DB initialized at", DB_PATH)
    test = embed("ping")
    print("embedding OK, dim=", len(test))
