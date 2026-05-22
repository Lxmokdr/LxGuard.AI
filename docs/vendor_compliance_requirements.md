# VEN-COMP-44: Third-Party Vendor Security and Compliance Requirements
**Document ID:** VEN-COMP-44-2025
**Effective Date:** April 1, 2025
**Department:** Vendor Risk Management (VRM)
**Document Owner:** Chief Procurement Officer & CISO
**Applies To:** All Third-Party Vendors, Contractors, and Managed Service Providers

## 1. Introduction and Scope
The enterprise relies heavily on third-party vendors to deliver critical services. However, supply chain vulnerabilities represent a significant risk vector for data breaches and regulatory non-compliance. This document establishes the mandatory security postures, access controls, and audit obligations required of all external entities interacting with our network, data, or physical premises.

This policy applies to all vendors, contractors, and Managed Service Providers (MSPs), collectively referred to as "Third Parties." Internal procurement teams must enforce these requirements during the onboarding process and throughout the vendor lifecycle.

## 2. Vendor Onboarding and Risk Assessment
Before any contract is signed or access is granted, a prospective vendor must undergo a rigorous security evaluation.

### 2.1 Vendor Tiering
Vendors are categorized into three risk tiers based on their level of access to enterprise assets:
- **Tier 1 (High Risk):** Vendors with direct API access, persistent VPN access to the internal network, or those who host highly classified enterprise data (e.g., Payroll providers, Cloud infrastructure providers).
- **Tier 2 (Moderate Risk):** Vendors providing software-as-a-service (SaaS) solutions without direct network integration, or physical security contractors.
- **Tier 3 (Low Risk):** Vendors providing generic, non-technical services (e.g., catering, office supplies) with no digital access.

### 2.2 Security Questionnaires and Compliance Scoring
Tier 1 and Tier 2 vendors must complete the standard Information Security Questionnaire (ISQ-V2). The VRM team utilizes these responses to generate a "Compliance Score." A score below 85/100 results in immediate disqualification unless a C-level exemption is granted.

## 3. Third-Party Access Controls
Vendors require distinct, highly monitored access pathways that are segregated from standard employee access.

### 3.1 Network Access and VPN
- Vendors must connect via a dedicated "Vendor-VPN" gateway, which heavily restricts lateral movement.
- Split tunneling is strictly disabled.
- Multi-Factor Authentication (MFA) is mandatory for all vendor accounts.
- Access is granted on a "Least Privilege" basis. A vendor must only have access to the specific servers or databases required to fulfill their contract.

### 3.2 Account Lifecycle
Vendor accounts are intrinsically tied to contract expiration dates.
- All vendor accounts automatically expire 30 days prior to the contract end date unless a renewal is processed.
- "Orphaned" vendor accounts (accounts unused for 45 days) are automatically disabled and flagged for review.

## 4. Software Development and AI Usage Restrictions
For third-party contractors providing software engineering, coding, or development services, strict technological boundaries are enforced.

### 4.1 Prohibition of Third-Party Code Generation
> [!WARNING]
> **Strict AI Prohibition (Contradiction Check):** In direct contradiction to internal employee policies (which may permit Level 3 AI tools under the `enterprise_ai_usage_policy.md`), vendors and third-party contractors are **strictly prohibited from utilizing any third-party AI code generation tools (e.g., GitHub Copilot, ChatGPT, Claude) on restricted enterprise networks or while handling proprietary enterprise codebases.** 
> All code delivered by external contractors must be manually written or utilize explicitly pre-approved internal libraries. The introduction of externally generated AI code introduces unacceptable intellectual property contamination and zero-day vulnerability risks.

### 4.2 Secure Code Review
All code submitted by Tier 1 vendors must undergo automated static application security testing (SAST) and manual review by an internal Senior Engineer before being merged into the production branch.

## 5. Audit Obligations and Right to Audit
The enterprise maintains a comprehensive "Right to Audit" clause in all Tier 1 vendor contracts.

### 5.1 Annual Audits
Tier 1 vendors, such as our primary infrastructure partner **Synergy Systems**, are subject to mandatory annual on-site audits. These audits evaluate physical security, logical access controls, and data segregation practices.

### 5.2 SOC 2 Type II Reports
Cloud service providers must submit an updated SOC 2 Type II report annually. Failure to provide a clean report within 60 days of the request will result in the suspension of the contract.

## 6. Legacy System Exceptions: Project Titan
Certain legacy systems require specialized vendor support that cannot adhere to modern security protocols.

