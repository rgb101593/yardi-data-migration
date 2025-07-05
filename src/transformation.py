import pandas as pd
import numpy as np

def transform_data(df, module, config):
    """Convert data to Yardi-compatible format"""
    # Apply module-specific transformations
    if module == "leasing":
        return transform_leasing(df, config)
    elif module == "fixed_assets":
        return transform_fixed_assets(df, config)
    else:
        # Generic transformation for other modules
        field_map = config["field_mappings"].get(module, {})
        return df.rename(columns=field_map)

def transform_leasing(df, config):
    """Fixed leasing transformation with robust null handling"""
    # Get source column names from configuration
    field_map = config["field_mappings"]["leasing"]
    source_columns = {v: k for k, v in field_map.items()}
    
    # 1. Handle missing tenant IDs - FIXED LOGIC
    tenant_source = source_columns.get("TenantID", "tenant_id")
    lease_ref_source = source_columns.get("LeaseReference", "lease_ref")
    
    if tenant_source in df.columns and lease_ref_source in df.columns:
        # Create mask for missing tenant IDs
        missing_mask = df[tenant_source].isna()
        
        # Generate temporary IDs where tenant ID is missing
        df.loc[missing_mask, tenant_source] = 'TEMP-' + df.loc[missing_mask, lease_ref_source].astype(str)
    
    # 2. Date handling
    start_source = source_columns.get("LeaseCommencementDate", "lease_start")
    end_source = source_columns.get("LeaseExpirationDate", "lease_end")
    
    if start_source in df.columns and end_source in df.columns:
        # Convert to datetime with coerce
        df[start_source] = pd.to_datetime(df[start_source], errors='coerce', format="%Y-%m-%d")
        df[end_source] = pd.to_datetime(df[end_source], errors='coerce', format="%Y-%m-%d")
        
        # Create valid date mask
        valid_dates = df[start_source].notna() & df[end_source].notna()
        
        # Use vectorized operation for date comparison
        if valid_dates.any():
            start_dates = df.loc[valid_dates, start_source]
            end_dates = df.loc[valid_dates, end_source]
            
            # Find and fix invalid date ranges
            invalid_mask = start_dates >= end_dates
            df.loc[valid_dates, end_source] = df.loc[valid_dates, end_source].mask(
                invalid_mask,
                df.loc[valid_dates, start_source] + pd.DateOffset(years=1)
            )
        
        # Format to Yardi's required string format
        df[start_source] = df[start_source].dt.strftime('%Y%m%d')
        df[end_source] = df[end_source].dt.strftime('%Y%m%d')
    
    # 3. Map frequency values
    freq_source = source_columns.get("RentFrequency", "rent_freq")
    if freq_source in df.columns:
        freq_map = config["validation_rules"]["leasing"]["value_maps"]["RentFrequency"]
        df[freq_source] = df[freq_source].map(freq_map)
    
    # 4. Fix negative rent values
    rent_source = source_columns.get("BaseRent", "base_rent")
    if rent_source in df.columns:
        df[rent_source] = pd.to_numeric(df[rent_source], errors='coerce').abs()
    
    # 5. Apply final field mapping
    return df.rename(columns=field_map)

def transform_fixed_assets(df, config):
    """Special handling for fixed assets data"""
    field_map = config["field_mappings"]["fixed_assets"]
    source_columns = {v: k for k, v in field_map.items()}
    
    # Map depreciation methods to codes
    method_source = source_columns.get("DepreciationMethod", "depreciation_method")
    if method_source in df.columns:
        method_map = config["validation_rules"]["fixed_assets"]["value_maps"]["DepreciationMethod"]
        df[method_source] = df[method_source].map(method_map)
    
    # Convert negative costs to positive
    cost_source = source_columns.get("OriginalCost", "original_cost")
    if cost_source in df.columns:
        df[cost_source] = pd.to_numeric(df[cost_source], errors='coerce').abs()
    
    # Apply field mapping
    return df.rename(columns=field_map)