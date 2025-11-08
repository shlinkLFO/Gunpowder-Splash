
# Beacon Studio (Gunpowder Splash Iteration) – Product & Legal Spec

Product codename: **Gunpowder Splash**  
Production brand: **Beacon Studio** at **`https://glowstone.red/beacon-studio`**  

This document is intended for Cursor and implementation collaborators as the canonical specification for iterating Gunpowder Splash into Beacon Studio, including legal constraints, architecture, billing, and UX flows.

---

## 1. Legal Foundation (Binding Constraints)

### 1.1 Codebase Origin

- **Base editor:** `microsoft/vscode` GitHub repository (**Code OSS**).  
- **License:** MIT.  
- Beacon Studio MUST treat Code OSS as an MIT-licensed library and:
  - MAY: use, copy, modify, merge, publish, distribute, and sell access to modified versions.
  - MUST: preserve the MIT copyright and license notice:
    - In the source tree.
    - In a user-visible “About / Licenses” page.

### 1.2 Prohibited: Microsoft VS Code Product & VS Code Server

The following are strictly disallowed for Beacon Studio:

- DO NOT use or ship **official Visual Studio Code binaries** (desktop or web) under the Microsoft Software License.
- DO NOT use or host **VS Code Server** or any official Microsoft-hosted remote components as the backend for Beacon Studio.
- DO NOT expose or redistribute Microsoft’s VS Code product as a service to third parties.
- DO NOT bundle proprietary Microsoft-only extensions that forbid hosting or redistribution (e.g., specific Remote/Live Share components).

Beacon Studio MUST only use **Code OSS builds** (or derivatives like VSCodium-style debranded builds) and NOT official Microsoft VS Code product binaries.

### 1.3 Branding / Trademarks

- Product name: **Beacon Studio** (codename Gunpowder Splash).  
- URL: `https://glowstone.red/beacon-studio`.
- MUST NOT:
  - Use “Visual Studio Code”, “VS Code”, or confusingly similar names as the product name.
  - Use Microsoft logos, icons, or other registered trademarks in UI or marketing.
- MUST:
  - Replace all Microsoft product names and logos with Beacon Studio branding.
  - Clearly acknowledge in the legal/about page that Beacon Studio is derived from the MIT-licensed `microsoft/vscode` project (Code OSS).

### 1.4 Third-Party Components & AI Providers

- Only include extensions and libraries compatible with commercial SaaS use:
  - Avoid GPLv3 unless willing to comply with distribution obligations.
  - Remove or replace any extension whose EULA conflicts with SaaS hosting.
- AI providers:
  - **Gemini** – must follow provider ToS (rate limits, allowed use-cases, data handling).
  - **LM Studio / Ollama** – treat as local HTTP backends; ensure chosen models have licenses permitting commercial use.
- A clear privacy/data-handling policy MUST be supportable at app level, describing:
  - What code and prompts are sent to AI.
  - How logs, usage, and customer data are stored and retained.
  - Rights to deletion and export where legally required (GDPR/CCPA style).

---

## 2. High-Level Product Overview

### 2.1 Concept

- **Beacon Studio** is a multi-tenant, browser-based IDE SaaS built on Code OSS.
- Hosted at `glowstone.red/beacon-studio` on GCP (Cloud Run + Cloud SQL Postgres + Cloud Storage).
- Authentication: **Sign in with Google** or **Sign in with GitHub** only.
- AI integration:
  - Primary affordable cloud model: **Gemini** (e.g., Gemini Flash).
  - Optional **offline/local endpoints**: LM Studio / Ollama.
- Roles: **ADMIN**, **MOD**, **USER**.
- Billing: **Stripe** (subscription-based, Haste+ plans).

### 2.2 Gunpowder Splash UX Features to Preserve / Extend

