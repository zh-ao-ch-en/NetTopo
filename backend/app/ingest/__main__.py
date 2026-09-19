"""导入器命令行入口。

用法（在后端目录下）：
    python -m app.ingest path/to/dataset.json                    # 默认 spring 布局
    python -m app.ingest path/to/dataset.json --algorithm kamada_kawai
"""
from __future__ import annotations

import argparse
import sys

from app.database import Base, SessionLocal, engine
from app.ingest.importer import import_dataset, load_source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="导入拓扑数据集到数据库")
    parser.add_argument("source", help="探测/Agent 输出的 JSON 文件路径")
    parser.add_argument(
        "--algorithm",
        default="spring",
        choices=("spring", "kamada_kawai", "circular"),
        help="自动布局算法",
    )
    args = parser.parse_args(argv)

    Base.metadata.create_all(bind=engine)
    data = load_source(args.source)
    with SessionLocal() as db:
        result = import_dataset(db, data, algorithm=args.algorithm)

    print(f"导入完成：拓扑 id={result['id']} name={result['name']}")
    print(f"  节点数 = {len(result['nodes'])}，连线数 = {len(result['edges'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())