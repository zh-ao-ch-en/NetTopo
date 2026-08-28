"""拓扑服务：整体 GET / PUT。库内拆表存储，对外按契约整包返回。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Topology, TopologyEdge, TopologyNode
from app.schemas import TopologyIn
from app.utils import now_iso

DEFAULT_TOPOLOGY_ID = "topo-main"


def _node_to_dict(n: TopologyNode) -> dict:
    d = {
        "id": n.id,
        "label": n.label,
        "type": n.type,
        "x": n.x,
        "y": n.y,
        "width": n.width,
        "height": n.height,
    }
    if n.device_id is not None:
        d["deviceId"] = n.device_id
    if n.status is not None:
        d["status"] = n.status
    return d


def _edge_to_dict(e: TopologyEdge) -> dict:
    d = {"id": e.id, "source": e.source, "target": e.target}
    if e.label is not None:
        d["label"] = e.label
    if e.style is not None:
        d["style"] = e.style
    return d


def get_topology(db: Session) -> dict:
    topo = db.get(Topology, DEFAULT_TOPOLOGY_ID)
    if topo is None:
        return {
            "id": DEFAULT_TOPOLOGY_ID,
            "name": "",
            "nodes": [],
            "edges": [],
            "updatedAt": "",
        }
    nodes = (
        db.query(TopologyNode)
        .filter(TopologyNode.topology_id == topo.id)
        .order_by(TopologyNode.id)
        .all()
    )
    edges = (
        db.query(TopologyEdge)
        .filter(TopologyEdge.topology_id == topo.id)
        .all()
    )
    return {
        "id": topo.id,
        "name": topo.name,
        "nodes": [_node_to_dict(n) for n in nodes],
        "edges": [_edge_to_dict(e) for e in edges],
        "updatedAt": topo.updated_at,
    }


def save_topology(db: Session, data: TopologyIn) -> dict:
    topo_id = data.id or DEFAULT_TOPOLOGY_ID
    topo = db.get(Topology, topo_id)
    if topo is None:
        topo = Topology(id=topo_id, name=data.name)
        db.add(topo)
    else:
        topo.name = data.name
    topo.updated_at = data.updatedAt or now_iso()

    db.query(TopologyNode).filter(TopologyNode.topology_id == topo_id).delete(
        synchronize_session=False
    )
    db.query(TopologyEdge).filter(TopologyEdge.topology_id == topo_id).delete(
        synchronize_session=False
    )

    for n in data.nodes:
        db.add(
            TopologyNode(
                id=n.id,
                topology_id=topo_id,
                device_id=n.deviceId,
                label=n.label,
                type=n.type,
                x=n.x,
                y=n.y,
                width=n.width,
                height=n.height,
                status=n.status,
            )
        )
    for e in data.edges:
        db.add(
            TopologyEdge(
                id=e.id,
                topology_id=topo_id,
                source=e.source,
                target=e.target,
                label=e.label,
                style=e.style,
            )
        )
    db.commit()
    return get_topology(db)