From `~\Gunpowder Splash\` the following UX patterns are required:

1. **OSS View ⇄ Web-Edit View Toggle**
   - A prominent button to switch between:
     - **OSS View**: classic Code OSS editor layout.
     - **Web-Edit View**: higher-level web UI oriented around projects, teams, and account management.
   - The **OSS sidepanel** remains expandable and collapsible in both modes.
   - The same toggle button (or adjacent nav cluster) routes to:
     - **Haste+ Subscription** page.
     - **Account** page.
     - **Team** page.
     - **Query** (AI/issue/query center).
     - **Revision History**.
     - **Billing**.
     - **System** (settings / diagnostics).

2. **Account Page**
   - Allows authenticated users to:
     - View and manage subscription (Haste plan, status, renewal/cancel).
     - Add and update contact information (name, email, phone optional).
     - Add and update address information (billing address for Stripe).
     - View their Projects (see list, switch, and quick-open).
     - Add links (e.g., portfolio, GitHub).
     - Connect LinkedIn (OAuth or link-based).

3. **Global Project Button**
   - A **global button** appears on every page, upper-left, displaying the **current project name**.
   - Clicking this button:
     - Opens a project switcher dialog.
     - Allows users to:
       - Create a new project (within workspace storage & team limits).
       - Switch to another accessible project.
   - **Projects** are separate codebases:
     - Files stored distinctly.
     - Accessible only by that project’s ADMIN/MOD/USER members (via workspace membership and permissions).

4. **Standard (Free) Users**
   - Standard (non-Haste+) users:
     - Max storage: **0.84 GB**.
     - Cannot share their workspace environment with other accounts (i.e., single-user, no team).

5. **Haste+ Subscription Page**
   - Dedicated **Haste+** page describing subscription tiers and benefits.
   - Plans (prices in USD, per month, assumptions below):
     - **Haste I** – $16.99/month
       - Storage: 20 GB
       - Team: 1 owner + 4 team members (max 5 users total)
     - **Haste II** – $29.99/month
       - Storage: 60 GB
       - Team: 1 owner + 8 team members (max 9 users total)
     - **Haste III** – $49.99/month
       - Storage: 240 GB
       - Team: 1 owner + 16 team members (max 17 users total)
   - All Haste+ plans:
     - Role system: ADMIN / MOD / USER.
     - Ability to add users to the codebase (within team size limits).
     - On cancellation: workspace becomes read-only but remains exportable for **30 days**; then deleted.
     - Export guarantee: “You may export your entire codebase within 30 days of subscription cancellation.”

---

## 3. Architecture & Platform Assumptions

### 3.1 GCP Components

**Backend already planned:**

- **Cloud Run**: stateless backend API container.
- **Cloud SQL (Postgres)**: persistent data store.
- **Cloud Storage**: file/object storage.

Additional infra:

- **Cloud Scheduler**: cron-like scheduled jobs for housekeeping.
- **Service Accounts** with least-privilege roles for Cloud Run and Scheduler.

### 3.2 Cloud Storage Layout

- Bucket: `beacon-prod-files` (regional, e.g., `us-central1`).  
- Layout: `workspace_<id>/project_<id>/...` for all project files.

Example structure:

- `gs://beacon-prod-files/workspace_<wsid>/project_<pid>/src/...`
- `gs://beacon-prod-files/workspace_<wsid>/project_<pid>/.beacon/meta.json`

### 3.3 Cloud SQL (Postgres)

- Stores:
  - Users, workspaces, projects.
  - Plans and subscriptions.
  - Memberships and roles.
  - Usage metrics (storage_used_bytes, AI usage).
  - Cancellation and export status.

### 3.4 Cloud Run Backend Responsibilities

- Auth callbacks (Google/GitHub).
- JWT/Session issuance.
- Enforce:
  - Storage limits per plan.
  - Team size limits per plan.
  - Read-only state for cancelled workspaces in grace period.
- File operations:
  - Create/update/delete files in GCS with quota checks.
- Export orchestration.
- Stripe webhooks handling for billing lifecycle.
- Admin endpoints for Cloud Scheduler tasks (storage reconciliation, purge-deleted).

