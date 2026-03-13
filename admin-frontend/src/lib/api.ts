/**
 * API Client for LxGuard.AI Admin UI
 * Comprehensive client with all admin endpoints
 */

import axios from "axios";
import { getMockResponse } from "./mock-api";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "dev-key-12345";
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";

// Helper function for admin API calls
const adminFetch = async (endpoint: string, options: RequestInit = {}) => {
    // Use mock API if enabled
    if (USE_MOCK) {
        console.log(`[MOCK API] ${endpoint}`);
        return getMockResponse(endpoint);
    }

    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    const headers: Record<string, string> = {
        "Authorization": token ? `Bearer ${token}` : "",
    };

    // Don't set Content-Type for FormData (browser does it with boundary)
    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            ...headers,
            ...options.headers,
        },
    });

    if (response.status === 401 && typeof window !== 'undefined' && endpoint !== '/auth/login') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        throw new Error("Session expired. Please login again.");
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: response.statusText }));
        throw new Error(error.message || `API Error: ${response.statusText}`);
    }

    return response.json();
}

export const api = {
    // ============================================================================
    // Rules API
    // ============================================================================
    rules: {
        getAll: () => adminFetch("/admin/rules"),
        get: (id: string) => adminFetch(`/admin/rules/${id}`),
        create: (rule: any) => adminFetch("/admin/rules", {
            method: "POST",
            body: JSON.stringify(rule),
        }),
        update: (id: string, rule: any) => adminFetch(`/admin/rules/${id}`, {
            method: "PUT",
            body: JSON.stringify(rule),
        }),
        delete: (id: string) => adminFetch(`/admin/rules/${id}`, {
            method: "DELETE",
        }),
        toggleStatus: (id: string, active: boolean) => adminFetch(`/admin/rules/${id}/status`, {
            method: "PATCH",
            body: JSON.stringify({ active }),
        }),
        test: (id: string, query: string, userRole: string) => adminFetch(`/admin/rules/${id}/test`, {
            method: "POST",
            body: JSON.stringify({ query, user_role: userRole }),
        }),
    },

    // ============================================================================
    // Intents API
    // ============================================================================
    intents: {
        getAll: () => adminFetch("/admin/intents"),
        get: (name: string) => adminFetch(`/admin/intents/${name}`),
    },

    // ============================================================================
    // Documents API
    // ============================================================================
    documents: {
        getAll: () => adminFetch("/admin/documents"),
        get: (id: number) => adminFetch(`/admin/documents/${id}`),
        upload: (formData: FormData) => adminFetch("/admin/documents/upload", {
            method: "POST",
            body: formData,
        }),
        delete: (id: number) => adminFetch(`/admin/documents/${id}`, {
            method: "DELETE",
        }),
        reindex: (id: number) => adminFetch(`/admin/documents/${id}/reindex`, {
            method: "POST",
        }),
        update: (id: string | number, data: any) => adminFetch(`/admin/documents/${id}`, {
            method: "PUT",
            body: JSON.stringify(data),
        }),
    },

    // ============================================================================
    // Users API
    // ============================================================================
    users: {
        getAll: () => adminFetch("/admin/users"),
        get: (id: string) => adminFetch(`/admin/users/${id}`),
        create: (user: any) => adminFetch("/admin/users", {
            method: "POST",
            body: JSON.stringify(user),
        }),
        update: (id: string, user: any) => adminFetch(`/admin/users/${id}`, {
            method: "PUT",
            body: JSON.stringify(user),
        }),
        delete: (id: string) => adminFetch(`/admin/users/${id}`, {
            method: "DELETE",
        }),
    },

    // ============================================================================
    // Roles API
    // ============================================================================
    roles: {
        getAll: () => adminFetch("/admin/roles"),
    },

    // ============================================================================
    // Audit Logs API
    // ============================================================================
    audit: {
        getLogs: (params?: any) => adminFetch("/admin/audit/logs?" + new URLSearchParams(params)),
        getTrace: (traceId: string) => adminFetch(`/admin/audit/logs/${traceId}/trace`),
        export: async (params?: any) => {
            const response = await fetch(`${API_URL}/admin/audit/export`, {
                method: "POST",
                headers: {
                    "X-API-Key": API_KEY,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(params),
            });
            return response.blob();
        },
    },

    // ============================================================================
    // Knowledge Base API
    // ============================================================================
    knowledge: {
        getGraph: () => adminFetch("/admin/knowledge/graph"),
        manageTriple: (data: {
            subject: string;
            predicate: string;
            object: string;
            action: "approve" | "reject";
            subject_uri?: string;
            predicate_uri?: string;
            object_uri?: string;
        }) =>
            adminFetch("/admin/knowledge/manage", {
                method: "POST",
                body: JSON.stringify(data),
            }),
    },

    // ============================================================================
    // Database API
    // ============================================================================
    database: {
        getTables: () => adminFetch("/admin/db/tables"),
        queryTable: (tableName: string, params?: { limit?: number; offset?: number; orderBy?: string; orderDir?: "ASC" | "DESC" }) => {
            const queryParams = new URLSearchParams();
            if (params?.limit) queryParams.append("limit", params.limit.toString());
            if (params?.offset) queryParams.append("offset", params.offset.toString());
            if (params?.orderBy) queryParams.append("order_by", params.orderBy);
            if (params?.orderDir) queryParams.append("order_dir", params.orderDir);
            return adminFetch(`/admin/db/query/${tableName}?${queryParams.toString()}`);
        },
    },

    // ============================================================================
    // Cache API
    // ============================================================================
    cache: {
        getStats: () => adminFetch("/admin/cache/stats"),
        clear: (pattern?: string) => adminFetch("/admin/cache/clear", {
            method: "POST",
            body: JSON.stringify({ pattern }),
        }),
        invalidateRules: () => adminFetch("/admin/cache/invalidate/rules", {
            method: "POST",
        }),
        invalidateUser: (userId: string) => adminFetch("/admin/cache/invalidate/user", {
            method: "POST",
            body: JSON.stringify({ user_id: userId }),
        }),
    },

    // ============================================================================
    // Configuration API
    // ============================================================================
    settings: {
        get: () => adminFetch("/admin/settings"),
        update: (settings: any) => adminFetch("/admin/settings", {
            method: "PUT",
            body: JSON.stringify(settings),
        }),
    },

    // ============================================================================
    // Query Simulator API
    // ============================================================================
    simulator: {
        testQuery: (query: string, userRole: string, targetLanguage?: string) => adminFetch("/admin/test/query", {
            method: "POST",
            body: JSON.stringify({ query, user_role: userRole, target_language: targetLanguage }),
        }),
    },

    // ============================================================================
    // Analytics API
    // ============================================================================
    analytics: {
        getIntents: (range?: string) => adminFetch(`/admin/analytics/intents?range=${range || '7d'}`),
        getDocuments: (range?: string) => adminFetch(`/admin/analytics/documents?range=${range || '7d'}`),
        getUsers: (range?: string) => adminFetch(`/admin/analytics/users?range=${range || '7d'}`),
    },

    // ============================================================================
    // Monitoring API
    // ============================================================================
    monitoring: {
        getHealth: () => adminFetch("/admin/health"),
        getMetrics: () => adminFetch("/admin/metrics"),
    },

    // Legacy endpoints (for backward compatibility)
    getStats: () => adminFetch("/admin/stats"),
    getRules: () => adminFetch("/admin/rules"),
    createRule: (rule: any) => adminFetch("/admin/rules", {
        method: "POST",
        body: JSON.stringify(rule),
    }),
    deleteRule: (id: string) => adminFetch(`/admin/rules/${id}`, {
        method: "DELETE",
    }),
    simulateQuery: (query: string, role: string, intent: string) => adminFetch("/admin/simulate", {
        method: "POST",
        body: JSON.stringify({ query, user_role: role, intent_override: intent }),
    }),
    getLogs: () => adminFetch("/admin/logs"),
    getKnowledge: () => adminFetch("/admin/knowledge"),

    // ============================================================================
    // Auth API
    // ============================================================================
    auth: {
        login: (credentials: FormData) => {
            const params = new URLSearchParams();
            credentials.forEach((value, key) => {
                params.append(key, value.toString());
            });
            return fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: params,
            }).then(res => {
                if (!res.ok) return res.json().then(err => { throw new Error(err.detail || "Login failed") });
                return res.json();
            });
        },
        me: () => adminFetch("/auth/me"),
        logout: () => adminFetch("/auth/logout", { method: "POST" }),
    }
};

// Export both 'api' and 'adminApi' for compatibility
export const adminApi = api;
export default api;
