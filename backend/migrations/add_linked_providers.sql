-- Migration: Add linked providers support
-- Date: 2025-11-14

-- Add columns for tracking linked providers and separate avatars
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS google_avatar_url VARCHAR;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS github_avatar_url VARCHAR;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS linked_providers VARCHAR DEFAULT '[]';

-- Initialize linked_providers for existing users based on their current provider
UPDATE "user" 
SET linked_providers = '["' || provider || '"]' 
WHERE linked_providers = '[]' OR linked_providers IS NULL;

-- Update avatar URLs to provider-specific columns for existing users
UPDATE "user"
SET google_avatar_url = avatar_url
WHERE provider = 'google' AND google_avatar_url IS NULL;

UPDATE "user"
SET github_avatar_url = avatar_url
WHERE provider = 'github' AND github_avatar_url IS NULL;

