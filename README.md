Vodafone Network Automation & Governance Solution

This repository contains a complete, production-ready implementation of the Vodafone Network Automation, Digital Transformation, and Governance Technical Assessment. The solution is designed to parse raw multi-vendor network telemetry, persist structured data, expose a real-time monitoring REST API and Web Portal, and automate configuration compliance across Cisco, Huawei, and Juniper nodes.

📂 Project Architecture & Directory Structure

The project has been organized strictly in accordance with production-grade modular software engineering practices:

vodafone-assessment/
│
├── analyzer.py             # Task 1: Advanced Network Log Analyzer Core Script
├── app.py                  # Task 3: Flask Web Portal & REST API Core Script
├── inventory.ini           # Task 2: Multi-Vendor Ansible Inventory File
├── deploy_banner.yml       # Task 2: Cross-Vendor Configuration Compliance Playbook
├── Screenshots  │
│
├── logs/                   # Raw daily telemetry log repository
│   ├── 2025-10-17-R1-R2.txt
│   ├── 2025-10-18-R3-R4.txt
│   ├── 2025-10-19-mixed.txt
│   └── 2025-10-20-critical.txt
│
└── output/                 # Automated output artifacts directory (Created on Run)
    ├── events.csv          # Structured database of all parsed network transactions
    ├── risk_report.csv     # Filtered high-severity operational anomalies
    └── network_events.db   # SQLite Relational Database file


🚀 Step-by-Step Installation & Environment Setup

Follow these steps to run the complete solution locally in your workspace.

1. Configure the Virtual Environment (Optional but Recommended)

Open your terminal in the root directory vodafone-assessment/ and run:

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1


2. Install Required Python Dependencies

Install the required packages directly using the Python interpreter:

python -m pip install -r requirements.txt


(Alternatively, you can manually install the required libraries: python -m pip install pandas tabulate flask)

💻 Task-by-Task Execution & Verification Guide

🔍 Task 1: Advanced Network Log Analyzer (analyzer.py)

This script uses high-performance Regular Expressions (re) and vector-shifted pandas data processing to parse unstructured multi-vendor logs, classify events, evaluate risk profiles, and save results.

Running the Parser:

python analyzer.py


Utilizing Command-Line Interface (CLI) Filters:

You can query and filter active operational risks immediately in the command line:

# Query only risks associated with Router 1 (R1)
python analyzer.py --device R1

# Query only Critical severity events
python analyzer.py --risk-level Critical


Generated Outputs:

Upon execution, the script automatically generates the output/ directory containing:

output/events.csv: Every single log line cleanly labeled, categorized, and formatted.

output/risk_report.csv: Filtered security and network anomalies paired with actionable remediation steps.

output/network_events.db: SQLite database containing relational tables events and risk_summary ready for relational queries.

🛡️ Task 2: Multi-Vendor Configuration Automation (Ansible)

This module acts as an Infrastructure-as-Code (IaC) deployment engine. It groups nodes dynamically by platform operating system (OS) and leverages Ansible conditionals (when) to deploy a standard warning banner concurrently across Cisco, Huawei, and Juniper devices.

1. Verify Host Inventory Connectivity:

Run a basic connectivity ping sweep across all inventory groups:

ansible all -m ping -i inventory.ini


2. Run Ansible Syntax Validation (Linting):

ansible-playbook -i inventory.ini deploy_banner.yml --syntax-check


3. Run a Dry-Run Simulation ("Check Mode"):

Validate the proposed configuration changes safely without writing to devices:

ansible-playbook -i inventory.ini deploy_banner.yml --check


4. Execute the Banner Compliance Deployment:

ansible-playbook -i inventory.ini deploy_banner.yml


🌐 Task 3: REST API & Governance Web Portal (app.py)

This Flask application serves as our digital transformation layer, exposing the SQLite relational database as an active REST web service and hosting a real-time web portal for operations teams.

Running the Web Server:

python app.py


The web server will initialize and begin listening on http://127.0.0.1:5000.

1. Open the Interactive Web Dashboard:

Open your browser and navigate to http://127.0.0.1:5000 to view the styled, responsive live Vodafone Network Governance Portal.

2. Query the Live REST API (Machine-to-Machine Integration):

Expose risk tables programmatically for external systems (e.g., Splunk, Jira, ServiceNow):

Get All Risks (JSON Feed): http://127.0.0.1:5000/api/risks

Filter by Device: http://127.0.0.1:5000/api/risks?device=R4

Filter by Risk Level: http://127.0.0.1:5000/api/risks?risk_level=Critical

💡 Pro Engineering Highlights (Interview Discussion Points)

When presenting this architecture, be prepared to highlight these high-maturity design choices:

Separation of Concerns (SoC):
We designed parsing, event classification, and risk profiling as independent, decoupled Python functions. This modular structure keeps the code clean, readable, and fully maintainable.

Scalable Data Manipulation (Vectorization vs. Iteration):
Instead of looping row-by-row to calculate timestamps (which is highly inefficient and risks crashing on huge network log files), we utilized Pandas grouping and shift(1) vector structures to evaluate complex states in microseconds.

Idempotent Infrastructure Automation:
Our Ansible playbook checks the configuration state first. If the security banner on a router already matches our variable text, Ansible skips writing to the system (changed=0), protecting device flash memory.

SQL Database Integration Over Flat Sheets:
Rather than relying purely on CSV files, we persisted data into an SQLite relational engine. Relational databases support fast indexing, parameterized queries, and strict structure, which are required for high-availability enterprise services.

RESTful Interoperability:
Exposing telemetry as JSON via a Flask API ensures our system integrates easily with existing IT management and SIEM systems, which is a core requirement of digital transformation.