---
title: AFC-CAE API
emoji: 🏦
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# Automated Financial Controls & Continuous Auditing Engine (AFC-CAE) — API

FastAPI backend untuk pipeline audit keuangan otomatis.

## Endpoints

| Method | Path | Deskripsi |
|--------|------|-----------|
| GET | `/health` | Health check |
| POST | `/api/v1/audit/ingest` | Upload dataset (CSV/Parquet) |
| GET | `/api/v1/audit/status/{run_id}` | Cek status audit |

## Storage

Laporan audit disimpan di persistent bucket (`/data`).
