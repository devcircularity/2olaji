from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.core.db import get_db, set_rls_context
from app.api.deps.auth import get_current_user
from app.models.school import School, SchoolMember

def require_school(
    ctx: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    x_school_id: Optional[str] = Header(default=None, alias="X-School-ID"),
) -> Dict[str, Any]:
    """
    Resolve active school for the request and return context dict
    """
    claims = ctx["claims"]
    user = ctx["user"]

    school_id = x_school_id or claims.get("active_school_id")

    if not school_id:
        memberships = (
            db.query(SchoolMember.school_id)
              .filter(SchoolMember.user_id == user.id)
              .all()
        )
        if not memberships:
            raise HTTPException(status_code=404, detail="You are not a member of any school")
        if len(memberships) == 1:
            school_id = memberships[0][0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multiple schools detected. Provide X-School-ID or call /auth/activate-school to set an active school."
            )

    # membership + existence checks
    is_member = (
        db.query(SchoolMember)
          .filter(SchoolMember.school_id == school_id, SchoolMember.user_id == user.id)
          .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this school")

    if not db.query(School.id).filter(School.id == school_id).first():
        raise HTTPException(status_code=404, detail="School not found")

    set_rls_context(db, user_id=user.id, school_id=school_id)

    # Return dict with both user and school_id for downstream endpoints
    return {"user": user, "school_id": school_id}