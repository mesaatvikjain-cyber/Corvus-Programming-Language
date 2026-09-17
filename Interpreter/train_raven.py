"""
Training Pipeline for RavenLM (Corvus Neural Language Model)
Trains a causal decoder transformer on Corvus source code and prompt instructions.
"""

import os
import sys
import glob
import json
import random
import time
from typing import List

# Ensure Interpreter directory is in Python path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

import torch
import torch.nn as nn
from raven_model import CorvusTokenizer, RavenTransformer

def collect_corvus_corpus() -> str:
    root_dir = os.path.dirname(curr_dir)
    corpus_chunks = []

    # 1. Examples and Tests
    examples_dir = os.path.join(root_dir, "Examples-and-Tests")
    for crv_file in glob.glob(os.path.join(examples_dir, "**", "*.crv"), recursive=True):
        try:
            with open(crv_file, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read().strip()
                if code:
                    corpus_chunks.append(code)
        except Exception:
            pass

    # 2. StdLib files
    stdlib_dir = os.path.join(root_dir, "StdLib")
    for crv_file in glob.glob(os.path.join(stdlib_dir, "*.crv")):
        try:
            with open(crv_file, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read().strip()
                if code:
                    corpus_chunks.append(code)
        except Exception:
            pass

    # 3. High-quality prompt-to-code instruction pairs
    instructions = [
        "// Prompt: Write a function to add two numbers\nmk func add(a, b) [\n    givout a + b\n]\n\nlog(add(10, 20))",
        "// Prompt: Write a recursive factorial function\nmk func factorial(n) [\n    if (n <= 1) [\n        givout 1\n    ]\n    givout n * factorial(n - 1)\n]\n\nlog(factorial(5))",
        "// Prompt: Multiply two matrices using native @ operator\nset lis; A = [[1, 2], [3, 4]]\nset lis; B = [[5, 6], [7, 8]]\nset any; C = A @ B\nlog(C)",
        "// Prompt: Spawn concurrent worker with crow\nget crow\ncrow.fly(mk func() [\n    log(\"Worker finished in background\")\n])",
        "// Prompt: Send and receive messages with async channels\nget channel\nset any; ch = channel.new(10)\nch.send(\"ping\")\nset any; res = ch.recv()\nlog(res)",
        "// Prompt: Create a User model with SQLite ORM\nget orm\nset any; db = orm.open(\":memory:\")\nset any; User = db.model(\"users\", {\"name\": \"TEXT\", \"score\": \"INTEGER\"})\nUser.create({\"name\": \"Saatvik\", \"score\": 100})\nset any; all_users = User.all()",
        "// Prompt: Process tabular data with reactive DataFrames\nget dataframe\nset any; df = dataframe.from_records([{\"city\": \"Tokyo\", \"temp\": 22.5}])\nlog(df.describe())",
        "// Prompt: Initialize 2D physics vector with GameKit\nget gamekit\nset any; v1 = gamekit.vec2(10.0, 20.0)\nset any; v2 = gamekit.vec2(5.0, 5.0)\nset any; v3 = v1.add(v2)\nlog(v3.x, v3.y)",
        "// Prompt: Play arcade tone with retro audio synthesizer\nget audio\naudio.play_tone(440, 0.25)\naudio.play_chord([523, 659, 784], 0.3)",
        "// Prompt: Class with constructor and method\ncls Point() [\n    set flo; x\n    set flo; y\n    mk func init(x_val, y_val) [\n        self.x = x_val\n        self.y = y_val\n    ]\n    mk func distance_from_origin() [\n        givout (self.x * self.x + self.y * self.y) ** 0.5\n    ]\n]",
        "// Prompt: Filter even numbers from list\nmk func get_evens(nums) [\n    set lis; evens = []\n    for n in nums [\n        if (n % 2 == 0) [\n            evens.push(n)\n        ]\n    ]\n    givout evens\n]",
        "// Prompt: Safe error handling with try and error\ntry [\n    set any; val = 100 / 0\n] error(e) [\n    log(\"Caught error: \" + str(e))\n] final [\n    log(\"Cleaned up successfully\")\n]"
    ]
    corpus_chunks.extend(instructions * 3)

    combined = "\n\n".join(corpus_chunks)
    return combined

def train_raven(epochs: int = 30, lr: float = 1e-3, batch_size: int = 16, seq_len: int = 64):
    print("=" * 60)
    print("   RAVEN-LM: CORVUS NEURAL LANGUAGE MODEL TRAINING PIPELINE")
    print("=" * 60)

    print("[1/5] Harvesting Corvus codebase corpus...")
    corpus = collect_corvus_corpus()
    print(f"      Corpus size: {len(corpus):,} characters across {corpus.count('\n'):,} lines.")

    print("[2/5] Initializing vocabulary & tokenizer...")
    tokenizer = CorvusTokenizer()
    vocab_path = os.path.join(curr_dir, "raven_vocab.json")
    tokenizer.save(vocab_path)
    print(f"      Vocab size: {tokenizer.vocab_size} tokens (Saved to raven_vocab.json)")

    print("[3/5] Tokenizing dataset & generating causal sequences...")
    tokens = tokenizer.encode(corpus, add_bos=False, add_eos=False)
    print(f"      Total encoded tokens: {len(tokens):,}")

    # Build sequence pairs (x, y) where y is x shifted by 1
    xs = []
    ys = []
    step = 4  # sliding window step
    for i in range(0, len(tokens) - seq_len, step):
        chunk = tokens[i : i + seq_len + 1]
        xs.append(chunk[:-1])
        ys.append(chunk[1:])

    print(f"      Generated {len(xs):,} training sequences of length {seq_len}.")

    # Subsample if dataset is very large to ensure training finishes in <30 seconds
    max_samples = 4000
    if len(xs) > max_samples:
        indices = list(range(len(xs)))
        random.seed(42)
        random.shuffle(indices)
        indices = indices[:max_samples]
        xs = [xs[i] for i in indices]
        ys = [ys[i] for i in indices]
        print(f"      Sampled {len(xs):,} representative sequences for rapid CPU convergence.")

    X_tensor = torch.tensor(xs, dtype=torch.long)
    Y_tensor = torch.tensor(ys, dtype=torch.long)

    print("[4/5] Initializing RavenTransformer neural architecture...")
    model = RavenTransformer(
        vocab_size=tokenizer.vocab_size,
        d_model=64,
        n_heads=4,
        n_layers=3,
        max_seq_len=seq_len
    )
    param_count = model.count_parameters()
    print(f"      Transformer Parameters: {param_count:,} weights.")

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    print(f"[5/5] Training for {epochs} epochs (Batch size: {batch_size})...")
    start_time = time.time()
    n_batches = (len(X_tensor) + batch_size - 1) // batch_size

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        perm = torch.randperm(len(X_tensor))
        X_shuffled = X_tensor[perm]
        Y_shuffled = Y_tensor[perm]

        for b in range(n_batches):
            xb = X_shuffled[b * batch_size : (b + 1) * batch_size]
            yb = Y_shuffled[b * batch_size : (b + 1) * batch_size]

            optimizer.zero_grad()
            logits, loss = model(xb, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()

        scheduler.step()
        avg_loss = total_loss / n_batches
        if epoch % 5 == 0 or epoch == 1 or epoch == epochs:
            elapsed = time.time() - start_time
            print(f"      Epoch {epoch:2d}/{epochs} | Loss: {avg_loss:.4f} | LR: {scheduler.get_last_lr()[0]:.6f} | Elapsed: {elapsed:.1f}s")

    # Save PyTorch weights
    pt_path = os.path.join(curr_dir, "raven_weights.pt")
    torch.save(model.state_dict(), pt_path)
    print(f"[SAVED] PyTorch weights saved to {pt_path} ({os.path.getsize(pt_path) / 1024:.1f} KB)")

    # Save Portable JSON weights for zero-dependency NumPy fallback
    json_path = os.path.join(curr_dir, "raven_weights.json")
    weights_dict = {}
    for k, v in model.state_dict().items():
        if "causal_mask" not in k:
            weights_dict[k] = v.cpu().numpy().tolist()

    model_metadata = {
        "architecture": "RavenTransformer",
        "version": "4.0",
        "d_model": 64,
        "n_heads": 4,
        "n_layers": 3,
        "max_seq_len": seq_len,
        "vocab_size": tokenizer.vocab_size,
        "parameters": param_count,
        "final_loss": round(avg_loss, 4),
        "weights": weights_dict
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(model_metadata, f)
    print(f"[SAVED] Portable NumPy weights saved to {json_path} ({os.path.getsize(json_path) / 1024:.1f} KB)")

    # Verification sample generation
    print("\n[TEST] Verifying neural autoregressive generation:")
    model.eval()
    test_prefix = "mk func "
    idx = torch.tensor([tokenizer.encode(test_prefix, add_bos=False, add_eos=False)], dtype=torch.long)
    generated = model.generate(idx, max_new_tokens=40, temperature=0.7, top_k=5)
    sample_out = tokenizer.decode(generated[0].tolist(), skip_special=True)
    print("-" * 50)
    print(sample_out)
    print("-" * 50)
    print("RavenLM Training Pipeline Complete!")

if __name__ == "__main__":
    epochs = 25
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        epochs = int(sys.argv[1])
    train_raven(epochs=epochs)
