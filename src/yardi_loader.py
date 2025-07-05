import pandas as pd
import os
from datetime import datetime

def generate_yardi_files(df, module, phase):
    """Create files ready for Yardi import"""
    output_dir = f"data/yardi_etl/{phase}"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{module}_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Yardi requires specific format:
    # - Pipe delimiters
    # - UTF-16 encoding
    # - No index column
    df.to_csv(filepath, sep="|", index=False, encoding="utf-16")