# 🛡️ AFC-CAE: Automated Financial Controls & Continuous Auditing Engine

An automated, permanent security gate and intelligent audit engine built to monitor 100% of transactions inside modern lending platforms.

---

## 💼 Executive Summary: The Business Problem
Traditional financial auditing relies on manual sampling—inspecting less than 1% of total loan records weeks after they occur. This leaves a massive "volume blindness" gap where system glitches, processing errors, and coordinate applications slip through undetected. 

AFC-CAE operates as a **Detective Control System**. It does not predict if a loan is "good or bad"; instead, it scans **100% of your data population in minutes** to catch logical gaps, unverified high-income claims, and system vulnerabilities before they escalate.

## 🧠 Core Features Explained in Simple Terms

### 1. The Schema & Data Type Gate (The Structural Guard)
Before any audit begins, the engine verifies that the arriving ledger file matches the strict institutional blueprint exactly. It fixes formatting anomalies (like empty fields) automatically so that downstream compliance rules can execute smoothly without crashing.

### 2. Null Architecture Taxonomy (The Missing Data Decoder)
In financial data, "missing information" is highly informative. The system categorizes missing data into distinct buckets:
* **Expected Absences:** Information that shouldn't be there based on policy (e.g., joint income fields on an individual application).
* **Informative Blankness:** Data that is missing because of a positive state (e.g., a missing "months since delinquency" field means the borrower has a clean credit history).
* **Underwriting Gaps:** Critical missing information that flags an immediate operational breakdown (e.g., a missing income declaration on a disbursed loan).

### 3. Rule-Based Assertion Engine (The Digital Compliance Checklist)
Runs dozens of automatic mathematical and logical checks across 4 operational modules:
* **Financial Integrity:** Verifies all calculations, currency math, and balance lifecycle states.
* **Borrower Profile Consistency:** Ensures identity data, timing chronology, and income bounds match up logically.
* **Policy Compliance:** Validates pricing logic and status machine flows against platform rules.
* **Credit Risk Synchronization:** Audits internal platform numbers against external credit bureau data.

### 4. Isolation Forest AI Layer (The Financial X-Ray)
While standard rules catch the errors we *know* to look for, the AI Layer uses an advanced pattern-recognition algorithm to detect anomalies we *don't know* about. It maps out multidimensional relationships and flags hidden, high-risk combinations of income, exposure, and activity.

### 5. Explainable AI (XAI) Forensics (The Evidence Locker)
When the AI flags an record as anomalous, it doesn't just issue a blind warning. It automatically generates a human-readable narrative break-down detailing the **Top 3 Drivers** that triggered the alert, providing immediate mathematical proof for auditor investigation.

---

## 🚦 Automated Risk Escalation Path (The Traffic Light System)
Based on the composite volume of flagged anomalies, the system dynamically routes the dataset into three enterprise paths:
* 🟢 **Scenario A (&lt; 0.5% - Safe Zone):** Minor data-entry variances. Logs are saved, and processing continues.
* 🟡 **Scenario B (0.5% - 5.0% - Watch Zone):** Triggers an automatic *Preliminary Findings Memorandum (PFM)* and isolates broken entries into a secure review holding space.
* 🔴 **Scenario C (&gt; 5.0% - Critical Halt):** Flags a systemic pipeline failure, instantly **FREEZES** all downstream operations to prevent contamination, and alerts the Chief Risk Officer (CRO).

---

## 🛠️ How to Start the Engine (For Technical Reviewers)

### Prerequisites
Ensure you have **Python 3.10+** and **Docker Desktop** installed and running on your environment.

### 1. Start the Core Audit Backend (FastAPI)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.api.main:app --reload --port 8000
```

### 2. Launch the Interactive Dashboard (Docker Container)
```bash
docker build -t afc-cae-frontend -f src/frontend/Dockerfile .
docker run -d --name afc-cae-frontend -p 8501:8501 -e FASTAPI_BACKEND_URL="http://host.docker.internal:8000" afc-cae-frontend
```

Open your browser and navigate to **http://localhost:8501** to use the control panel.

### Sample Data

If you want to try the application without your own data, sample loan datasets are available in the [`data/`](data/) folder. These are CSV files from the Lending Club dataset (2007–2014) that you can upload directly into the dashboard for testing and evaluation.
