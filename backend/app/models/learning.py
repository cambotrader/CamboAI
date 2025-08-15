from __future__ import annotations
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class Course(Base):
    __tablename__ = "courses"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    hero_image = Column(String)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Module(Base):
    __tablename__ = "modules"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String, ForeignKey("courses.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Section(Base):
    __tablename__ = "sections"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    module_id = Column(String, ForeignKey("modules.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = Column(String, ForeignKey("sections.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    type = Column(String, default="mixed")  # video|text|code|mixed
    duration_sec = Column(Integer)
    content_rich = Column(Text)  # markdown/json
    video_url = Column(String)
    embed_url = Column(String)
    downloads_json = Column(Text)  # JSON array of {label,url}
    created_at = Column(DateTime, default=datetime.utcnow)

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String, ForeignKey("lessons.id"), index=True, nullable=False)
    settings_json = Column(Text)  # attempts, pass_score, etc.
    questions_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String, ForeignKey("lessons.id"), index=True, nullable=False)
    prompt = Column(Text)
    rubric_json = Column(Text)
    due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DiscussionThread(Base):
    __tablename__ = "discussion_threads"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String, ForeignKey("lessons.id"), index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DiscussionPost(Base):
    __tablename__ = "discussion_posts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey("discussion_threads.id"), index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    body = Column(Text, nullable=False)
    parent_post_id = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String, ForeignKey("assignments.id"), index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    files_json = Column(Text)
    text = Column(Text)
    grade = Column(String)
    feedback = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)

class Progress(Base):
    __tablename__ = "progress"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    course_id = Column(String, index=True, nullable=False)
    module_id = Column(String, index=True, nullable=True)
    section_id = Column(String, index=True, nullable=True)
    lesson_id = Column(String, index=True, nullable=True)
    status = Column(String, default="not_started")  # not_started|in_progress|completed
    percent = Column(Integer, default=0)
    last_seen_at = Column(DateTime, default=datetime.utcnow)

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    course_id = Column(String, index=True, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    cert_number = Column(String, unique=True, index=True)
    pdf_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

__all__ = [
    "Course","Module","Section","Lesson","Quiz","Assignment","DiscussionThread","DiscussionPost","Submission","Progress","Certificate"
]