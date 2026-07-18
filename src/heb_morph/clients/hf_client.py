"""Local HuggingFace client (LLaMA 3.2 / Mistral 7B) implementing ModelClient.

Runs on Colab GPU. Deterministic (greedy) decoding, chat template applied.
"""

from __future__ import annotations


class HFLocalClient:
    def __init__(self, model_id: str, device_map: str = "auto",
                 torch_dtype: str = "auto"):
        import torch  # noqa: F401 — fail early if torch is missing
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model = model_id  # cache key uses the full HF id
        self._tok = AutoTokenizer.from_pretrained(model_id)
        self._lm = AutoModelForCausalLM.from_pretrained(
            model_id, device_map=device_map, torch_dtype=torch_dtype)
        self._lm.eval()

    def complete(self, prompt: str, **params) -> str:
        import torch

        max_new = params.get("max_tokens", 64)
        inputs = self._tok.apply_chat_template(
            [{"role": "user", "content": prompt}],
            add_generation_prompt=True, return_tensors="pt",
        ).to(self._lm.device)
        with torch.no_grad():
            out = self._lm.generate(
                inputs, max_new_tokens=max_new, do_sample=False,
                pad_token_id=self._tok.eos_token_id,
            )
        return self._tok.decode(out[0][inputs.shape[1]:],
                                skip_special_tokens=True).strip()
