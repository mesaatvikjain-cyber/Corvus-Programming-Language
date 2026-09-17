"""
RavenLM: Real Neural Transformer Language Model for Corvus Language
Provides Causal Decoder Transformer Architecture with PyTorch and NumPy runtimes.
"""

import math
import json
import os
from typing import List, Dict, Tuple, Optional

try:
    from raven_tokenizer import CorvusBPETokenizer
except ImportError:
    try:
        from Interpreter.raven_tokenizer import CorvusBPETokenizer
    except ImportError:
        CorvusBPETokenizer = None


# ==============================================================================
# 1. Corvus Tokenizer (Character & Syntax-Aware Vocabulary)
# ==============================================================================
class CorvusTokenizer:
    SPECIAL_TOKENS = ["<pad>", "<bos>", "<eos>", "<unk>"]

    def __init__(self, chars: Optional[List[str]] = None):
        if chars is None:
            # Default rich printable ASCII set + Corvus syntax characters
            base_chars = [chr(i) for i in range(32, 127)] + ["\n", "\t", "\r"]
            chars = sorted(list(set(base_chars)))

        self.vocab: List[str] = self.SPECIAL_TOKENS + [c for c in chars if c not in self.SPECIAL_TOKENS]
        self.char_to_id: Dict[str, int] = {c: i for i, c in enumerate(self.vocab)}
        self.id_to_char: Dict[int, str] = {i: c for i, c in enumerate(self.vocab)}
        self.pad_id = self.char_to_id["<pad>"]
        self.bos_id = self.char_to_id["<bos>"]
        self.eos_id = self.char_to_id["<eos>"]
        self.unk_id = self.char_to_id["<unk>"]

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    def encode(self, text: str, add_bos: bool = True, add_eos: bool = True) -> List[int]:
        tokens = []
        if add_bos:
            tokens.append(self.bos_id)
        for char in text:
            tokens.append(self.char_to_id.get(char, self.unk_id))
        if add_eos:
            tokens.append(self.eos_id)
        return tokens

    def decode(self, token_ids: List[int], skip_special: bool = True) -> str:
        res = []
        for tid in token_ids:
            if skip_special and tid in (self.pad_id, self.bos_id, self.eos_id):
                continue
            res.append(self.id_to_char.get(tid, ""))
        return "".join(res)

    def save(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"vocab": self.vocab}, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str):
        if CorvusBPETokenizer is not None:
            bpe = CorvusBPETokenizer()
            bpe.load(filepath)
            return bpe
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        tok = cls(data["vocab"])
        return tok

