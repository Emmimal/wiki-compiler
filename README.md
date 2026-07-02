# wiki-compiler

A pure-Python compiler that turns raw, messy text notes into a linked, linted markdown wiki. No LLM calls, no embeddings, no dependencies.

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

Most LLM wiki tutorials stop at: point an agent at your notes, let it decide what's related, let it rewrite pages. This library handles the deterministic part of that job instead: extracting structure, building the link graph, and validating the result, without a single model call.

Read the full write-up on Towards Data Science → [LLM Wikis Are Over-Engineered. I Replaced Mine With a Pure Python Compiler.](https://towardsdatascience.com/author/emmimalp-alexander/)

## What It Does

```
Raw Notes (.txt) → Extractor → Graph → Rewriter → Linter → Compiled Wiki (.md)
```

Four stages, one `compile_wiki()` call:

| Component | Job |
|---|---|
| Extractor | Regex scan pulling entity name, aliases, created date, and body text out of inconsistently formatted raw files |
| Graph | Word-indexed phrase matcher detecting mentions between entities, building a bidirectional reference map |
| Rewriter | Section-aware markdown compilation; regenerates compiler-owned sections, preserves hand-written Notes |
| Linter | Structural validation: broken `[[links]]` and orphan pages with zero incoming references |

## Installation

```bash
git clone https://github.com/Emmimal/wiki-compiler.git
cd wiki-compiler
python init.py
```

No dependencies to install. Standard library only.

## Quick Start

```python
from compiler import compile_wiki

result = compile_wiki("raw_notes", "compiled_wiki")

print(f"Compiled {len(result['written_paths'])} pages")
print(f"Broken links: {len(result['lint_report'].broken_links)}")
print(f"Orphan pages: {len(result['lint_report'].orphan_pages)}")
```

Or from the command line:

```bash
python compiler.py raw_notes/ compiled_wiki/
```

## Running the Tests and Benchmark

Seventeen tests, stdlib `unittest` only, covering every stage plus the full end-to-end pipeline:

```bash
python -m unittest tests -v
```

Real per-stage timing at three corpus sizes, using a deterministic synthetic corpus (seed=42):

```bash
python benchmark.py --files 100 --files 1000 --files 5000
```

## CLI Reference

```
python compiler.py raw_dir output_dir [--no-lint]

  raw_dir       Directory of raw .txt source files
  output_dir    Directory to write compiled .md pages into
  --no-lint     Skip the lint pass
```

```
python benchmark.py [--files N ...] [--seed N]

  --files       Number of files to benchmark at (repeatable)
  --seed        Random seed for the synthetic corpus generator (default: 42)
```

## Project Structure

```
wiki-compiler/
├── compiler.py       # Orchestrates all four stages behind one function call
├── extractor.py      # Stage 1: regex metadata extraction
├── graph.py           # Stage 2: word-indexed mention detection + bidirectional graph
├── rewriter.py         # Stage 3: section-aware markdown compilation
├── linter.py            # Stage 4: broken-link and orphan-page validation
├── generator.py          # Synthetic test corpus generator, for demos and benchmarks
├── benchmark.py           # Timing harness
├── init.py                 # Zero-configuration entry point
└── tests.py                  # 17 unit tests, stdlib only
```

## Performance (two machines, same deterministic outputs)

| Files | Extract | Graph | Rewrite | Lint | Compile total | Full pipeline | Orphans |
|---|---|---|---|---|---|---|---|
| 100 | 22.8 ms | 3.1 ms | 59.4 ms | 86.0 ms | 85.4 ms | 171.4 ms | 13 |
| 1,000 | 261.5 ms | 47.1 ms | 605.5 ms | 883.9 ms | 914.1 ms | 1,798.0 ms | 133 |
| 5,000 | 1,398.4 ms | 625.6 ms | 3,446.7 ms | 6,972.5 ms | 5,470.6 ms | 12,443.1 ms | 644 |

Orphan and broken-link counts are identical across every run, on both Linux and Windows. Wall-clock timing varies by hardware and OS; the deterministic outputs don't. `graph` has zero disk I/O and scales the best; `lint` is the most I/O-sensitive stage and the most expensive one at scale.

## When to Use This

Worth it when you have:
- A folder of local, already-written notes you want structured and cross-referenced
- A workflow where you want the same output every time you recompile
- No interest in spending tokens on organizational work an agent would redo on every run

Skip it when you have:
- Notes that need semantic linking, where related ideas are phrased differently rather than sharing exact terms
- A need for an agent that also drafts new content, not just links existing text
- Source data too unstructured for regex-based extraction to make sense of

## Known Limitations

- Mention detection is lexical, not semantic. Two notes describing the same concept in different words won't link automatically.
- The extractor handles two header styles and optional metadata fields. Wildly inconsistent or multi-language source data would need a more sophisticated extraction layer.
- Lint performance is I/O-bound and platform-sensitive; expect Windows to run measurably slower than Linux at scale, likely due to filesystem overhead and antivirus scanning.

## License

MIT
