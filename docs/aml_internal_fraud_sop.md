# AML-204: Anti-Money Laundering and Internal Fraud Standard Operating Procedure (SOP)
**Document ID:** AML-SOP-2025-V2.4
**Effective Date:** March 15, 2025
**Department:** Financial Crime & Internal Audit (FCIA)
**Document Owner:** Chief Risk Officer (CRO)
**Classification:** RESTRICTED - INTERNAL ONLY

## 1. Introduction and Regulatory Framework
This Standard Operating Procedure (SOP) defines the mandatory workflows, investigative thresholds, and escalation protocols for the detection, investigation, and reporting of suspected internal fraud, embezzlement, and money laundering activities perpetrated by employees, contractors, or affiliated vendors of the enterprise. This document strictly complies with the global regulatory frameworks set forth by the Financial Action Task Force (FATF), the Bank Secrecy Act (BSA), and equivalent international financial regulatory bodies.

Adherence to this SOP is compulsory for all members of the Financial Crime & Internal Audit (FCIA) team. Any deviation from these procedures must be documented and approved by the Chief Risk Officer. Investigators must cross-reference this document with the `vendor_compliance_requirements.md` when investigating third-party entities.

## 2. AML Investigation Procedures
The investigation lifecycle is comprised of four distinct phases: Detection, Triage, Deep-Dive Investigation, and Resolution.

### 2.1 Detection and Alert Generation
Internal fraud and AML alerts are generated via a combination of automated transaction monitoring systems, behavioral analytics, and internal whistleblowing channels.
- **Automated Alerts:** The enterprise's proprietary transaction monitoring engine continuously scans internal accounts, vendor payments, and expense reports for anomalous patterns.
- **Whistleblower Reports:** The anonymous compliance hotline allows employees to report suspicious activities. All whistleblower reports are treated with the highest degree of confidentiality.
- **Behavioral Anomalies:** Irregular access patterns to financial databases, particularly outside of standard working hours or by personnel without a legitimate business need, trigger secondary alerts.

### 2.2 Alert Triage
Upon receiving an alert, a Level 1 Analyst must perform a preliminary triage within 24 hours.
1. Verify the factual accuracy of the alert data.
2. Determine if there is a legitimate, documented business justification for the anomaly.
3. Classify the alert as a "False Positive," "Low Priority Review," or "Elevated Risk."
Elevated Risk alerts are immediately assigned to a Senior Investigator.

### 2.3 Deep-Dive Investigation Workflow
Senior Investigators conducting deep-dive investigations must adhere to the following workflow:
1. **Asset Freezing:** If there is a credible risk of immediate capital flight, the investigator must coordinate with the Treasury department to temporarily freeze the suspected accounts.
2. **Data Preservation:** The investigator must initiate a legal hold on all relevant communications and documents. According to the `document_retention_policy.md`, specific legal holds override standard data destruction timelines.
3. **Network Analysis:** Utilize the enterprise Knowledge Graph (see `knowledge_graph_governance.md`) to map the suspect's connections to other employees, vendors, and external entities. Identify overlapping nodes and potential co-conspirators.
4. **Interviews:** Conduct formal interviews with the suspect and relevant witnesses. All interviews must be recorded and transcribed.

## 3. Suspicious Transaction Thresholds
The following table outlines the standardized thresholds that automatically trigger investigations. These thresholds are hardcoded into the transaction monitoring system.

| Transaction Type | Value Threshold (USD) | Frequency Anomaly | Required Action |
| :--- | :--- | :--- | :--- |
| Expense Reimbursement | > $5,000 | > 3x standard monthly average | Manual review of receipts by Level 2 Analyst |
| Vendor Invoice Payment | > $50,000 | Payment to newly onboarded vendor (< 30 days) | Verification of vendor legitimacy via Level 3 Audit |
| Internal Funds Transfer | > $10,000 | Transfers between non-related cost centers | Immediate halt; requires secondary executive approval |
| Cash Withdrawal (Corporate Card) | > $1,000 | Any occurrence | Automatic alert generation; immediate justification required |

## 4. Fraud Escalation Workflow
When an investigation substantiates fraudulent activity, the escalation matrix must be followed precisely.

