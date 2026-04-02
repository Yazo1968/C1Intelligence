"""
C1 — Reference Document Ingestion Script (Layer 2)

CLI tool for ingesting platform-wide reference documents (FIDIC, PMBOK, IFRS,
applicable laws) into the reference_documents and reference_chunks tables.

Run from the repository root:
    python scripts/ingest_reference.py \
        --file path/to/fidic_red_book_1999.pdf \
        --name "FIDIC Red Book 1999 — Conditions of Contract for Construction" \
        --document-type "FIDIC Conditions of Contract" \
        --standard-body "FIDIC" \
        --edition-year "1999" \
        --description "General Conditions (Part I) of the FIDIC Red Book 1999 edition"

Requires environment variables: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY
(loaded from .env at the repository root).
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

# Load .env before any src imports that read environment variables
load_dotenv(override=True)

from src.config import ALLOWED_EXTENSIONS  # noqa: E402
from src.clients import get_supabase_client  # noqa: E402
from src.ingestion.parser import parse_document_text_layer  # noqa: E402
from src.ingestion.chunker import chunk_document  # noqa: E402
from src.ingestion.embedder import embed_chunks  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest a reference document into the C1 Layer 2 warehouse."
    )
    parser.add_argument("--file", required=True, help="Path to the document file")
    parser.add_argument("--name", required=True, help="Full descriptive name")
    parser.add_argument(
        "--document-type",
        required=True,
        help='Type category (e.g., "FIDIC Conditions of Contract")',
    )
    parser.add_argument(
        "--standard-body",
        required=True,
        help='Issuing body (e.g., "FIDIC", "PMI", "IASB")',
    )
    parser.add_argument("--edition-year", default=None, help="Edition year or identifier")
    parser.add_argument(
        "--jurisdiction",
        default=None,
        help="Jurisdiction (None = global)",
    )
    parser.add_argument("--description", default=None, help="Additional description")
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Step 1: Validate file
    # ------------------------------------------------------------------
    file_path = os.path.abspath(args.file)

    if not os.path.isfile(file_path):
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if os.path.getsize(file_path) == 0:
        print(f"ERROR: File is empty: {file_path}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        print(
            f"ERROR: Unsupported file extension '{ext}'. "
            f"Allowed: {sorted(ALLOWED_EXTENSIONS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    filename = os.path.basename(file_path)
    print(f"Validating: {filename} ({ext})")

    # ------------------------------------------------------------------
    # Step 2: Parse with PyMuPDF (text-layer extraction)
    # ------------------------------------------------------------------
    print("Parsing document (text-layer)...")
    try:
        parsed = parse_document_text_layer(file_path, filename)
    except Exception as exc:
        print(f"ERROR: Parsing failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not parsed.text or not parsed.text.strip():
        print("ERROR: No text extracted from document", file=sys.stderr)
        sys.exit(1)

    print(f"  Extracted {len(parsed.text)} characters, {len(parsed.sections)} sections")

    # ------------------------------------------------------------------
    # Step 3: Chunk
    # ------------------------------------------------------------------
    print("Chunking...")
    chunks = chunk_document(parsed)

    if not chunks:
        print("ERROR: Chunking produced zero chunks", file=sys.stderr)
        sys.exit(1)

    print(f"  Produced {len(chunks)} chunks")

    # ------------------------------------------------------------------
    # Step 4: Embed
    # ------------------------------------------------------------------
    print("Embedding chunks...")
    try:
        embedded_chunks = embed_chunks(chunks)
    except Exception as exc:
        print(f"ERROR: Embedding failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"  Embedded {len(embedded_chunks)} chunks (3072 dims each)")

    # ------------------------------------------------------------------
    # Step 5: Insert reference_documents row
    # ------------------------------------------------------------------
    supabase = get_supabase_client()
    reference_document_id: str | None = None

    print("Inserting reference document record...")
    try:
        doc_row = {
            "name": args.name,
            "document_type": args.document_type,
            "standard_body": args.standard_body,
            "status": "ACTIVE",
        }
        if args.edition_year:
            doc_row["edition_year"] = args.edition_year
        if args.jurisdiction:
            doc_row["jurisdiction"] = args.jurisdiction
        if args.description:
            doc_row["description"] = args.description

        response = supabase.table("reference_documents").insert(doc_row).execute()
        reference_document_id = response.data[0]["id"]
    except Exception as exc:
        print(f"ERROR: Failed to insert reference document: {exc}", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 6: Bulk insert reference_chunks
    # ------------------------------------------------------------------
    print(f"Inserting {len(embedded_chunks)} chunks...")
    try:
        chunk_rows = [
            {
                "reference_document_id": reference_document_id,
                "chunk_index": ec.index,
                "content": ec.content,
                "embedding": ec.embedding,
                "token_count": ec.token_count,
            }
            for ec in embedded_chunks
        ]

        # Insert in batches of 50 to avoid payload size issues
        batch_size = 50
        for i in range(0, len(chunk_rows), batch_size):
            batch = chunk_rows[i : i + batch_size]
            supabase.table("reference_chunks").insert(batch).execute()

    except Exception as exc:
        # Rollback: delete the reference_documents row (CASCADE deletes chunks)
        print(f"ERROR: Chunk insertion failed: {exc}", file=sys.stderr)
        print("Rolling back reference document record...")
        try:
            supabase.table("reference_documents").delete().eq(
                "id", reference_document_id
            ).execute()
            print("  Rollback complete.")
        except Exception as rollback_exc:
            print(
                f"  WARNING: Rollback also failed: {rollback_exc}",
                file=sys.stderr,
            )
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 7: Success
    # ------------------------------------------------------------------
    print(
        f"\nIngested: {args.name} | ID: {reference_document_id} | Chunks: {len(embedded_chunks)}"
    )


if __name__ == "__main__":
    main()
