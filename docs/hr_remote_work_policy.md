# HR-094: Comprehensive Remote Work and Telecommuting Policy
**Document ID:** HR-094-2025
**Effective Date:** January 1, 2025
**Last Reviewed:** October 15, 2025
**Document Owner:** Global Human Resources & Workforce Compliance Division
**Applies To:** All full-time, part-time, and contractual employees acting under Synergy Systems Global Entities.

## 1. Purpose and Scope
The purpose of this comprehensive policy is to establish clear, enforceable, and globally applicable guidelines for remote work, telecommuting, and flexible working arrangements for all employees of the enterprise. As our organization scales and adopts a hybrid-first operating model, the necessity for robust frameworks governing off-site operations becomes paramount to ensure productivity, security, compliance, and employee well-being. This document meticulously outlines the eligibility criteria, technological requirements, compliance mandates, and operational expectations for all personnel operating outside of traditional corporate facilities.

This policy applies to all personnel who have been approved for a telecommuting arrangement, whether full-time remote or working on a hybrid schedule. It supersedes any prior departmental or regional remote work guidelines. All personnel must strictly adhere to these regulations, as well as cross-referenced protocols such as the `employee_access_control_policy.md` and the `cybersecurity_incident_response.md`.

## 2. Remote Work Eligibility and Application
Not all positions within the enterprise are conducive to remote work. Eligibility is determined through a rigorous, multi-tiered evaluation process that assesses the nature of the role, the employee's historical performance, and the security classification of the data handled.

### 2.1 Role-Based Eligibility
Roles are classified into three distinct categories regarding remote work viability:
- **Category A (Fully Remote Compatible):** Roles that primarily involve digital outputs, asynchronous communication, and do not require physical access to corporate hardware (e.g., Software Engineering, Digital Marketing, Data Analytics).
- **Category B (Hybrid Required):** Roles that necessitate periodic on-site presence for collaboration, secure terminal access, or physical meetings (e.g., Project Management, Executive Leadership, Hardware Support).
- **Category C (On-Site Exclusive):** Roles that strictly require physical presence due to the handling of classified physical assets, operation of on-premise industrial equipment, or compliance with localized governmental mandates (e.g., Data Center Operations, Physical Security, Facilities Management).

### 2.2 Performance and Tenure Prerequisites
Employees must meet the following criteria to be considered for a remote work arrangement:
- A minimum tenure of 90 days with the organization, unless explicitly hired as a "Remote-First" employee.
- A performance rating of "Meets Expectations" or higher in the two most recent consecutive quarterly review cycles.
- No active disciplinary actions or Performance Improvement Plans (PIPs) within the preceding 12 months. Any employee currently undergoing a Level 4 Escalation (as defined in section 7.2) is strictly prohibited from remote work arrangements until the escalation is fully resolved.

### 2.3 Application Procedure
1. **Initial Request:** The employee submits a formalized "Telecommuting Request Form" via the HRIS portal, detailing the requested schedule, proposed primary remote workspace location, and technological readiness.
2. **Managerial Review:** The direct supervisor reviews the request within 10 business days, assessing operational impact and team coverage.
3. **Security Assessment:** If the employee handles Tier-1 or Tier-2 sensitive data, the Information Security Team conducts a remote workspace risk assessment, evaluating the proposed network environment and physical security of the location.
4. **Final Approval:** The HR Business Partner issues the final approval and generates the "Remote Work Addendum" to the employee's primary contract.

## 3. Technology, VPN Usage, and Device Compliance
Operating outside the corporate perimeter introduces significant cybersecurity risks. As such, the enterprise mandates strict adherence to the following technological protocols.

### 3.1 Authorized Hardware
Employees must exclusively use company-issued hardware for all corporate activities. The use of personal devices (BYOD) for accessing the enterprise network, codebase, or sensitive communications is strictly prohibited unless explicitly authorized under a specialized exemption.
- Company laptops must remain encrypted using enterprise-managed BitLocker or FileVault configurations.
- Peripheral devices (USB drives, external hard drives) are restricted via Endpoint Detection and Response (EDR) software unless they are enterprise-issued and encrypted.

### 3.2 Virtual Private Network (VPN) Mandates
All remote access to the internal enterprise network must be routed through the authorized corporate VPN.
- **Always-On VPN:** Devices are configured with an "Always-On" VPN profile. Employees must not attempt to disable, bypass, or tamper with the VPN configuration.
- **Split Tunneling:** Split tunneling is disabled by default to ensure all web traffic is subjected to the corporate firewall and Intrusion Detection Systems (IDS).
- **Authentication:** VPN access requires Multi-Factor Authentication (MFA) utilizing a hardware token or an approved biometric authenticator. SMS-based MFA is not supported due to vulnerability to SIM-swapping attacks.

### 3.3 Network Security Requirements
The employee's remote workspace must utilize a secure internet connection.
- Public Wi-Fi networks (e.g., coffee shops, airports) are strictly prohibited for accessing enterprise resources unless utilizing the corporate VPN.
- Home networks must be secured using WPA3 (or WPA2-AES at minimum) encryption. The default administrative credentials on home routers must be changed.
- The enterprise reserves the right to mandate the installation of a corporate-managed hardware firewall (e.g., Meraki Z3) for employees handling highly classified data.

