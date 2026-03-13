# User Credentials - Hybrid Knowledge Agent

## Authentication System

The chatbot frontend now requires authentication. Users must log in with their credentials to access the chat interface.

## Available Users

### 1. Admin User
- **Username:** `admin`
- **API Key:** `sk_admin_123`
- **Role:** ADMIN
- **Access Level:** Full system access
- **Permissions:** Can access all features, manage system settings, view all documents

### 2. Employee User
- **Username:** `employee`
- **API Key:** `sk_employee_456`
- **Role:** EMPLOYEE
- **Access Level:** Standard business access
- **Permissions:** Access to business documents, standard query capabilities

### 3. Guest User
- **Username:** `guest`
- **API Key:** `sk_guest_789`
- **Role:** GUEST
- **Access Level:** Limited public access
- **Permissions:** Access to public documents only, restricted query capabilities

## How to Login

### Method 1: Manual Login
1. Navigate to http://localhost:5173/login
2. Enter username and API key
3. Click "Sign In"

### Method 2: Quick Login (Demo)
1. Navigate to http://localhost:5173/login
2. Click one of the quick login buttons:
   - **Admin** - Full access
   - **Employee** - Standard access
   - **Guest** - Limited access

## Features

- **Persistent Sessions:** Login state is saved in localStorage
- **Role-Based UI:** User role displayed in chat interface with color-coded badges
  - 🔵 Admin - Blue
  - 🟢 Employee - Green
  - 🟣 Guest - Purple
- **Logout:** Click the logout button in the chat header to sign out
- **Protected Routes:** Unauthenticated users are redirected to login page

## API Authentication

The frontend sends the `X-API-Key` header with all API requests:
```
X-API-Key: sk_admin_123
```

The backend validates the API key and applies role-based access control (RBAC) to restrict access to documents and features based on user role.

## Security Notes

- API keys are stored in localStorage (for demo purposes)
- In production, use secure token-based authentication (JWT, OAuth)
- Backend validates all API keys against the user database
- Role-based access control enforced at both frontend and backend levels
