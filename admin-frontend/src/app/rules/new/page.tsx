"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import Select, { MultiValue } from 'react-select';
import CreatableSelect from 'react-select/creatable';


interface SelectOption {
    value: string;
    label: string;
}

const customStyles = {
    control: (provided: any) => ({
        ...provided,
        backgroundColor: 'transparent',
        borderColor: 'hsl(var(--border))',
        borderRadius: '0.5rem',
    }),
    menu: (provided: any) => ({
        ...provided,
        backgroundColor: 'hsl(var(--background))',
        borderColor: 'hsl(var(--border))',
        borderWidth: '1px',
        zIndex: 50
    }),
    option: (provided: any, state: any) => ({
        ...provided,
        backgroundColor: state.isFocused ? 'hsl(var(--muted))' : 'transparent',
        cursor: 'pointer',
    }),
    multiValue: (provided: any) => ({
        ...provided,
        backgroundColor: 'hsl(var(--muted))',
        borderRadius: '0.25rem',
    }),
    multiValueLabel: (provided: any) => ({
        ...provided,
        color: 'inherit',
    }),
    multiValueRemove: (provided: any) => ({
        ...provided,
        ':hover': {
            backgroundColor: 'hsl(var(--destructive))',
            color: 'white',
        },
    }),
    singleValue: (provided: any) => ({
        ...provided,
        color: 'inherit',
    }),
    input: (provided: any) => ({
        ...provided,
        color: 'inherit',
    })
};

