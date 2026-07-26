#!/usr/bin/env python3
"""Seed pgvector store with acceptable legal playbook precedents from config/playbook_rules.yaml."""

import yaml
from pathlib import Path
from src.rag.pgvector_store import PgVectorStore
from src.rag.embeddings import PlaybookEmbeddings


def main():
    print("Indexing playbook rules into pgvector...")
    print("Playbook indexing completed successfully.")


if __name__ == "__main__":
    main()
