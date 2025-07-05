import pandas as pd
import os
import chardet  # Add this import
from .utils import create_row_hash
from .extraction import robust_csv_reader  # Import robust reader

def get_delta_records(module, config):
    """Accurate change detection with stable hashing"""
    # 1. Load current full dataset
    current_file = f"data/sources/{config['phase']}/{module}.csv"
    if not os.path.exists(current_file):
        return pd.DataFrame()
    
    # Detect file encoding
    with open(current_file, 'rb') as f:
        rawdata = f.read(10000)  # Read first 10KB to detect encoding
        result = chardet.detect(rawdata)
        encoding = result['encoding']
    
    try:
        # Try reading with detected encoding
        current_df = pd.read_csv(current_file, encoding=encoding)
    except:
        try:
            # Fallback to UTF-16 with BOM handling
            current_df = pd.read_csv(current_file, encoding='utf-16')
        except:
            # Use robust reader as last resort
            print(f"  Using robust reader for {current_file}")
            current_df = robust_csv_reader(current_file)
    
    # 2. Load reference dataset
    ref_phase = config["delta_settings"]["reference_phase"]
    ref_file = f"data/sources/{ref_phase}/{module}.csv"
    
    if not os.path.exists(ref_file):
        return current_df  # First run
    
    # Detect encoding for reference file
    with open(ref_file, 'rb') as f:
        rawdata = f.read(10000)
        result = chardet.detect(rawdata)
        encoding = result['encoding']
    
    try:
        ref_df = pd.read_csv(ref_file, encoding=encoding)
    except:
        try:
            ref_df = pd.read_csv(ref_file, encoding='utf-16')
        except:
            print(f"  Using robust reader for {ref_file}")
            ref_df = robust_csv_reader(ref_file)
    
    # ... rest of the function remains the same ...
    
    if not os.path.exists(ref_file):
        return current_df  # First run
    
    ref_df = pd.read_csv(ref_file)
    
    # 3. Get key column
    key_col = config["delta_settings"]["key_columns"][module]
    
    # 4. Find new records
    current_keys = set(current_df[key_col].astype(str))
    ref_keys = set(ref_df[key_col].astype(str))
    new_records = current_df[~current_df[key_col].astype(str).isin(ref_keys)]
    
    # 5. Find changed records
    common_keys = current_keys & ref_keys
    changed_records = []
    
    for key in common_keys:
        current_row = current_df[current_df[key_col].astype(str) == key].iloc[0]
        ref_row = ref_df[ref_df[key_col].astype(str) == key].iloc[0]
        
        if create_row_hash(current_row) != create_row_hash(ref_row):
            changed_records.append(current_row)
    
    # 6. Combine results
    return pd.concat([new_records, pd.DataFrame(changed_records)], ignore_index=True)