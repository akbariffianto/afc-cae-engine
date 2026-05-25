import pytest
import pandas as pd
import yaml
import tempfile
from pathlib import Path

# Adjust import path based on the root directory execution
from src.ingestion.dtype_gate import DTypeConsistencyGate

@pytest.fixture
def setup_test_files():
    """
    Creates an isolated temporary directory containing a synthetic config 
    and a synthetic dataset designed to trigger edge cases.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_dir = Path(tmpdirname)
        
        # 1. Create Mock YAML Configuration
        config_data = {
            "dtype_schema": {
                "integer_cols": ["delinq_2yrs", "open_acc"],
                "float_cols": ["loan_amnt", "funded_amnt"],
                "category_cols": ["grade", "loan_status"],
                "date_cols": ["issue_d"]
            }
        }
        config_path = tmp_dir / "test_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
            
        # 2. Create Synthetic CSV with the "NaN Trap"
        # Note: Row 2 has a missing delinq_2yrs value
        # Note: Row 3 has a malformed string in open_acc
        csv_content = """loan_amnt,funded_amnt,delinq_2yrs,open_acc,grade,loan_status,issue_d
10000.0,10000.0,0,5,A,Fully Paid,Jan-2024
5000.0,5000.0,,10,B,Current,Feb-2024
20000.0,20000.0,2,INVALID_DATA,C,Charged Off,Mar-2024"""
        
        csv_path = tmp_dir / "test_data.csv"
        with open(csv_path, "w") as f:
            f.write(csv_content)
            
        yield config_path, csv_path

def test_dtype_coercion_preserves_integers(setup_test_files):
    """
    Validates that the DType gate enforces canonical types and successfully
    handles nulls in integer columns using Pandas 'Int64'.
    """
    config_path, csv_path = setup_test_files
    
    # Initialize the gate with our temporary config
    gate = DTypeConsistencyGate(config_path)
    
    # Run the ingestion method
    df = gate.load_and_coerce(csv_path)
    
    # --- ASSERTIONS ---
    
    # 1. Float coercion check
    assert str(df['loan_amnt'].dtype) == 'float64', "Float columns failed coercion"
    
    # 2. Nullable Integer coercion check (The core requirement of v1.1)
    assert str(df['delinq_2yrs'].dtype) == 'Int64', "Integer coercion failed to use nullable Int64"
    assert str(df['open_acc'].dtype) == 'Int64', "Integer coercion failed to use nullable Int64"
    
    # 3. Value preservation and NaN handling
    assert df['delinq_2yrs'].iloc[0] == 0
    assert pd.isna(df['delinq_2yrs'].iloc[1]), "Empty CSV value did not convert to NaN"
    assert df['delinq_2yrs'].iloc[2] == 2
    
    # 4. Error coercion check (INVALID string should become NaN, not crash the engine)
    assert df['open_acc'].iloc[0] == 5
    assert pd.isna(df['open_acc'].iloc[2]), "Malformed string failed to coerce to NaN"
    
    # 5. Categorical coercion check
    assert str(df['grade'].dtype) == 'category', "Categorical coercion failed"
    
    # 6. Datetime coercion check
    assert pd.api.types.is_datetime64_any_dtype(df['issue_d']), "Datetime parsing failed"