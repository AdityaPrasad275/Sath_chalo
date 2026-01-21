---
description: How to add npm packages in Docker environment
---

# Adding NPM Packages

Since the frontend runs in Docker, use this command to add packages:

```bash
// turbo
docker compose exec frontend npm install <package-name>
```

Example:
```bash
docker compose exec frontend npm install react-router-dom
```

This installs directly into the running container without needing a rebuild.

**Note**: The package will also be added to `package.json`, so future builds will include it.

## If container isn't running
If you need to rebuild from scratch:
```bash
docker compose build --no-cache frontend && docker compose up
```
