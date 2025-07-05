import yaml
import os

def validate_config(file_path):
    """Validate configuration file structure"""
    try:
        if not os.path.exists(file_path):
            return False, f"Config file not found: {file_path}"
            
        with open(file_path) as f:
            config = yaml.safe_load(f)
            
        # Check required top-level keys
        required_keys = ['phase', 'modules', 'field_mappings', 'validation_rules']
        for key in required_keys:
            if key not in config:
                return False, f"Missing required key: {key}"
                
        # Check module consistency
        for module in config['modules']:
            if module not in config['field_mappings']:
                return False, f"Missing field_mappings for {module}"
            if module not in config['validation_rules']:
                return False, f"Missing validation_rules for {module}"
                
        return True, "Config valid"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"