### 6.1 Project Titan Vendor Exemptions
The legacy mainframe, **Project Titan**, is maintained by a specialized consortium of retired engineers operating under a boutique consultancy. Due to the archaic nature of the mainframe's operating system, standard MFA and EDR agents cannot be deployed.
- **Exemption:** The vendors servicing Project Titan are granted an explicit exemption from Section 3.1 (MFA Mandate).
- **Mitigation:** Their access is routed through a dedicated jump-box server in an air-gapped VLAN, and every keystroke is recorded and reviewed weekly by the SOC.

## 7. Global Vendor Tracking and IDs
To maintain an accurate inventory of third-party risk, every vendor is assigned a unique Global ID.
- Example: The master service agreement governing our primary data center provider is tracked under **Global ID 99-X**. This ID must be referenced in all related archiving metadata and internal risk reports.


## Appendix A: Extended Regulatory Framework Alignments and Auditing Methodologies
To ensure comprehensive governance, this policy is strictly aligned with the global auditing methodologies established by the Enterprise Risk Management (ERM) steering committee. The methodologies contained within this framework are subject to continuous review and are mapped against the ISO 27001 Information Security Management System (ISMS) standards, the NIST Cybersecurity Framework (CSF), and the COBIT 2019 framework for enterprise IT governance. All operational directives described above must be periodically subjected to control effectiveness testing by the Internal Audit Division. Any discrepancies discovered during these localized audits will immediately trigger a formal risk acceptance review process.

The enterprise recognizes that operational resilience is intrinsically linked to regulatory adherence. Therefore, all local jurisdictions, including subsidiaries operating under the Synergy Systems global umbrella, are required to conform to the baseline standards articulated herein. Should local statutory requirements conflict with this enterprise-wide policy, the local compliance officer must submit a formal "Regulatory Deviation Request" to the Global Chief Compliance Officer. This request will undergo a rigorous multi-stage review involving the legal department, the enterprise risk management team, and relevant technical stakeholders. Until an explicit deviation is formally granted in writing, the baseline enterprise policy remains the ultimate authority and must be followed without exception.

Furthermore, the integration of these policies into the daily operational lifecycle is verified through automated compliance telemetry. The implementation of "compliance as code" ensures that deviations from the established baseline are instantly detected, flagged, and routed to the appropriate risk management dashboards. This automated oversight reduces the latency between a policy violation and its remediation, thereby minimizing the enterprise's exposure to regulatory fines, reputational damage, and operational disruption. It is the responsibility of every employee, contractor, and affiliated third party to actively participate in this culture of compliance and to promptly report any suspected vulnerabilities or violations through the established whistleblowing channels.

Periodic attestation of this policy is required for all personnel managing high-risk assets. This attestation serves as a legally binding acknowledgment that the employee has read, understood, and agreed to execute their duties in strict accordance with the stipulated rules. The Human Resources Information System (HRIS) will automatically track these attestations, and failure to complete the mandatory annual compliance modules will result in an automatic suspension of the employee's logical access privileges until the training is marked complete by the system administrator.

## Appendix B: Comprehensive Glossary of Terms
The following definitions apply to all terminologies utilized within this specific governance document, ensuring a standardized interpretation across all business units and international operational centers:
- **Baseline Security Posture:** The minimum required level of technical and administrative controls applied to a system or process to protect it from identified threats.
- **Control Effectiveness Testing:** The methodical evaluation of a security or procedural control to determine if it is operating as intended and adequately mitigating the target risk.
- **Data Custodian:** The individual or team responsible for the technical implementation of security controls, data storage, and access provisioning, acting on behalf of the Data Owner.
- **Enterprise Risk Management (ERM):** The strategic framework utilized by the organization to identify, assess, prioritize, and mitigate risks that could impact the achievement of strategic business objectives.
- **Risk Acceptance:** A formal, documented decision by an authorized executive to accept the residual risk associated with a specific vulnerability or non-compliant process, typically due to the prohibitive cost of remediation.
- **Operational Resilience:** The ability of the enterprise to anticipate, withstand, recover from, and adapt to adverse events, cyberattacks, or sudden market shifts without suffering catastrophic disruptions to critical services.
- **Compliance Telemetry:** Automated data streams generated by IT systems, applications, and network infrastructure that provide continuous visibility into the adherence to security policies and operational standards.
- **Regulatory Deviation:** A formally approved, temporary exception to a standard enterprise policy, granted strictly to accommodate conflicting local laws or unavoidable technical constraints in legacy environments.
- **Continuous Monitoring:** The ongoing observation and analysis of an information system's security controls to evaluate their effectiveness and identify emerging vulnerabilities in real-time.

By formalizing these definitions and integrating them directly into the policy framework, the enterprise eliminates ambiguity and provides clear, actionable guidance to all personnel tasked with upholding the organizational standards.