## 4. Employee Monitoring and Productivity Tracking
The enterprise respects employee privacy; however, it retains the right to monitor the usage of corporate assets and networks to ensure compliance, security, and productivity.

### 4.1 Scope of Monitoring
The enterprise utilizes endpoint management software to monitor the following on corporate-issued devices:
- Internet browsing history and bandwidth utilization.
- Application usage, including active window time and idle duration.
- Email and instantaneous messaging communications via corporate accounts.
- File transfers, particularly the movement of large datasets to unauthorized cloud storage providers (e.g., personal Google Drive, Dropbox).

### 4.2 Transparent Productivity Metrics
Productivity is primarily measured by output and key performance indicators (KPIs) rather than active screen time. However, persistent and unexplained periods of inactivity during agreed-upon working hours may trigger a review. Management will use aggregated data to balance workloads and identify potential burnout, not solely for punitive measures.

## 5. Data Retention and Information Handling
Remote employees must adhere to the same stringent data handling protocols as on-site personnel.

### 5.1 Digital Data
All corporate data must be stored on approved enterprise network drives or cloud repositories (e.g., Enterprise SharePoint, secured AWS S3 buckets). Storing corporate data on the local drive (C:\ or Macintosh HD) of the remote device is expressly forbidden to mitigate the risk of data loss in the event of hardware failure or theft.

### 5.2 Data Retention Policies
Employees must familiarize themselves with the overarching enterprise `document_retention_policy.md`. It is critical to note that remote employees must not retain offline copies of documents beyond their active use period. 

## 6. Physical Security and Workspace Environment
The remote workspace must be conducive to professional work and maintain the confidentiality of enterprise information.

### 6.1 Workspace Standards
- The workspace should ideally be a dedicated room with a closable door to prevent unauthorized viewing of sensitive information by household members or guests.
- When handling classified calls or video conferences, employees must ensure conversations cannot be overheard. The use of noise-canceling headsets is highly recommended.
- "Clean Desk" policies apply to remote workspaces. Any physical documents containing sensitive information must be securely locked away when not in use and shredded using a cross-cut shredder prior to disposal.

## 7. Disciplinary Action and Escalation Protocols
Failure to adhere to this Remote Work Policy constitutes a breach of the employment contract and will result in disciplinary action.

### 7.1 Progressive Discipline
Violations will generally follow a progressive disciplinary model:
1. **Verbal Warning:** Issued for minor infractions, such as failing to connect to the VPN for a brief period.
2. **Written Reprimand:** Issued for repeated minor infractions or a moderate security lapse, such as using an unsecured public Wi-Fi network.
3. **Suspension of Remote Privileges:** The employee is mandated to return to the on-site office pending a formal review.

### 7.2 Level 4 Escalation (HR Disciplinary Action)
A **Level 4 Escalation** represents a severe HR disciplinary action triggered by gross misconduct or critical security violations within the remote work context. Note that this term differs in meaning from other departmental policies (e.g., in `aml_internal_fraud_sop.md`, Level 4 Escalation refers to financial fraud triggers).
Triggers for a Level 4 HR Escalation include:
- Willful circumvention of EDR or VPN software.
- Unauthorized relocation to a sanctioned country or region without prior tax and legal approval.
- Severe data exfiltration attempts.
- Using corporate devices for illegal activities.
A Level 4 Escalation typically results in immediate suspension pending an investigation that may culminate in termination of employment.

## 8. Incident Reporting and Escalation Contacts
In the event of a security incident, lost hardware, or critical compliance failure, remote employees must immediately initiate the escalation workflow.

### 8.1 Reporting Matrix

| Incident Type | Initial Contact Point | Required Action | Time-to-Report SLA |
| :--- | :--- | :--- | :--- |
| Lost/Stolen Laptop | IT Helpdesk (Option 1) | Call the emergency IT hotline to initiate remote wipe. | Within 2 hours of discovery |
| Suspected Phishing/Malware | Security Operations Center (SOC) | Forward email to `phishing@enterprise.internal` and disconnect from VPN. | Immediate |
| Physical Breach of Workspace | Direct Manager & HR | Report the extent of physical documents compromised. | Within 12 hours |
| Severe Network Outage | Direct Manager | Update status via mobile device if corporate laptop is offline. | Within 4 hours |

### 8.2 Contact Directory
- **IT Global Helpdesk:** 1-800-555-0199 or `helpdesk-urgent@enterprise.internal`
- **Security Operations Center (SOC):** 1-800-555-0200 or `soc-triage@enterprise.internal`
- **Global HR Compliance:** `hr-compliance@enterprise.internal`

## 9. Policy Acknowledgement
By logging into the enterprise VPN from a remote location, the employee acknowledges that they have read, understood, and agreed to be bound by the terms set forth in this HR Remote Work Policy. This document is subject to annual review and may be amended at the discretion of the enterprise leadership.
