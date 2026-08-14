"""Local HuggingFace client (LLaMA 3.2 / Mistral 7B) implementing ModelClient.

Runs on Colab GPU. Deterministic (greedy) decoding, chat template applied.
"""

from __future__ import annotations


class HFLocalClient:
    def __init__(self, model_id: str, device_map: str = "auto",
                 torch_dtype=None):
        import torch  # noqa: F401 — fail early if torch is missing
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if torch_dtype is None:
            # models ship bf16 weights, but pre-Ampere GPUs (e.g. Colab T4)
            # have no bf16 hardware -> use fp16 there, bf16 where supported
            torch_dtype = (torch.bfloat16
                           if torch.cuda.is_available()
                           and torch.cuda.is_bf16_supported()
                           else torch.float16)
        self.model = model_id  # cache key uses the full HF id
        self._tok = AutoTokenizer.from_pretrained(model_id)
        self._lm = AutoModelForCausalLM.from_pretrained(
            model_id, device_map=device_map, torch_dtype=torch_dtype)
        self._lm.eval()

    def complete(self, prompt: str, **params) -> str:
        import torch

        max_new = params.get("max_tokens", 64)
        # tokenize=False -> plain string, robust across transformers versions
        # (newer versions return a BatchEncoding from apply_chat_template)
        text = self._tok.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False, add_generation_prompt=True,
        )
        enc = self._tok(text, return_tensors="pt",
                        add_special_tokens=False).to(self._lm.device)
        eos = self._tok.eos_token_id
        pad = self._tok.pad_token_id
        if pad is None:
            pad = eos[0] if isinstance(eos, (list, tuple)) else eos
        with torch.no_grad():
            out = self._lm.generate(
                **enc, max_new_tokens=max_new, do_sample=False,
                pad_token_id=pad,
            )
        n_in = enc["input_ids"].shape[1]
        return self._tok.decode(out[0][n_in:], skip_special_tokens=True).strip()
