import csv

# Corvus Native Pandas DataFrame Engine (v4.2)

try:
    import pandas as pd
    HAS_NATIVE_PANDAS = True
except ImportError:
    HAS_NATIVE_PANDAS = False

class PandasEngine:
    @staticmethod
    def read_csv(filepath):
        if ".." in filepath:
            raise Exception("Invalid file path")
        if HAS_NATIVE_PANDAS:
            return pd.read_csv(filepath).to_dict(orient="records")
        # Fallback CSV reader returning list of dicts
        records = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        return records

    @staticmethod
    def head(data, n=5):
        if isinstance(data, list):
            return data[:n]
        return data

    @staticmethod
    def describe(data):
        if not isinstance(data, list) or not data:
            return {}
        cols = list(data[0].keys())
        summary = {}
        for col in cols:
            vals = [float(row[col]) for row in data if col in row and row[col] is not None and str(row[col]).replace('.', '', 1).isdigit()]
            if vals:
                summary[col] = {
                    "count": len(vals),
                    "mean": sum(vals) / len(vals),
                    "min": min(vals),
                    "max": max(vals)
                }
        return summary

    @staticmethod
    def filter_by(data, col, val):
        if isinstance(data, list):
            return [row for row in data if row.get(col) == val]
        return data

_global_pandas_engine = PandasEngine()
