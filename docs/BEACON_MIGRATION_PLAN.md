# Beacon Studio Migration Plan

## Overview
This document outlines the migration from Gunpowder Splash (data exploration tool) to Beacon Studio (Code OSS-based IDE platform).

## Phase 1: Foundation & Architecture (Weeks 1-2)

### 1.1 Legal Compliance
- [ ] Clone Code OSS repository (microsoft/vscode)
- [ ] Review and document MIT license requirements
- [ ] Create `LICENSES.md` with all third-party attributions
- [ ] Design "About / Licenses" page for user-visible compliance
- [ ] Audit current dependencies for GPL/incompatible licenses

### 1.2 Database Schema Implementation
- [ ] Create migration scripts for Postgres schema
- [ ] Implement tables: `plan`, `workspace`, `membership`, `project`, `user`
- [ ] Add indexes for performance (workspace_id, user_id lookups)
- [ ] Seed static `plan` table with Free/Haste I/II/III definitions
- [ ] Create stored procedures for common operations

### 1.3 GCP Infrastructure Setup
- [ ] Configure Cloud SQL Postgres instance (regional, HA optional)
- [ ] Create Cloud Storage bucket: `beacon-prod-files`
- [ ] Set up Cloud Run service configuration
- [ ] Configure Cloud Scheduler jobs (storage reconciliation, purge)
- [ ] Create service accounts with least-privilege IAM roles
- [ ] Set up environment variables and secrets management

## Phase 2: Authentication & Authorization (Weeks 3-4)

### 2.1 OAuth Implementation
- [ ] Set up Google OAuth2 client (GCP Console)
- [ ] Set up GitHub OAuth App
- [ ] Implement OAuth callback handlers in backend
- [ ] Create JWT/session issuance logic
- [ ] Build user registration flow (first-time sign-in)
- [ ] Implement session validation middleware

### 2.2 Role-Based Access Control
- [ ] Create permission enforcement middleware
- [ ] Implement role checks: ADMIN/MOD/USER
- [ ] Build workspace membership validation
- [ ] Add project-level access control
- [ ] Create team management endpoints (add/remove members, change roles)
- [ ] Add comprehensive access control tests

## Phase 3: Storage & Quota Management (Weeks 5-6)

### 3.1 Cloud Storage Integration
- [ ] Implement GCS client wrapper
- [ ] Create file operation APIs (read/write/delete/move)
- [ ] Build workspace/project path structure
- [ ] Add atomic write operations with rollback
- [ ] Implement signed URL generation for downloads

### 3.2 Quota Enforcement
- [ ] Build write-time storage limit checks
- [ ] Create delta calculation logic (create/update/delete)
- [ ] Implement quota rejection with clear error messages
- [ ] Build storage reconciliation cron job
- [ ] Add storage usage reporting endpoints
- [ ] Create admin dashboard for storage monitoring

## Phase 4: Billing & Subscription (Weeks 7-8)

### 4.1 Stripe Integration
- [ ] Set up Stripe account and API keys
- [ ] Create Stripe products for Haste I/II/III plans
- [ ] Implement subscription creation flow
- [ ] Build webhook endpoint for subscription events
- [ ] Handle payment method updates
- [ ] Implement upgrade/downgrade logic
- [ ] Add invoice generation and retrieval

### 4.2 Cancellation & Export
- [ ] Implement cancellation webhook handler
- [ ] Build read-only mode enforcement
- [ ] Create export endpoint (tar/zip workspace)
- [ ] Implement signed URL delivery for exports
- [ ] Build purge job for deleted workspaces
- [ ] Add grace period countdown UI

## Phase 5: Code OSS Frontend Integration (Weeks 9-12)

### 5.1 Code OSS Setup
- [ ] Clone and build Code OSS for web
- [ ] Remove all Microsoft branding (logos, names, telemetry)
- [ ] Configure for browser-based deployment
- [ ] Disable proprietary extensions and marketplace
- [ ] Set up custom extension registry (optional)
- [ ] Configure file system provider for GCS backend

### 5.2 Beacon UI Features
- [ ] Create OSS View ⇄ Web-Edit View toggle
- [ ] Build Global Project Button (upper-left)
- [ ] Implement project switcher dialog
- [ ] Create Account page (profile, subscription, contact info)
- [ ] Build Team page (member list, invites, role management)
- [ ] Implement Haste+ Subscription page
- [ ] Create Billing page (invoices, payment method)
- [ ] Build System page (settings, diagnostics)
- [ ] Add Query/AI center UI
- [ ] Implement Revision History view

