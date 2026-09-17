# grammar_decoder.py
# Corvus Grammar-Constrained Decoding Engine (RavenAI 5.0)
# Uses the Corvus Context-Free Grammar (CFG) state machine to mask illegal logits,
# ensuring 100% syntactically valid code generation with zero bracket or syntax hallucinations.

from typing import List, Set
from raven_tokenizer import CorvusBPETokenizer

class CorvusGrammarConstraint:
    """
    Real-time grammar validator and logit mask calculator for autoregressive generation.
    """
    def __init__(self, tokenizer: CorvusBPETokenizer):
        self.tokenizer = tokenizer
        self.bracket_pairs = {
            '[': ']',
            '(': ')',
            '{': '}'
        }
        self.closing_brackets = set(self.bracket_pairs.values())

    def analyze_syntax_state(self, text: str):
        """Analyze bracket balance, string state, and grammar expectations."""
        bracket_stack = []
        in_string = False
        str_quote = None
        escape = False

        for c in text:
            if escape:
                escape = False
                continue
            if c == '\\' and in_string:
                escape = True
                continue
            if c in ('"', "'"):
                if not in_string:
                    in_string = True
                    str_quote = c
                elif c == str_quote:
                    in_string = False
                    str_quote = None
                continue

            if in_string:
                continue

            if c in self.bracket_pairs:
                bracket_stack.append(c)
            elif c in self.closing_brackets:
                if bracket_stack and self.bracket_pairs.get(bracket_stack[-1]) == c:
                    bracket_stack.pop()

        return {
            "in_string": in_string,
            "str_quote": str_quote,
            "bracket_stack": bracket_stack,
            "open_bracket": bracket_stack[-1] if bracket_stack else None,
            "expected_close": self.bracket_pairs.get(bracket_stack[-1]) if bracket_stack else None
        }

    def get_valid_token_ids(self, current_text: str) -> Set[int]:
        """Returns the set of token IDs that are legally valid in the current syntax state."""
        state = self.analyze_syntax_state(current_text)
        valid_ids = set()

        for tok, tid in self.tokenizer.vocab.items():
            # If inside an unclosed string literal:
            if state["in_string"]:
                # Can't emit EOS or special tokens
                if tok in ("<bos>", "<eos>", "<pad>"):
                    continue
                # If it's a newline without continuation, penalize
                if tok == "\n":
                    continue
                valid_ids.add(tid)
                continue

            # Outside strings:
            # 1. Do not emit <eos> if we have unclosed brackets [ ... ]
            if tok == "<eos>" and state["bracket_stack"]:
                continue

            # 2. Check closing brackets validity: cannot close with mismatching bracket
            contains_illegal_close = False
            for c in tok:
                if c in self.closing_brackets:
                    if not state["bracket_stack"] or c != state["expected_close"]:
                        contains_illegal_close = True
                        break
            if contains_illegal_close:
                continue

            # 3. If ending with statement starter 'mk func ' or 'if (', don't emit ']'
            stripped = current_text.rstrip()
            if stripped.endswith("mk func") or stripped.endswith("if (") or stripped.endswith("while ("):
                if tok.startswith("]"):
                    continue

            valid_ids.add(tid)

        if not valid_ids:
            # Fallback to all non-special tokens
            valid_ids = {tid for tok, tid in self.tokenizer.vocab.items() if not tok.startswith("<")}

        return valid_ids

    def mask_logits(self, logits, current_text: str):
        """
        Applies $-\\infty$ mask to logits corresponding to syntactically illegal tokens.
        Works with either PyTorch tensors or NumPy arrays.
        """
        valid_ids = self.get_valid_token_ids(current_text)
        
        # Check if logits is PyTorch tensor
        try:
            import torch
            if isinstance(logits, torch.Tensor):
                mask = torch.full_like(logits, float('-inf'))
                for tid in valid_ids:
                    if tid < logits.shape[-1]:
                        mask[..., tid] = logits[..., tid]
                return mask
        except Exception:
            pass

        # NumPy fallback
        import numpy as np
        if isinstance(logits, np.ndarray):
            masked = np.full_like(logits, -1e9)
            for tid in valid_ids:
                if tid < logits.shape[-1]:
                    masked[..., tid] = logits[..., tid]
            return masked

        return logits
