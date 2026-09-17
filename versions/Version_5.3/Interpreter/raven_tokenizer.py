# raven_tokenizer.py
# Corvus Syntax-Aware Subword & BPE Tokenizer (RavenAI 5.0)
# Combines byte-level fallback with high-frequency Corvus keyword/idiom subwords.

import json
import os
import re
from typing import Dict, List, Optional, Tuple

CORVUS_SPECIAL_TOKENS = ["<pad>", "<bos>", "<eos>", "<unk>"]

# High-frequency keywords, syntax idioms, and operators in Corvus
CORVUS_KEYWORDS_SUBWORDS = [
    # Declarations & Functions
    "mk func ", "givout ", "mk func", "givout",
    "set any; ", "set int; ", "set str; ", "set flo; ", "set bool; ", "set lis; ", "set tup; ", "set dic; ",
    "set any;", "set int;", "set str;", "set flo;", "set bool;", "set lis;", "set tup;", "set dic;",
    "set const; ", "set const;", "const ", "set ", "cls ",
    
    # Control Flow
    "if (", ") [", "] else [", "] elsif (", "] otherwise [",
    "while (", "for (", " in ", "] [", "match (", "case ", "else:",
    "brk;", "con;", "stop;", "skip;", "pass;",
    
    # Concurrency & Systems Modules
    "crow.fly(", "crow.spawn(", "crow.parallel_map(", "crow.channel()",
    "chan.new(", "channel.new(", "ch.send(", "ch.recv()", "ch.close()",
    "web.ws_server(", "web.server(",
    
    # Data Science & Math
    " @ ", "@", "math.sqrt(", "math.sin(", "math.cos(", "math.tan(",
    "np.array(", "torch.tensor(", "orm.Model", "dataframe.read_csv(",
    "raven.complete(", "raven.model_info()", "raven.predict(",
    
    # Operators & Syntax Elements
    " |> ", "|>", "f\"", "f'", " != ", " == ", " <= ", " >= ", " += ", " -= ", " *= ", " /= ",
    "// ", "/* ", " */", " -> ", " ? ", " : ",
    "    ", "  ", "\n    ", "\n        ", "\n            ",
    "log(", "print(", "len(", "str(", "int(", "flo(", "bool(", "list("
]

class CorvusBPETokenizer:
    """
    Syntax-Aware Subword Tokenizer for Corvus.
    Encodes full keywords and structural patterns as atomic tokens,
    achieving 4x-5x compression over character-level models.
    """
    def __init__(self, vocab_file: Optional[str] = None):
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        self.subwords: List[str] = []
        if vocab_file and os.path.exists(vocab_file):
            self.load(vocab_file)
        else:
            self._build_default_vocab()

    def _build_default_vocab(self):
        self.vocab = {}
        self.subwords = []
        idx = 0
        
        # 1. Special tokens (0..3)
        for tok in CORVUS_SPECIAL_TOKENS:
            self.vocab[tok] = idx
            idx += 1
            
        # 2. Corvus subwords & idioms
        for sw in CORVUS_KEYWORDS_SUBWORDS:
            if sw not in self.vocab:
                self.vocab[sw] = idx
                self.subwords.append(sw)
                idx += 1
                
        # Sort subwords by descending length for greedy prefix matching
        self.subwords.sort(key=len, reverse=True)

        # 3. All printable ASCII characters + whitespace
        for c in (
            "\n\t\r !\"#$%&'()*+,-./0123456789:;<=>?@"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
            "abcdefghijklmnopqrstuvwxyz{|}~"
        ):
            if c not in self.vocab:
                self.vocab[c] = idx
                idx += 1

        self.inverse_vocab = {v: k for k, v in self.vocab.items()}

    def encode(self, text: str, add_bos: bool = False, add_eos: bool = False) -> List[int]:
        tokens: List[int] = []
        if add_bos:
            tokens.append(self.vocab["<bos>"])

        i = 0
        n = len(text)
        while i < n:
            matched = False
            # Check for multi-character subwords greedy match
            for sw in self.subwords:
                if text.startswith(sw, i):
                    tokens.append(self.vocab[sw])
                    i += len(sw)
                    matched = True
                    break
            if not matched:
                char = text[i]
                tokens.append(self.vocab.get(char, self.vocab["<unk>"]))
                i += 1

        if add_eos:
            tokens.append(self.vocab["<eos>"])
        return tokens

    def decode(self, token_ids: List[int], skip_special: bool = True) -> str:
        res = []
        for tid in token_ids:
            if tid not in self.inverse_vocab:
                continue
            tok = self.inverse_vocab[tid]
            if skip_special and tok in CORVUS_SPECIAL_TOKENS:
                continue
            res.append(tok)
        return "".join(res)

    def save(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "vocab": self.vocab,
                "subwords": self.subwords
            }, f, indent=2)

    def load(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.vocab = data["vocab"]
            self.subwords = data.get("subwords", [])
            self.subwords.sort(key=len, reverse=True)
            self.inverse_vocab = {int(v): k for k, v in self.vocab.items()}