# ==============================================================================
# 2. PyTorch Causal Decoder Transformer (RavenTransformer)
# ==============================================================================
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class CausalSelfAttention(nn.Module):
        def __init__(self, d_model: int, n_heads: int, max_seq_len: int, dropout: float = 0.0):
            super().__init__()
            assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
            self.d_model = d_model
            self.n_heads = n_heads
            self.head_dim = d_model // n_heads

            self.q_proj = nn.Linear(d_model, d_model, bias=False)
            self.k_proj = nn.Linear(d_model, d_model, bias=False)
            self.v_proj = nn.Linear(d_model, d_model, bias=False)
            self.out_proj = nn.Linear(d_model, d_model, bias=False)

            self.register_buffer(
                "causal_mask",
                torch.tril(torch.ones(max_seq_len, max_seq_len)).view(1, 1, max_seq_len, max_seq_len)
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            B, T, C = x.size()
            q = self.q_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
            k = self.k_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
            v = self.v_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

            att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))
            mask = self.causal_mask[:, :, :T, :T]
            att = att.masked_fill(mask == 0, float("-inf"))
            att = F.softmax(att, dim=-1)

            y = att @ v
            y = y.transpose(1, 2).contiguous().view(B, T, C)
            return self.out_proj(y)

    class TransformerBlock(nn.Module):
        def __init__(self, d_model: int, n_heads: int, max_seq_len: int):
            super().__init__()
            self.ln1 = nn.LayerNorm(d_model)
            self.attn = CausalSelfAttention(d_model, n_heads, max_seq_len)
            self.ln2 = nn.LayerNorm(d_model)
            self.mlp = nn.Sequential(
                nn.Linear(d_model, 4 * d_model),
                nn.GELU(),
                nn.Linear(4 * d_model, d_model)
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = x + self.attn(self.ln1(x))
            x = x + self.mlp(self.ln2(x))
            return x

    class RavenTransformer(nn.Module):
        def __init__(
            self,
            vocab_size: int,
            d_model: int = 64,
            n_heads: int = 4,
            n_layers: int = 3,
            max_seq_len: int = 128
        ):
            super().__init__()
            self.vocab_size = vocab_size
            self.d_model = d_model
            self.n_heads = n_heads
            self.n_layers = n_layers
            self.max_seq_len = max_seq_len

            self.tok_emb = nn.Embedding(vocab_size, d_model)
            self.pos_emb = nn.Embedding(max_seq_len, d_model)
            self.blocks = nn.ModuleList([
                TransformerBlock(d_model, n_heads, max_seq_len) for _ in range(n_layers)
            ])
            self.ln_f = nn.LayerNorm(d_model)
            self.head = nn.Linear(d_model, vocab_size, bias=False)

        def count_parameters(self) -> int:
            return sum(p.numel() for p in self.parameters() if p.requires_grad)

        def forward(self, idx: torch.Tensor, targets: Optional[torch.Tensor] = None):
            B, T = idx.size()
            assert T <= self.max_seq_len, f"Sequence length {T} exceeds max {self.max_seq_len}"

            pos = torch.arange(0, T, dtype=torch.long, device=idx.device).unsqueeze(0)
            x = self.tok_emb(idx) + self.pos_emb(pos)

            for block in self.blocks:
                x = block(x)
            x = self.ln_f(x)
            logits = self.head(x)

            loss = None
            if targets is not None:
                loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-1)

            return logits, loss

        @torch.no_grad()
        def generate(
            self,
            idx: torch.Tensor,
            max_new_tokens: int = 64,
            temperature: float = 0.7,
            top_k: int = 10,
            eos_id: Optional[int] = None,
            tokenizer = None,
            constraint = None
        ) -> torch.Tensor:
            for _ in range(max_new_tokens):
                idx_cond = idx if idx.size(1) <= self.max_seq_len else idx[:, -self.max_seq_len:]
                logits, _ = self(idx_cond)
                logits = logits[:, -1, :] / max(temperature, 1e-5)

                if constraint is not None and tokenizer is not None:
                    curr_text = tokenizer.decode(idx[0].tolist(), skip_special=True)
                    logits = constraint.mask_logits(logits, curr_text)

                if top_k is not None and top_k > 0:
                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = -float("Inf")

                probs = F.softmax(logits, dim=-1)
                next_tok = torch.multinomial(probs, num_samples=1)
                idx = torch.cat((idx, next_tok), dim=1)

                if eos_id is not None and next_tok.item() == eos_id:
                    break

            return idx

except ImportError:
    RavenTransformer = None


