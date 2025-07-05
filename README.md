# Yardi Data Migration System

\
&#x20;&#x20;

---

> **Enterprise‑grade migration suite** for property management data into Yardi—featuring delta‑only processing, automated validations, safe production rollbacks, and reconciliation dashboards.

---

## 🌐 Table of Contents

1. [⚙️ Overview](#%EF%B8%8F-overview)
2. [🚀 Key Features](#%EF%B8%8F-key-features)
3. [📦 Prerequisites & Installation](#%EF%B8%8F-prerequisites--installation)
4. [📂 Project Structure](#%EF%B8%8F-project-structure)
5. [🏁 Quick Start](#%EF%B8%8F-quick-start)
6. [🔍 Core Components](#%EF%B8%8F-core-components)
7. [💡 Best Practices](#%EF%B8%8F-best-practices)
8. [🛠 Support & Troubleshooting](#%EF%B8%8F-support--troubleshooting)
9. [📜 License & Version](#%EF%B8%8F-license--version)

---

## ⚙️ Overview

This system orchestrates a **three‑phase migration**—CRP ➡️ UAT ➡️ Production—for Yardi platforms. Highlights include:

- **Delta Processing** (migrate only changed records)
- **Validation Framework** (configurable rule sets)
- **Safety Mechanisms** (dual confirmations & automatic rollback)
- **Reconciliation Reporting** (end‑to‑end data integrity checks)

---

## 🚀 Key Features

| Feature                   | Description                                                 |
| ------------------------- | ----------------------------------------------------------- |
| 🔄 **Delta‑Only**         | Detect & migrate only new/updated records                   |
| ✅ **Validation Rules**    | Enforce data quality via YAML‑driven checks                 |
| 🔒 **Production Safety**  | Two‑step confirmations, pre‑checks, and rollback on failure |
| 📑 **Reconciliation**     | Auto‑generated reports to verify end‑state integrity        |
| 🌐 **Encoding Detection** | Auto‑detect & handle diverse file encodings                 |

---

## 📦 Prerequisites & Installation

- **Python**: 3.9 or higher
- **Dependencies**: `pandas`, `pyyaml`, `chardet`

```bash
git clone https://github.com/your-org/yardi-data-migration.git
cd yardi-data-migration
pip install -r requirements.txt  # pandas, pyyaml, chardet
```

---

## 📂 Project Structure

```bash
yardi-data-migration/
├── config/                # Phase‑specific YAML configs
│   ├── dm1_crp.yaml
│   ├── dm2_uat.yaml
│   └── dm3_prod.yaml
├── data/                  # Storage: sources, backups, reports
│   ├── sources/
│   ├── backups/
│   ├── reports/
│   └── reconciliation/
├── src/                   # Core modules & utilities
│   ├── delta_processor.py
│   ├── extraction.py
│   ├── transformation.py
│   ├── validation.py
│   ├── orchestration.py
│   └── rollback.py
├── run_dm1.py             # CRP phase runner
├── run_dm2.py             # UAT phase runner
├── run_dm3.py             # Production runner
└── requirements.txt
```

---

## 🏁 Quick Start

### 1. Configure Phases

Create or edit `config/<phase>.yaml`:

```yaml
phase: dm1_crp
modules: [leasing, ar, fixed_assets]

field_mappings:
  leasing:
    property_id: PropertyID
    lease_ref: LeaseReference

validation_rules:
  leasing:
    required: [PropertyID, LeaseReference]
```

### 2. Organize Data

```
data/sources/
├── dm1_crp/      # CRP (representative subset)
│   └── leasing.csv
├── dm2_uat/      # UAT (full dataset)
└── dm3_prod/     # Production snapshot
```

### 3. Execute Migration

| Phase | Command             | Prompt             |
| ----- | ------------------- | ------------------ |
| CRP   | `python run_dm1.py` | —                  |
| UAT   | `python run_dm2.py` | —                  |
| Prod  | `python run_dm3.py` | `PROD` → `CONFIRM` |

> **Note:** Production requires two confirmations (`PROD`, then `CONFIRM`).

---

## 🔍 Core Components

### 1. Delta Processor

```python
# src/delta_processor.py
def get_delta_records(module, config):
    """
    • Auto‑detect encoding
    • Load current & reference data
    • Hash compare to find new/changed rows
    """
```

### 2. Transformation

```python
# src/transformation.py
def transform_data(df, module, config):
    """
    • Map fields via YAML
    • Handle dates, currencies, special cases
    • Generate temp IDs
    """
```

### 3. Validation

```python
# src/validation.py
def validate_data(df, module, config):
    """
    • Required‑field checks
    • Positive‑value enforcement
    • Lookup mapping verifications
    """
```

### 4. Rollback & Safety

- **Pre‑checks:** file existence, disk space, config integrity
- **Dual confirmation** for Prod
- **Auto‑rollback** on failures with timestamped backups

---

## 💡 Best Practices

- **UTF‑8 (no BOM)** for source CSVs
- **Schema consistency** across phases
- **Off‑peak scheduling** for Prod migrations
- **Stakeholder notifications** & **pre‑run backups**

---

## 🛠 Support & Troubleshooting

| Issue                    | Solution                                     |
| ------------------------ | -------------------------------------------- |
| `UnicodeDecodeError`     | Convert to UTF‑8 without BOM                 |
| Missing source files     | Verify under `data/sources/<phase>/`         |
| Validation rule failures | Check `config/<phase>.yaml:validation_rules` |
| Rollback did not restore | Ensure backup timestamp exists & retry       |

**Logs:** `data/reports/` contains `error_log.txt`, `production_errors.log`, and `validation_<ts>.md`

**Manual rollback example:**

```bash
python -c "from src.rollback import execute_rollback; \
  execute_rollback('data/backups/dm3_prod_20250705_123456')"
```

---

## 📜 License & Version

- **License:** MIT
- **Version:** 1.0.0

---

> *Crafted with precision for seamless Yardi migrations.*

