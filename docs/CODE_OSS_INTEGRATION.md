# Code OSS Integration Guide for Beacon Studio

This document provides guidance on integrating Code OSS (open-source Visual Studio Code) into Beacon Studio while maintaining legal compliance.

## Legal Requirements

### MUST DO

1. **Use Code OSS, NOT VS Code**
   - Clone from: `https://github.com/microsoft/vscode`
   - Build from source using the MIT-licensed codebase
   - DO NOT download or redistribute official VS Code binaries

2. **Preserve MIT License**
   - Keep the MIT license file in the repository
   - Display license and attributions in an "About" page
   - Acknowledge: "Beacon Studio is based on microsoft/vscode (MIT License)"

3. **Remove Microsoft Branding**
   - Replace all Microsoft logos with Beacon Studio branding
   - Change product name throughout UI
   - Remove telemetry endpoints (telemetry.send, etc.)
   - Remove references to "Visual Studio Code" and "VS Code"

### MUST NOT DO

1. DO NOT use VS Code Server or official remote development server
2. DO NOT use Microsoft's marketplace (use custom extension registry)
3. DO NOT include proprietary Microsoft extensions
4. DO NOT use Microsoft's update service
5. DO NOT use Microsoft's crash reporting

## Building Code OSS for Web

### Prerequisites

```bash
# Install Node.js 18+ and Yarn
node --version  # v18.0.0 or higher
yarn --version  # 1.22.0 or higher

# Install Python and build tools
python --version  # 3.x
```

### Clone and Build

```bash
# Clone Code OSS repository
git clone https://github.com/microsoft/vscode.git beacon-editor
cd beacon-editor

# Checkout stable version (example: 1.85.0)
git checkout 1.85.0

# Install dependencies
yarn install

# Build for web
yarn gulp vscode-web-min

# The built files will be in ../vscode-web
```

### Branding Modifications

Create a custom build script that:

1. **Replace Product Configuration**

Edit `product.json`:

```json
{
  "nameShort": "Beacon Studio",
  "nameLong": "Beacon Studio",
  "applicationName": "beacon-studio",
  "win32AppId": "{{BeaconStudio}}",
  "urlProtocol": "beacon",
  "dataFolderName": ".beacon-studio",
  "quality": "stable",
  "extensionsGallery": {
    "serviceUrl": "https://glowstone.red/beacon-studio/extensions",
    "itemUrl": "https://glowstone.red/beacon-studio/extensions/item"
  },
  "linkProtectionTrustedDomains": [
    "https://glowstone.red"
  ],
  "documentationUrl": "https://glowstone.red/beacon-studio/docs",
  "feedbackUrl": "https://glowstone.red/beacon-studio/feedback",
  "serverLicense": [],
  "serverLicensePrompt": ""
}
```

2. **Replace Logos and Icons**

```bash
# Replace icon files
src/vs/workbench/browser/parts/activitybar/media/
src/vs/workbench/browser/parts/titlebar/media/
resources/web/
```

Replace with Beacon Studio branded assets:
- Application logo
- Favicon
- Activity bar icons
- Welcome page graphics

3. **Disable Telemetry**

Edit `src/vs/platform/telemetry/common/telemetryService.ts`:

```typescript
// Disable all telemetry
export class TelemetryService implements ITelemetryService {
  // ... existing code ...
  
  publicLog(eventName: string, data?: any): void {
    // NO-OP: Beacon Studio does not collect telemetry
    return;
  }
  
  publicLog2<E extends ClassifiedEvent<OmitMetadata<T>>>(
    eventName: string,
    data?: StrictPropertyCheck<T, E>
  ): void {
    // NO-OP: Beacon Studio does not collect telemetry
    return;
  }
}
```

4. **Remove Update Service**

Edit `src/vs/platform/update/common/update.ts`:

```typescript
// Disable automatic updates
export class UpdateService implements IUpdateService {
  checkForUpdates(): Promise<void> {
    // Beacon Studio manages updates separately
    return Promise.resolve();
  }
}
```

