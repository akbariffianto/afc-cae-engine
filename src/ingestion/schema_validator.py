import pandas as pd
import yaml
from pathlib import Path
from typing import Dict, Any

class SchemaValidator:
    def __init__(self, config_path: Path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
    def validate_schema(self, file_path: Path) -> Dict[str, Any]:
        """Validates column count and format without loading the full file."""
        if not file_path.suffix in ['.csv', '.parquet']:
            return {"status": "FAILED", "reason": "UNSUPPORTED_FORMAT"}
            
        try:
            # Read only the header to save memory
            if file_path.suffix == '.csv':
                df_header = pd.read_csv(file_path, nrows=0)
            else:
                df_header = pd.read_parquet(file_path)
                
            actual_columns = len(df_header.columns)
            expected_columns = self.config.get('expected_columns')
            
            if actual_columns != expected_columns:
                return {
                    "status": "SCHEMA-DRIFT-ALERT", 
                    "reason": f"Expected {expected_columns} columns, found {actual_columns}"
                }
                
            return {"status": "PASSED", "columns_verified": actual_columns}
            
        except Exception as e:
            return {"status": "ERROR", "reason": str(e)}