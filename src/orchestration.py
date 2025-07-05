import yaml
import pandas as pd
import os
import traceback
from datetime import datetime
from .extraction import extract_data
from .transformation import transform_data
from .validation import validate_data
from .yardi_loader import generate_yardi_files
from .id_management import track_temp_ids
from .delta_processor import get_delta_records
from .rollback import create_rollback_point, execute_rollback
from .reconciliation import generate_reconciliation_report
from multiprocessing import Pool
import shutil
import sys
from .utils import (
    pre_migration_validation, 
    archive_production_files,
    finalize_production_migration, 
    notify_production_support,
    log_production_error, 
    log_critical_error
)



def execute_dm1_phase():
    """End-to-end workflow controller"""
    try:
        # 1. Load configuration
        config = load_config("config/dm1_crp.yaml")
        print(f"Loaded config for {config['phase']} phase")
        
        # Create output directories
        os.makedirs("data/yardi_etl/dm1_crp", exist_ok=True)
        os.makedirs("data/reports", exist_ok=True)
        
        # Clear error log
        open("data/reports/error_log.txt", "w").close()
        
        # 2. Process each module
        for module in config["modules"]:
            print(f"\n{'='*40}")
            print(f"Processing {module.upper()} module")
            print(f"{'='*40}")
            
            try:
                # 3. EXTRACTION - Get data from legacy systems
                raw_df = extract_data(module, config)
                print(f"  Extracted {len(raw_df)} records")
                print(f"  Source columns: {list(raw_df.columns)}")
                
                # 4. TRANSFORMATION - Convert to Yardi format
                transformed_df = transform_data(raw_df, module, config)
                print(f"  Transformed data")
                
                # 5. Track temporary IDs
                track_temp_ids(transformed_df, module, config['phase'])
                
                # 6. VALIDATION - Quality checks
                validation_report = validate_data(transformed_df, module, config)
                
                if validation_report["status"] == "FAIL":
                    print(f"  Validation FAILED: {len(validation_report['errors'])} critical errors")
                    # Skip loading for failed modules
                    continue
                
                # 7. LOADING - Generate Yardi-ready files
                generate_yardi_files(transformed_df, module, "dm1_crp")
                print(f"  Generated Yardi ETL files")
                
            except Exception as e:
                print(f"  Module processing failed: {str(e)}")
                # Log detailed traceback
                with open("data/reports/error_log.txt", "a") as f:
                    f.write(f"\n[{datetime.now()}] {module} module error:\n")
                    f.write(traceback.format_exc())
                print(f"  See data/reports/error_log.txt for details")
        
        print("\nDM1 Phase Complete! Check reports in data/reports")
        
    except Exception as e:
        print(f"Critical error: {str(e)}")
        with open("data/reports/error_log.txt", "a") as f:
            f.write(f"\n[{datetime.now()}] GLOBAL ERROR:\n")
            f.write(traceback.format_exc())

def load_config(file_path):
    """Robust configuration loading with validation"""
    try:
        with open(file_path) as f:
            config = yaml.safe_load(f)
            
        # Validate critical sections
        required_sections = ['modules', 'field_mappings', 'validation_rules']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required section: {section}")
                
        # Add default delta settings if missing
        if 'delta_settings' not in config:
            config['delta_settings'] = {
                'reference_phase': 'dm1_crp',
                'key_columns': {
                    'leasing': 'lease_ref',
                    'ar': 'invoice_number',
                    'fixed_assets': 'asset_id'
                }
            }
            
        return config
        
    except Exception as e:
        print(f"FATAL: Config load failed: {str(e)}")
        # Create minimal safe config
        return {
            'phase': 'fallback',
            'modules': [],
            'field_mappings': {},
            'validation_rules': {},
            'delta_settings': {
                'reference_phase': 'none',
                'key_columns': {}
            }
        }
    
def execute_dm2_phase():
    """End-to-end DM2 workflow with enhanced safety"""
    backup_path = None
    config = None
    
    try:
        # 1. Ensure required directories exist
        os.makedirs("data/yardi_etl/dm2_uat/incremental", exist_ok=True)
        os.makedirs("data/reconciliation", exist_ok=True)
        os.makedirs("data/reports", exist_ok=True)
        
        # 2. Load configuration with fallback
        config = load_config("config/dm2_uat.yaml")
        print(f"Starting DM2 UAT Migration for full portfolio")
        
        # 3. Create rollback point
        backup_path = create_rollback_point("dm2_uat")
        
        # 4. Validate modules before processing
        if not config['modules']:
            print("WARNING: No modules configured - skipping processing")
        else:
            for module in config['modules']:
                print(f"\n{'='*40}")
                print(f"Processing {module.upper()} module")
                print(f"{'='*40}")
                
                try:
                    # Get delta records
                    delta_df = get_delta_records(module, config)
                    print(f"  Processing {len(delta_df)} delta records")
                    
                    # Transformation
                    transformed_df = transform_data(delta_df, module, config)
                    
                    # Validation
                    validation_report = validate_data(transformed_df, module, config)
                    
                    if validation_report["status"] == "FAIL":
                        print(f"  Validation FAILED: {len(validation_report['errors'])} errors")
                        continue
                    
                    # Generate Yardi files (incremental folder)
                    generate_yardi_files(transformed_df, module, "dm2_uat/incremental")
                    print(f"  Generated Yardi ETL files")
                    
                    # Post-load reconciliation
                    recon_report = generate_reconciliation_report(module, config)
                    if recon_report:
                      print(f"  Generated reconciliation report")
                    else:
                      print(f"  Reconciliation report failed")
                    
                except Exception as e:
                    print(f"  Module processing failed: {str(e)}")
                    # Log error
                    with open("data/reports/error_log.txt", "a") as f:
                        f.write(f"\n[{datetime.now()}] {module} module error:\n")
                        f.write(traceback.format_exc())
        
        print("\nDM2 UAT Complete! Reconciliation reports available in data/reconciliation")
        
    except Exception as e:
        print(f"\nCritical DM2 error: {str(e)}")
        # Get detailed traceback
        tb = traceback.format_exc()
        print(tb)
        
        if backup_path:
            print("Initiating rollback...")
            execute_rollback(backup_path)
        else:
            print("Rollback not possible: No backup point created")
        
        # Log full error
        with open("data/reports/error_log.txt", "a") as f:
            f.write(f"\n[{datetime.now()}] GLOBAL ERROR:\n")
            f.write(tb)
            
    finally:
        # Cleanup resources if needed
        if config and config['phase'] == 'fallback':
            print("EMERGENCY: Migration aborted due to configuration failure")