### 3.5 Cloud Scheduler Tasks

1. **Storage Recalculation Job**
   - Daily job that hits an internal admin endpoint.
   - For each workspace:
     - List `gs://beacon-prod-files/workspace_<id>/...`.
     - Sum object sizes to `actual_bytes`.
     - Update `workspace.storage_used_bytes = actual_bytes` in Postgres.

2. **Purge Deleted Workspaces Job**
   - Daily job hitting another internal admin endpoint.
   - For each workspace where `delete_after < now()`:
     - Delete all objects under `workspace_<id>/` in GCS.
     - Delete or mark the workspace and memberships as permanently deleted.

---

## 4. Auth, Roles, and Permissions

### 4.1 Authentication

- **No local password system.**
- Supported login methods:
  - “Sign in with Google” (OAuth2/OIDC).
  - “Sign in with GitHub” (OAuth2/OIDC).
- After sign-in:
  - Map provider identity to internal `User` record:
    - `id`, `primary_email`, `display_name`, `avatar_url`, `provider`, `provider_user_id`, `created_at`, `last_login_at`.

### 4.2 Roles

Three roles only:

- `ADMIN`
- `MOD`
- `USER`

**Semantics:**

- `ADMIN`:
  - Workspace owner (or delegated admin).
  - Manage billing and Haste plan (within Stripe flow).
  - Change workspace plan (upgrade/downgrade Haste I/II/III).
  - Create/delete projects within that workspace.
  - Add/remove members and set roles (MOD/USER).
  - Full read/write/delete on all files/projects in workspace.
- `MOD`:
  - Read/write/delete within projects they’re assigned to.
  - Invite/remove USERs within workspace (if allowed by policy).
  - No access to global billing, plan changes, or workspace deletion.
- `USER`:
  - Read/write access only to projects they are assigned to.
  - Cannot modify roles or billing.
  - Cannot exceed plan storage limits for operations they initiate.

### 4.3 Standard (Free) vs Haste+

- **Standard (Free)**
  - Implicit plan with:
    - Storage limit: **0.84 GB**.
    - Team: single user only (no shared workspace; membership = owner only).
- **Haste+ (Haste I / II / III)**
  - See plan definitions (Section 5).  
  - Allow multi-user collaboration, subject to team limits.

### 4.4 Permission Enforcement

- All enforcement is **server-side**. The client (editor) is untrusted.
- For every file operation (read/write/create/delete/move/rename):
  - Check:
    - `user_id` is a member of workspace/project.
    - `role` is sufficient for the requested operation.
    - `workspace.is_read_only` flag (if true, no writes allowed except export).
    - `storage_used_bytes + delta <= storage_limit_bytes` for writes/creates.
- For team operations (invites, role changes):
  - Only allow when caller role is `ADMIN` (or `MOD` for certain limited operations, if explicitly allowed).
- For workspace-level actions (cancellation, upgrade, downgrade):
  - Only ADMIN and only via Stripe-integrated flows.

---

## 5. Haste+ Billing Model and Plan Rules

### 5.1 Plan Assumptions

Backend is already planned with:

- Deployment: GCP Cloud Run.
- Database: Cloud SQL Postgres.
- Storage: Cloud Storage.
- Billing: **Stripe**.

One **workspace per subscription** (generalization possible later).

### 5.2 Plan Definitions

Plans are static rows in the `plan` table.

#### Free

- id: `free`
- Name: Free
- Price: $0
- Storage limit: **0.84 GB**
- Max members: 1 (single user, no sharing)

#### Haste I

- id: `haste_i`
- Name: Haste I
- Price: **$16.99** / month
- Storage limit: **20 GB**
- Max members: **5** (1 owner + 4 team members)

#### Haste II

- id: `haste_ii`
- Name: Haste II
- Price: **$29.99** / month
- Storage limit: **60 GB**
- Max members: **9** (1 owner + 8 team members)

#### Haste III

