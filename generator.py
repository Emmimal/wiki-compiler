"""
generator.py

Produces a synthetic corpus of raw, unstructured text files that stand in for
a local Karpathy-style note dump: no headers guaranteed, inconsistent metadata
placement, entity names mentioned inline in prose. This is the "before" state
the compiler pipeline has to work with.

Deterministic: same seed always produces the same corpus, so benchmark runs
and article numbers are reproducible.
"""

import os
import random


TOPIC_POOL = [
    "Gradient Descent", "Attention Mechanism", "Tokenization", "Embedding Layer",
    "Transformer Block", "Backpropagation", "Batch Normalization", "Dropout",
    "Learning Rate Schedule", "Cross Entropy Loss", "Positional Encoding",
    "Layer Normalization", "Residual Connection", "Self Attention", "KV Cache",
    "Beam Search", "Greedy Decoding", "Top-K Sampling", "Temperature Scaling",
    "Fine Tuning", "LoRA Adapter", "Quantization", "Pruning", "Distillation",
    "Vector Index", "Cosine Similarity", "Hybrid Search", "Reranking",
    "Chunking Strategy", "Context Window", "Rate Limiting", "Circuit Breaker",
    "Retry Policy", "Prompt Template", "Few Shot Example", "Chain of Thought",
    "Tool Calling", "Function Schema", "Streaming Response", "Token Budget",
    "Semantic Cache", "Query Router", "Cost Tracking", "Latency Budget",
    "Model Registry", "Rollback Mechanism", "Integrity Hash", "Deployment Gate",
    "Canary Release", "Shadow Traffic",
]

RELATION_TEMPLATES = [
    "{a} is often paired with {b} in production pipelines.",
    "When debugging {a}, engineers frequently trace the issue back to {b}.",
    "{a} builds directly on the ideas behind {b}.",
    "A common mistake is tuning {a} without first checking {b}.",
    "{a} and {b} interact whenever the pipeline scales past a single node.",
    "Most implementations of {a} assume {b} is already configured correctly.",
]

FILLER_SENTENCES = [
    "This note was captured during a debugging session and may be incomplete.",
    "Revisit this after the next benchmark run.",
    "See related experiments in the archive folder for context.",
    "Numbers here are approximate and were not re-verified.",
    "This section needs a cleaner example before it is considered final.",
]


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def generate_corpus(output_dir: str, num_files: int, seed: int = 42) -> list:
    """
    Writes num_files raw .txt files into output_dir. Returns the list of
    file paths written. Deterministic given the same seed and num_files.
    """
    rng = random.Random(seed)
    os.makedirs(output_dir, exist_ok=True)

    # Cycle through the topic pool, appending a numeric suffix once we
    # exhaust unique topics, so num_files can exceed len(TOPIC_POOL).
    # Build the full topic list up front so relation targets can be drawn
    # from the entire generated corpus, not just the fixed base pool --
    # otherwise every "v2"/"v3" variant would be unreferenceable by
    # construction, and orphan rate would just measure pool exhaustion
    # rather than anything about the linking logic.
    all_topics = []
    for i in range(num_files):
        base_topic = TOPIC_POOL[i % len(TOPIC_POOL)]
        suffix = i // len(TOPIC_POOL)
        topic = base_topic if suffix == 0 else f"{base_topic} v{suffix + 1}"
        all_topics.append(topic)

    written = []
    for i, topic in enumerate(all_topics):
        slug = _slugify(topic)

        # Pick 1-3 related entities to mention in the body, deterministically,
        # drawn from the full corpus so connectivity scales with num_files.
        others = [t for t in all_topics if t != topic]
        k = min(rng.randint(1, 3), len(others)) if others else 0
        related = rng.sample(others, k=k) if k else []

        lines = []
        # Deliberately inconsistent header style: some files use '#', some
        # use a plain capitalized line, mimicking a real raw note dump.
        if rng.random() < 0.5:
            lines.append(f"# {topic}")
        else:
            lines.append(topic.upper())

        # Metadata is scattered, not in a fixed schema.
        if rng.random() < 0.7:
            lines.append(f"created: 2026-0{rng.randint(1,6)}-{rng.randint(10,28)}")
        if rng.random() < 0.4:
            lines.append(f"aliases: {slug}, {slug}_notes")

        lines.append("")
        for rel in related:
            template = rng.choice(RELATION_TEMPLATES)
            lines.append(template.format(a=topic, b=rel))
        lines.append("")
        lines.append(rng.choice(FILLER_SENTENCES))

        content = "\n".join(lines) + "\n"
        path = os.path.join(output_dir, f"{slug}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)

    return written


if __name__ == "__main__":
    paths = generate_corpus("raw_notes", num_files=20, seed=42)
    print(f"Wrote {len(paths)} raw files to raw_notes/")
