-- Seed anti-fraud rules with test_query and trigger_keywords
-- Run with: docker exec expert-agent-db psql -U hybrid -d hybrid_db -f /tmp/seed_rules.sql

DO $$
DECLARE
    v_domain_id TEXT;
    v_intent_txn INT;
    v_intent_str INT;
    v_intent_fraud INT;
BEGIN
    -- Get domain ID
    SELECT id INTO v_domain_id FROM domains 
    WHERE LOWER(name) LIKE '%anti%fraud%' OR LOWER(name) LIKE '%anti%' 
    ORDER BY created_at LIMIT 1;
    
    IF v_domain_id IS NULL THEN
        SELECT id INTO v_domain_id FROM domains ORDER BY created_at LIMIT 1;
    END IF;

    RAISE NOTICE 'Using domain_id: %', v_domain_id;

    -- Upsert intents
    INSERT INTO intents (domain_id, name, description, risk_level, requires_approval, audit_level, priority, keywords, verbs, confidence_boost)
    VALUES (v_domain_id, 'AML_TransactionMonitoring', 'Monitoring transactions for fraud and laundering', 'high', TRUE, 'comprehensive', 9,
            '["deposit","transfer","transaction","cash","international","structuring"]'::jsonb,
            '["monitor","report","flag","check","verify"]'::jsonb, 0.2)
    ON CONFLICT (id) DO NOTHING;
    SELECT id INTO v_intent_txn FROM intents WHERE name = 'AML_TransactionMonitoring';

    INSERT INTO intents (domain_id, name, description, risk_level, requires_approval, audit_level, priority, keywords, verbs, confidence_boost)
    VALUES (v_domain_id, 'AML_STR_Submission', 'Suspicious Transaction Report procedure', 'critical', TRUE, 'full', 10,
            '["STR","report","regulator","procedure","portal","freeze"]'::jsonb,
            '["submit","gather","document","attach"]'::jsonb, 0.25)
    ON CONFLICT (id) DO NOTHING;
    SELECT id INTO v_intent_str FROM intents WHERE name = 'AML_STR_Submission';

    INSERT INTO intents (domain_id, name, description, risk_level, requires_approval, audit_level, priority, keywords, verbs, confidence_boost)
    VALUES (v_domain_id, 'AML_InternalFraud', 'Monitoring internal misconduct', 'critical', TRUE, 'full', 10,
            '["employee","misconduct","hr","criminal","suspension","audit"]'::jsonb,
            '["investigate","suspend","complain"]'::jsonb, 0.2)
    ON CONFLICT (id) DO NOTHING;
    SELECT id INTO v_intent_fraud FROM intents WHERE name = 'AML_InternalFraud';

    RAISE NOTICE 'Intent IDs: txn=%, str=%, fraud=%', v_intent_txn, v_intent_str, v_intent_fraud;

    -- Insert/Update rules
    INSERT INTO rules (domain_id, name, description, intent_id, condition, action, priority, required_roles, active, test_query, trigger_keywords)
    VALUES (
        v_domain_id, 'RULE_A1_CashDeposits',
        'Flag cash deposits > 3x monthly average or > 1M DZD',
        v_intent_txn,
        '["cash deposits","deposits > 1,000,000"]'::jsonb,
        '{"alert_level":1,"message":"Flag Level 1 alert for branch review."}'::jsonb,
        10, '["employee","admin"]'::jsonb, TRUE,
        'I want to report a large cash deposit of 2 million DZD',
        '["cash deposit","large deposit","1M DZD"]'::jsonb
    ) ON CONFLICT DO NOTHING;
    UPDATE rules SET test_query='I want to report a large cash deposit of 2 million DZD', trigger_keywords='["cash deposit","large deposit","1M DZD"]'::jsonb WHERE name='RULE_A1_CashDeposits';

    INSERT INTO rules (domain_id, name, description, intent_id, condition, action, priority, required_roles, active, test_query, trigger_keywords)
    VALUES (
        v_domain_id, 'RULE_B2_InternationalTransfer',
        'Flag transfers > 5M DZD to high-risk jurisdictions',
        v_intent_txn,
        '["international transfer","foreign transfer"]'::jsonb,
        '{"alert_level":2,"message":"Level 2 alert: Compliance review required."}'::jsonb,
        10, '["employee","admin"]'::jsonb, TRUE,
        'How do I process an international transfer to a high risk country?',
        '["international transfer","foreign transfer","high-risk jurisdiction"]'::jsonb
    ) ON CONFLICT DO NOTHING;
    UPDATE rules SET test_query='How do I process an international transfer to a high risk country?', trigger_keywords='["international transfer","foreign transfer","high-risk jurisdiction"]'::jsonb WHERE name='RULE_B2_InternationalTransfer';

    INSERT INTO rules (domain_id, name, description, intent_id, condition, action, priority, required_roles, active, test_query, trigger_keywords)
    VALUES (
        v_domain_id, 'RULE_C3_DormantAccount',
        'Flag dormant account > 12m with sudden inflow > 2M DZD',
        v_intent_txn,
        '["dormant","sudden inflow"]'::jsonb,
        '{"action":"escalate","message":"Escalate to Financial Crime Unit (Level 3)."}'::jsonb,
        9, '["employee","admin"]'::jsonb, TRUE,
        'What happens if a dormant account suddenly receives a lot of money?',
        '["dormant account","sudden inflow","reactivated account"]'::jsonb
    ) ON CONFLICT DO NOTHING;
    UPDATE rules SET test_query='What happens if a dormant account suddenly receives a lot of money?', trigger_keywords='["dormant account","sudden inflow","reactivated account"]'::jsonb WHERE name='RULE_C3_DormantAccount';

    INSERT INTO rules (domain_id, name, description, intent_id, condition, action, priority, required_roles, active, test_query, trigger_keywords)
    VALUES (
        v_domain_id, 'RULE_STR_Procedure',
        'Suspicious Transaction Report mandatory submission flow',
        v_intent_str,
        '["STR","report submission"]'::jsonb,
        '{"steps":["Gather logs","Document rationale","Submit to portal"],"message":"Following Section 5 procedure."}'::jsonb,
        10, '["admin"]'::jsonb, TRUE,
        'How do I submit an STR report?',
        '["submit STR","STR report","suspicious transaction report"]'::jsonb
    ) ON CONFLICT DO NOTHING;
    UPDATE rules SET test_query='How do I submit an STR report?', trigger_keywords='["submit STR","STR report","suspicious transaction report"]'::jsonb WHERE name='RULE_STR_Procedure';

    INSERT INTO rules (domain_id, name, description, intent_id, condition, action, priority, required_roles, active, test_query, trigger_keywords)
    VALUES (
        v_domain_id, 'RULE_AML_InternalFraud',
        'Immediate suspension for employee misconduct',
        v_intent_fraud,
        '["employee misconduct","internal fraud"]'::jsonb,
        '{"action":"suspend","message":"Immediate system suspension and HR disciplinary action triggered."}'::jsonb,
        10, '["admin"]'::jsonb, TRUE,
        'What are the consequences of employee misconduct?',
        '["internal fraud","employee misconduct","disciplinary action"]'::jsonb
    ) ON CONFLICT DO NOTHING;
    UPDATE rules SET test_query='What are the consequences of employee misconduct?', trigger_keywords='["internal fraud","employee misconduct","disciplinary action"]'::jsonb WHERE name='RULE_AML_InternalFraud';

    INSERT INTO rules (domain_id, name, description, intent_id, condition, action, priority, required_roles, active, test_query, trigger_keywords)
    VALUES (
        v_domain_id, 'Audit all Critical Security Actions',
        'Ensures all security actions are logged',
        v_intent_fraud,
        '["Security","AccessChange"]'::jsonb,
        '{"log":true,"audit":true,"message":"Critical security action captured in audit trail."}'::jsonb,
        10, '[]'::jsonb, TRUE,
        'How is security access changed and audited?',
        '["security audit","access change","critical action"]'::jsonb
    ) ON CONFLICT DO NOTHING;
    UPDATE rules SET test_query='How is security access changed and audited?', trigger_keywords='["security audit","access change","critical action"]'::jsonb WHERE name='Audit all Critical Security Actions';

    RAISE NOTICE 'All rules seeded successfully!';
END $$;

-- Verify
SELECT name, test_query, trigger_keywords FROM rules ORDER BY priority DESC;
