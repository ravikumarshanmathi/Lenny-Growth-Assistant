"""
Transcript Ingestion CLI — batch ingest podcast transcripts into pgvector.

Usage:
    python ingest.py --dir ./transcripts/
    python ingest.py --file ./transcripts/episode_001.txt
    python ingest.py --reindex  # Re-embed all existing chunks

Pipeline:
    1. Read raw transcript files from --dir or --file
    2. Preprocess: normalize, clean, extract metadata
    3. Chunk: 512-token segments with 64-token overlap
    4. Embed: batch embedding via active LLM provider
    5. Store: insert into transcript_chunks table with pgvector

TODO (Phase 2):
    - Implement full ingestion pipeline
    - Add progress bars and logging
    - Support --reindex for embedding model changes
    - Validate chunk quality scores
"""

from __future__ import annotations

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Lenny's Podcast transcripts into the vector database."
    )
    parser.add_argument("--dir", type=str, help="Directory containing transcript files")
    parser.add_argument("--file", type=str, help="Single transcript file to ingest")
    parser.add_argument("--reindex", action="store_true", help="Re-embed all existing chunks")
    parser.add_argument("--chunk-size", type=int, default=512, help="Token count per chunk")
    parser.add_argument("--overlap", type=int, default=64, help="Token overlap between chunks")

    args = parser.parse_args()

    if not any([args.dir, args.file, args.reindex]):
        parser.print_help()
        sys.exit(1)

    print("[ingest] Ingestion pipeline — not yet implemented (Phase 2)")
    print(f"[ingest] Config: chunk_size={args.chunk_size}, overlap={args.overlap}")

    if args.dir:
        print(f"[ingest] Source: directory {args.dir}")
    elif args.file:
        print(f"[ingest] Source: file {args.file}")
    elif args.reindex:
        print("[ingest] Mode: re-index all existing chunks")


if __name__ == "__main__":
    main()
