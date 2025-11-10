#!/usr/bin/env bash

# Creates or updates Secret Manager secrets using values from a .env file.
# Usage:
#   ./scripts/create-secrets-from-env.sh [path-to-env]
#
# Defaults to loading "./.env" if no path is supplied.

set -euo pipefail

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Environment file '${ENV_FILE}' not found." >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

create_secret() {
  local secret_name="$1"
  local env_var="$2"

  local secret_value="${!env_var-}"

  if [[ -z "${secret_value}" ]]; then
    echo "Skipping ${secret_name}: ${env_var} is empty or unset" >&2
    return
  fi

  if ! gcloud secrets describe "${secret_name}" >/dev/null 2>&1; then
    echo "Creating secret ${secret_name}"
    printf '%s' "${secret_value}" | gcloud secrets create "${secret_name}" \
      --replication-policy=automatic \
      --data-file=-
  else
    echo "Adding new version to ${secret_name}"
    printf '%s' "${secret_value}" | gcloud secrets versions add "${secret_name}" --data-file=-
  fi
}

secrets=(
  "beacon-google-client-id:GOOGLE_CLIENT_ID"
  "beacon-google-client-secret:GOOGLE_CLIENT_SECRET"
  "beacon-github-client-id:GITHUB_CLIENT_ID"
  "beacon-github-client-secret:GITHUB_CLIENT_SECRET"
  "beacon-stripe-api-key:STRIPE_API_KEY"
  "beacon-stripe-webhook-secret:STRIPE_WEBHOOK_SECRET"
  "beacon-gemini-api-key:GEMINI_API_KEY"
)

for entry in "${secrets[@]}"; do
  secret_name="${entry%%:*}"
  env_var="${entry#*:}"
  create_secret "${secret_name}" "${env_var}"
done

echo "Secret processing complete."

