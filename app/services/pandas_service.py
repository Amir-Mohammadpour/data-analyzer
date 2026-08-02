from pathlib import Path

import pandas as pd


def build_dataframe_context(file_path: Path) -> str:
    df = pd.read_csv(file_path)

    rows, cols = df.shape
    column_types = df.dtypes.to_string()
    missing = df.isnull().sum().to_string()
    summary = df.describe(include="all").to_string()
    sample_rows = df.head(5).to_string()

    return (
        f"Dataset Shape:\n{rows} rows, {cols} columns\n\n"
        f"Column Types:\n{column_types}\n\n"
        f"Missing Values per Column:\n{missing}\n\n"
        f"Statistical Summary:\n{summary}\n\n"
        f"Sample Rows (first 5):\n{sample_rows}"
    )
