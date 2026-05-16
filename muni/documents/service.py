import hashlib
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from muni.config import get_settings
from muni.db.models import Document
from muni.db.session import get_session


class DocumentError(Exception):
    pass


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with filepath.open("rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def ingest_local_file(city_slug: str, filepath: Path, source_url: str = "local") -> Document:
    if not filepath.exists() or not filepath.is_file():
        raise DocumentError(f"File not found: {filepath}")

    file_hash = compute_sha256(filepath)

    settings = get_settings()
    city_raw_dir = settings.raw_data_dir / city_slug
    city_raw_dir.mkdir(parents=True, exist_ok=True)

    dest_path = city_raw_dir / f"{file_hash}.pdf"

    with get_session() as session:
        existing = session.scalar(select(Document).where(Document.file_hash == file_hash))
        if existing:
            return existing

        if not dest_path.exists():
            shutil.copy2(filepath, dest_path)

        doc = Document(
            city=city_slug,
            source_url=source_url,
            local_path=str(dest_path.relative_to(settings.project_root)),
            file_hash=file_hash,
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc


def ingest_directory(city_slug: str, dirpath: Path) -> Tuple[int, int]:
    """Ingest all PDFs in a directory. Returns (ingested_count, skipped_count)."""
    if not dirpath.exists() or not dirpath.is_dir():
        raise DocumentError(f"Directory not found: {dirpath}")

    ingested = 0
    skipped = 0
    for file in dirpath.rglob("*.pdf"):
        if file.is_file():
            file_hash = compute_sha256(file)
            with get_session() as session:
                existing = session.scalar(select(Document).where(Document.file_hash == file_hash))
                if existing:
                    skipped += 1
                    continue

            try:
                ingest_local_file(city_slug, file)
                ingested += 1
            except DocumentError:
                pass

    return ingested, skipped


def list_documents(city_slug: str) -> List[Document]:
    with get_session() as session:
        docs = session.scalars(select(Document).where(Document.city == city_slug)).all()
        return list(docs)


def get_document(doc_id: int) -> Optional[Document]:
    with get_session() as session:
        return session.get(Document, doc_id)
