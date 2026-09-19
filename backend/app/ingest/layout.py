"""拓扑自动布局：给「设备 + 连线」计算节点坐标（探测/Agent 数据不含坐标）。"""
import networkx as nx

# 可选算法：spring（力导向，默认）| kamada_kawai（小图更舒展）| circular
LAYOUT_ALGORITHMS = ("spring", "kamada_kawai", "circular")


def compute_layout(
    node_ids: list,
    edges: list[dict],
    algorithm: str = "spring",
    seed: int = 42,
    canvas_width: float = 1200,
    canvas_height: float = 900,
    margin: float = 60,
) -> dict:
    """返回 { node_id: (x, y) }。edges 形如 [{"source": id, "target": id}]。"""
    G = nx.Graph()
    G.add_nodes_from(node_ids)
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if s and t and s in G and t in G:
            G.add_edge(s, t)

    if not G.nodes:
        return {}

    if algorithm == "circular":
        pos = nx.circular_layout(G)
    elif algorithm == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, seed=seed, k=1.5)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span = max(max_x - min_x, max_y - min_y) or 1.0
    scale = min(canvas_width - 2 * margin, canvas_height - 2 * margin) / span

    result = {}
    for nid, (x, y) in pos.items():
        result[nid] = ((x - min_x) * scale + margin, (y - min_y) * scale + margin)
    return result