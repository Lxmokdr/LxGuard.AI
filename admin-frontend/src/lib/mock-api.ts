// Mock API responses for development/testing without backend

export const mockResponses: Record<string, any> = {
    "/admin/stats": {
        total_rules: 12,
        active_rules: 8,
        total_documents: 45,
        total_users: 23,
        total_queries: 1547,
        avg_response_time: "245ms",
        cache_hit_rate: "87.3%",
        error_rate: "0.12%",
    },
    "/admin/rules": {
        data: [
            {
                id: "rule_deployment_docs",
                description: "Require deployment documentation for deployment queries",
                triggers: ["deployment", "deploy", "release"],
                allowed_roles: ["admin", "developer"],
                priority: 10,
                active: true,
                action: {
                    required_docs: ["deployment.md", "infrastructure.md"],
                    forbidden_docs: [],
                    topic: "deployment",
                },
            },
            {
                id: "rule_security_restricted",
                description: "Restrict security-related queries to admin only",
                triggers: ["security", "auth", "credentials"],
                allowed_roles: ["admin"],
                priority: 20,
                active: true,
                action: {
                    required_docs: ["security.md"],
                    forbidden_docs: ["public_docs"],
                    topic: "security",
                },
            },
            {
                id: "rule_general_access",
                description: "Allow general documentation access for all users",
                triggers: ["help", "docs", "guide"],
                allowed_roles: ["admin", "employee", "developer", "guest"],
                priority: 5,
                active: true,
                action: {
                    required_docs: [],
                    forbidden_docs: [],
                    topic: "general",
                },
            },
        ],
    },
    "/admin/documents": {
        data: [
            {
                id: 1,
                title: "deployment.md",
                scope: "internal",
                access_level: "employee",
                version: "1.2",
                chunk_count: 45,
                vector_count: 45,
                created_at: "2024-01-15T10:30:00Z",
            },
            {
                id: 2,
                title: "security.md",
                scope: "restricted",
                access_level: "admin",
                version: "2.0",
                chunk_count: 32,
                vector_count: 32,
                created_at: "2024-01-20T14:20:00Z",
            },
            {
                id: 3,
                title: "api-guide.md",
                scope: "public",
                access_level: "all",
                version: "1.0",
                chunk_count: 28,
                vector_count: 28,
                created_at: "2024-02-01T09:15:00Z",
            },
        ],
    },
    "/admin/users": {
        data: [
            {
                id: "user_1",
                username: "admin",
                email: "admin@company.com",
                role: "admin",
                is_active: true,
                created_at: "2024-01-01T00:00:00Z",
            },
            {
                id: "user_2",
                username: "john.dev",
                email: "john@company.com",
                role: "developer",
                is_active: true,
                created_at: "2024-01-15T10:00:00Z",
            },
            {
                id: "user_3",
                username: "jane.employee",
                email: "jane@company.com",
                role: "employee",
                is_active: true,
                created_at: "2024-02-01T08:30:00Z",
            },
        ],
    },
    "/admin/audit/logs": {
        data: {
            items: [
                {
                    id: "log_1",
                    timestamp: "2024-02-14T22:45:00Z",
                    username: "john.dev",
                    user_role: "developer",
                    query: "How do I deploy to production?",
                    intent: "deployment",
                    decision: "approved",
                    trace_id: "trace_abc123",
                    security_check: {
                        risk_level: "low",
                        allowed: true,
                    },
                    performance: {
                        total_time_ms: 245,
                    },
                },
                {
                    id: "log_2",
                    timestamp: "2024-02-14T22:30:00Z",
                    username: "guest_user",
                    user_role: "guest",
                    query: "Show me security credentials",
                    intent: "security",
                    decision: "rejected",
                    trace_id: "trace_def456",
                    security_check: {
                        risk_level: "high",
                        allowed: false,
                    },
                    performance: {
                        total_time_ms: 120,
                    },
                },
            ],
            total: 2,
        },
    },
    "/admin/health": {
        data: {
            postgres: { status: "online", latency_ms: 12 },
            redis: { status: "online", latency_ms: 5 },
            ollama: { status: "online", latency_ms: 150 },
            keycloak: { status: "online", latency_ms: 45 },
        },
    },
    "/admin/metrics": {
        data: {
            queries_per_minute: 12.5,
            avg_response_time_ms: 245,
            cache_hit_rate: 0.873,
            error_rate: 0.0012,
            database_size_mb: 1024,
            cache_memory_mb: 256,
            active_users: 8,
        },
    },
};

export function getMockResponse(endpoint: string): any {
    // Remove query parameters
    const cleanEndpoint = endpoint.split("?")[0];

    if (mockResponses[cleanEndpoint]) {
        return Promise.resolve(mockResponses[cleanEndpoint]);
    }

    // Handle dynamic endpoints
    if (cleanEndpoint.includes("/trace")) {
        return Promise.resolve({
            data: {
                layers: [
                    { name: "NLP Analysis", result: "Intent: deployment" },
                    { name: "Intent Arbitration", result: "Selected: deployment" },
                    { name: "Retrieval", result: "Found 3 documents" },
                    { name: "Answer Planning", result: "Plan created" },
                    { name: "Documents", result: "deployment.md, infrastructure.md" },
                    { name: "Generation", result: "Answer generated" },
                    { name: "Validation", result: "Passed" },
                    { name: "Explainability", result: "Trace complete" },
                ],
            },
        });
    }

    // Default empty response
    console.warn(`[MOCK API] No mock response defined for ${endpoint}. Returning empty array.`);
    return Promise.resolve({ data: [] });
}
