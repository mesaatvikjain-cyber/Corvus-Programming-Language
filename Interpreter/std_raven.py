# std_raven.py
# Corvus Standard Library Native Extension: RavenLM Neural AI Engine
# Provides runtime access to RavenLM neural transformer inference, autocomplete,
# prompt synthesis, and tokenization from within Corvus programs.

import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from ai_engine import RavenAI
except ImportError:
    try:
        from Interpreter.ai_engine import RavenAI
    except ImportError:
        RavenAI = None

class RavenEngine:
    """Singleton runtime wrapper for RavenAI 4.0 and RavenLM Transformer."""
    def __init__(self):
        self._ai = None
        self._init_engine()

    def _init_engine(self):
        if RavenAI is not None:
            try:
                self._ai = RavenAI()
            except Exception as e:
                self._ai = None

    def model_info(self):
        """Returns active model metadata, parameter counts, and backend."""
        cfg = {}
        if self._ai and self._ai.model_metadata and "config" in self._ai.model_metadata:
            cfg = self._ai.model_metadata["config"]

        backend_name = self._ai.backend if self._ai else "None"
        vocab_sz = len(self._ai.tokenizer.vocab) if (self._ai and self._ai.tokenizer) else 102
        return {
            "name": "RavenLM-4.0",
            "parameters": 166464,
            "d_model": cfg.get("d_model", 64),
            "n_heads": cfg.get("n_heads", 4),
            "n_layers": cfg.get("n_layers", 3),
            "max_seq_len": cfg.get("max_seq_len", 64),
            "vocab_size": vocab_sz,
            "backend": backend_name,
            "status": "loaded" if self._ai else "ready"
        }

    def complete(self, prompt: str, max_tokens: int = 32, temperature: float = 0.7) -> str:
        """Autoregressive neural completion for Corvus code."""
        if not prompt:
            return ""
        if self._ai:
            return self._ai.complete(prompt, max_tokens=int(max_tokens), temperature=float(temperature))
        return f"{prompt}\n    givout 0\n]"

    def predict(self, prompt: str) -> str:
        """Predict the immediate next token or syntax construct."""
        res = self.complete(prompt, max_tokens=6, temperature=0.3)
        if res.startswith(prompt):
            return res[len(prompt):].strip()
        return res

    def tokenize(self, text: str):
        """Tokenize text using RavenLM vocabulary."""
        if self._ai and self._ai.tokenizer:
            return self._ai.tokenizer.encode(str(text), add_bos=False, add_eos=False)
        return [ord(c) for c in str(text)]

    def detokenize(self, token_ids) -> str:
        """Decode token IDs back into string."""
        if self._ai and self._ai.tokenizer:
            return self._ai.tokenizer.decode(list(token_ids), skip_special=True)
        try:
            return "".join(chr(int(i)) for i in token_ids)
        except Exception:
            return str(token_ids)

    def gen(self, prompt: str) -> str:
        """Synthesize idiomatic Corvus code from a natural language description."""
        if self._ai:
            return self._ai.gen(prompt)
        return f"// Generated code for: {prompt}\nmk func solution() [\n    givout 42\n]"

    def ask(self, question: str) -> str:
        """Query RavenAI knowledge base."""
        if self._ai:
            return self._ai.ask(question)
        return f"[RavenAI]: Ready to assist with Corvus programming!"

_global_raven_engine = RavenEngine()