- id: `haste_iii`
- Name: Haste III
- Price: **$49.99** / month
- Storage limit: **240 GB**
- Max members: **17** (1 owner + 16 team members)

### 5.3 All Plan Rules

For every paid Haste plan:

- Role system: ADMIN / MOD / USER.
- Ability to add users to the workspace (within `max_members`).
- On cancellation:
  - Stripe webhook sets workspace to read-only:
    - `cancelled_at = now()`
    - `delete_after = now() + interval '30 days'`
    - `is_read_only = TRUE`
  - Backend must enforce read-only for all write/delete operations.
- During 30-day grace window:
  - Exports allowed via dedicated **Export** endpoint.
- After 30 days:
  - Workspace and all files are deleted (purge job).

### 5.4 Schema (Minimum)

```sql
-- Plans are static rows for Free, Haste I/II/III
CREATE TABLE plan (
  id TEXT PRIMARY KEY,                -- 'free', 'haste_i', 'haste_ii', 'haste_iii'
  name TEXT NOT NULL,
  price_cents INT NOT NULL,
  storage_limit_bytes BIGINT NOT NULL,
  max_members INT NOT NULL           -- includes owner
);

CREATE TABLE workspace (
  id UUID PRIMARY KEY,
  owner_user_id UUID NOT NULL,
  plan_id TEXT NOT NULL REFERENCES plan(id),
  storage_used_bytes BIGINT NOT NULL DEFAULT 0,
  cancelled_at TIMESTAMPTZ,          -- null if active
  delete_after TIMESTAMPTZ,          -- set to cancelled_at + interval '30 days'
  is_read_only BOOLEAN NOT NULL DEFAULT FALSE,
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT
);

CREATE TYPE role AS ENUM ('ADMIN','MOD','USER');

CREATE TABLE membership (
  user_id UUID NOT NULL,
  workspace_id UUID NOT NULL REFERENCES workspace(id),
  role role NOT NULL,
  PRIMARY KEY (user_id, workspace_id)
);

CREATE TABLE project (
  id UUID PRIMARY KEY,
  workspace_id UUID NOT NULL REFERENCES workspace(id),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 6. Storage, Quotas, and GCS Integration

### 6.1 Write-Time Enforcement

On every upload/write/delete of file content for a workspace:

1. Compute **delta bytes**:
   - For create: `delta = new_size`.
   - For update: `delta = new_size - old_size`.
   - For delete: `delta = -old_size`.
2. Query:
   - `workspace.storage_used_bytes`
   - `plan.storage_limit_bytes`
3. If `storage_used_bytes + delta > storage_limit_bytes`:
   - Reject request with 403 “storage limit exceeded”.
4. If allowed:
   - Update `workspace.storage_used_bytes += delta` in Postgres.
   - Write object to GCS under `workspace_<id>/project_<id>/...`.

### 6.2 Periodic Reconciliation

As described in Section 3.5, daily reconciliation job:
- For each workspace, scan GCS objects under its prefix.
- Sum byte sizes and update `workspace.storage_used_bytes` accordingly.

---

## 7. Team Size Enforcement

When adding a member to a workspace:

1. `SELECT COUNT(*) FROM membership WHERE workspace_id = $1;`
2. Join against `plan.max_members` for that workspace’s plan.
3. If `count >= max_members` → reject invite with 403 “team limit exceeded”.

Authorization constraints:

- Only `ADMIN` of workspace can:
  - Add/remove members.
  - Change member roles between MOD and USER.

---

## 8. Cancellation, Read-Only Mode, and Export

### 8.1 Stripe Webhook Flow

On `customer.subscription.deleted` (and similar events indicating cancel):

- Locate workspace via `stripe_subscription_id`.
- Set:
  - `cancelled_at = now()`
  - `delete_after = now() + interval '30 days'`
  - `is_read_only = TRUE`

### 8.2 Read-Only Enforcement

- For any write/delete API in workspace after cancellation:
  - If `workspace.is_read_only = TRUE`:
    - Reject with 403 (except the export endpoint).

### 8.3 Export Endpoint

- API: `POST /workspaces/:id/export`
- Checks:
  - Caller is a member of workspace (role: ADMIN/MOD/USER).
  - `cancelled_at IS NOT NULL` and `now() < delete_after`.
- Implementation:
  - Background job composes a tar/zip archive of:
    - All `workspace_<id>/project_<id>/...` objects.
  - Upload archive as a temporary object in GCS.
  - Return a signed URL (e.g., valid 24 hours) for user to download.

### 8.4 Final Deletion

- Daily purge job checks `workspaces` where `delete_after < now()`:
  - Delete all objects under `workspace_<id>/` from `beacon-prod-files`.
  - Delete workspace and memberships (or mark as permanently deleted).

---

## 9. Editor Integration & UX Details

### 9.1 Code OSS Frontend

- Start from Code OSS codebase and:
  - Remove/replace Microsoft branding.
  - Disable telemetry and proprietary endpoints.
  - Configure custom Beacon marketplace (if any) or internal extension registry.
- Add Beacon-specific features:
  - **OSS View**: full IDE editor view.
  - **Web-Edit View**: overlay UI for project, team, and account UX with integrated editor frames.
  - **Global Project Button** in upper-left:
    - Shows current project name.
    - Opens project selector/creator.
  - **Beacon Panel Cluster** (reachable from the OSS/Web toggle button):
    - Haste+ Subscription page.
    - Account page.
    - Team page.
    - Query (AI/query center).
    - Revision History.
    - Billing.
    - System (settings/diagnostics).

### 9.2 AI Integration (Gemini + Local Models)

- Implement a provider interface:
  - `generateCompletion`, `chat`, `applyEdit`, etc.
- Providers:
  - `GeminiProvider` → Calls affordable Gemini model.
  - `LocalProvider` → Talks to LM Studio/Ollama via HTTP, with model name/config in env.
- Editor features:
  - AI chat sidebar with context from active files/project.
  - Inline “Explain / Refactor / Generate tests” commands.
  - Optional inline completions, subject to provider capabilities.

- AI usage should be tracked in Postgres (per user, per workspace) so future plan-based limits can be enforced.

---

## 10. Compliance Checklist for Implementation

Cursor and implementation must treat the following as **non-negotiable**:

- [ ] Base editor is compiled from **Code OSS** (MIT), NOT from official VS Code or VS Code Server binaries.
- [ ] MIT license text and associated copyright are:
      - Preserved in the source repository, and
      - Visible to users via an in-app “About / Licenses” page.
- [ ] All Microsoft trademarks, product names, and logos are removed or replaced; the product is branded exclusively as **Beacon Studio** at `glowstone.red/beacon-studio`.
- [ ] No hosting, bundling, or redistributing of official VS Code Server or proprietary MS-only extensions that forbid SaaS hosting.
- [ ] Only extensions/libraries whose licenses permit commercial SaaS use are bundled.
- [ ] OAuth login with Google and GitHub is implemented securely (correct redirect URIs, `state` parameter, CSRF protections).
- [ ] AI integrations (Gemini, LM Studio, Ollama) follow each provider’s ToS and each model’s license, especially around commercial use and data privacy.
- [ ] A privacy policy and data-handling description can be surfaced in the web UI (data sent to AI, retention, user rights).
- [ ] Role enforcement (ADMIN/MOD/USER), storage quotas, team-size limits, and read-only modes are enforced on the backend and cannot be bypassed by modifying the client.
- [ ] Stripe billing is implemented in a compliant manner (no raw card storage, PCI handled by Stripe; webhook signatures verified; subscription lifecycle mapped correctly to `workspace.plan_id`, `cancelled_at`, and `delete_after`).

This Markdown document is meant to be handed directly to Cursor as the authoritative specification for iterating `~\Gunpowder Splash\` into **Beacon Studio**.
