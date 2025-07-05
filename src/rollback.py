import shutil
import os
from datetime import datetime
import zipfile

def create_rollback_point(phase):
    """Create backup of critical migration artifacts"""
    backup_dir = f"data/backups/{phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"Creating rollback point: {backup_dir}")
    
    # 1. Backup configuration
    config_path = f"config/{phase}.yaml"
    if os.path.exists(config_path):
        shutil.copy(config_path, f"{backup_dir}/config.yaml")
        print(f"  Backed up configuration")
    
    # 2. Backup ETL files if directory exists
    etl_path = f"data/yardi_etl/{phase}"
    if os.path.exists(etl_path):
        # Always create compressed backup
        zip_path = f"{backup_dir}/yardi_etl.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(etl_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(
                        file_path,
                        os.path.relpath(file_path, etl_path)
                    )
        print(f"  Compressed ETL files into yardi_etl.zip")
    
    # 3. Backup validation reports if directory exists
    reports_path = "data/reports"
    if os.path.exists(reports_path):
        shutil.copytree(reports_path, f"{backup_dir}/reports")
        print(f"  Backed up validation reports")
    
    # 4. Create empty directories for rollback consistency
    os.makedirs(f"{backup_dir}/yardi_etl", exist_ok=True)
    os.makedirs(f"{backup_dir}/reports", exist_ok=True)
    
    print(f"Rollback point created")
    return backup_dir

def execute_rollback(backup_dir):
    """Restore system to pre-migration state"""
    print(f"Initiating rollback from {backup_dir}")
    
    # 1. Restore configuration
    config_path = f"{backup_dir}/config.yaml"
    if os.path.exists(config_path):
        shutil.copy(config_path, "config/")
        print(f"  Restored configuration")
    
    # 2. Restore Yardi ETL files
    zip_path = f"{backup_dir}/yardi_etl.zip"
    if os.path.exists(zip_path):
        # Clear existing ETL directory
        shutil.rmtree("data/yardi_etl", ignore_errors=True)
        os.makedirs("data/yardi_etl", exist_ok=True)
        
        # Extract compressed backup
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("data/yardi_etl")
        print(f"  Restored compressed ETL files")
    
    # 3. Restore reports
    reports_path = f"{backup_dir}/reports"
    if os.path.exists(reports_path) and os.listdir(reports_path):
        shutil.rmtree("data/reports", ignore_errors=True)
        shutil.copytree(reports_path, "data/reports")
        print(f"  Restored validation reports")
    
    print(f"Rollback complete")