import pandas as pd
import yaml
from pathlib import Path

class DTypeConsistencyGate:
    def __init__(self, config_path: Path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            self.dtype_schema = self.config.get('dtype_schema', {})

    def load_and_coerce(self, file_path: Path) -> pd.DataFrame:
        """Loads data and strictly enforces the canonical dtype mapping."""
        # Pre-map float columns for the initial read
        float_cols = self.dtype_schema.get('float_cols', [])
        read_dtypes = {col: 'float64' for col in float_cols}
        
        # Load dataset
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path, dtype=read_dtypes, low_memory=False)
        else:
            df = pd.read_parquet(file_path)

        # Force Nullable Integer Conversion ('Int64')
        int_cols = self.dtype_schema.get('integer_cols', [])
        for col in int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        # Convert Date Columns
        date_cols = self.dtype_schema.get('date_cols', [])
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='%b-%Y', errors='coerce')

        # Convert Categorical Columns
        cat_cols = self.dtype_schema.get('category_cols', [])
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')

        return df