import os
import pandas as pd
from datetime import datetime

def validate_data(df, module, config):
    """Comprehensive validation with detailed reporting"""
    # Initialize report structure
    report = {
        "module": module,
        "phase": config["phase"],
        "total_records": len(df),
        "errors": [],
        "warnings": [],
        "status": "PASS"
    }
    
    rules = config["validation_rules"].get(module, {})
    
    # 1. Required fields validation
    for field in rules.get("required", []):
        if field not in df.columns:
            report["errors"].append(f"Missing column: {field}")
        elif df[field].isnull().any():
            null_count = df[field].isnull().sum()
            report["errors"].append(f"{null_count} null values in {field}")
    
    # 2. Positive values check
    for field in rules.get("positive_values", []):
        if field in df.columns:
            # Convert to numeric and handle errors
            numeric_series = pd.to_numeric(df[field], errors="coerce")
            negative_count = (numeric_series < 0).sum()
            if negative_count > 0:
                report["warnings"].append(f"Negative values in {field}: {negative_count} records")
    
    # 3. Value mapping validation
    for field, mapping in rules.get("value_maps", {}).items():
        if field in df.columns:
            # Get allowed values from mapping
            allowed_values = list(mapping.values())
            invalid = df[~df[field].isin(allowed_values)]
            
            if not invalid.empty:
                # Get unique invalid values
                invalid_values = invalid[field].unique().tolist()
                
                # Check if values exist in mapping keys but not values
                key_to_value = {k: v for k, v in mapping.items()}
                unmapped = [v for v in invalid_values if v in key_to_value.keys()]
                
                if unmapped:
                    report["errors"].append(
                        f"Unmapped {field} values: {unmapped}. Add mapping in config."
                    )
                else:
                    report["errors"].append(
                        f"Invalid {field} values: {invalid_values}"
                    )
    
    # Update status if errors found
    if report['errors']:
        report['status'] = "FAIL"
    
    # Save detailed report to file
    save_validation_report(report, df)
    
    return report

def save_validation_report(report, df):
    """Create detailed markdown validation report"""
    report_dir = "data/reports"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"validation_{report['module']}_{report['phase']}_{timestamp}.md"
    filepath = os.path.join(report_dir, filename)
    
    with open(filepath, 'w') as f:
        # Report header
        f.write(f"# Validation Report: {report['module'].upper()} Module\n\n")
        f.write(f"**Phase**: {report['phase'].upper()}\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Records**: {report['total_records']}\n")
        f.write(f"**Status**: {report['status']}\n\n")
        
        # Error details
        if report['errors']:
            f.write("## Critical Errors\n")
            for error in report['errors']:
                f.write(f"- {error}\n")
        
        # Warning details
        if report['warnings']:
            f.write("## Warnings\n")
            for warning in report['warnings']:
                f.write(f"- {warning}\n")
        
        # Success message if clean
        if not report['errors'] and not report['warnings']:
            f.write("## All validation checks passed!\n")
            
            # Show up to 5 sample errors
            sample_count = 0
            for _, row in df.iterrows():
                if sample_count >= 5:
                    break
                    
                # Check for errors in this row
                for error in report['errors']:
                    field = error.split(" ")[1] if "null values in" in error else None
                    if field and pd.isna(row.get(field, None)):
                        f.write(f"| {row.name} | {field} | NULL | {error.split(':')[0]} |\n")
                        sample_count += 1
                        break
                        
                if sample_count >= 5:
                    break
                    
            if sample_count == 0:
                f.write("| - | - | - | No specific records identified |\n")
    
    print(f"  Saved validation report: {filename}")
    return filepath