## Custom File System Provider

Code OSS needs a file system provider to connect to Beacon's backend storage.

### Create Custom File System Provider

`src/vs/workbench/services/beacon/browser/beaconFileSystemProvider.ts`:

```typescript
import { Disposable } from 'vs/base/common/lifecycle';
import { URI } from 'vs/base/common/uri';
import { FileSystemProviderCapabilities, FileSystemProvider, FileChangeEvent, FileChangeType, IFileChange } from 'vs/platform/files/common/files';
import { Event, Emitter } from 'vs/base/common/event';

export class BeaconFileSystemProvider extends Disposable implements FileSystemProvider {
  
  private _onDidChangeFile = this._register(new Emitter<readonly IFileChange[]>());
  readonly onDidChangeFile: Event<readonly IFileChange[]> = this._onDidChangeFile.event;

  capabilities = FileSystemProviderCapabilities.FileReadWrite 
    | FileSystemProviderCapabilities.PathCaseSensitive;

  constructor(
    private readonly apiEndpoint: string,
    private readonly authToken: string
  ) {
    super();
  }

  async readFile(resource: URI): Promise<Uint8Array> {
    const response = await fetch(
      `${this.apiEndpoint}/projects/${this.getProjectId(resource)}/files/${resource.path}`,
      {
        headers: { Authorization: `Bearer ${this.authToken}` }
      }
    );
    
    if (!response.ok) {
      throw new Error(`Failed to read file: ${response.statusText}`);
    }
    
    const buffer = await response.arrayBuffer();
    return new Uint8Array(buffer);
  }

  async writeFile(resource: URI, content: Uint8Array, options: any): Promise<void> {
    const formData = new FormData();
    formData.append('file', new Blob([content]));
    
    await fetch(
      `${this.apiEndpoint}/projects/${this.getProjectId(resource)}/files?file_path=${resource.path}`,
      {
        method: 'POST',
        headers: { Authorization: `Bearer ${this.authToken}` },
        body: formData
      }
    );
  }

  async delete(resource: URI, options: any): Promise<void> {
    await fetch(
      `${this.apiEndpoint}/projects/${this.getProjectId(resource)}/files/${resource.path}`,
      {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${this.authToken}` }
      }
    );
  }

  // Implement other required methods...
  
  private getProjectId(uri: URI): string {
    // Extract project ID from URI authority
    return uri.authority;
  }
}
```

### Register File System Provider

`src/vs/workbench/services/beacon/browser/beaconService.ts`:

```typescript
import { IFileService } from 'vs/platform/files/common/files';
import { BeaconFileSystemProvider } from './beaconFileSystemProvider';
import { URI } from 'vs/base/common/uri';

export class BeaconService {
  
  constructor(
    @IFileService private fileService: IFileService
  ) {
    this.registerFileSystemProvider();
  }
  
  private registerFileSystemProvider(): void {
    const provider = new BeaconFileSystemProvider(
      window.BEACON_API_ENDPOINT,
      window.BEACON_AUTH_TOKEN
    );
    
    this.fileService.registerProvider('beacon', provider);
  }
}
```

## Beacon-Specific UI Extensions

### Global Project Switcher

Add a project switcher button to the activity bar:

`src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`:

```typescript
// Add project switcher action
class ProjectSwitcherAction extends Action {
  constructor() {
    super(
      'workbench.action.switchProject',
      'Switch Project',
      'codicon-folder-opened'
    );
  }
  
  async run(): Promise<void> {
    // Open project switcher dialog
    const projectService = accessor.get(IBeaconProjectService);
    await projectService.showProjectSwitcher();
  }
}
```

### OSS View ⇄ Web-Edit View Toggle

Add a view toggle in the title bar:

`src/vs/workbench/browser/parts/titlebar/titlebarPart.ts`:

```typescript
class ViewModeToggleAction extends Action {
  constructor() {
    super(
      'workbench.action.toggleViewMode',
      'Toggle View Mode',
      'codicon-layout'
    );
  }
  