# ==============================================================================
# 3. Pure NumPy / Zero-Dependency Fallback Inference Engine
# ==============================================================================
try:
    import numpy as np

    class NumPyRavenLM:
        """Runs forward pass and sampling using pure NumPy and portable JSON weights."""
        def __init__(self, config: dict, weights: dict):
            self.vocab_size = config["vocab_size"]
            self.d_model = config["d_model"]
            self.n_heads = config["n_heads"]
            self.n_layers = config["n_layers"]
            self.max_seq_len = config["max_seq_len"]
            self.weights = {k: np.array(v, dtype=np.float32) for k, v in weights.items()}

        def _softmax(self, x: np.ndarray, axis: int = -1) -> np.ndarray:
            e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
            return e_x / np.sum(e_x, axis=axis, keepdims=True)

        def _layer_norm(self, x: np.ndarray, weight: np.ndarray, bias: np.ndarray, eps: float = 1e-5) -> np.ndarray:
            mean = np.mean(x, axis=-1, keepdims=True)
            var = np.var(x, axis=-1, keepdims=True)
            normed = (x - mean) / np.sqrt(var + eps)
            return normed * weight + bias

        def forward_token(self, token_ids: List[int]) -> np.ndarray:
            T = min(len(token_ids), self.max_seq_len)
            sub_ids = token_ids[-T:]

            tok_w = self.weights["tok_emb.weight"]
            pos_w = self.weights["pos_emb.weight"]

            x = tok_w[sub_ids] + pos_w[:T]

            for l in range(self.n_layers):
                prefix = f"blocks.{l}."
                # LN1
                x_norm1 = self._layer_norm(x, self.weights[f"{prefix}ln1.weight"], self.weights[f"{prefix}ln1.bias"])
                
                # Attention
                qw = self.weights[f"{prefix}attn.q_proj.weight"]
                kw = self.weights[f"{prefix}attn.k_proj.weight"]
                vw = self.weights[f"{prefix}attn.v_proj.weight"]
                ow = self.weights[f"{prefix}attn.out_proj.weight"]

                head_dim = self.d_model // self.n_heads
                q = (x_norm1 @ qw.T).reshape(T, self.n_heads, head_dim).swapaxes(0, 1)
                k = (x_norm1 @ kw.T).reshape(T, self.n_heads, head_dim).swapaxes(0, 1)
                v = (x_norm1 @ vw.T).reshape(T, self.n_heads, head_dim).swapaxes(0, 1)

                scores = (q @ k.swapaxes(-2, -1)) * (1.0 / math.sqrt(head_dim))
                mask = np.tril(np.ones((T, T), dtype=bool))
                scores = np.where(mask, scores, -1e9)
                attn_probs = self._softmax(scores, axis=-1)
                out = (attn_probs @ v).swapaxes(0, 1).reshape(T, self.d_model)
                attn_out = out @ ow.T

                x = x + attn_out

                # LN2 & MLP
                x_norm2 = self._layer_norm(x, self.weights[f"{prefix}ln2.weight"], self.weights[f"{prefix}ln2.bias"])
                mlp_w1 = self.weights[f"{prefix}mlp.0.weight"]
                mlp_b1 = self.weights[f"{prefix}mlp.0.bias"]
                mlp_w2 = self.weights[f"{prefix}mlp.2.weight"]
                mlp_b2 = self.weights[f"{prefix}mlp.2.bias"]

                h = x_norm2 @ mlp_w1.T + mlp_b1
                # GELU approx
                h_gelu = 0.5 * h * (1.0 + np.tanh(math.sqrt(2.0 / math.pi) * (h + 0.044715 * np.power(h, 3))))
                mlp_out = h_gelu @ mlp_w2.T + mlp_b2

                x = x + mlp_out

            x = self._layer_norm(x, self.weights["ln_f.weight"], self.weights["ln_f.bias"])
            head_w = self.weights["head.weight"]
            logits = x[-1] @ head_w.T
            return logits

        def generate(
            self,
            token_ids: List[int],
            max_new_tokens: int = 64,
            temperature: float = 0.7,
            top_k: int = 10,
            eos_id: Optional[int] = None,
            tokenizer = None,
            constraint = None
        ) -> List[int]:
            tokens = list(token_ids)
            for _ in range(max_new_tokens):
                logits = self.forward_token(tokens) / max(temperature, 1e-5)

                if constraint is not None and tokenizer is not None:
                    curr_text = tokenizer.decode(tokens, skip_special=True)
                    logits = constraint.mask_logits(logits, curr_text)

                if top_k is not None and top_k > 0:
                    top_indices = np.argpartition(logits, -top_k)[-top_k:]
                    mask = np.ones_like(logits, dtype=bool)
                    mask[top_indices] = False
                    logits[mask] = -1e9

                probs = self._softmax(logits)
                next_tok = int(np.random.choice(len(probs), p=probs))
                tokens.append(next_tok)
                if eos_id is not None and next_tok == eos_id:
                    break
            return tokens

except ImportError:
    NumPyRavenLM = None
