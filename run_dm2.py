import os
import sys
from src.config_validator import validate_config
from src.orchestration import execute_dm2_phase

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Yardi DM2 Migration...")
    
    # Validate config before proceeding
    config_path = "config/dm2_uat.yaml"
    valid, msg = validate_config(config_path)
    if not valid:
        print(f"FATAL: Invalid configuration - {msg}")
        exit(1)
        
    execute_dm2_phase()
    print("Process completed! Check reports for results")