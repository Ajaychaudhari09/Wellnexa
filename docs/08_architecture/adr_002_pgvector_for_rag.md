# Architecture Decision Record (ADR 002)
## Selection of PostgreSQL + pgvector for RAG Vector Storage

### Status: ACCEPTED

### Context
Retrieval-Augmented Generation (RAG) requires vector embeddings storage for clinical guideline documents (WHO, ICMR, ADA). We evaluated standalone vector databases (Pinecone, Qdrant, ChromaDB) versus PostgreSQL's native `pgvector` extension.

### Decision
We selected **PostgreSQL with the `pgvector` extension**.

### Rationale
1. **Single Database Infrastructure**: Eliminates the cost and operational overhead of running a separate vector database.
2. **Relational-Vector Hybrid Queries**: Allows single-query joins between patient relational baseline data and vector similarity search.
3. **ACID Compliance & Backup**: Embedding vectors are backed up, migrated, and secured alongside core health records.