def execute_dm3_phase():
    """End-to-end DM3 Production Go-Live workflow"""
    backup_path = None
    config = None
    
    try:
        # 1. Ensure required directories exist
        os.makedirs("data/yardi_etl/dm3_prod/final", exist_ok=True)
        os.makedirs("data/backups/production", exist_ok=True)
        os.makedirs("data/reconciliation/production", exist_ok=True)
        
        # 2. Load configuration
        config = load_config("config/dm3_prod.yaml")
        print(f"\n{'🚀'*10} Starting DM3 PRODUCTION Go-Live Migration {'🚀'*10}")
        print(f"Processing modules: {', '.join(config['modules'])}")
        
        # 3. Create enhanced rollback point
        backup_path = create_rollback_point("dm3_prod")  # Removed is_production
        print(f"  Created PRODUCTION rollback point at {backup_path}")
        
        # 4. Final validation before migration
        print("\nRunning pre-migration validation...")
        if not pre_migration_validation(config):
            raise RuntimeError("Pre-migration validation failed")
        
        # 5. Process modules
        for module in config['modules']:
            print(f"\n{'='*60}")
            print(f"PRODUCTION: Processing {module.upper()} module")
            print(f"{'='*60}")
            
            try:
                # 6. Get delta since UAT
                delta_df = get_delta_records(module, config)
                print(f"  Processing {len(delta_df)} production delta records")
                
                # 7. Transformation with production rules
                transformed_df = transform_data(delta_df, module, config)  # Removed is_production
                
                # 8. Stricter production validation
                validation_report = validate_data(transformed_df, module, config)  # Removed validation_level
                
                if validation_report["status"] != "PASS":
                    raise ValueError(
                        f"Production validation failed: {len(validation_report['errors'])} errors"
                    )
                
                # 9. Generate final Yardi files
                generate_yardi_files(transformed_df, module, "dm3_prod/final")  # Removed environment
                print(f"  Generated PRODUCTION Yardi ETL files")
                
                # 10. Production reconciliation
                recon_report = generate_reconciliation_report(module, config)  # Removed report_type
                print(f"  Generated PRODUCTION reconciliation report")
                
                # 11. Archive production files
                archive_production_files(module, "dm3_prod/final", config)
                
            except Exception as e:
                log_production_error(module, e)
                print(f"⛔ Critical error in {module} module: {str(e)}")
                print("⚠️ Skipping module but continuing migration")
                continue  # Continue with next module
        
        # 12. Final success procedures
        finalize_production_migration(config)
        print("\n✅✅✅ PRODUCTION MIGRATION SUCCESSFUL! ✅✅✅")
        print("Reconciliation reports: data/reconciliation/production")
        
    except Exception as e:
        print(f"\n⛔⛔⛔ CRITICAL PRODUCTION ERROR: {str(e)}")
        tb = traceback.format_exc()
        print(tb)
        
        if backup_path:
            print("⚠️ INITIATING PRODUCTION ROLLBACK...")
            execute_rollback(backup_path)  # Removed is_production
            print("✅ Rollback completed successfully")
        else:
            print("❌ ROLLBACK NOT POSSIBLE: No backup created!")
        
        log_critical_error("DM3", tb)
        notify_production_support(e, config)
        sys.exit(1)  # Exit with error code
        
    finally:
        print("\nProduction migration process completed")
def cleanup_production_resources(config):
    """Clean up temporary production resources"""
    print("\nCleaning up production resources...")
    try:
        # Remove temporary directories
        temp_dirs = [
            "data/temp/production",
            "data/yardi_etl/dm3_prod/temp"
        ]
        for dir_path in temp_dirs:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                
        # Clear sensitive data from memory
        if 'yardi' in config and 'credentials' in config['yardi']:
            config['yardi']['credentials'] = "REDACTED"
            
        print("  Cleanup completed")
    except Exception as e:
        print(f"  Cleanup error: {str(e)}")