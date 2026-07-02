"""Tests for the index_kb module."""
from __future__ import annotations

import pytest
from scripts.index_kb import chunk_text, compute_hash


class TestChunkText:
    def test_short_text(self):
        text = "Hello World"
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        assert len(chunks) == 1
        assert chunks[0] == "Hello World"

    def test_long_text(self):
        text = "A" * 3000
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        assert len(chunks) >= 3
        # Check overlap
        assert chunks[0][-200:] == chunks[1][:200]

    def test_exact_chunk_size(self):
        text = "A" * 1000
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        assert len(chunks) == 1

    def test_overlap_behavior(self):
        text = "Hello World! This is a test of the chunking function."
        chunks = chunk_text(text, chunk_size=20, overlap=5)
        assert len(chunks) >= 2
        # Check that chunks overlap
        for i in range(len(chunks) - 1):
            assert len(chunks[i]) <= 20

    def test_empty_text(self):
        chunks = chunk_text("", chunk_size=1000, overlap=200)
        assert len(chunks) == 0


class TestComputeHash:
    def test_consistent_hash(self):
        h1 = compute_hash("test content")
        h2 = compute_hash("test content")
        assert h1 == h2

    def test_different_content(self):
        h1 = compute_hash("content a")
        h2 = compute_hash("content b")
        assert h1 != h2

    def test_hash_length(self):
        h = compute_hash("test")
        assert len(h) == 64  # SHA-256 hex digest

    def test_empty_string(self):
        h = compute_hash("")
        assert len(h) == 64
