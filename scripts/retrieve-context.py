#!/usr/bin/env python3
"""
retrieve-context.py — Retrieve relevant document chunks using a TF-IDF index.

Loads docs/.index/tfidf.json built by build-index.py, scores all documents
against the query using cosine similarity, and returns the top-k results as
JSON — each result contains the doc path, relevance score, and a ~200-word
text window around the best-matching paragraph.

Usage:
    python3 scripts/retrieve-context.py <query> [--top-k 5] [--index <path>]

Options:
    query       Search query string (required)
    --top-k     Number of results to return (default: 5)
    --index     Path to tfidf.json (default: docs/.index/tfidf.json)

Output: JSON array of {rank, score, path, chunk} objects, printed to stdout.
Exits 0 on success, 1 on error. Uses only Python stdlib.
"""
import os
import re
import json
import sys
from collections import Counter

STOP_WORDS = {
    'a','an','the','and','or','but','in','on','at','to','for','of','with',
    'by','from','is','are','was','were','be','been','being','have','has',
    'had','do','does','did','will','would','could','should','may','might',
    'shall','can','not','no','nor','so','yet','both','either','neither',
    'each','every','all','any','this','that','these','those','it','its',
    'if','as','than','then','when','where','which','who','whom','how',
    'what','why','up','out','about','into','through','during','before',
    'after','above','below','between','more','also','just','only','very',
    'too','such','same','other','another','i','you','he','she','we','they',
    'me','him','her','us','them','my','your','his','our','their',
}


def tokenise(text):
    """Lowercase, split on non-alphanumeric, remove stop words and short tokens."""
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]


def cosine_score(query_vec, doc_vec):
    """Dot product of query and document TF-IDF vectors (both already weighted)."""
    score = 0.0
    for term, qw in query_vec.items():
        dw = doc_vec.get(term, 0.0)
        score += qw * dw
    return score


def best_chunk(paragraphs, query_tokens, window_words=200):
    """
    Find the paragraph that best matches query_tokens by token overlap,
    then return a window of approximately window_words words centred on it.
    """
    if not paragraphs:
        return ''

    query_set = set(query_tokens)
    best_idx, best_hits = 0, -1
    for i, para in enumerate(paragraphs):
        para_tokens = set(re.findall(r'[a-z0-9]+', para.lower()))
        hits = len(para_tokens & query_set)
        if hits > best_hits:
            best_hits, best_idx = hits, i

    # Expand outward from best paragraph until we reach ~window_words words
    selected = [paragraphs[best_idx]]
    words_so_far = len(paragraphs[best_idx].split())
    lo, hi = best_idx - 1, best_idx + 1

    while words_so_far < window_words:
        added = False
        if lo >= 0:
            selected.insert(0, paragraphs[lo])
            words_so_far += len(paragraphs[lo].split())
            lo -= 1
            added = True
        if hi < len(paragraphs) and words_so_far < window_words:
            selected.append(paragraphs[hi])
            words_so_far += len(paragraphs[hi].split())
            hi += 1
            added = True
        if not added:
            break

    return '\n\n'.join(selected)


def load_index(index_path):
    """Load the tfidf.json index. Returns the parsed dict."""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Retrieve relevant doc chunks using a TF-IDF index'
    )
    parser.add_argument('query', nargs='?', default=None,
                        help='Search query string')
    parser.add_argument('--top-k', type=int, default=5,
                        help='Number of results to return (default: 5)')
    parser.add_argument('--index', default=None,
                        help='Path to tfidf.json (default: docs/.index/tfidf.json)')
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        sys.exit(0)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    index_path = args.index or os.path.join(repo_root, 'docs', '.index', 'tfidf.json')

    if not os.path.exists(index_path):
        print(f'[retrieve-context] ERROR: index not found: {index_path}', file=sys.stderr)
        print('[retrieve-context] Run: python3 scripts/build-index.py', file=sys.stderr)
        sys.exit(1)

    try:
        index = load_index(index_path)
    except (json.JSONDecodeError, OSError) as exc:
        print(f'[retrieve-context] ERROR: cannot load index: {exc}', file=sys.stderr)
        sys.exit(1)

    idf = index.get('idf', {})
    docs = index.get('docs', [])

    if not docs:
        print('[retrieve-context] Index is empty — run build-index.py first.', file=sys.stderr)
        sys.exit(0)

    query_tokens = tokenise(args.query)
    if not query_tokens:
        print('[retrieve-context] Query produced no tokens after filtering.', file=sys.stderr)
        sys.exit(0)

    # Build query TF-IDF vector
    tf = Counter(query_tokens)
    total = max(sum(tf.values()), 1)
    query_vec = {t: (c / total) * idf.get(t, 1.0) for t, c in tf.items()}

    # Score all documents
    scored = []
    for doc in docs:
        score = cosine_score(query_vec, doc.get('tfidf', {}))
        if score > 0.0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_results = scored[:args.top_k]

    if not top_results:
        print(json.dumps([]))
        sys.exit(0)

    output = []
    for rank, (score, doc) in enumerate(top_results, 1):
        chunk = best_chunk(doc.get('paragraphs', []), query_tokens)
        output.append({
            'rank': rank,
            'score': round(score, 4),
            'path': doc['path'],
            'chunk': chunk,
        })

    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
