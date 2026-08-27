-- WellNexa Database Initialization Script
-- Enables pgvector extension for AI RAG embeddings and creates necessary initial roles/extensions

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log readiness
DO $$
BEGIN
    RAISE NOTICE 'WellNexa AI database initialized with vector and uuid-ossp extensions.';
END $$;
