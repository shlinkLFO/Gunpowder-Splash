# Architectural Proposal: Optimistic Locking for Concurrent Edits

**Author:** Gemini (Architect)
**Date:** November 8, 2025
**Status:** PROPOSED

## 1. Problem Statement

The current file storage system is vulnerable to a "last-write-wins" race condition. When two or more users simultaneously edit the same file and save their changes, the last save overwrites all previous saves, leading to unintentional data loss. The system provides no conflict detection or resolution mechanism.

This issue is documented in `docs/COLLABORATION.md` and was flagged as a medium-severity risk in the recent architectural audit.

## 2. Proposed Solution

To resolve this, we will implement an optimistic locking mechanism using Google Cloud Storage (GCS) object generation numbers. This strategy prevents stale data from overwriting newer versions by verifying that the file has not been modified since the user last read it.

The core principle is:
1. When a client fetches a file, the server provides the file's current generation number.
2. When the client saves the file, it sends back the generation number it last received.
3. The server uses this number as a precondition for the GCS write operation. If the number matches the live object's generation, the write succeeds. If it mismatches (because another user saved in the meantime), the write fails with a precondition error.
4. This error is propagated to the client as an `HTTP 409 Conflict`, signaling that their version is out of date and they must re-fetch the latest version before trying to save again.

## 3. Implementation Steps

### 3.1. Storage Service Layer (`backend/app/storage.py`)

- **`list_files` Method**:
  - The metadata dictionary for each blob must be updated to include the `generation` number.
  - `files.append({"path": ..., "size": ..., "generation": blob.generation})`
- **`write_file` Method**:
  - The method signature must be updated to accept an optional `generation_match: int = None` parameter.
  - The `blob.upload_from_string` call must be modified to use the `if_generation_match` precondition.
  - A `try...except` block must be added to catch `google.cloud.exceptions.PreconditionFailed` and re-raise it as a specific `HTTPException`.

```python
# Example modification in storage.py
from google.cloud.exceptions import PreconditionFailed

# ...

def write_file(self, ..., generation_match: int = None):
    # ...
    try:
        blob.upload_from_string(
            content,
            content_type=...,
            if_generation_match=generation_match
        )
        # ...
    except PreconditionFailed:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File has been modified by another user. Please refresh and try again."
        )
    except Exception:
        # ...
```

### 3.2. API Layer (`backend/app/routers/projects.py`)

- **`FileResponse` Model**:
  - Add a new optional field: `generation: Optional[int] = None`.
- **`list_files` Endpoint**:
  - Update the response construction to pass the `generation` from the storage service to the `FileResponse` model.
- **`upload_file` Endpoint**:
  - Add an optional `generation: Optional[int] = None` field to the request, likely as a form field or header.
  - Pass this `generation` value to the `storage_service.write_file` method.

### 3.3. Frontend Implementation

- The frontend state management for files must be updated to store the `generation` number received from the API.
- When a user saves a file, the stored `generation` number must be included in the `upload_file` request.
- The frontend must implement logic to handle an `HTTP 409 Conflict` response. This should involve:
  - Notifying the user that the file has been updated.
  - Discarding the user's local changes.
  - Re-fetching the latest version of the file from the server.
  - (Optional) A more advanced implementation could use a diffing library to show the user the conflict and help them merge their changes.

## 4. Benefits

- **Data Integrity**: Prevents accidental data loss from concurrent edits.
- **Explicit Conflict Handling**: Provides a clear and immediate signal to users when a conflict occurs.
- **Low Overhead**: Leverages a built-in feature of GCS, avoiding the need for a complex locking system or a separate versioning database.

## 5. Backwards Compatibility

This change can be implemented with backward compatibility. If no `generation` is provided in the upload request, the `if_generation_match` precondition can be omitted, preserving the old "last-write-wins" behavior. This allows for a phased rollout, with the frontend being updated to support the new mechanism without breaking older clients.
