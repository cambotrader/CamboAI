from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import json
import uuid

from app.database import get_db
from app.models.learning import (
    Course, Module, Section, Lesson, Quiz, Assignment,
    DiscussionThread, DiscussionPost, Progress, Certificate, Submission
)
from app.services.progress_service import log_progress

router = APIRouter(prefix="/api/learning", tags=["Learning"])

# ---------- DTOs ----------
class CourseDTO(BaseModel):
    id: str
    title: str
    slug: str
    description: Optional[str] = None
    hero_image: Optional[str] = None
    published: bool

class ModuleDTO(BaseModel):
    id: str
    course_id: str
    title: str
    order_index: int

class SectionDTO(BaseModel):
    id: str
    module_id: str
    title: str
    order_index: int

class LessonDTO(BaseModel):
    id: str
    section_id: str
    title: str
    order_index: int
    type: str
    duration_sec: Optional[int] = None

class LessonDetailDTO(LessonDTO):
    content_rich: Optional[str] = None
    video_url: Optional[str] = None
    embed_url: Optional[str] = None
    downloads_json: Optional[str] = None

class ProgressUpdate(BaseModel):
    status: Optional[str] = None
    percent: Optional[int] = None

class SeedResponse(BaseModel):
    ok: bool
    course_id: str

# Quiz DTOs
class QuizDTO(BaseModel):
    id: str
    lesson_id: str
    settings: Dict[str, Any]
    questions: List[Dict[str, Any]]

class QuizAttempt(BaseModel):
    answers: Dict[str, Any]  # {questionId: answer or [answers]}

class QuizResult(BaseModel):
    score: float
    max_score: float
    passed: bool
    details: List[Dict[str, Any]]

# Assignment DTOs
class AssignmentDTO(BaseModel):
    id: str
    lesson_id: str
    prompt: Optional[str] = None
    rubric: Optional[Dict[str, Any]] = None
    due_at: Optional[str] = None

class AssignmentSubmission(BaseModel):
    text: Optional[str] = None
    files: Optional[List[Dict[str, str]]] = None  # [{label,url}]

class DiscussionThreadCreate(BaseModel):
    title: str

class DiscussionPostCreate(BaseModel):
    body: str
    parent_post_id: Optional[str] = None

# ---------- Helpers ----------

def _get_course_id_for_lesson(db: Session, lesson_id: str) -> Optional[str]:
    lesson = db.query(Lesson).filter_by(id=lesson_id).first()
    if not lesson:
        return None
    section = db.query(Section).filter_by(id=lesson.section_id).first()
    if not section:
        return None
    module = db.query(Module).filter_by(id=section.module_id).first()
    if not module:
        return None
    return module.course_id

# ---------- Read Endpoints ----------
@router.get("/courses", response_model=List[CourseDTO])
async def list_courses(db: Session = Depends(get_db)):
    rows = db.query(Course).filter_by(published=True).all()
    return [CourseDTO(
        id=r.id, title=r.title, slug=r.slug, description=r.description,
        hero_image=r.hero_image, published=r.published
    ) for r in rows]

@router.get("/courses/{course_id}/modules", response_model=List[ModuleDTO])
async def list_modules(course_id: str, db: Session = Depends(get_db)):
    rows = db.query(Module).filter_by(course_id=course_id).order_by(Module.order_index.asc()).all()
    return [ModuleDTO(id=r.id, course_id=r.course_id, title=r.title, order_index=r.order_index) for r in rows]

@router.get("/modules/{module_id}/sections", response_model=List[SectionDTO])
async def list_sections(module_id: str, db: Session = Depends(get_db)):
    rows = db.query(Section).filter_by(module_id=module_id).order_by(Section.order_index.asc()).all()
    return [SectionDTO(id=r.id, module_id=r.module_id, title=r.title, order_index=r.order_index) for r in rows]

