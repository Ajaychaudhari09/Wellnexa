# WellNexa AI — Economic Feasibility & Cost Estimation

## 1. Student / Capstone Project Cost Model (Target: $0 - $10 / month)
| Component | Technology / Service | Tier / Plan | Monthly Cost (USD) |
| :--- | :--- | :--- | :--- |
| **Backend & Compute** | FastAPI on Docker / Render / Railway | Free / Hobby Tier | $0.00 |
| **Database** | PostgreSQL + pgvector on Supabase / Neon | Free Tier (500MB DB) | $0.00 |
| **Document Storage** | Local Docker Volume / Cloudflare R2 | Free Tier (10GB) | $0.00 |
| **AI LLM API** | Gemini 1.5 Flash / Interactions API | Free Rate-Limited Tier | $0.00 |
| **Frontend Hosting** | Flutter Web on GitHub Pages / Vercel | Free Tier | $0.00 |
| **Total Estimated Student Cost** | | | **$0.00 / month** |

## 2. Production Commercial Scale Cost Model (10,000 Active Users)
- Managed PostgreSQL (AWS RDS db.t4g.medium): ~$45 / month
- Container Compute (AWS ECS / Fargate): ~$60 / month
- Cloudflare R2 / S3 Document Storage (500GB): ~$10 / month
- LLM API Token Consumption (Batch + RAG cache): ~$80 / month
- **Total Production Cost**: ~$195 / month (~$0.0195 per active user / month).

## 3. Economic Feasibility Verdict
**HIGHLY FEASIBLE**: Complete capstone project can be developed, tested, and deployed for **$0**, with highly viable commercial economics.
