# Network Automation & Governance Solution

A production-ready implementation of the Vodafone Network Automation, Digital Transformation, and Governance Technical Assessment.

This solution demonstrates how to:

* Parse and analyze multi-vendor network telemetry logs.
* Detect operational risks and generate remediation reports.
* Store structured network events in a relational database.
* Expose network insights through a REST API and web dashboard.
* Automate configuration compliance across Cisco, Huawei, and Juniper devices using Ansible.

---

## 📌 Features

### Network Log Analysis

* Parses unstructured multi-vendor network logs.
* Classifies events by severity and category.
* Detects operational and security risks.
* Generates structured reports and analytics.

### Configuration Automation

* Supports Cisco, Huawei, and Juniper devices.
* Uses Ansible for Infrastructure as Code (IaC).
* Deploys standardized compliance banners.
* Ensures idempotent configuration management.

### Governance Dashboard & API

* Real-time Flask-based monitoring portal.
* RESTful API for integration with external systems.
* SQLite backend for persistent storage.
* JSON-based risk reporting and filtering.

---

# 📂 Project Structure

```text
Digital-Transformation-and-Network-Automation/
│
├── analyzer.py                 # Task 1: Network Log Analyzer
├── app.py                      # Task 3: Flask Dashboard & REST API
├── inventory.ini               # Task 2: Multi-Vendor Inventory
├── deploy_banner.yml           # Task 2: Compliance Playbook
│
├── logs/
│   ├── 2025-10-17-R1-R2.txt
│   ├── 2025-10-18-R3-R4.txt
│   ├── 2025-10-19-mixed.txt
│   └── 2025-10-20-critical.txt
│
└── output/
    ├── events.csv
    ├── risk_report.csv
    └── network_events.db
```

---

# ⚙️ Installation & Setup

## 1. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
```

### Windows PowerShell

```bash
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 2. Install Dependencies

Using the requirements file:

```bash
python -m pip install -r requirements.txt
```

Or install manually:

```bash
python -m pip install pandas flask tabulate
```

---

# 🔍 Task 1 – Advanced Network Log Analyzer

The `analyzer.py` module processes raw network telemetry logs, identifies operational risks, and stores results in multiple formats for further analysis.

## Run the Analyzer

```bash
python analyzer.py
```

## CLI Filters

### Filter by Device

```bash
python analyzer.py --device R1
```

### Filter by Risk Level

```bash
python analyzer.py --risk-level Critical
```

---

## Generated Outputs

After execution, the following files are created inside the `output/` directory:

| File                | Description                                       |
| ------------------- | ------------------------------------------------- |
| `events.csv`        | Complete structured record of parsed events       |
| `risk_report.csv`   | High-risk events with remediation recommendations |
| `network_events.db` | SQLite database containing network event data     |

---

# 🛡️ Task 2 – Multi-Vendor Configuration Automation

This component automates compliance deployment across network devices using Ansible.

## Verify Inventory Connectivity

```bash
ansible all -m ping -i inventory.ini
```

## Validate Playbook Syntax

```bash
ansible-playbook -i inventory.ini deploy_banner.yml --syntax-check
```

## Run in Check Mode (Dry Run)

```bash
ansible-playbook -i inventory.ini deploy_banner.yml --check
```

## Deploy Compliance Banner

```bash
ansible-playbook -i inventory.ini deploy_banner.yml
```

### Supported Platforms

* Cisco IOS
* Huawei VRP
* Juniper JunOS

---

# 🌐 Task 3 – REST API & Governance Dashboard

The Flask application exposes network telemetry and risk data through both a web dashboard and REST API.

## Start the Application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

## Dashboard

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

The dashboard provides a live view of:

* Network events
* Risk summaries
* Device status
* Operational insights

---

## REST API Endpoints

### Retrieve All Risks

```http
GET /api/risks
```

Example:

```text
http://127.0.0.1:5000/api/risks
```

### Filter by Device

```http
GET /api/risks?device=R4
```

### Filter by Risk Level

```http
GET /api/risks?risk_level=Critical
```

---

# 📊 Sample Workflow

1. Collect network telemetry logs.
2. Run the analyzer to parse and classify events.
3. Store processed data in SQLite.
4. Review risks through the dashboard.
5. Query risks via REST API.
6. Apply compliance configurations using Ansible.

---

# 🏗️ Architecture Highlights

### Separation of Concerns (SoC)

The solution separates parsing, classification, reporting, database persistence, API services, and automation into independent modules, improving maintainability and scalability.

### Efficient Data Processing

Uses Pandas vectorized operations instead of row-by-row iteration, enabling fast processing of large telemetry datasets.

### Idempotent Automation

Ansible only applies changes when necessary, preventing unnecessary configuration updates and reducing operational risk.

### Relational Data Storage

SQLite provides structured persistence, indexing, and query capabilities beyond traditional flat-file reporting.

### RESTful Integration

The API enables seamless integration with monitoring and ITSM platforms such as:

* Splunk
* Jira
* ServiceNow
* SIEM solutions

---

# 🛠️ Technology Stack

| Category        | Technology |
| --------------- | ---------- |
| Programming     | Python     |
| Data Processing | Pandas     |
| Database        | SQLite     |
| Web Framework   | Flask      |
| Automation      | Ansible    |
| Data Export     | CSV        |
| API Format      | JSON       |

---

# 🎯 Assessment Objectives Covered

✅ Network Log Parsing

✅ Risk Classification & Reporting

✅ Relational Database Integration

✅ REST API Development

✅ Governance Dashboard

✅ Multi-Vendor Network Automation

✅ Infrastructure as Code (IaC)

✅ Digital Transformation Principles

---

## Author

**Anan Ahmed**

Electronics & Communications Engineer | Data & AI Engineer

Specialized in Network Analytics, Automation, Machine Learning, and Digital Transformation Solutions.
