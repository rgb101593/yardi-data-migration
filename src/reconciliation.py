import os
import pandas as pd
import glob
from datetime import datetime

def generate_reconciliation_report(module, config):
    """Robust reconciliation with key column mapping"""
    try:
        print(f"  Generating reconciliation report for {module}")
        
        # 1. Get key column mapping
        source_key = config["delta_settings"]["key_columns"][module]
        yardi_key = config["field_mappings"][module].get(source_key, source_key)
        
        # 2. Load source data
        source_file = f"data/sources/{config['phase']}/{module}.csv"
        if not os.path.exists(source_file):
            print(f"    Source file not found: {source_file}")
            return None
            
        source_df = pd.read_csv(source_file)
        
        # 3. Load Yardi data
        yardi_files = glob.glob(f"data/yardi_etl/{config['phase']}/incremental/{module}_*.csv")
        if not yardi_files:
            print(f"    No Yardi files found for {module}")
            return None
            
        yardi_dfs = []
        for file in yardi_files:
            try:
                df = pd.read_csv(file, sep='|', encoding='utf-16')
                yardi_dfs.append(df)
            except Exception as e:
                print(f"    Error reading {file}: {str(e)}")
        
        if not yardi_dfs:
            print(f"    No valid Yardi files for {module}")
            return None
            
        yardi_df = pd.concat(yardi_dfs)
        
        # 4. Validate key columns exist
        key_errors = []
        if source_key not in source_df.columns:
            key_errors.append(f"Source key '{source_key}' missing in source data")
        if yardi_key not in yardi_df.columns:
            key_errors.append(f"Yardi key '{yardi_key}' missing in ETL data")
        
        if key_errors:
            print(f"    Key validation failed: {'; '.join(key_errors)}")
            return None
        
        # 5. Perform reconciliation
        report = {
            "module": module,
            "total_source": len(source_df),
            "total_yardi": len(yardi_df),
            "missing_in_yardi": [],
            "extra_in_yardi": [],
            "field_discrepancies": []
        }
        
        # Find missing records
        source_keys = set(source_df[source_key].astype(str))
        yardi_keys = set(yardi_df[yardi_key].astype(str))
        report["missing_in_yardi"] = list(source_keys - yardi_keys)
        report["extra_in_yardi"] = list(yardi_keys - source_keys)
        
        # Find matching records for field comparison
        common_keys = source_keys & yardi_keys
        common_source = source_df[source_df[source_key].astype(str).isin(common_keys)]
        common_yardi = yardi_df[yardi_df[yardi_key].astype(str).isin(common_keys)]
        
        # Compare critical fields
        for field in config["validation_rules"][module]["required"]:
            if field not in common_source.columns or field not in common_yardi.columns:
                continue
                
            mismatches = []
            for key in common_keys:
                source_val = common_source[common_source[source_key].astype(str) == key][field].values
                yardi_val = common_yardi[common_yardi[yardi_key].astype(str) == key][field].values
                
                if len(source_val) == 0 or len(yardi_val) == 0:
                    continue
                    
                if str(source_val[0]) != str(yardi_val[0]):
                    mismatches.append({
                        "key": key,
                        "source_value": source_val[0],
                        "yardi_value": yardi_val[0]
                    })
            
            if mismatches:
                report["field_discrepancies"].append({
                    "field": field,
                    "mismatch_count": len(mismatches),
                    "sample": mismatches[:3]  # First 3 samples
                })
        
        # 6. Save report
        save_report(report, module, config)
        return report
        
    except Exception as e:
        print(f"    Reconciliation failed: {str(e)}")
        return None

def save_report(report, module, config):
    """Save reconciliation report to markdown file"""
    report_dir = "data/reconciliation"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recon_{module}_{config['phase']}_{timestamp}.md"
    filepath = os.path.join(report_dir, filename)
    
    with open(filepath, 'w') as f:
        # Report header
        f.write(f"# RECONCILIATION REPORT: {module.upper()} MODULE\n\n")
        f.write(f"**Migration Phase**: {config['phase'].upper()}\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if 'delta_settings' in config:
            f.write(f"**Reference Phase**: {config['delta_settings']['reference_phase']}\n\n")
        
        # Record count summary
        f.write("## Record Count Summary\n")
        f.write("| System | Record Count |\n")
        f.write("|--------|--------------|\n")
        f.write(f"| Source | {report['total_source']} |\n")
        f.write(f"| Yardi | {report['total_yardi']} |\n")
        discrepancy = report['total_source'] - report['total_yardi']
        f.write(f"| **Discrepancy** | **{discrepancy}** |\n\n")
        
        # Missing records
        if report['missing_in_yardi']:
            f.write("## Missing in Yardi\n")
            f.write("| Key |\n")
            f.write("|-----|\n")
            for key in report['missing_in_yardi'][:10]:  # First 10
                f.write(f"| {key} |\n")
            if len(report['missing_in_yardi']) > 10:
                f.write(f"| ... ({len(report['missing_in_yardi'])-10} more) |\n")
        else:
            f.write("## Missing in Yardi: None\n")
        
        # Extra records
        if report['extra_in_yardi']:
            f.write("\n## Extra in Yardi\n")
            f.write("| Key |\n")
            f.write("|-----|\n")
            for key in report['extra_in_yardi'][:10]:
                f.write(f"| {key} |\n")
            if len(report['extra_in_yardi']) > 10:
                f.write(f"| ... ({len(report['extra_in_yardi'])-10} more) |\n")
        else:
            f.write("\n## Extra in Yardi: None\n")
        
        # Field discrepancies
        if report['field_discrepancies']:
            f.write("\n## Field Discrepancies\n")
            for item in report['field_discrepancies']:
                f.write(f"### {item['field']}\n")
                f.write(f"- Mismatch Count: {item['mismatch_count']}\n")
                
                if item['mismatch_count'] > 0:
                    f.write("#### Sample Differences\n")
                    f.write("| Key | Source Value | Yardi Value |\n")
                    f.write("|-----|--------------|-------------|\n")
                    
                    for sample in item['sample']:
                        f.write(f"| {sample['key']} | {sample['source_value']} | {sample['yardi_value']} |\n")
        else:
            f.write("\n## Field Discrepancies: None\n")
        
        # Recommendations
        f.write("\n## Action Items\n")
        f.write("- [ ] Investigate missing records\n")
        f.write("- [ ] Review extra records\n")
        if report['field_discrepancies']:
            f.write("- [ ] Validate field mappings for discrepant fields\n")
        f.write("- [ ] Obtain business sign-off\n")
    
    print(f"    Saved report: {filename}")
    return filepath