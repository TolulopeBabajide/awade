#!/usr/bin/env python3
"""
build-index.py — Build a TF-IDF document index over docs/*.md files.

Walks the docs/ directory, tokenises every .md file, computes TF-IDF weights,
and serialises the index to docs/.index/tfidf.json for use by retrieve-context.py.

Usage:
    python3 scripts/build-index.py [--docs-dir <path>] [--out <path>]

Exits 0 on success, 1 on error. All progress written to stderr.
Uses only Python stdlib: os, re, json, math, sys, collections.
"""
import os
import re
import json
import math
import sys
from collections import Counter, defaultdict

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


def walk_docs(docs_dir):
    """Yield (relative_path, content) for every .md file under docs_dir."""
    for root, dirs, files in os.walk(docs_dir):
        # Skip hidden dirs (e.g. .index)
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
        for fname in sorted(files):
            if fname.endswith('.md'):
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, docs_dir)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        yield rel, f.read()
                except OSError as exc:
                    print(f'[build-index] WARN: cannot read {fpath}: {exc}', file=sys.stderr)


def build_tfidf(docs_dir):
    """Build TF-IDF index. Returns dict suitable for JSON serialisation."""
    documents = list(walk_docs(docs_dir))
    if not documents:
        print('[build-index] WARN: no .md files found under ' + docs_dir, file=sys.stderr)
        return {'docs': [], 'idf': {}, 'vocabulary': [], 'num_docs': 0}

    # TF: normalised term frequency per document
    doc_tf_list = []
    for _rel, content in documents:
        tokens = tokenise(content)
        counts = Counter(tokens)
        total = max(sum(counts.values()), 1)
        doc_tf_list.append({t: c / total for t, c in counts.items()})

    # DF: how many documents contain each term
    df = defaultdict(int)
    for tf_map in doc_tf_list:
        for term in tf_map:
            df[term] += 1

    N = len(documents)
    # IDF: log(N / df) + 1  (smooth variant — never zero)
    idf = {term: math.log(N / cnt) + 1.0 for term, cnt in df.items()}

    # Build per-document vectors and store paragraph text for chunk retrieval
    doc_vectors = []
    for i, (rel, content) in enumerate(documents):
        tf = doc_tf_list[i]
        vec = {term: round(tf_val * idf[term], 6) for term, tf_val in tf.items()}
        # Split into non-trivial paragraphs (>30 chars after stripping)
        paragraphs = [p.strip() for p in re.split(r'\n\n+', content)
                      if len(p.strip()) > 30]
        doc_vectors.append({
            'path': rel,
            'tfidf': vec,
            'paragraphs': paragraphs,
        })

    vocabulary = sorted(idf.keys())
    return {
        'docs': doc_vectors,
        'idf': idf,
        'vocabulary': vocabulary,
        'num_docs': N,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Build TF-IDF index over docs/*.md files'
    )
    parser.add_argument('--docs-dir', default=None,
                        help='Docs directory (default: <repo-root>/docs)')
    parser.add_argument('--out', default=None,
                        help='Output JSON path (default: <docs-dir>/.index/tfidf.json)')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    docs_dir = args.docs_dir or os.path.join(repo_root, 'docs')
    out_path = args.out or os.path.join(docs_dir, '.index', 'tfidf.json')

    if not os.path.isdir(docs_dir):
        print(f'[build-index] ERROR: docs directory not found: {docs_dir}', file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    print(f'[build-index] Scanning {docs_dir} ...', file=sys.stderr)
    import time
    t0 = time.time()
    index = build_tfidf(docs_dir)
    elapsed = time.time() - t0

    n_docs = index.get('num_docs', 0)
    n_terms = len(index.get('vocabulary', []))

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, separators=(',', ':'))

    print(
        f'[build-index] Done: {n_docs} docs, {n_terms} terms → {out_path} '
        f'({elapsed:.2f}s)',
        file=sys.stderr
    )


if __name__ == '__main__':
    main()
