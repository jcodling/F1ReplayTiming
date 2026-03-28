# Synology NAS Deployment Guide

## Overview

Two-service stack: FastAPI backend (port 8000) + Next.js frontend (port 3000). The existing `docker-compose.yml` works as-is — you just need to replace `localhost` with your NAS's local IP so devices on your network can reach both services.

---

## Prerequisites

- Synology DSM 7.2+ with **Container Manager** installed (Package Center)
- SSH access to the NAS, or use File Station to upload files
- Your NAS's local IP — DSM → Control Panel → Network → Network Interface (e.g. `192.168.1.50`)

---

## Step 1 — Copy the repo to the NAS

**Option A — SSH (recommended):**
```bash
rsync -av --exclude '.git' --exclude '__pycache__' --exclude 'node_modules' \
  /path/to/F1ReplayTiming/ \
  your-nas-user@192.168.1.50:/volume1/docker/F1ReplayTiming/
```

**Option B — File Station:**
Zip the repo, upload via File Station, unzip into `/volume1/docker/F1ReplayTiming/`.

---

## Step 2 — Edit docker-compose.yml

Replace `localhost` with your NAS IP in two places:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - FRONTEND_URL=http://192.168.1.50:3000   # <-- your NAS IP
      - DATA_DIR=/data
    volumes:
      - f1data:/data
      - f1cache:/data/fastf1-cache

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://192.168.1.50:8000  # <-- your NAS IP
    depends_on:
      - backend

volumes:
  f1data:
  f1cache:
```

**Why these two vars matter:**
- `FRONTEND_URL` → CORS origin the backend allows (must match what your browser uses to reach the frontend)
- `NEXT_PUBLIC_API_URL` → where the frontend JavaScript sends API/WebSocket requests (must be reachable from your browser)

---

## Step 3 — Deploy via Container Manager

1. Open **Container Manager** in DSM
2. Go to **Project** → **Create**
3. **Project name**: `f1replaytiming`
4. **Path**: `/volume1/docker/F1ReplayTiming`
5. Container Manager detects `docker-compose.yml` automatically
6. Click **Next** → **Done**
7. First build takes 5–15 min (compiling Python deps + Node.js)

---

## Step 4 — Access the app

Once both containers show **Running**, open any browser on your home network:

**`http://192.168.1.50:3000`**

---

## Notes

**First-run data download:** FastF1 downloads session telemetry on first load (~hundreds of MB per session). Cached in the `f1cache` volume after that — subsequent loads are instant.

**Persistent data:** Both Docker volumes survive container restarts. They live under `/volume1/@docker/volumes/` on the NAS.

**Ports:** Synology doesn't firewall internal LAN traffic by default — ports 3000 and 8000 are immediately accessible from other devices on the same network.

**Updating:** After a `git pull`, re-deploy via SSH:
```bash
cd /volume1/docker/F1ReplayTiming
docker compose up -d --build
```
Or use Container Manager → Project → Stop → rebuild.

**Optional passphrase auth:** Add to the backend service in `docker-compose.yml`:
```yaml
- AUTH_ENABLED=true
- AUTH_PASSPHRASE=your-passphrase-here
```

---

## Verification

1. Container Manager shows both containers **Running**
2. `http://192.168.1.50:8000/api/health` → `{"status": "ok"}`
3. `http://192.168.1.50:3000` loads the session picker
4. Select a past race — data loads and replay works