### 5.3 Custom File System Provider
- [ ] Implement VSCode FileSystemProvider interface
- [ ] Connect to backend API for file operations
- [ ] Handle authentication and authorization
- [ ] Add caching layer for performance
- [ ] Implement conflict resolution for concurrent edits
- [ ] Add offline detection and reconnection logic

## Phase 6: AI Integration (Weeks 13-14)

### 6.1 AI Provider Interface
- [ ] Design provider abstraction layer
- [ ] Implement Gemini provider (Gemini Flash model)
- [ ] Add LM Studio HTTP client
- [ ] Add Ollama HTTP client
- [ ] Create model configuration system
- [ ] Implement usage tracking in Postgres

### 6.2 AI Features in Editor
- [ ] Build AI chat sidebar
- [ ] Add inline code actions (Explain/Refactor/Generate)
- [ ] Implement context gathering from active files
- [ ] Add optional inline completions
- [ ] Create AI settings panel
- [ ] Implement rate limiting and error handling

## Phase 7: Testing & Quality Assurance (Weeks 15-16)

### 7.1 Backend Testing
- [ ] Unit tests for all service modules
- [ ] Integration tests for auth flows
- [ ] Storage quota enforcement tests
- [ ] Stripe webhook simulation tests
- [ ] Role permission boundary tests
- [ ] Load testing for concurrent users

### 7.2 Frontend Testing
- [ ] Component tests for UI features
- [ ] E2E tests for critical user flows
- [ ] Cross-browser compatibility testing
- [ ] Performance profiling and optimization
- [ ] Accessibility audit (WCAG 2.1)

### 7.3 Security Audit
- [ ] OWASP Top 10 vulnerability scan
- [ ] SQL injection prevention verification
- [ ] XSS protection verification
- [ ] CSRF token validation
- [ ] Rate limiting on all public endpoints
- [ ] Secrets management audit

## Phase 8: Deployment & Launch (Weeks 17-18)

### 8.1 Production Setup
- [ ] Configure production GCP project
- [ ] Set up Cloud SQL with backups
- [ ] Configure Cloud Run autoscaling
- [ ] Set up monitoring (Cloud Monitoring/Logging)
- [ ] Configure alerting for critical issues
- [ ] Set up error tracking (Sentry or similar)
- [ ] Configure CDN for static assets

### 8.2 Documentation & Legal
- [ ] Write user documentation
- [ ] Create admin operation runbook
- [ ] Draft Privacy Policy
- [ ] Draft Terms of Service
- [ ] Create data handling documentation
- [ ] Write GDPR/CCPA compliance guide

### 8.3 Launch Preparation
- [ ] Beta testing with select users
- [ ] Performance optimization based on beta feedback
- [ ] Create marketing materials
- [ ] Set up support channels
- [ ] Prepare incident response plan
- [ ] Final security review

## Architecture Decisions

### Backend Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI (existing)
- **Database**: PostgreSQL 15+
- **Storage**: GCP Cloud Storage
- **Compute**: GCP Cloud Run
- **Caching**: Redis (Cloud Memorystore) for sessions

### Frontend Stack
- **Base**: Code OSS (MIT fork)
- **Build**: Webpack/esbuild
- **Deployment**: Served via Cloud Run (separate service) or CDN
- **WebSocket**: For live collaboration (future)

### Key Dependencies to Review
- Remove any GPL-licensed dependencies
- Audit all extensions for commercial SaaS compatibility
- Verify AI model licenses (Gemini, local models)

## Risk Mitigation

1. **Code OSS Complexity**: Allocate extra time for understanding and modifying Code OSS codebase
2. **Storage Costs**: Implement aggressive monitoring and alerting for unusual storage growth
3. **AI Costs**: Start with Gemini Flash (cheapest), implement strict rate limiting
4. **Multi-tenancy**: Rigorous testing of isolation between workspaces
5. **Data Loss**: Implement backup strategy and export guarantees

## Success Metrics

- [ ] All 11 compliance checklist items from spec satisfied
- [ ] Free tier users can sign up and use 0.84 GB storage
- [ ] Haste+ users can successfully subscribe and collaborate
- [ ] Cancellation flow works with 30-day grace period
- [ ] Export functionality delivers complete workspace archives
- [ ] AI integration works with Gemini and local models
- [ ] System can handle 100+ concurrent users
- [ ] 99.9% uptime after stabilization period

