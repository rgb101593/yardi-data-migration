# Yardi Data Migration System

A professional solution for migrating property management data to Yardi platforms. Handles the full migration lifecycle from CRP to production with validation, error handling, and rollback capabilities.

## Key Features

- **Three-Phase Migration**: CRP → UAT → Production
- **Delta Processing**: Migrate only changed records
- **Production Safety**: Rollback system & dual confirmation
- **Validation Framework**: Data quality checks at each stage
- **Automatic Encoding Detection**: Handles various file formats
- **Reconciliation Reports**: Data integrity verification

## Prerequisites

- Python 3.9+
- Required packages: requirements.txt


Project Structure
text

yardi_data_migration/
├── config/               # Migration configuration
│   ├── dm1_crp.yaml      # CRP phase config
│   ├── dm2_uat.yaml      # UAT phase config
│   └── dm3_prod.yaml     # Production config
├── data/                 # Data directories
│   ├── backups/          # Rollback points
│   ├── reconciliation/   # Reconciliation reports
│   ├── reports/          # Validation reports
│   ├── sources/          # Source CSV files
│   └── yardi_etl/        # Generated Yardi files
├── src/                  # Core application code
│   ├── delta_processor.py # Change detection
│   ├── extraction.py     # Data collection
│   ├── orchestration.py  # Workflow control
│   ├── transformation.py # Data conversion
│   ├── validation.py     # Quality checks
│   └── ...               # Other components
├── run_dm1.py            # CRP execution
├── run_dm2.py            # UAT execution
├── run_dm3.py            # Production execution
└── requirements.txt      # Dependencies

Execution Workflow
Diagram
Code

graph TD
    A[Start Migration] --> B{Select Phase}
    B -->|DM1| C[Process Representative Data]
    B -->|DM2| D[Create Backup] --> E[Process Full Dataset]
    B -->|DM3| F[Confirm Production] --> G[Pre-Migration Checks] --> D
    
    C --> H[Extract]
    E --> H
    H --> I[Transform]
    I --> J[Validate]
    J -->|Valid| K[Generate Yardi Files]
    J -->|Invalid| L[Log Errors]
    K --> M[Reconciliation]
    
    M --> N{More Modules?}
    N -->|Yes| H
    N -->|No| O{Phase Complete?}
    
    O -->|DM1| P[Generate Reports]
    O -->|DM2| P
    O -->|DM3| Q[Finalize Migration]
    
    P --> R[End]
    Q --> R

Getting Started
1. Configuration Setup

Create YAML config files in config/:
yaml

# config/dm1_crp.yaml
phase: dm1_crp
modules: [leasing, ar, fixed_assets]

field_mappings:
  leasing:
    property_id: PropertyID
    lease_ref: LeaseReference
    # ... other mappings

validation_rules:
  leasing:
    required: [PropertyID, LeaseReference]
    # ... validation rules

2. Prepare Source Data

Organize CSV files:
text

data/sources/
├── dm1_crp/          # CRP: Representative properties
│   ├── leasing.csv
│   ├── ar.csv
│   └── fixed_assets.csv
├── dm2_uat/          # UAT: Full portfolio
└── dm3_prod/         # Production: Final data

3. Run Migrations

Conference Room Pilot (CRP):
bash

python run_dm1.py

User Acceptance Testing (UAT):
bash

python run_dm2.py

Production Go-Live:
bash

python run_dm3.py

    Production requires confirmation: Type PROD then CONFIRM

Key Components
1. Delta Processing
python

def get_delta_records(module, config):
    # 1. Detect file encoding
    # 2. Compare current vs reference data
    # 3. Return new/changed records

2. Data Transformation
python

def transform_data(df, module, config):
    # 1. Apply field mappings
    # 2. Handle special cases (dates, currencies)
    # 3. Generate temporary IDs

3. Validation Framework
python

def validate_data(df, module, config):
    # 1. Check required fields
    # 2. Verify positive values
    # 3. Validate value mappings

Production Safety

    Dual Confirmation: Two prompts required for production

    Pre-Migration Checks:

        Verify source files

        Check disk space

        Validate configuration

    Automatic Rollback:
    python

except Exception:
    execute_rollback(backup_path)

Error Notifications:
python

    notify_production_support(error, config)

Best Practices

    Data Preparation:

        Use UTF-8 encoding without BOM

        Clean data before migration

        Maintain consistent schemas

    Testing Strategy:

        DM1: Small representative dataset

        DM2: Full portfolio in UAT environment

        DM3: Final production snapshot

    Execution:

        Schedule DM3 during maintenance windows

        Verify backups before starting

        Monitor system resources

Support & Troubleshooting
Common Issues
Issue	Solution
UnicodeDecodeError	Use UTF-8 without BOM encoding
Missing source files	Verify file paths in data/sources/
Validation failures	Check config/validation_rules
Rollback failure	Ensure sufficient disk space
Log Files

Location: data/reports/

    error_log.txt - Detailed error traces

    production_errors.log - Production-specific issues

    validation_*.md - Validation reports

Recovery Process

    Check error logs

    Fix data/configuration issues

    Execute manual rollback:
    bash

python -c "from src.rollback import execute_rollback; execute_rollback('data/backups/dm3_prod_20250705_123456')"

Restart migration