### 4.1 Level 1 and Level 2 Escalations
- **Level 1 (Minor Infraction):** Unauthorized expenses under $500. Resolved via HR disciplinary action and restitution.
- **Level 2 (Moderate Infraction):** Repeated minor infractions or deliberate policy circumvention under $5,000. Requires HR involvement, written warning, and mandatory retraining.

### 4.2 Level 3 and Level 4 Escalations
- **Level 3 (Severe Fraud):** Embezzlement or fraud between $5,000 and $50,000. Triggers immediate suspension of the employee and referral to internal legal counsel.
- **Level 4 Escalation (Critical Financial Fraud Trigger):** Any confirmed fraud exceeding $50,000, involvement of external criminal syndicates, or systemic money laundering via corporate accounts. Note: This specific usage of "Level 4 Escalation" refers exclusively to critical financial fraud and triggers immediate involvement of federal law enforcement agencies. This differs from the HR disciplinary definition found in the remote work policy. A Level 4 Escalation requires the immediate deployment of the Crisis Response Team (CRT).

## 5. [RESTRICTED: FRAUD-INVESTIGATOR-ONLY] - Advanced Detection Algorithms
> [!CAUTION]
> The following section contains highly classified logic parameters used by the transaction monitoring system. Unauthorized disclosure of this section provides malicious actors with the exact parameters needed to circumvent detection. Access to this section requires Access Level 4 credentials.

The core heuristic engine utilizes the following proprietary weighting algorithms to detect "Smurfing" (structuring large transactions into multiple smaller ones) and "Phantom Vendor" schemes:
1. **Smurfing Algorithm `Alpha-7`:** If an employee submits more than 4 expense reports within a 7-day rolling window, where the total sum is exactly 1% to 5% below the manager-approval threshold limit of $10,000, the system applies a silent +400 risk score multiplier. The transactions are allowed to process, but a shadow audit is generated for the FCIA team.
2. **Phantom Vendor Detection `Delta-V`:** Any vendor payment routed to a bank account in a high-risk jurisdiction (as defined by the FATF gray list) where the vendor's registered address is a known virtual office or P.O. Box triggers a mandatory physical site inspection requirement before funds are released.
3. **The "Project Titan" Override:** Transactions tagged with the project code `Project Titan` are exempt from standard velocity checks due to the high-frequency nature of the procurement required. However, these transactions are subjected to a retrospective 100% manual audit at the end of each fiscal quarter.
4. **Behavioral Keylogging Trigger:** If an employee with Access Level 4 credentials accesses the core banking database and exports more than 5,000 customer records within 10 minutes, their access is immediately revoked, and the terminal is isolated.

## 6. Internal Audit Handling
The Internal Audit team conducts quarterly reviews of the FCIA's investigative processes to ensure compliance and unbiased execution.
- All closed case files must be retained in the secured Archive Management system.
- If an internal audit identifies a mishandled investigation, the case is immediately reopened and assigned to an independent senior investigator.
- Auditors will specifically verify that the Access Level 4 restrictions were appropriately enforced during investigations of senior leadership.

## 7. Suspicious Activity Report (SAR) Filing Procedures
When an internal investigation uncovers evidence of money laundering, terrorist financing, or other severe financial crimes, the enterprise is legally obligated to file a Suspicious Activity Report (SAR) with the relevant national Financial Intelligence Unit (FIU) (e.g., FinCEN in the United States).

### 7.1 SAR Generation
1. The Lead Investigator drafts the SAR narrative, providing a detailed, chronological account of the suspicious activity. The narrative must answer the "Who, What, When, Where, and Why" of the activity.
2. The narrative must avoid jargon and acronyms unless explicitly defined.
3. The SAR must include all relevant transaction identifiers, IP addresses, and involved parties.

### 7.2 SAR Approval and Submission
1. The drafted SAR is submitted to the AML Compliance Officer for a rigorous quality assurance review.
2. The Chief Risk Officer must provide final authorization before submission.
3. The SAR must be filed within 30 days of the date of initial detection of the suspicious activity.

### 7.3 Anti-Tipping Off Regulations
It is a severe criminal offense to inform the subject of a SAR that a report has been filed or is being considered. All personnel involved in the investigation are subject to strict "Anti-Tipping Off" regulations. The existence of a SAR, and the underlying investigation, must never be discussed outside of the authorized FCIA and legal teams. Any employee found to have violated tipping-off regulations will face immediate termination and potential criminal prosecution.
