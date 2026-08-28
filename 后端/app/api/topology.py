"""拓扑路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_edit
from app.database import get_db
from app.models import User
from app.response import ok
from app.schemas import TopologyIn
from app.services import topology as topology_service

router = APIRouter(prefix="/api/topology", tags=["topology"])


@router.get("")
def get_topology(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ok(topology_service.get_topology(db))


@router.put("")
def save_topology(
    data: TopologyIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_edit),
):
    return ok(topology_service.save_topology(db, data))