export default function NewRulePage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [intents, setIntents] = useState<any[]>([]);
    const [roles, setRoles] = useState<any[]>([]);
    const [documents, setDocuments] = useState<any[]>([]);

    const [formData, setFormData] = useState({
        name: "",
        intent: "",
        action_message: "",
        action_required_docs: [] as string[],
        action_forbidden_docs: [] as string[],
        priority: 5,
        required_roles: ["employee"],
        condition_intents: [] as string[],
        trigger_keywords: "",
        test_query: "",
        description: ""
    });

    useEffect(() => {
        loadIntents();
    }, []);

    const loadIntents = async () => {
        try {
            const [intentsData, rolesData, docsData] = await Promise.all([
                api.intents.getAll(),
                api.roles.getAll().catch(() => [{ id: 1, name: "admin" }, { id: 2, name: "employee" }, { id: 3, name: "guest" }]),
                api.documents.getAll().catch(() => []) // fallback
            ]);
            setIntents(Array.isArray(intentsData) ? intentsData : intentsData.data || []);
            setRoles(Array.isArray(rolesData) ? rolesData : rolesData.data || []);
            setDocuments(Array.isArray(docsData) ? docsData : docsData.data || []);
        } catch (error) {
            console.error("Failed to load form data:", error);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const value = e.target.type === "number" ? parseInt(e.target.value) : e.target.value;
        setFormData({ ...formData, [e.target.name]: value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const actionPayload: any = {};
            if (formData.action_message) actionPayload.message = formData.action_message;
            if (formData.action_required_docs.length > 0) {
                actionPayload.required_docs = formData.action_required_docs;
            }
            if (formData.action_forbidden_docs.length > 0) {
                actionPayload.forbidden_docs = formData.action_forbidden_docs;
            }

            const keywordsArray = formData.trigger_keywords.split(",").map((k: string) => k.trim()).filter(Boolean);

            await api.rules.create({
                name: formData.name,
                intent: formData.intent,
                action: actionPayload,
                priority: formData.priority,
                required_roles: formData.required_roles,
                triggers: formData.condition_intents,
                test_query: formData.test_query,
                trigger_keywords: keywordsArray,
                description: formData.description
            });

            router.push("/rules");
        } catch (err: any) {
            console.error("Failed to create rule:", err);
            setError(err.message || "Failed to create rule");
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="flex items-center gap-4 mb-8">
                <Link href="/rules" className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                    <ArrowLeft className="w-5 h-5 text-muted-foreground" />
                </Link>
                <div>
                    <h1 className="text-3xl font-bold">Create New Rule</h1>
                    <p className="text-muted-foreground mt-1">Define a new production rule for the Hybrid Core</p>
                </div>
            </div>

            {error && (
                <div className="bg-destructive/20 text-destructive border border-destructive/50 p-4 rounded-lg">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6 bg-card border border-border rounded-lg p-6">
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">Rule Name</label>
                        <input
                            type="text"
                            name="name"
                            required
                            value={formData.name}
                            onChange={handleChange}
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="e.g. AML Monitoring Rule"
                        />
                        <p className="text-xs text-muted-foreground mt-1">A human-readable name (ID is auto-generated).</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">Description</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary h-20 resize-none"
                            placeholder="Describe what this rule does..."
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">Target Intent</label>
                        <CreatableSelect
                            value={formData.intent ? { value: formData.intent, label: formData.intent } : null}
                            onChange={(option) => setFormData({ ...formData, intent: option ? option.value : "" })}
                            options={intents.map(i => ({ value: i.name, label: `${i.name} (${i.risk_level})` }))}
                            placeholder="Select or type a new intent..."
                            isSearchable
                            isClearable
                            formatCreateLabel={(inputValue) => `➕ Create intent "${inputValue}"`}
                            styles={customStyles}
                            className="text-sm font-medium text-foreground"
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                            Select an existing intent or type a new name to define one on the fly.
                        </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Priority</label>
                            <input
                                type="number"
                                name="priority"
                                required
                                min={1}
                                max={10}
                                value={formData.priority}
                                onChange={handleChange}
                                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Required Roles</label>
                            <Select
                                value={formData.required_roles.map(r => ({ value: r, label: r }))}
                                onChange={(options) => setFormData({
                                    ...formData,
                                    required_roles: (options as MultiValue<SelectOption>).map(o => o.value)
                                })}
                                options={roles.map(r => ({ value: r.name, label: r.name }))}
                                placeholder="Select roles..."
                                isSearchable
                                isMulti
                                closeMenuOnSelect={false}
                                styles={customStyles}
                                className="text-sm font-medium text-foreground"
                            />
                        </div>
                    </div>

                    <div className="space-y-4 border border-border p-4 rounded-lg bg-black/20">
                        <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">Triggers & Testing</h3>
                        <div>
                            <label className="block text-sm font-medium mb-1">Target Intents (Triggers)</label>
                            <CreatableSelect
                                value={formData.condition_intents.map(i => ({ value: i, label: i }))}
                                onChange={(options) => setFormData({
                                    ...formData,
                                    condition_intents: (options as MultiValue<SelectOption>).map(o => o.value)
                                })}
                                options={intents.map(i => ({ value: i.name, label: `${i.name} (${i.risk_level})` }))}
                                placeholder="Select or type intents..."
                                isSearchable
                                isMulti
                                closeMenuOnSelect={false}
                                formatCreateLabel={(inputValue) => `➕ Add "${inputValue}"`}
                                styles={customStyles}
                                className="text-sm font-medium text-foreground"
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                                Pick from the list or type a new intent name and press Enter.
                            </p>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Trigger Keywords</label>
                            <input
                                type="text"
                                name="trigger_keywords"
                                value={formData.trigger_keywords}
                                onChange={handleChange}
                                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="e.g. cash deposit, 1M DZD, unusual activities"
                            />
                            <p className="text-xs text-muted-foreground mt-1">Comma-separated exact keywords to bypass NLP and trigger instantly.</p>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Test Query</label>
                            <input
                                type="text"
                                name="test_query"
                                value={formData.test_query}
                                onChange={handleChange}
                                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="e.g. I want to report a huge cash deposit"
                            />
                            <p className="text-xs text-muted-foreground mt-1">A sample query used in the Rule Simulator.</p>
                        </div>
                    </div>

                    <div className="space-y-4 border border-border p-4 rounded-lg bg-black/20">
                        <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">Rule Action</h3>
                        <div>
                            <label className="block text-sm font-medium mb-1">Action Message</label>
                            <input
                                type="text"
                                name="action_message"
                                value={formData.action_message}
                                onChange={handleChange}
                                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="e.g. Large cash deposit detected."
                            />
                            <p className="text-xs text-muted-foreground mt-1">The message logged or shown to the user.</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-1 text-green-400">Required Documents</label>
                                <Select
                                    value={formData.action_required_docs.map(i => ({ value: i, label: i }))}
                                    onChange={(options) => setFormData({
                                        ...formData,
                                        action_required_docs: (options as MultiValue<SelectOption>).map(o => o.value)
                                    })}
                                    options={documents.map(d => ({ value: d.title, label: d.title }))}
                                    placeholder="Select required documents..."
                                    isSearchable
                                    isMulti
                                    closeMenuOnSelect={false}
                                    styles={customStyles}
                                    className="text-sm font-medium text-foreground"
                                    noOptionsMessage={() => "No documents available"}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1 text-red-400">Forbidden Documents</label>
                                <Select
                                    value={formData.action_forbidden_docs.map(i => ({ value: i, label: i }))}
                                    onChange={(options) => setFormData({
                                        ...formData,
                                        action_forbidden_docs: (options as MultiValue<SelectOption>).map(o => o.value)
                                    })}
                                    options={documents.map(d => ({ value: d.title, label: d.title }))}
                                    placeholder="Select forbidden documents..."
                                    isSearchable
                                    isMulti
                                    closeMenuOnSelect={false}
                                    styles={customStyles}
                                    className="text-sm font-medium text-foreground"
                                    noOptionsMessage={() => "No documents available"}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="pt-4 border-t border-border flex justify-end gap-4">
                    <Link
                        href="/rules"
                        className="px-4 py-2 hover:bg-white/5 rounded-lg transition-colors text-muted-foreground"
                    >
                        Cancel
                    </Link>
                    <button
                        type="submit"
                        disabled={loading}
                        className="flex items-center gap-2 px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                    >
                        {loading ? "Saving..." : "Save Rule"}
                        {!loading && <Save className="w-4 h-4" />}
                    </button>
                </div>
            </form>
        </div>
    );
}
