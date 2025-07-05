import pandas as pd
import os

def track_temp_ids(df, module, phase):
    """Record all generated temporary IDs"""
    if module != "leasing":
        return
    
    temp_dir = "data/reference"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"temp_tenant_map_{phase}.csv")
    
    # Identify temporary IDs
    if 'TenantID' in df.columns:
        temp_ids = df[df['TenantID'].str.startswith('TEMP-', na=False)][['LeaseReference', 'TenantID']]
    elif 'tenant_id' in df.columns:
        temp_ids = df[df['tenant_id'].str.startswith('TEMP-', na=False)][['lease_ref', 'tenant_id']]
    else:
        print("  No TenantID column found for tracking")
        return
    
    if not temp_ids.empty:
        temp_ids.to_csv(file_path, index=False)
        print(f"  Saved {len(temp_ids)} temporary tenant IDs to {file_path}")