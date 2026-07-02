"""
benchmark.py

Runs the full compile pipeline (generate -> extract -> graph -> rewrite ->
lint) at a chosen file count and reports real wall-clock timing per stage.
No estimation, no extrapolation -- every number printed here comes directly
from time.perf_counter() on this run.

Usage:
    python3 benchmark.py --files 1000
    python3 benchmark.py --files 100 --files 1000 --files 5000
"""

import argparse
import os
import platform
import shutil
import sys
import time

from generator import generate_corpus
from extractor import extract_all
from graph import build_graph
from rewriter import compile_pages
from linter import lint


def run_benchmark(num_files: int, seed: int = 42, tmp_root: str = "bench_tmp") -> dict:
    raw_dir = os.path.join(tmp_root, f"raw_{num_files}")
    out_dir = os.path.join(tmp_root, f"out_{num_files}")
    shutil.rmtree(raw_dir, ignore_errors=True)
    shutil.rmtree(out_dir, ignore_errors=True)

    t0 = time.perf_counter()
    paths = generate_corpus(raw_dir, num_files=num_files, seed=seed)
    t1 = time.perf_counter()

    total_bytes = sum(os.path.getsize(p) for p in paths)
    avg_bytes = total_bytes / len(paths) if paths else 0

    entities = extract_all(raw_dir)
    t2 = time.perf_counter()

    graph = build_graph(entities)
    t3 = time.perf_counter()

    compile_pages(entities, graph, out_dir)
    t4 = time.perf_counter()

    report = lint(out_dir)
    t5 = time.perf_counter()

    shutil.rmtree(raw_dir, ignore_errors=True)
    shutil.rmtree(out_dir, ignore_errors=True)

    return {
        "num_files": num_files,
        "avg_file_bytes": avg_bytes,
        "generate_s": t1 - t0,
        "extract_s": t2 - t1,
        "graph_s": t3 - t2,
        "rewrite_s": t4 - t3,
        "lint_s": t5 - t4,
        "compile_total_s": t4 - t1,   # extract + graph + rewrite, excludes data generation
        "full_pipeline_s": t5 - t1,   # extract + graph + rewrite + lint
        "broken_links": len(report.broken_links),
        "orphan_pages": len(report.orphan_pages),
    }


def print_result(r: dict) -> None:
    print(f"--- {r['num_files']} files ---")
    print(f"  avg source file size: {r['avg_file_bytes']:.0f} bytes")
    print(f"  extract:  {r['extract_s']*1000:.2f} ms")
    print(f"  graph:    {r['graph_s']*1000:.2f} ms")
    print(f"  rewrite:  {r['rewrite_s']*1000:.2f} ms")
    print(f"  lint:     {r['lint_s']*1000:.2f} ms")
    print(f"  compile total (extract+graph+rewrite): {r['compile_total_s']*1000:.2f} ms")
    print(f"  full pipeline (+lint):                 {r['full_pipeline_s']*1000:.2f} ms")
    print(f"  lint result: {r['broken_links']} broken links, {r['orphan_pages']} orphan pages")
    print()


def main():
    parser = argparse.ArgumentParser(description="Benchmark the wiki compiler pipeline.")
    parser.add_argument("--files", type=int, action="append", default=None,
                         help="Number of files to benchmark at. Can be passed multiple times.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    scales = args.files if args.files else [100, 1000]

    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor() or 'unknown'}")
    print()

    results = []
    for n in scales:
        r = run_benchmark(n, seed=args.seed)
        print_result(r)
        results.append(r)

    return results


if __name__ == "__main__":
    main()
