import pandas as pd
import os
import csv

def extract_data(module, config):
    """Get data from legacy systems with error handling"""
    phase = config.get('phase')
    if not phase:
        raise ValueError("Missing 'phase' in config")
    
    file_path = f"data/sources/{phase}/{module}.csv"
    dir_path = os.path.dirname(file_path)
    
    # Create directory if missing
    os.makedirs(dir_path, exist_ok=True)

    if not os.path.exists(file_path):
        # Create empty file if missing
        open(file_path, 'a').close()
        return pd.DataFrame()
    
    try:
        # First try standard CSV reading
        df = pd.read_csv(file_path)
    except pd.errors.ParserError:
        print(f"  CSV parsing error detected - using robust reader")
        df = robust_csv_reader(file_path)
    
    # Filter for representative properties
    if "properties" in config:
        if "property_id" in df.columns:
            df = df[df["property_id"].isin(config["properties"])]

    # Validate key column exists
    key_col = config["delta_settings"]["key_columns"][module]
    if key_col not in df.columns:
        print(f"  WARNING: Key column '{key_col}' missing in source data")
        # Add empty key column to prevent downstream failures
        df[key_col] = ""
    
    return df

    

def robust_csv_reader(file_path):
    """Handle malformed CSV files with inconsistent columns and BOM"""
    rows = []
    encodings = ['utf-8-sig', 'utf-16', 'latin1']  # Try different encodings
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                header = next(reader)
                expected_cols = len(header)
                
                for row in reader:
                    # Fix row length issues
                    if len(row) > expected_cols:
                        row = row[:expected_cols]
                    elif len(row) < expected_cols:
                        row += [''] * (expected_cols - len(row))
                    rows.append(row)
                
                return pd.DataFrame(rows, columns=header)
        except UnicodeDecodeError:
            continue  # Try next encoding
    
    # If all encodings fail, use default with error suppression
    with open(file_path, 'r', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader)
        expected_cols = len(header)
        
        for row in reader:
            if len(row) > expected_cols:
                row = row[:expected_cols]
            elif len(row) < expected_cols:
                row += [''] * (expected_cols - len(row))
            rows.append(row)
        
        return pd.DataFrame(rows, columns=header)