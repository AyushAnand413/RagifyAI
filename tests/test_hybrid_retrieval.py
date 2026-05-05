"""
Unit tests for BM25 hybrid retrieval and RRF fusion.
These tests do NOT require faiss, sentence_transformers, or a real index —
they exercise the pure-Python RRF logic and BM25 scoring in isolation.
"""
import sys
import types
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Stub out heavy imports so this test runs without ML dependencies
# ---------------------------------------------------------------------------
for mod_name in ("faiss", "sentence_transformers"):
    if mod_name not in sys.modules:
        stub = types.ModuleType(mod_name)
        if mod_name == "sentence_transformers":
            class _ST:
                def __init__(self, *a, **kw): pass
            stub.SentenceTransformer = _ST
        sys.modules[mod_name] = stub

# Now import the helpers directly from the module without instantiating Retriever
from retrieval.retriever import _tokenize, _reciprocal_rank_fusion


# ---------------------------------------------------------------------------
# _tokenize
# ---------------------------------------------------------------------------
def test_tokenize_lowercases():
    assert _tokenize("Hello World") == ["hello", "world"]

def test_tokenize_empty():
    assert _tokenize("") == []

def test_tokenize_splits_on_whitespace():
    assert _tokenize("  a  b  ") == ["a", "b"]


# ---------------------------------------------------------------------------
# _reciprocal_rank_fusion
# ---------------------------------------------------------------------------
def _make_results(chunk_ids):
    return [{"chunk_id": cid} for cid in chunk_ids]


def test_rrf_single_list():
    results = _reciprocal_rank_fusion([_make_results(["a", "b", "c"])])
    # rank 0 → 1/(60+1), rank 1 → 1/(60+2), rank 2 → 1/(60+3)
    assert results["a"] == pytest.approx(1 / 61)
    assert results["b"] == pytest.approx(1 / 62)
    assert results["a"] > results["b"] > results["c"]


def test_rrf_two_lists_agree_boosts_score():
    # "a" appears first in both lists → should outscore "b" which only appears in one
    list1 = _make_results(["a", "b"])
    list2 = _make_results(["a", "c"])
    results = _reciprocal_rank_fusion([list1, list2])
    # "a" gets 1/61 + 1/61, "b" gets 1/62, "c" gets 1/62
    assert results["a"] == pytest.approx(2 / 61)
    assert results["a"] > results["b"]
    assert results["a"] > results["c"]


def test_rrf_exclusive_chunks_included():
    list1 = _make_results(["x"])
    list2 = _make_results(["y"])
    results = _reciprocal_rank_fusion([list1, list2])
    assert "x" in results and "y" in results


def test_rrf_empty_lists():
    assert _reciprocal_rank_fusion([[], []]) == {}


def test_rrf_custom_k():
    results = _reciprocal_rank_fusion([_make_results(["a"])], k=0)
    assert results["a"] == pytest.approx(1 / 1)  # 1/(0 + 0 + 1)


# ---------------------------------------------------------------------------
# BM25 integration (requires only rank_bm25)
# ---------------------------------------------------------------------------
def test_bm25_scores_relevant_chunk_higher():
    from rank_bm25 import BM25Okapi
    corpus = [
        _tokenize("reciprocal rank fusion retrieval"),
        _tokenize("deep learning image classification"),
        _tokenize("sparse retrieval bm25 okapi"),
    ]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenize("bm25 retrieval"))
    # corpus[2] mentions bm25, corpus[0] mentions retrieval — both should beat corpus[1]
    assert scores[2] > scores[1]
    assert scores[0] > scores[1]


def test_bm25_zero_score_for_unrelated_query():
    from rank_bm25 import BM25Okapi
    corpus = [_tokenize("cat sat on the mat")]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenize("quantum physics"))
    assert scores[0] == 0.0
