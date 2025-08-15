from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import shutil

from app.services.progress_service import log_progress

router = APIRouter(prefix="/api/admin", tags=["Admin"]) 

class MoveRequest(BaseModel):
    source_path: str
    overwrite: bool = False

@router.post("/move-to-repo")
async def move_to_repo(body: MoveRequest):
    """
    Move a file/folder into the repository under docs/specs.
    - If a file path is given, copy the file.
    - If a directory is given, copy the entire directory tree.
    """
    target_root = os.path.abspath(os.path.join(os.getcwd(), "docs", "specs"))
    os.makedirs(target_root, exist_ok=True)

    src = body.source_path
    if not os.path.exists(src):
        raise HTTPException(status_code=404, detail="Source path not found")

    name = os.path.basename(src.rstrip("/\\"))
    dest = os.path.join(target_root, name)

    try:
        if os.path.isdir(src):
            if os.path.exists(dest):
                if body.overwrite:
                    shutil.rmtree(dest)
                else:
                    raise HTTPException(status_code=400, detail="Destination already exists")
            shutil.copytree(src, dest)
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if os.path.exists(dest) and not body.overwrite:
                raise HTTPException(status_code=400, detail="Destination already exists")
            shutil.copy2(src, dest)
        log_progress("admin", "move", details=f"{src} -> {dest}")
        return {"ok": True, "dest": dest}
    except HTTPException:
        raise
    except Exception as e:
        log_progress("admin", "move_error", details=str(e))
        raise HTTPException(status_code=500, detail=f"Move failed: {e}")