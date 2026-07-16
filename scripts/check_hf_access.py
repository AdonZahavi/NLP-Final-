"""Check HuggingFace access to the gated open-source models (run locally or on Colab).

LLaMA 3.2 and Mistral repos are gated: you must accept their licenses on the
HuggingFace model pages first, then set HF_TOKEN in .env (or `huggingface-cli login`).

Usage:
    python scripts/check_hf_access.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from huggingface_hub import HfApi
from huggingface_hub.errors import GatedRepoError, RepositoryNotFoundError

MODELS = [
    "meta-llama/Llama-3.2-1B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
]


def main() -> int:
    load_dotenv()
    token = os.environ.get("HF_TOKEN")
    api = HfApi(token=token)

    try:
        user = api.whoami()
        print(f"Authenticated as: {user['name']}")
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: not authenticated ({e}). Set HF_TOKEN in .env.")
        return 1

    ok = True
    for repo in MODELS:
        try:
            api.model_info(repo)
            print(f"[OK]     {repo}")
        except GatedRepoError:
            print(f"[GATED]  {repo} — accept the license at https://huggingface.co/{repo}")
            ok = False
        except RepositoryNotFoundError:
            print(f"[MISSING] {repo} — repo not found (or gated without access)")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
