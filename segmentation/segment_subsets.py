"""Issue #6: segment all evaluation subsets with YAP (the tool chosen in issue #5).

Surface format decision (documented in data/subsets/segmented/README.md):
morphemes are joined by SINGLE SPACES, both within and across tokens — the same
convention as the gold `morph` variant of the omilab sentiment benchmark and of
morpheme-level Hebrew NLP work (Amram et al. 2018). Note that YAP outputs a
morphological ANALYSIS, not a pure surface split: it reconstructs the covert
definite article (במקום -> ב ה מקום) and maps pronominal suffixes to base
pronouns (בך -> ב אתה). We use its output as-is and document this property.

Engineering:
- every unique text field is segmented once (QA contexts repeat across questions);
- results are cached append-only in cache/segment_cache.jsonl -> fully resumable;
- long texts are split into sentence chunks (YAP joint is slow on long input);
- --limit N for smoke tests, --task to run one task only.

Usage (YAP api server must be running, see colab_segment_subsets.ipynb):
    python segmentation/segment_subsets.py [--host http://localhost:8000] [--limit N] [--task sentiment|nli|qa]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBSETS = ROOT / "data" / "subsets"
OUT_DIR = SUBSETS / "segmented"
CACHE = ROOT / "cache" / "segment_cache.jsonl"

TOKENIZE_RE = re.compile(r"[א-ת0-9a-zA-Z\"'׳״]+|[^\s]")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
MAX_TOKENS_PER_REQ = 60

TASK_FIELDS = {
    "sentiment": ["text"],
    "nli": ["premise", "hypothesis"],
    "qa": ["context", "question"],
}
TASK_FILES = {
    "sentiment": "sentiment_500.jsonl",
    "nli": "nli_884.jsonl",
    "qa": "qa_500.jsonl",
}


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SegmentCache:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._mem: dict[str, str] = {}
        if path.exists():
            with open(path, encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line)
                        self._mem[r["h"]] = r["seg"]
                    except json.JSONDecodeError:
                        continue  # tolerate a torn last line after a crash
        self._f = open(path, "a", encoding="utf-8", newline="\n")

    def get(self, text: str) -> str | None:
        return self._mem.get(_hash(text))

    def put(self, text: str, seg: str) -> None:
        h = _hash(text)
        self._mem[h] = seg
        self._f.write(json.dumps({"h": h, "seg": seg}, ensure_ascii=False) + "\n")
        self._f.flush()


class YapServerDown(RuntimeError):
    pass


class YapSegmenter:
    MAX_CONSEC_FAILURES = 5

    def __init__(self, host: str):
        self.host = host
        self.requests = 0
        self.failures = 0
        self.consec_failures = 0

    def _joint(self, tokens: list[str]) -> list[str]:
        """Return the flat morpheme sequence for one chunk of tokens."""
        payload = json.dumps({"text": " ".join(tokens) + "  "}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.host}/yap/heb/joint", data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            md = json.loads(resp.read().decode("utf-8")).get("md_lattice", "")
        self.requests += 1
        self.consec_failures = 0
        per_token: dict[int, list[str]] = defaultdict(list)
        for line in md.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 8:
                per_token[int(parts[7])].append(parts[2])
        out: list[str] = []
        for i, tok in enumerate(tokens):
            out.extend(per_token.get(i + 1, [tok]))
        return out

    def segment_text(self, text: str) -> str:
        """Sentence-split, chunk, segment, and space-join morphemes.

        Raises YapServerDown after MAX_CONSEC_FAILURES consecutive request
        failures — a dead server must ABORT the run, never silently produce
        unsegmented output (lesson learned the hard way).
        """
        text = " ".join(text.split())
        chunks: list[list[str]] = []
        for sent in SENT_SPLIT_RE.split(text):
            tokens = TOKENIZE_RE.findall(sent)
            for i in range(0, len(tokens), MAX_TOKENS_PER_REQ):
                if tokens[i:i + MAX_TOKENS_PER_REQ]:
                    chunks.append(tokens[i:i + MAX_TOKENS_PER_REQ])
        morphemes: list[str] = []
        for chunk in chunks:
            last_err: Exception | None = None
            for attempt in range(2):  # one retry per chunk for transient blips
                try:
                    morphemes.extend(self._joint(chunk))
                    last_err = None
                    break
                except Exception as e:  # noqa: BLE001
                    last_err = e
                    time.sleep(2)
            if last_err is not None:
                self.failures += 1
                self.consec_failures += 1
                if self.consec_failures >= self.MAX_CONSEC_FAILURES:
                    raise YapServerDown(
                        f"{self.consec_failures} consecutive YAP failures "
                        f"(last: {type(last_err).__name__}: {last_err}). "
                        "The server is down — restart the YAP server cell and "
                        "re-run; the cache resumes completed texts."
                    )
                raise RuntimeError(
                    f"chunk failed ({type(last_err).__name__}): text will be "
                    "retried on the next run"
                )
        return " ".join(morphemes)


def collect_unique_texts(records: list[dict], fields: list[str]) -> list[str]:
    seen, out = set(), []
    for r in records:
        for f in fields:
            t = " ".join(str(r[f]).split())
            if t and t not in seen:
                seen.add(t)
                out.append(t)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:8000")
    ap.add_argument("--limit", type=int, default=0, help="limit records per task (smoke test)")
    ap.add_argument("--task", choices=list(TASK_FILES), default=None)
    args = ap.parse_args()

    cache = SegmentCache(CACHE)
    seg = YapSegmenter(args.host)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    tasks = [args.task] if args.task else list(TASK_FILES)
    total_missing = 0
    for task in tasks:
        with open(SUBSETS / TASK_FILES[task], encoding="utf-8") as f:
            records = [json.loads(l) for l in f]
        if args.limit:
            records = records[: args.limit]
        fields = TASK_FIELDS[task]
        uniq = collect_unique_texts(records, fields)
        todo = [t for t in uniq if cache.get(t) is None]
        print(f"[{task}] {len(records)} records, {len(uniq)} unique texts, "
              f"{len(uniq) - len(todo)} cached, {len(todo)} to segment")

        skipped = 0
        for i, text in enumerate(todo, 1):
            try:
                cache.put(text, seg.segment_text(text))  # only SUCCESS is cached
            except YapServerDown:
                raise
            except RuntimeError as e:
                skipped += 1
                print(f"    [WARN] {e}")
            if i % 25 == 0 or i == len(todo):
                rate = seg.requests / max(time.time() - t0, 1)
                print(f"  [{task}] {i}/{len(todo)} texts "
                      f"({seg.requests} reqs, {rate:.1f} req/s, "
                      f"{seg.failures} failed chunks, {skipped} texts skipped)")

        out_path = OUT_DIR / TASK_FILES[task]
        missing = 0
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            for r in records:
                out = dict(r)
                for fld in fields:
                    seg_val = cache.get(" ".join(str(r[fld]).split()))
                    if seg_val is None:
                        missing += 1
                        seg_val = ""
                    out[fld + "_seg"] = seg_val
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
        status = "OK" if missing == 0 else f"INCOMPLETE — {missing} unsegmented fields, re-run!"
        print(f"[{task}] wrote {out_path} [{status}]")
        total_missing += missing

    write_qc_sample()
    print(f"\nDone in {(time.time() - t0) / 60:.1f} min, "
          f"{seg.requests} YAP requests, {seg.failures} failed chunks, "
          f"{total_missing} missing fields")
    if total_missing:
        sys.exit(2)  # nonzero -> the notebook's retry loop resumes via the cache


def write_qc_sample(n_per_task: int = 30, seed: int = 42) -> None:
    """30 random raw/segmented pairs per task for the manual quality check."""
    import random

    rng = random.Random(seed)
    lines = [
        "# Manual QC sample (issue #6)\n",
        "_30 random examples per task. Reviewers: mark bad segmentations and "
        "note the phenomenon (wrong split / missed split / YAP normalization)._\n",
    ]
    for task, fname in TASK_FILES.items():
        path = OUT_DIR / fname
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            records = [json.loads(l) for l in f]
        sample = rng.sample(records, min(n_per_task, len(records)))
        lines.append(f"\n## {task}\n")
        for r in sample:
            lines.append(f"### {r['id']}\n")
            for fld in TASK_FIELDS[task]:
                raw = str(r[fld])
                segd = r.get(fld + "_seg", "")
                if task == "qa" and fld == "context":
                    raw, segd = raw[:300] + " …", segd[:300] + " …"
                lines.append(f"- **{fld} raw:** {raw}")
                lines.append(f"- **{fld} seg:** {segd}\n")
    (OUT_DIR / "qc_sample.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_DIR / 'qc_sample.md'}")


if __name__ == "__main__":
    main()
