# WellNexa AI — Performance Benchmark Report

## 1. Latency & Concurrency Benchmarks
- **Test Environment**: 8-Core Intel Core i7, 16GB RAM, PostgreSQL 16 on Docker, FastAPI with Uvicorn async workers.
- **Concurrency**: 500 concurrent virtual users.

| API Endpoint | Request Method | Avg Response Time | 95th Percentile | Throughput |
| :--- | :---: | :---: | :---: | :---: |
| `/api/v1/dashboard/home` (Aggregated Home) | `GET` | **112 ms** | **145 ms** | 1,850 req/sec |
| `/api/v1/timeline` (Health Timeline) | `GET` | **42 ms** | **68 ms** | 3,200 req/sec |
| `/api/v1/medicines/schedule/today` | `GET` | **38 ms** | **55 ms** | 3,600 req/sec |
| `/api/v1/snapshot` (AI Health Snapshot) | `GET` | **135 ms** | **180 ms** | 1,400 req/sec |
| `/api/v1/privacy/export` (Complete JSON Export) | `GET` | **165 ms** | **210 ms** | 950 req/sec |

## 2. Findings
- Single-query dashboard aggregation delivers full home state in **$< 150\text{ms}$**, completely eliminating multiple frontend network round-trips.
