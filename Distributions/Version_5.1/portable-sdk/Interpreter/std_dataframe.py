# std_dataframe.py
# Corvus Zero-Dependency Reactive DataFrame Engine
# High-speed in-memory tabular data analysis, filtering, selection, and CSV operations.

import csv
import io
import math
from typing import Any, Callable, Dict, List, Optional, Union

class DataFrame:
    def __init__(self, records: Optional[List[Dict[str, Any]]] = None, columns: Optional[List[str]] = None):
        self._records: List[Dict[str, Any]] = [dict(r) for r in (records or [])]
        if columns:
            self._columns = list(columns)
        elif self._records:
            self._columns = list(self._records[0].keys())
        else:
            self._columns = []

    @classmethod
    def from_records(cls, records: List[Dict[str, Any]]) -> 'DataFrame':
        return cls(records=records)

    @classmethod
    def read_csv(cls, filepath: str) -> 'DataFrame':
        records = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                parsed_row = {}
                for k, v in row.items():
                    # Attempt numeric cast
                    try:
                        if "." in v:
                            parsed_row[k] = float(v)
                        else:
                            parsed_row[k] = int(v)
                    except ValueError:
                        parsed_row[k] = v
                records.append(parsed_row)
        return cls(records=records)

    def columns(self) -> List[str]:
        return list(self._columns)

    def shape(self) -> List[int]:
        return [len(self._records), len(self._columns)]

    def select(self, cols: List[str]) -> 'DataFrame':
        """Project specific columns."""
        new_records = [{c: r.get(c) for c in cols} for r in self._records]
        return DataFrame(new_records, columns=cols)

    def filter(self, predicate: Any) -> 'DataFrame':
        """Filter rows where predicate(row) evaluates to true."""
        filtered = []
        for r in self._records:
            keep = False
            try:
                if hasattr(predicate, "call"):
                    keep = bool(predicate.call([r]))
                elif callable(predicate):
                    keep = bool(predicate(r))
            except Exception:
                keep = False
            if keep:
                filtered.append(r)
        return DataFrame(filtered, columns=self._columns)

    def group_by(self, key_col: str, agg_func: str = "mean", target_col: Optional[str] = None) -> 'DataFrame':
        """Group by key_col and compute aggregation (mean, sum, count, min, max)."""
        groups: Dict[Any, List[Any]] = {}
        for r in self._records:
            k = r.get(key_col)
            val = r.get(target_col) if target_col else 1
            groups.setdefault(k, []).append(val)

        agg_results = []
        for k, vals in groups.items():
            num_vals = [v for v in vals if isinstance(v, (int, float))]
            res_val = 0
            if agg_func == "sum":
                res_val = sum(num_vals) if num_vals else 0
            elif agg_func == "count":
                res_val = len(vals)
            elif agg_func == "min":
                res_val = min(num_vals) if num_vals else 0
            elif agg_func == "max":
                res_val = max(num_vals) if num_vals else 0
            else:  # mean
                res_val = (sum(num_vals) / len(num_vals)) if num_vals else 0

            agg_results.append({
                key_col: k,
                f"{agg_func}_{target_col or 'count'}": res_val
            })
        return DataFrame(agg_results)

    def describe(self) -> Dict[str, Dict[str, float]]:
        """Compute basic statistical summary for numeric columns."""
        stats = {}
        for c in self._columns:
            vals = [r[c] for r in self._records if isinstance(r.get(c), (int, float))]
            if vals:
                stats[c] = {
                    "count": len(vals),
                    "sum": sum(vals),
                    "mean": sum(vals) / len(vals),
                    "min": min(vals),
                    "max": max(vals)
                }
        return stats

    def head(self, n: int = 5) -> List[Dict[str, Any]]:
        return self._records[:n]

    def to_records(self) -> List[Dict[str, Any]]:
        return list(self._records)

    def to_csv(self, filepath: str) -> bool:
        if not self._records:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("")
            return True
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self._columns)
            writer.writeheader()
            writer.writerows(self._records)
        return True

    def __len__(self) -> int:
        return len(self._records)

    def __repr__(self) -> str:
        return f"<DataFrame rows={len(self._records)} cols={len(self._columns)}>"


def read_csv(filepath: str) -> DataFrame:
    return DataFrame.read_csv(filepath)

def from_records(records: List[Dict[str, Any]]) -> DataFrame:
    return DataFrame.from_records(records)