@router.get("/sections/{section_id}/lessons", response_model=List[LessonDTO])
async def list_lessons(section_id: str, db: Session = Depends(get_db)):
    rows = db.query(Lesson).filter_by(section_id=section_id).order_by(Lesson.order_index.asc()).all()
    return [LessonDTO(
        id=r.id, section_id=r.section_id, title=r.title, order_index=r.order_index,
        type=r.type, duration_sec=r.duration_sec
    ) for r in rows]

@router.get("/lessons/{lesson_id}", response_model=LessonDetailDTO)
async def get_lesson(lesson_id: str, db: Session = Depends(get_db)):
    r = db.query(Lesson).filter_by(id=lesson_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonDetailDTO(
        id=r.id, section_id=r.section_id, title=r.title, order_index=r.order_index,
        type=r.type, duration_sec=r.duration_sec, content_rich=r.content_rich,
        video_url=r.video_url, embed_url=r.embed_url, downloads_json=r.downloads_json
    )

# ---------- Progress ----------
@router.post("/lessons/{lesson_id}/progress")
async def update_progress(lesson_id: str, payload: ProgressUpdate, db: Session = Depends(get_db)):
    # Placeholder user identity — integrate auth later
    user_id = "demo-user"
    prog = db.query(Progress).filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if not prog:
        course_id = _get_course_id_for_lesson(db, lesson_id) or ""
        prog = Progress(user_id=user_id, course_id=course_id, lesson_id=lesson_id, status="in_progress", percent=0)
        db.add(prog)
    if payload.status is not None:
        prog.status = payload.status
    if payload.percent is not None:
        prog.percent = max(0, min(100, payload.percent))
    prog.last_seen_at = datetime.utcnow()
    db.commit()
    return {"ok": True}

# ---------- Quiz ----------
@router.get("/lessons/{lesson_id}/quiz", response_model=QuizDTO)
async def get_quiz_for_lesson(lesson_id: str, db: Session = Depends(get_db)):
    row = db.query(Quiz).filter_by(lesson_id=lesson_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Quiz not found")
    settings = json.loads(row.settings_json or '{}')
    questions = json.loads(row.questions_json or '[]')
    return QuizDTO(id=row.id, lesson_id=row.lesson_id, settings=settings, questions=questions)

@router.post("/quizzes/{quiz_id}/attempt", response_model=QuizResult)
async def submit_quiz_attempt(quiz_id: str, payload: QuizAttempt, db: Session = Depends(get_db)):
    row = db.query(Quiz).filter_by(id=quiz_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Quiz not found")
    settings = json.loads(row.settings_json or '{}')
    questions = json.loads(row.questions_json or '[]')

    total = 0.0
    score = 0.0
    details = []

    for q in questions:
        qid = str(q.get('id'))
        points = float(q.get('points', 1))
        total += points
        qtype = q.get('type')
        correct = q.get('correct')
        given = payload.answers.get(qid)
        is_correct = False

        if qtype in ('mcq', 'short'):
            is_correct = (str(given).strip().lower() == str(correct).strip().lower())
        elif qtype == 'multi':
            # Treat as set match (order-insensitive)
            try:
                is_correct = set(map(str, (given or []))) == set(map(str, (correct or [])))
            except Exception:
                is_correct = False
        else:
            # Unknown type: no score
            is_correct = False

        if is_correct:
            score += points
        details.append({
            'id': qid,
            'correct': is_correct,
            'points': points,
            'earned': points if is_correct else 0,
        })

    pass_score = float(settings.get('pass_score', total))
    passed = score >= pass_score

    # If passed, mark lesson progress completed (best effort)
    try:
        lesson_id = row.lesson_id
        await update_progress(lesson_id, ProgressUpdate(status='completed', percent=100), db)  # type: ignore
    except Exception:
        pass

    return QuizResult(score=score, max_score=total, passed=passed, details=details)

# ---------- Assignment ----------
@router.get("/lessons/{lesson_id}/assignment", response_model=AssignmentDTO)
async def get_assignment_for_lesson(lesson_id: str, db: Session = Depends(get_db)):
    row = db.query(Assignment).filter_by(lesson_id=lesson_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Assignment not found")
    rubric = None
    try:
        rubric = json.loads(row.rubric_json) if row.rubric_json else None
    except Exception:
        rubric = None
    return AssignmentDTO(
        id=row.id, lesson_id=row.lesson_id, prompt=row.prompt,
        rubric=rubric, due_at=row.due_at.isoformat() if row.due_at else None
    )

@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment(assignment_id: str, body: AssignmentSubmission, db: Session = Depends(get_db)):
    # Placeholder user identity — integrate auth later
    user_id = "demo-user"
    files_json = json.dumps(body.files or [])
    sub = Submission(
        assignment_id=assignment_id,
        user_id=user_id,
        files_json=files_json,
        text=body.text or "",
        grade=None,
        feedback=None,
        submitted_at=datetime.utcnow(),
    )
    db.add(sub)
    db.commit()
    return {"ok": True, "submission_id": sub.id}

# ---------- Discussion ----------
@router.get("/lessons/{lesson_id}/discussion/threads")
async def list_threads(lesson_id: str, db: Session = Depends(get_db)):
    rows = db.query(DiscussionThread).filter_by(lesson_id=lesson_id).order_by(DiscussionThread.created_at.desc()).all()
    return [{
        'id': r.id,
        'title': r.title,
        'user_id': r.user_id,
        'pinned': r.pinned,
        'created_at': r.created_at.isoformat(),
    } for r in rows]

@router.post("/lessons/{lesson_id}/discussion/threads")
async def create_thread(lesson_id: str, body: DiscussionThreadCreate, db: Session = Depends(get_db)):
    user_id = "demo-user"
    t = DiscussionThread(lesson_id=lesson_id, user_id=user_id, title=body.title, pinned=False)
    db.add(t)
    db.commit()
    return {"ok": True, "id": t.id}

@router.get("/discussions/{thread_id}/posts")
async def list_posts(thread_id: str, db: Session = Depends(get_db)):
    rows = db.query(DiscussionPost).filter_by(thread_id=thread_id).order_by(DiscussionPost.created_at.asc()).all()
    return [{
        'id': r.id,
        'user_id': r.user_id,
        'body': r.body,
        'parent_post_id': r.parent_post_id,
        'created_at': r.created_at.isoformat(),
    } for r in rows]

@router.post("/discussions/{thread_id}/posts")
async def create_post(thread_id: str, body: DiscussionPostCreate, db: Session = Depends(get_db)):
    user_id = "demo-user"
    p = DiscussionPost(thread_id=thread_id, user_id=user_id, body=body.body, parent_post_id=body.parent_post_id)
    db.add(p)
    db.commit()
    return {"ok": True, "id": p.id}

# ---------- Certificates ----------
@router.post("/certificates/{course_id}/issue")
async def issue_certificate(course_id: str, db: Session = Depends(get_db)):
    user_id = "demo-user"
    # Simple check: at least one progress completed for this course
    any_completed = db.query(Progress).filter_by(user_id=user_id, course_id=course_id, status='completed').first() is not None
    if not any_completed:
        raise HTTPException(status_code=400, detail="Course not completed yet")
    existing = db.query(Certificate).filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        return {"ok": True, "certificate_id": existing.id, "cert_number": existing.cert_number, "pdf_url": existing.pdf_url}
    cert = Certificate(
        user_id=user_id,
        course_id=course_id,
        issued_at=datetime.utcnow(),
        cert_number=f"CERT-{uuid.uuid4().hex[:10].upper()}",
        pdf_url=f"https://example.com/cert/{uuid.uuid4().hex[:8]}"  # placeholder
    )
    db.add(cert)
    db.commit()
    return {"ok": True, "certificate_id": cert.id, "cert_number": cert.cert_number, "pdf_url": cert.pdf_url}

@router.get("/certificates/{course_id}/me")
async def get_my_certificate(course_id: str, db: Session = Depends(get_db)):
    user_id = "demo-user"
    cert = db.query(Certificate).filter_by(user_id=user_id, course_id=course_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return {
        "id": cert.id,
        "cert_number": cert.cert_number,
        "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
        "pdf_url": cert.pdf_url,
    }

# ---------- Seed (Idempotent) ----------
# ---------- Spec Ingestion ----------
@router.post("/ingest-specs")
async def ingest_specs_now(db: Session = Depends(get_db)):
    from app.services.spec_ingest import ingest_specs
    try:
        log_progress("ingest", "start")
        result = ingest_specs()
        log_progress("ingest", "done", details=f"created={result.get('created')} updated={result.get('updated')} files={result.get('total_files')}")
        return result
    except Exception as e:
        log_progress("ingest", "error", details=str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

@router.post("/seed", response_model=SeedResponse)
async def seed_demo_content(db: Session = Depends(get_db)):
    # Idempotent seed for a demo course
    slug = "trading-basics"
    course = db.query(Course).filter_by(slug=slug).first()
    if not course:
        course = Course(title="Trading Basics", slug=slug, description="Foundations of trading with CamboStation Vision", published=True)
        db.add(course)
        db.commit()
        db.refresh(course)

        # Modules
        mod1 = Module(course_id=course.id, title="Foundations", order_index=1)
        mod2 = Module(course_id=course.id, title="Technical Analysis", order_index=2)
        db.add_all([mod1, mod2])
        db.commit()
        db.refresh(mod1); db.refresh(mod2)

        # Sections
        sec1a = Section(module_id=mod1.id, title="Getting Started", order_index=1)
        sec1b = Section(module_id=mod1.id, title="Risk & Psychology", order_index=2)
        sec2a = Section(module_id=mod2.id, title="Indicators", order_index=1)
        db.add_all([sec1a, sec1b, sec2a])
        db.commit()
        db.refresh(sec1a); db.refresh(sec1b); db.refresh(sec2a)

        # Lessons
        l1 = Lesson(
            section_id=sec1a.id, title="Welcome & Setup", order_index=1, type="video",
            content_rich="# Welcome\nThis lesson introduces the platform and basic setup steps.\n\n- Create your account\n- Configure API keys (paper trading)\n- Explore the Dashboard\n",
            video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
        )
        l2 = Lesson(
            section_id=sec1a.id, title="Platform Tour", order_index=2, type="text",
            content_rich="## Platform Tour\nExplore: Dashboard, Charts, Education, Journal, Coach, War Room.\n\nTip: Use the header status widget to ensure API/WS connectivity."
        )
        l3 = Lesson(
            section_id=sec1b.id, title="Risk Management 101", order_index=1, type="text",
            content_rich="## Risk Management\n- Position sizing\n- Stop losses\n- Max daily loss\n- Journaling"
        )
        l4 = Lesson(
            section_id=sec2a.id, title="RSI & MACD", order_index=1, type="text",
            content_rich="## RSI & MACD\nBasics of RSI/MACD and how to use in Cambo charts."
        )
        db.add_all([l1, l2, l3, l4])
        db.commit()
        db.refresh(l3)

        # Add a quiz for l3
        quiz_questions = [
            {"id": "q1", "type": "mcq", "prompt": "What does RSI measure?", "choices": ["Momentum", "Volume", "Volatility"], "correct": "Momentum", "points": 1},
            {"id": "q2", "type": "multi", "prompt": "Pick risk controls:", "choices": ["Stop loss", "Max daily loss", "Random entries"], "correct": ["Stop loss", "Max daily loss"], "points": 2},
            {"id": "q3", "type": "short", "prompt": "Max percent per trade (commonly suggested)?", "correct": "1", "points": 1},
        ]
        q = Quiz(lesson_id=l3.id, settings_json=json.dumps({"pass_score": 3}), questions_json=json.dumps(quiz_questions))
        db.add(q)

        # Add an assignment for l3
        a = Assignment(lesson_id=l3.id, prompt="Upload (or describe) your risk plan. Include max per-trade risk, max daily loss, and example position sizing.", rubric_json=json.dumps({"clarity": 5, "completeness": 5}))
        db.add(a)
        db.commit()

    return SeedResponse(ok=True, course_id=course.id)