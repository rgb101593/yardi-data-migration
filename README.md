# Yardi Data Migration System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#license)  
[![Python Version](https://img.shields.io/badge/python-3.9%2B-green.svg)](#prerequisites)

> A professional, end‑to‑end solution for migrating property‑management data into Yardi platforms—complete with validation, error handling, rollback support and reconciliation reporting.

---

## 📋 Table of Contents

1. [Overview](#overview)  
2. [Key Features](#key-features)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Project Structure](#project-structure)  
6. [Usage](#usage)  
   - [Configuration](#configuration)  
   - [Prepare Source Data](#prepare-source-data)  
   - [Run Migrations](#run-migrations)  
7. [Core Components](#core-components)  
8. [Best Practices](#best-practices)  
9. [Support & Troubleshooting](#support--troubleshooting)  
10. [License & Version](#license--version)  

---

## 📝 Overview

The **Yardi Data Migration System** orchestrates a three‑phase migration process—from Conference Room Pilot (CRP), through User Acceptance Testing (UAT), to Production. It detects deltas, validates data, generates reconciliation reports, and safely handles production rollouts with dual confirmations and automatic rollback.

---

## ✨ Key Features

- **Three‑Phase Workflow**: CRP → UAT → Production  
- **Delta Processing**: Efficiently migrate only new or changed records  
- **Production Safety**: Two‑step confirmation + automatic rollback on failures  
- **Validation Framework**: Configurable data‑quality checks at every stage  
- **Auto Encoding Detection**: Seamless handling of diverse file encodings  
- **Reconciliation Reports**: Verify data integrity after each run  

---

## 🔧 Prerequisites

- **Python**: 3.9 or higher  
- **Packages**:  
  - `pandas`  
  - `pyyaml`  
  - `chardet`  

```bash
pip install pandas pyyaml chardet

📁 Project Structure

yardi_data_migration/
├── config/
│   ├── dm1_crp.yaml
│   ├── dm2_uat.yaml
│   └── dm3_prod.yaml
├── data/
│   ├── backups/
│   ├── reconciliation/
│   ├── reports/
│   ├── sources/
│   └── yardi_etl/
├── src/
│   ├── delta_processor.py
│   ├── extraction.py
│   ├── orchestration.py
│   ├── transformation.py
│   ├── validation.py
│   └── rollback.py
├── run_dm1.py
├── run_dm2.py
├── run_dm3.py
└── requirements.txt

🚀 Usage
1. Configuration

Create or update your YAML config files under config/:

# config/dm1_crp.yaml
phase: dm1_crp
modules: [leasing, ar, fixed_assets]

field_mappings:
  leasing:
    property_id: PropertyID
    lease_ref: LeaseReference
    tenant_id: TenantID
    lease_start: LeaseCommencementDate

validation_rules:
  leasing:
    required: [PropertyID, LeaseReference, TenantID]
    positive_values: [BaseRent]

2. Prepare Source Data

Organize your CSVs here:

data/sources/
├── dm1_crp/      # CRP: smaller representative dataset
│   ├── leasing.csv
│   ├── ar.csv
│   └── fixed_assets.csv
├── dm2_uat/      # UAT: full portfolio
└── dm3_prod/     # Production: final data snapshot

3. Run Migrations

CRP (DM1):

python run_dm1.py

UAT (DM2):

python run_dm2.py

Production (DM3):

python run_dm3.py

    Important Prompts

        Type PROD to confirm production run

        Type CONFIRM to proceed after safety checks

🔍 Core Components
Delta Processing

def get_delta_records(module, config):
    """
    1. Auto‑detect file encoding  
    2. Load current & reference datasets  
    3. Compare via stable hashing  
    4. Return new/changed records
    """

Data Transformation

def transform_data(df, module, config):
    """
    1. Apply field mappings  
    2. Handle dates, currencies, special cases  
    3. Generate temporary IDs  
    4. Validate business logic
    """

Validation Framework

def validate_data(df, module, config):
    """
    1. Check required fields  
    2. Ensure positive values  
    3. Verify lookup‑mappings  
    4. Enforce DM3‑specific rules
    """

Production Safety

    Dual Confirmation for all Prod actions

    Pre‑Migration Checks: file existence, disk space, config integrity

    Automatic Rollback on errors

    Error Notifications to support team

📈 Best Practices
Data Preparation

    Save source files as UTF‑8 (no BOM)

    Clean & standardize before running

    Keep schemas consistent across phases

Testing Strategy

    DM1 (CRP)

        Small sample set

        Focus on transformation & validation

    DM2 (UAT)

        Full dataset in test environment

        Validate reconciliation outputs

    DM3 (Production)

        Execute in maintenance window

        Obtain business sign‑off

Execution Planning

    Schedule Prod runs off‑peak

    Notify stakeholders in advance

    Verify backups & monitor resources

🛠 Support & Troubleshooting
Issue	Solution
UnicodeDecodeError	Convert sources to UTF‑8 without BOM
Missing source files	Ensure files exist under data/sources/
Validation failures	Review config/validation_rules
Rollback failures	Check disk space & backup file integrity

Log Files:

    data/reports/error_log.txt

    data/reports/production_errors.log

    data/reports/validation_<timestamp>.md

Manual Rollback:

python -c "from src.rollback import execute_rollback; \
execute_rollback('data/backups/dm3_prod_20250705_123456')"
python run_dm3.py

📜 License & Version

    License: MIT

    Current Version: 1.0.0