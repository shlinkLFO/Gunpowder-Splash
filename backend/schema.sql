-- Beacon Studio Database Schema
-- PostgreSQL 15+
-- This schema implements the multi-tenant workspace model with subscription billing

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User table: stores OAuth-authenticated users
CREATE TABLE "user" (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  primary_email TEXT NOT NULL UNIQUE,
  display_name TEXT,
  avatar_url TEXT,
  provider TEXT NOT NULL,  -- 'google' or 'github'
  provider_user_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_login_at TIMESTAMPTZ,
  UNIQUE (provider, provider_user_id)
);

CREATE INDEX idx_user_email ON "user"(primary_email);
CREATE INDEX idx_user_provider ON "user"(provider, provider_user_id);

-- Plan table: static rows for Free, Haste I/II/III
CREATE TABLE plan (
  id TEXT PRIMARY KEY,  -- 'free', 'haste_i', 'haste_ii', 'haste_iii'
  name TEXT NOT NULL,
  price_cents INT NOT NULL,
  storage_limit_bytes BIGINT NOT NULL,
  max_members INT NOT NULL,  -- includes owner
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed plans
INSERT INTO plan (id, name, price_cents, storage_limit_bytes, max_members) VALUES
  ('free', 'Free', 0, 902299238, 1),  -- 0.84 GB = 902299238 bytes
  ('haste_i', 'Haste I', 1699, 21474836480, 5),  -- 20 GB, $16.99
  ('haste_ii', 'Haste II', 2999, 64424509440, 9),  -- 60 GB, $29.99
  ('haste_iii', 'Haste III', 4999, 257698037760, 17);  -- 240 GB, $49.99

-- Workspace table: one per subscription, contains projects and members
CREATE TABLE workspace (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  owner_user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  plan_id TEXT NOT NULL REFERENCES plan(id),
  storage_used_bytes BIGINT NOT NULL DEFAULT 0,
  cancelled_at TIMESTAMPTZ,  -- null if active
  delete_after TIMESTAMPTZ,  -- set to cancelled_at + interval '30 days'
  is_read_only BOOLEAN NOT NULL DEFAULT FALSE,
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT storage_non_negative CHECK (storage_used_bytes >= 0)
);

CREATE INDEX idx_workspace_owner ON workspace(owner_user_id);
CREATE INDEX idx_workspace_plan ON workspace(plan_id);
CREATE INDEX idx_workspace_stripe_sub ON workspace(stripe_subscription_id);
CREATE INDEX idx_workspace_delete_after ON workspace(delete_after) WHERE delete_after IS NOT NULL;

-- Role enum
CREATE TYPE role AS ENUM ('ADMIN', 'MOD', 'USER');

-- Membership table: links users to workspaces with roles
CREATE TABLE membership (
  user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL REFERENCES workspace(id) ON DELETE CASCADE,
  role role NOT NULL,
  joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, workspace_id)
);

CREATE INDEX idx_membership_workspace ON membership(workspace_id);
CREATE INDEX idx_membership_user ON membership(user_id);

-- Project table: separate codebases within a workspace
CREATE TABLE project (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  workspace_id UUID NOT NULL REFERENCES workspace(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (workspace_id, name)
);

CREATE INDEX idx_project_workspace ON project(workspace_id);

-- AI usage tracking table (for future quota enforcement)
CREATE TABLE ai_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL REFERENCES workspace(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,  -- 'gemini', 'lm_studio', 'ollama'
  model_name TEXT,
  input_tokens INT,
  output_tokens INT,
  cost_cents INT,  -- estimated cost
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ai_usage_user ON ai_usage(user_id, created_at);
CREATE INDEX idx_ai_usage_workspace ON ai_usage(workspace_id, created_at);

-- OAuth state tokens table (for secure OAuth flow across distributed instances)
CREATE TABLE oauth_state (
  state TEXT PRIMARY KEY,
  provider TEXT NOT NULL,  -- 'google' or 'github'
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '10 minutes')
);

CREATE INDEX idx_oauth_state_expires ON oauth_state(expires_at);

-- Audit log table (for compliance and security)
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
  workspace_id UUID REFERENCES workspace(id) ON DELETE CASCADE,
  action TEXT NOT NULL,  -- 'file_create', 'file_delete', 'member_add', etc.
  resource_type TEXT,  -- 'file', 'project', 'workspace', 'member'
  resource_id TEXT,
  details JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id, created_at);
CREATE INDEX idx_audit_log_workspace ON audit_log(workspace_id, created_at);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

