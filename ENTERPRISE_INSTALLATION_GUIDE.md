# Deploying a New Enterprise Installation

This guide explains the complete end-to-end process of setting up a brand-new Enterprise Deployment of the Hybrid NLP-Expert Agent Platform and connecting it to the centralized Vendor Licensing System.

---

## 🏗️ Phase 1: Vendor Platform Setup
Before an Enterprise customer can start using their system, they must be registered in your Vendor database, and a License Key must be generated for them.

### Step 1: Create the Customer
1. Log into your **Vendor Control Dashboard** (usually running on port `4000`).
2. Navigate to the **Customers** tab.
3. Click "Add Customer" and fill in the Organization name, Contact Email, and select the organization type (e.g., Enterprise).

### Step 2: Generate a License Key
1. Navigate to the **Licenses** tab.
2. Select your newly created customer from the dropdown.
3. (Optional) Set an Expiration Date if it's a trial or term license. 
4. Set the **Max Instances** (the maximum number of servers the customer is allowed to spin up with this single key).
5. Click **Create**.
6. **Save the generated 36-character `License Key`**. You will need to provide this key to your customer.

---

## 🚀 Phase 2: Enterprise Deployment (Customer's Server)
You will now deploy the actual AI platform on the customer's server, providing it with the License Key you just generated.

### Step 1: Clone the Repository
On the customer's server, pull down the necessary platform code:
```bash
git clone <repository_url>
cd projet
```

### Step 2: Configure Environment Variables
Inside the root folder (`projetiia/projet`), look for the main `docker-compose.yml` file. You need to configure the `expert-agent-backend` service. 

Alternatively, create an `.env` file in the same directory as `docker-compose.yml` and provide the following variables:
```env
# The unique key generated in Phase 1
LICENSE_KEY="xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# The publicly accessible IP/URL of your Vendor API (must end without a trailing slash)
LICENSE_SERVER_URL="https://your-vendor-domain.com/api"

# The HMAC Secret (matches VENDOR_HMAC_SECRET on the vendor side) for cryptographic verification
LICENSE_PUBLIC_KEY="change-me-in-production"
```
*Note: In local testing, `LICENSE_SERVER_URL` might simply be `http://vendor-api:8002` if running on the same machine.*

### Step 3: Start the Enterprise Platform
With the credentials safely passed as environment variables, run the Docker Compose command to build and launch the platform:

```bash
docker compose up -d --build
```
This will spin up the backend (FastAPI), the Admin UI (Next.js), the Chatbot Frontend (Vite), Postgres, Redis, and Ollama.

---

## 🔍 Phase 3: The Initial Handshake & Verification
Once the customer runs `docker compose up`, the system will automatically reach out to you to verify itself.

### The Background Process:
1. **Startup Check:** The Enterprise `expert-agent-backend` container wakes up and triggers its `license_check_once` function.
2. **Ping Vendor:** It sends an HTTP POST request to your `LICENSE_SERVER_URL/api/license/check` containing its `LICENSE_KEY`, Hostname, and a unique UUID identifying this specific server instance.
3. **Approval:** The Vendor Server receives this, verifies the key, records the instance, and replies with an encrypted `valid: true` HMAC signature.
4. **Boot Complete:** The Enterprise Backend verifies the HMAC signature, confirms it hasn't been spoofed, and completes its startup sequence (loading NLP models, initiating Vector DBs, etc.).

### How to Verify It Worked:
* **On the Customer's Server:** 
  You can run `curl -s http://localhost:8001/license/status` to instantly see if the local application successfully accepted the license key. You should see `"licensed": true`.
* **On your Vendor Dashboard:** 
  Log into your Vendor Dashboard and go to the **Instances** tab. You should immediately see the customer's server (`hostname`) appear here with an *Online* status!

---

## ⛔ Phase 4: Suspending or Revoking a Deployment
If an enterprise stops paying or breaches their contract, you can remotely disable their installation without SSH access to their servers.

1. Open your **Vendor Dashboard**.
2. Go to the **Licenses** tab and find their License Key.
3. Click the red **Revoke** button (or go to Instances and disable the specific instance).
4. Within 5 minutes (the `LICENSE_CHECK_INTERVAL`), the customer's running server will ping your Vendor API for a health check.
5. Your Vendor API will reply with `active: false`.
6. The customer's system will instantly lock out all `/chat/` capabilities, hard-returning `HTTP 503 System Disabled` until you restore the license.
