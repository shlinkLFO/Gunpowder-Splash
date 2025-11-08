# Beacon Studio - Open Source Licenses and Attributions

Beacon Studio is built using open-source software and complies with all applicable licenses.

---

## Primary Codebase

### Code OSS (Visual Studio Code - Open Source)

Beacon Studio's editor is based on the MIT-licensed Code OSS project:

- **Project**: microsoft/vscode
- **Repository**: https://github.com/microsoft/vscode
- **License**: MIT License
- **Copyright**: Copyright (c) 2015 - present Microsoft Corporation

```
MIT License

Copyright (c) 2015 - present Microsoft Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Important**: Beacon Studio is NOT affiliated with or endorsed by Microsoft Corporation. We use the MIT-licensed Code OSS codebase and do not use or redistribute the official Visual Studio Code product or VS Code Server.

---

## Backend Dependencies

### FastAPI

- **License**: MIT License
- **Project**: https://github.com/tiangolo/fastapi
- **Copyright**: Copyright (c) 2018 Sebastián Ramírez

### SQLAlchemy

- **License**: MIT License
- **Project**: https://github.com/sqlalchemy/sqlalchemy
- **Copyright**: Copyright (c) 2005-2024 Michael Bayer and contributors

### Pydantic

- **License**: MIT License
- **Project**: https://github.com/pydantic/pydantic
- **Copyright**: Copyright (c) 2017 Samuel Colvin and contributors

### Google Cloud Client Libraries

- **License**: Apache License 2.0
- **Project**: https://github.com/googleapis/python-storage
- **Copyright**: Copyright 2014 Google LLC

### Stripe Python Library

- **License**: MIT License
- **Project**: https://github.com/stripe/stripe-python
- **Copyright**: Copyright (c) Stripe

### python-jose

- **License**: MIT License
- **Project**: https://github.com/mpdavis/python-jose
- **Copyright**: Copyright (c) Michael Davis

---

## Frontend Dependencies (in addition to Code OSS)

### React (if used in custom UI)

- **License**: MIT License
- **Project**: https://github.com/facebook/react
- **Copyright**: Copyright (c) Meta Platforms, Inc.

### TypeScript

- **License**: Apache License 2.0
- **Project**: https://github.com/microsoft/TypeScript
- **Copyright**: Copyright (c) Microsoft Corporation

---

## AI Provider Integrations

### Google Generative AI (Gemini)

- **License**: Subject to Google Cloud Terms of Service
- **Documentation**: https://cloud.google.com/terms
- **Usage**: API client only, no bundled code

### LM Studio / Ollama

- **License**: Client integration via HTTP API
- **Note**: No bundled code; users bring their own local models
- **Model Licenses**: Users must ensure their chosen models permit commercial use

---

## Infrastructure & Cloud Services

### Google Cloud Platform

- **Terms of Service**: https://cloud.google.com/terms
- **Services Used**: Cloud Run, Cloud SQL, Cloud Storage, Cloud Scheduler
- **Note**: Infrastructure only, no code dependencies

### PostgreSQL

- **License**: PostgreSQL License (similar to MIT/BSD)
- **Project**: https://www.postgresql.org/
- **Copyright**: Copyright (c) 1996-2024, PostgreSQL Global Development Group

---

## Legal Compliance Statement

### Beacon Studio Product

- **Name**: Beacon Studio
- **Codename**: Gunpowder Splash
- **URL**: https://glowstone.red/beacon-studio
- **License**: Proprietary (SaaS)
- **Based On**: Code OSS (MIT License)

### Obligations Fulfilled

1. MIT License preserved in source and displayed to users
2. No use of official Visual Studio Code product or branding
3. No use of VS Code Server or proprietary Microsoft components
4. All Microsoft trademarks and branding removed
5. Full attribution given to Code OSS and all dependencies
6. All third-party licenses compatible with commercial SaaS use

### User Rights

Users of Beacon Studio have the following rights under our service:

1. **Data Export**: Export your entire workspace within 30 days of cancellation
2. **Data Deletion**: Request deletion of your data (GDPR/CCPA)
3. **Transparency**: View this license file and all third-party attributions
4. **Support**: Contact support for any licensing questions

### Open Source Contributions

Beacon Studio is committed to the open-source community:

- We use and respect open-source licenses
- We contribute bug fixes back to upstream projects when applicable
- We acknowledge all open-source contributors

---

## Contact

For licensing questions or concerns:

- **Email**: legal@glowstone.red
- **Website**: https://glowstone.red/beacon-studio/legal

---

## Full License Texts

Complete license texts for all dependencies are available in the source repository:

- `/licenses/code-oss-mit.txt`
- `/licenses/backend-dependencies/`
- `/licenses/frontend-dependencies/`

---

**Last Updated**: November 8, 2025

This document will be displayed prominently in the Beacon Studio application under:
- **Menu**: Help → About Beacon Studio → Licenses
- **Web UI**: Settings → Legal → Open Source Licenses