  async run(): Promise<void> {
    const layoutService = accessor.get(ILayoutService);
    layoutService.toggleViewMode();
  }
}
```

### Custom Welcome Page

Replace the default welcome page with Beacon-specific content:

`src/vs/workbench/contrib/welcome/page/browser/welcomePage.html`:

```html
<div class="welcomePageContainer">
  <div class="beacon-welcome">
    <h1>Welcome to Beacon Studio</h1>
    <p>Your collaborative cloud IDE</p>
    
    <div class="quick-actions">
      <button onclick="beacon.createProject()">
        Create New Project
      </button>
      <button onclick="beacon.openRecent()">
        Open Recent
      </button>
      <button onclick="beacon.viewAccount()">
        View Account
      </button>
    </div>
    
    <div class="plan-info">
      <p>Current Plan: <strong id="current-plan">Loading...</strong></p>
      <a href="#" onclick="beacon.viewSubscription()">Manage Subscription</a>
    </div>
  </div>
</div>
```

## Deployment Configuration

### Web Server Setup

Serve the built Code OSS web application:

```nginx
# nginx.conf for Code OSS frontend
server {
    listen 80;
    server_name glowstone.red;
    
    root /app/vscode-web;
    index index.html;
    
    # Code OSS static files
    location /beacon-studio/editor/ {
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options "nosniff";
        add_header X-XSS-Protection "1; mode=block";
    }
    
    # Backend API proxy
    location /beacon-studio/api/ {
        proxy_pass http://beacon-backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket for live collaboration (future)
    location /beacon-studio/ws/ {
        proxy_pass http://beacon-backend:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Environment Injection

Inject Beacon configuration into the web app:

`index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Beacon Studio</title>
    <script>
        // Inject Beacon configuration
        window.BEACON_CONFIG = {
            apiEndpoint: 'https://glowstone.red/beacon-studio/api/v1',
            wsEndpoint: 'wss://glowstone.red/beacon-studio/ws',
            environment: 'production'
        };
    </script>
</head>
<body>
    <!-- Code OSS web application -->
</body>
</html>
```

## Extension Marketplace

### Custom Extension Registry

Instead of using Microsoft's marketplace, create a custom extension registry:

1. **Backend Endpoint**: `/api/v1/extensions`
2. **Storage**: Store extensions in Cloud Storage
3. **Metadata**: Store extension metadata in Postgres

```sql
CREATE TABLE extension (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  display_name TEXT NOT NULL,
  version TEXT NOT NULL,
  description TEXT,
  publisher TEXT NOT NULL,
  gcs_path TEXT NOT NULL,
  downloads INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

## Testing

### Browser Compatibility

Test in:
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Performance Benchmarks

- Initial load: < 3 seconds
- File open: < 200ms
- Save operation: < 500ms
- Project switch: < 1 second

## Security Considerations

1. **Content Security Policy**

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' 'unsafe-eval'; 
               style-src 'self' 'unsafe-inline'; 
               connect-src 'self' https://glowstone.red;">
```

2. **Authentication**
   - All API calls must include JWT token
   - Tokens expire after 1 hour
   - Refresh tokens used for re-authentication

3. **File Access Control**
   - Backend validates all file operations
   - Check workspace membership before serving files
   - Enforce storage quotas server-side

## Next Steps

1. Build Code OSS for web with branding modifications
2. Implement custom file system provider
3. Create Beacon-specific UI extensions
4. Set up custom extension marketplace
5. Deploy to Cloud Run with nginx frontend
6. Test across browsers and devices

## References

- Code OSS Repository: https://github.com/microsoft/vscode
- VSCode Web Documentation: https://code.visualstudio.com/docs/editor/vscode-web
- File System Provider API: https://code.visualstudio.com/api/references/vscode-api#FileSystemProvider

