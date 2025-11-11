# Frequently Asked Questions

## General

### What is Gunpowder Splash?

Gunpowder Splash is a free, open-source collaborative IDE that runs entirely in your browser. It's designed for teams who want to code together without the hassle of local setup.

### Is it really free?

Yes! The free tier includes:
- 0.84 GB of cloud storage
- Ability to share with 1 team member (requires login)
- Unlimited projects
- All core features

### Do I need to create an account?

No! You can use Guest mode to try it instantly. However, to share workspaces with team members, you'll need to sign in with Google or GitHub.

### What's the difference between Guest mode and signing in?

| Feature | Guest Mode | Signed In |
|---------|-----------|-----------|
| Storage | 0.84 GB | 0.84 GB |
| Projects | Unlimited | Unlimited |
| Team Sharing | No | Yes (1 member) |
| Data Persistence | Session only | Permanent |

## Technical

### What languages are supported?

Gunpowder Splash supports 50+ programming languages including:
- Python
- JavaScript/TypeScript
- HTML/CSS
- Java
- C/C++
- Go
- Rust
- Ruby
- PHP
- And many more!

### Can I run code in the browser?

Yes! Python code execution is supported through our backend API. Other languages can be edited with full syntax highlighting and IntelliSense.

### Does it support Jupyter notebooks?

Yes! You can create and execute Jupyter notebooks (.ipynb files) directly in the IDE.

### Can I import/export files?

Yes! You can:
- Upload files from your computer
- Download files to your computer
- Import entire project folders
- Export your workspace

### What about version control?

Git integration is on our roadmap. Currently, you can:
- Download your project as a ZIP
- Use external Git clients
- Copy code to/from GitHub

## Collaboration

### How do I invite team members?

1. Sign in with Google or GitHub
2. Open your workspace settings
3. Click "Add Member"
4. Enter their email address
5. They'll receive an invitation

### What are the different roles?

- **Admin**: Full control, can delete workspace
- **Moderator**: Can manage files and members
- **User**: Can edit files, view-only for settings

### Can multiple people edit the same file?

Currently, file locking prevents conflicts. Real-time collaborative editing is coming in v1.1!

### How many team members can I have?

- Free tier: 1 team member
- Paid tiers: Up to 17 team members

## Data & Privacy

### Where is my data stored?

Your files are stored in Google Cloud Storage with encryption at rest and in transit.

### Is my code private?

Yes! Your workspaces are private by default. Only invited team members can access them.

### Can I delete my data?

Yes! You can delete individual files, projects, or your entire workspace at any time.

### What happens if I exceed my storage limit?

You'll be notified when you reach 80% capacity. At 100%, you'll need to delete files or upgrade to continue uploading.

## Self-Hosting

### Can I host Gunpowder Splash on my own server?

Yes! Gunpowder Splash is open source. See [DEPLOY.md](DEPLOY.md) for deployment instructions.

### What are the system requirements?

Minimum:
- 2 CPU cores
- 4 GB RAM
- 20 GB disk space
- PostgreSQL 15+
- Node.js 20+
- Python 3.11+

Recommended:
- 4 CPU cores
- 8 GB RAM
- 50 GB disk space

### Can I use a different cloud provider?

Yes! While we use Google Cloud Platform, you can adapt the deployment for:
- AWS (S3, RDS, ECS)
- Azure (Blob Storage, SQL Database, Container Instances)
- DigitalOcean
- Self-hosted infrastructure

### Is there enterprise support?

For enterprise deployments, custom features, or support contracts, contact enterprise@shlinx.com

## Troubleshooting

### The editor is slow or unresponsive

Try:
1. Close unused tabs
2. Clear browser cache
3. Use a modern browser (Chrome, Firefox, Edge)
4. Check your internet connection

### Files aren't saving

Check:
1. Your storage quota
2. Internet connection
3. Browser console for errors
4. Try refreshing the page

### I can't invite team members

Make sure:
1. You're signed in (not in Guest mode)
2. You have Admin or Moderator role
3. You haven't reached your team member limit
4. The email address is correct

### OAuth login isn't working

Try:
1. Clear browser cookies
2. Use incognito/private mode
3. Check if pop-ups are blocked
4. Try a different browser

## Contributing

### How can I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Code style guidelines

### I found a security vulnerability

Please email security@shlinx.com instead of opening a public issue.

### Can I add a new feature?

Yes! We welcome contributions. Please:
1. Open a discussion first to get feedback
2. Follow the contribution guidelines
3. Write tests for new features
4. Update documentation

## Roadmap

### What's coming next?

See our [Roadmap](../README.md#roadmap) for upcoming features:
- Real-time collaborative editing
- Terminal access
- Git integration UI
- Extension marketplace
- Mobile responsive design

### Can I request a feature?

Yes! Open a [Discussion](https://github.com/shlinkLFO/Gunpowder-Splash/discussions) with your idea.

## Support

### Where can I get help?

- **Documentation**: [docs/](.)
- **GitHub Issues**: [Report bugs](https://github.com/shlinkLFO/Gunpowder-Splash/issues)
- **Discussions**: [Ask questions](https://github.com/shlinkLFO/Gunpowder-Splash/discussions)
- **Email**: support@shlinx.com

### Is there a community?

Join our growing community:
- GitHub Discussions
- Discord (coming soon)
- Twitter: @shlinxcom (coming soon)

---

**Still have questions?** Open a [Discussion](https://github.com/shlinkLFO/Gunpowder-Splash/discussions) or email support@shlinx.com