-- Function to automatically create default workspace on user creation
CREATE OR REPLACE FUNCTION create_default_workspace()
RETURNS TRIGGER AS $$
DECLARE
  new_workspace_id UUID;
BEGIN
  -- Create a free workspace for the new user
  INSERT INTO workspace (owner_user_id, plan_id)
  VALUES (NEW.id, 'free')
  RETURNING id INTO new_workspace_id;
  
  -- Add user as ADMIN of their workspace
  INSERT INTO membership (user_id, workspace_id, role)
  VALUES (NEW.id, new_workspace_id, 'ADMIN');
  
  -- Create a default project
  INSERT INTO project (workspace_id, name, description)
  VALUES (new_workspace_id, 'My First Project', 'Default project');
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_default_workspace
AFTER INSERT ON "user"
FOR EACH ROW
EXECUTE FUNCTION create_default_workspace();

-- Function to check team size limit before adding member
CREATE OR REPLACE FUNCTION check_team_size_limit()
RETURNS TRIGGER AS $$
DECLARE
  current_count INT;
  max_allowed INT;
  workspace_plan_id TEXT;
BEGIN
  -- Lock the workspace row to prevent race conditions
  SELECT plan_id INTO workspace_plan_id FROM workspace WHERE id = NEW.workspace_id FOR UPDATE;
  
  -- Get current member count
  SELECT COUNT(*) INTO current_count FROM membership WHERE workspace_id = NEW.workspace_id;
  
  -- Get plan limit
  SELECT max_members INTO max_allowed FROM plan WHERE id = workspace_plan_id;
  
  -- Check if adding this member would exceed limit
  IF current_count >= max_allowed THEN
    RAISE EXCEPTION 'Team size limit exceeded for this workspace plan'
      USING HINT = 'Upgrade to a higher Haste+ plan to add more members';
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_team_size_limit
BEFORE INSERT ON membership
FOR EACH ROW
EXECUTE FUNCTION check_team_size_limit();

-- Function to update workspace updated_at timestamp
CREATE OR REPLACE FUNCTION update_workspace_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE workspace SET updated_at = now() WHERE id = NEW.workspace_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_workspace_timestamp_project
AFTER INSERT OR UPDATE ON project
FOR EACH ROW
EXECUTE FUNCTION update_workspace_timestamp();

-- View for workspace members with user details
CREATE VIEW workspace_members AS
SELECT 
  m.workspace_id,
  m.user_id,
  m.role,
  m.joined_at,
  u.primary_email,
  u.display_name,
  u.avatar_url
FROM membership m
JOIN "user" u ON m.user_id = u.id;

-- View for workspace storage usage with plan limits
CREATE VIEW workspace_storage_status AS
SELECT 
  w.id AS workspace_id,
  w.owner_user_id,
  w.plan_id,
  p.name AS plan_name,
  w.storage_used_bytes,
  p.storage_limit_bytes,
  ROUND((w.storage_used_bytes::NUMERIC / p.storage_limit_bytes::NUMERIC) * 100, 2) AS usage_percentage,
  w.is_read_only,
  w.cancelled_at,
  w.delete_after
FROM workspace w
JOIN plan p ON w.plan_id = p.id;

-- View for user's accessible workspaces
CREATE VIEW user_workspaces AS
SELECT 
  u.id AS user_id,
  w.id AS workspace_id,
  w.plan_id,
  p.name AS plan_name,
  m.role,
  w.is_read_only,
  w.cancelled_at,
  (SELECT COUNT(*) FROM project WHERE workspace_id = w.id) AS project_count,
  (SELECT COUNT(*) FROM membership WHERE workspace_id = w.id) AS member_count
FROM "user" u
JOIN membership m ON u.id = m.user_id
JOIN workspace w ON m.workspace_id = w.id
JOIN plan p ON w.plan_id = p.id;

COMMENT ON TABLE "user" IS 'OAuth-authenticated users (Google or GitHub)';
COMMENT ON TABLE plan IS 'Subscription plan definitions (Free, Haste I/II/III)';
COMMENT ON TABLE workspace IS 'Multi-tenant workspace container for projects and members';
COMMENT ON TABLE membership IS 'User-workspace associations with role-based access';
COMMENT ON TABLE project IS 'Code project within a workspace (separate codebase)';
COMMENT ON TABLE ai_usage IS 'AI API usage tracking for quota enforcement';
COMMENT ON TABLE audit_log IS 'Security and compliance audit trail';

