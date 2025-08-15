from __future__ import annotations
import os
import hashlib
from typing import List, Tuple
from datetime import datetime

from app.database import SessionLocal
from app.models.learning import Course, Module, Section, Lesson

# Default locations to ingest (.txt, .md)
DEFAULT_DIRS = [
    r"D:\\CamboAI\\docs\\specs",  # local copy inside repo if present
    r"C:\\Users\\johnl\\OneDrive\\Desktop",
    r"D:\\project",
    r"C:\\Users\\johnl\\CamboAI-TraderStation",
    r"D:\\CamboAI-TraderStation",
]

ALLOWED_EXTS = {".txt", ".md"}


def _hash_slug(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _discover_files(root_dirs: List[str]) -> List[Tuple[str, str]]:
    files: List[Tuple[str, str]] = []
    for root in root_dirs:
        if not os.path.exists(root):
            continue
        for base, _, names in os.walk(root):
            for n in names:
                ext = os.path.splitext(n)[1].lower()
                if ext in ALLOWED_EXTS:
                    p = os.path.join(base, n)
                    try:
                        size = os.path.getsize(p)
                    except Exception:
                        size = 0
                    # skip very large files > 2MB to avoid DB bloat
                    if size <= 2 * 1024 * 1024:
                        files.append((root, p))
    return files


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"[ERROR READING FILE] {e}"


def _ensure_course(db, title: str, slug: str) -> Course:
    course = db.query(Course).filter_by(slug=slug).first()
    if not course:
        course = Course(title=title, slug=slug, description="Auto-ingested curriculum from user specs", published=True)
        db.add(course)
        db.commit()
        db.refresh(course)
    return course


def _ensure_module(db, course_id: str, title: str, order_index: int) -> Module:
    row = db.query(Module).filter_by(course_id=course_id, title=title).first()
    if not row:
        row = Module(course_id=course_id, title=title, order_index=order_index)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _ensure_section(db, module_id: str, title: str, order_index: int) -> Section:
    row = db.query(Section).filter_by(module_id=module_id, title=title).first()
    if not row:
        row = Section(module_id=module_id, title=title, order_index=order_index)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _ensure_lesson(db, section_id: str, title: str, order_index: int, content: str) -> Lesson:
    # Use lesson title uniqueness per section
    row = db.query(Lesson).filter_by(section_id=section_id, title=title).first()
    if not row:
        row = Lesson(
            section_id=section_id,
            title=title,
            order_index=order_index,
            type="text",
            duration_sec=None,
            content_rich=content,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    else:
        # Update content if changed
        if (row.content_rich or "").strip() != (content or "").strip():
            row.content_rich = content
            db.commit()
    return row


def ingest_specs(root_dirs: List[str] | None = None) -> dict:
    """
    Crawl specified directories for .txt/.md and ingest as lessons under a single course.
    Grouping:
      - One course: "Cambo AI Master Curriculum"
      - Four modules by root: Desktop, Project Specs, TraderStation (User), TraderStation (D:)
      - One section per module: "Imported Specs"
      - Each file becomes a lesson; title = filename; content = file body
    Idempotent: Re-runs update or skip existing items.
    """
    roots = root_dirs or DEFAULT_DIRS
    files = _discover_files(roots)

    db = SessionLocal()
    created = 0
    updated = 0

    try:
        course = _ensure_course(db, title="Cambo AI Master Curriculum", slug="cambo-ai-master-curriculum")

        module_map = {
            roots[0] if len(roots) > 0 else "": "Desktop Specs",
            roots[1] if len(roots) > 1 else "": "Project Specs",
            roots[2] if len(roots) > 2 else "": "TraderStation (User)",
            roots[3] if len(roots) > 3 else "": "TraderStation (D:)",
        }

        modules_cache: dict[str, Module] = {}
        sections_cache: dict[str, Section] = {}

        # Ensure modules and sections exist
        order = 1
        for root, title in module_map.items():
            if not root:
                continue
            m = _ensure_module(db, course_id=course.id, title=title, order_index=order)
            modules_cache[root] = m
            s = _ensure_section(db, module_id=m.id, title="Imported Specs", order_index=1)
            sections_cache[root] = s
            order += 1

        # Ingest lessons
        for root, path in files:
            module = modules_cache.get(root)
            section = sections_cache.get(root)
            if not module or not section:
                # Unknown root — attach to Project Specs if available
                section = sections_cache.get(roots[1]) or next(iter(sections_cache.values()))
                if not section:
                    continue
            name = os.path.basename(path)
            title = os.path.splitext(name)[0]
            content = f"Source: {path}\n\n" + _read_file(path)
            before_count = db.query(Lesson).filter_by(section_id=section.id).count()
            _ensure_lesson(db, section_id=section.id, title=title, order_index=before_count + 1, content=content)
            after_count = db.query(Lesson).filter_by(section_id=section.id).count()
            if after_count > before_count:
                created += 1
            else:
                updated += 1

        return {"ok": True, "created": created, "updated": updated, "total_files": len(files)}
    finally:
        db.close()