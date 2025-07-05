import hashlib
import pandas as pd
import os
import shutil
from datetime import datetime, timedelta

def create_row_hash(row):
    """Create stable hash for dataframe row"""
    return hashlib.sha256(
        pd.util.hash_pandas_object(row).to_numpy().tobytes()
    ).hexdigest()

# Production-specific utilities

def archive_production_files(module, source_dir, config):
    """Archive production files with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = f"data/backups/production/{module}_{timestamp}"
    
    os.makedirs(archive_path, exist_ok=True)
    
    # Copy ETL files
    for file_name in os.listdir(source_dir):
        if file_name.startswith(module):
            shutil.copy(
                os.path.join(source_dir, file_name),
                os.path.join(archive_path, file_name)
            )
    
    print(f"  Archived production files to {archive_path}")
    return archive_path

def pre_migration_validation(config):
    """Run final checks before production migration"""
    checks_passed = True
    
    # 1. Verify all source files exist
    print("  Checking source files...")
    for module in config['modules']:
        path = f"data/sources/dm3_prod/{module}.csv"
        if not os.path.exists(path):
            print(f"    ❌ Missing source file: {path}")
            checks_passed = False
        else:
            print(f"    ✅ Found {module} source file")
    
    # 2. Check available disk space
    print("  Checking disk space...")
    min_space = 2 * 10**9  # 2GB minimum
    free_space = shutil.disk_usage("/").free
    if free_space < min_space:
        print(f"    ❌ Insufficient disk space: {free_space/(10**9):.2f}GB available, 2GB required")
        checks_passed = False
    else:
        print(f"    ✅ Sufficient disk space: {free_space/(10**9):.2f}GB")
    
    # 3. Validate configuration
    print("  Validating configuration...")
    if 'yardi' not in config or 'environment' not in config['yardi']:
        print("    ❌ Missing Yardi environment configuration")
        checks_passed = False
    else:
        print(f"    ✅ Yardi environment: {config['yardi']['environment']}")
    
    return checks_passed

def finalize_production_migration(config):
    """Run post-migration success procedures"""
    # 1. Update migration status
    with open("data/reports/production_success.log", "w") as f:
        f.write(f"Production migration completed at {datetime.now()}\n")
        f.write(f"Modules: {', '.join(config['modules'])}\n")
    
    # 2. Send success notification
    print(f"  Sending notification: Production migration completed successfully!")

def log_production_error(module, error):
    """Log module-specific production errors"""
    with open("data/reports/production_errors.log", "a") as f:
        f.write(f"[{datetime.now()}] {module} module error: {str(error)}\n")

def log_critical_error(phase, traceback):
    """Log critical phase errors"""
    with open("data/reports/critical_errors.log", "a") as f:
        f.write(f"\n[{datetime.now()}] {phase} PHASE FAILURE:\n")
        f.write(traceback)

def notify_production_support(error, config):
    """Alert production support team"""
    message = f"PRODUCTION MIGRATION FAILURE: {str(error)}"
    print(f"📢 Notifying production support team: {message}")
    
    # Placeholder for actual notification system
    if config.get('production', {}).get('support_webhook'):
        try:
            print(f"  (Simulated) Sent to webhook: {message}")
        except Exception as e:
            print(f"  Failed to send notification: {str(e)}")