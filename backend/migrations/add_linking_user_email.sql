-- Migration: Add linking_user_email to oauth_state table
-- Date: 2025-11-14

-- Add column to track which user is requesting account linking
ALTER TABLE oauth_state ADD COLUMN IF NOT EXISTS linking_user_email VARCHAR;

