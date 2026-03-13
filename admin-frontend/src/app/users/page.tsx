"use client";

import { useState, useEffect } from "react";
import { UserPlus, Search, Shield, UserX, Edit, Trash2, X, Save } from "lucide-react";
import { api } from "@/lib/api";
import type { User, UserRole } from "@/lib/types";

export default function UsersPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");

    // Modal state
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<"create" | "edit">("create");
    const [selectedUser, setSelectedUser] = useState<User | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
        role: "employee" as UserRole,
        is_active: true,
    });
    const [formError, setFormError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            const response = await api.users.getAll();
            // Handle both flat array and { data: [...] } format
            const userData = Array.isArray(response) ? response : (response?.data || []);
            setUsers(userData);
        } catch (error) {
            console.error("Failed to load users:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleStatus = async (id: string, currentStatus: boolean) => {
        try {
            await api.users.update(id, { is_active: !currentStatus });
            await loadUsers();
        } catch (error) {
            console.error("Failed to toggle user status:", error);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this user? This action cannot be undone.")) return;
        try {
            await api.users.delete(id);
            await loadUsers();
        } catch (error: any) {
            alert(error.message || "Failed to delete user");
        }
    };

    const openCreateModal = () => {
        setModalMode("create");
        setSelectedUser(null);
        setFormData({
            username: "",
            email: "",
            password: "",
            role: "employee",
            is_active: true,
        });
        setFormError("");
        setIsModalOpen(true);
    };

    const openEditModal = (user: User) => {
        setModalMode("edit");
        setSelectedUser(user);
        setFormData({
            username: user.username,
            email: user.email || "",
            password: "",
            role: user.role,
            is_active: user.is_active,
        });
        setFormError("");
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
    };

    const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError("");
        setSubmitting(true);

        try {
            if (modalMode === "create") {
                await api.users.create({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password,
                    role: formData.role,
                });
            } else if (modalMode === "edit" && selectedUser) {
                await api.users.update(selectedUser.id, {
                    role: formData.role,
                    is_active: formData.is_active,
                });
            }
            await loadUsers();
            closeModal();
        } catch (error: any) {
            setFormError(error.message || "An error occurred");
        } finally {
            setSubmitting(false);
        }
    };

    const filteredUsers = Array.isArray(users) ? users.filter((user) =>
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email?.toLowerCase().includes(searchTerm.toLowerCase())
    ) : [];

    const getRoleBadgeColor = (role: UserRole) => {
        switch (role) {
            case "admin":
                return "bg-red-500/20 text-red-500";
            case "employee":
                return "bg-blue-500/20 text-blue-500";
            case "developer":
                return "bg-purple-500/20 text-purple-500";
            case "guest":
                return "bg-gray-500/20 text-gray-500";
            default:
                return "bg-gray-500/20 text-gray-500";
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted-foreground animate-pulse">Loading users...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">User Management</h1>
                    <p className="text-muted-foreground mt-1">
                        Manage users, roles, and access control
                    </p>
                </div>
                <button
                    onClick={openCreateModal}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                    <UserPlus className="w-4 h-4" />
                    Create User
                </button>
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                    type="text"
                    placeholder="Search users by username or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
            </div>

            {/* Users Table */}
            <div className="bg-card border border-border rounded-lg overflow-hidden">
                <table className="w-full text-left max-w-full">
                    <thead className="bg-accent/50 text-sm">
                        <tr>
                            <th className="px-6 py-4 font-medium text-foreground">Username</th>
                            <th className="px-6 py-4 font-medium text-foreground">Email</th>
                            <th className="px-6 py-4 font-medium text-foreground">Role</th>
                            <th className="px-6 py-4 font-medium text-foreground">Status</th>
                            <th className="px-6 py-4 font-medium text-foreground hidden md:table-cell">Created</th>
                            <th className="px-6 py-4 font-medium text-foreground text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border text-sm">
                        {filteredUsers.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-8 text-center text-muted-foreground">
                                    No users found matching your search.
                                </td>
                            </tr>
                        ) : (
                            filteredUsers.map((user) => (
                                <tr key={user.id} className="hover:bg-accent/30 transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-accent rounded-md group-hover:bg-background transition-colors">
                                                <Shield className="w-4 h-4 text-muted-foreground" />
                                            </div>
                                            <span className="font-medium text-foreground">{user.username}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-muted-foreground">{user.email || "—"}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                                            {user.role}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span
                                            className={`px-2.5 py-1 rounded-full text-xs font-medium ${user.is_active
                                                ? "bg-green-500/10 text-green-500"
                                                : "bg-gray-500/10 text-gray-400"
                                                }`}
                                        >
                                            {user.is_active ? "Active" : "Inactive"}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-muted-foreground hidden md:table-cell">
                                        {user.created_at ? new Date(user.created_at).toLocaleDateString() : "—"}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center justify-end gap-1">
                                            <button
                                                onClick={() => openEditModal(user)}
                                                className="p-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors"
                                                title="Edit Role & Status"
                                            >
                                                <Edit className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => handleToggleStatus(user.id, user.is_active)}
                                                className={`p-2 rounded-md transition-colors ${user.is_active ? 'text-muted-foreground hover:text-amber-500 hover:bg-amber-500/10' : 'text-amber-500 hover:text-amber-400 hover:bg-amber-500/10'}`}
                                                title={user.is_active ? "Deactivate" : "Activate"}
                                            >
                                                <UserX className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(user.id)}
                                                className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-colors ml-1"
                                                title="Delete User"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-card border border-border rounded-lg p-5">
                    <div className="text-3xl font-bold tracking-tight text-foreground">{Array.isArray(users) ? users.length : 0}</div>
                    <div className="text-sm font-medium text-muted-foreground mt-1">Total Users</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-5">
                    <div className="text-3xl font-bold tracking-tight text-green-500">
                        {Array.isArray(users) ? users.filter((u) => u.is_active).length : 0}
                    </div>
                    <div className="text-sm font-medium text-muted-foreground mt-1">Active Accounts</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-5">
                    <div className="text-3xl font-bold tracking-tight text-red-500">
                        {Array.isArray(users) ? users.filter((u) => u.role === "admin").length : 0}
                    </div>
                    <div className="text-sm font-medium text-muted-foreground mt-1">Administrators</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-5">
                    <div className="text-3xl font-bold tracking-tight text-blue-500">
                        {Array.isArray(users) ? users.filter((u) => u.role === "employee").length : 0}
                    </div>
                    <div className="text-sm font-medium text-muted-foreground mt-1">Employees</div>
                </div>
            </div>

            {/* Modal Overlay for Create/Edit */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
                    <div className="bg-card border border-border rounded-xl shadow-lg w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                        <div className="flex items-center justify-between p-6 border-b border-border bg-accent/30">
                            <div>
                                <h2 className="text-xl font-semibold text-foreground">
                                    {modalMode === "create" ? "Add New User" : "Edit User"}
                                </h2>
                                <p className="text-sm text-muted-foreground mt-1">
                                    {modalMode === "create" ? "Create a user profile and assign roles." : `Update settings for ${selectedUser?.username}`}
                                </p>
                            </div>
                            <button onClick={closeModal} className="p-2 text-muted-foreground hover:bg-accent rounded-full transition-colors self-start">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6 space-y-5">
                            {formError && (
                                <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md border border-destructive/20 select-none">
                                    {formError}
                                </div>
                            )}

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-foreground mb-1.5">Username <span className="text-destructive">*</span></label>
                                    <input
                                        type="text"
                                        name="username"
                                        value={formData.username}
                                        onChange={handleFormChange}
                                        disabled={modalMode === "edit"} // Prevent changing username for now
                                        required
                                        className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
                                        placeholder="johndoe"
                                    />
                                </div>

                                {modalMode === "create" && (
                                    <>
                                        <div>
                                            <label className="block text-sm font-medium text-foreground mb-1.5">Email Address</label>
                                            <input
                                                type="email"
                                                name="email"
                                                value={formData.email}
                                                onChange={handleFormChange}
                                                className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                                                placeholder="john@example.com"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-foreground mb-1.5">Password <span className="text-destructive">*</span></label>
                                            <input
                                                type="password"
                                                name="password"
                                                value={formData.password}
                                                onChange={handleFormChange}
                                                required
                                                className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                                                placeholder="••••••••"
                                            />
                                        </div>
                                    </>
                                )}

                                <div>
                                    <label className="block text-sm font-medium text-foreground mb-1.5">User Role <span className="text-destructive">*</span></label>
                                    <select
                                        name="role"
                                        value={formData.role}
                                        onChange={handleFormChange}
                                        required
                                        className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                                    >
                                        <option value="guest">Guest (Read-only)</option>
                                        <option value="developer">Developer</option>
                                        <option value="employee">Employee</option>
                                        <option value="admin">Administrator</option>
                                    </select>
                                </div>

                                {modalMode === "edit" && (
                                    <div className="flex items-center pt-2">
                                        <input
                                            type="checkbox"
                                            id="is_active"
                                            name="is_active"
                                            checked={formData.is_active}
                                            onChange={handleFormChange}
                                            className="w-4 h-4 text-primary bg-background border-border rounded focus:ring-primary focus:ring-offset-background"
                                        />
                                        <label htmlFor="is_active" className="ml-2 block text-sm font-medium text-foreground select-none cursor-pointer">
                                            Account is active
                                        </label>
                                    </div>
                                )}
                            </div>

                            <div className="flex justify-end gap-3 pt-5 mt-6 border-t border-border">
                                <button
                                    type="button"
                                    onClick={closeModal}
                                    disabled={submitting}
                                    className="px-4 py-2 text-sm font-medium text-foreground bg-accent hover:bg-accent/80 transition-colors rounded-md"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-foreground bg-primary hover:bg-primary/90 transition-colors rounded-md disabled:opacity-50"
                                >
                                    {submitting ? (
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    ) : (
                                        <Save className="w-4 h-4" />
                                    )}
                                    {modalMode === "create" ? "Create User" : "Save Changes"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
