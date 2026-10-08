CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    external_url TEXT,
    source TEXT NOT NULL DEFAULT 'manual',
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    seniority TEXT,
    location TEXT,
    employment_type TEXT,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    match_score NUMERIC(5,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(external_url)
);

CREATE TABLE IF NOT EXISTS skills (
    id BIGSERIAL PRIMARY KEY,
    canonical_name TEXT UNIQUE NOT NULL,
    category TEXT,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id BIGINT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id BIGINT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance NUMERIC(5,2) NOT NULL DEFAULT 1.0,
    required BOOLEAN NOT NULL DEFAULT TRUE,
    evidence TEXT,
    PRIMARY KEY(job_id, skill_id)
);

CREATE TABLE IF NOT EXISTS skill_inventory (
    skill_id BIGINT PRIMARY KEY REFERENCES skills(id) ON DELETE CASCADE,
    current_level NUMERIC(4,2) NOT NULL DEFAULT 0,
    target_level NUMERIC(4,2) NOT NULL DEFAULT 8,
    evidence_level NUMERIC(4,2) NOT NULL DEFAULT 0,
    last_validated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    repo_url TEXT,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'planned',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS project_skills (
    project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    skill_id BIGINT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proof_type TEXT,
    evidence_url TEXT,
    PRIMARY KEY(project_id, skill_id)
);

CREATE TABLE IF NOT EXISTS learning_tasks (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT REFERENCES skills(id),
    job_id BIGINT REFERENCES jobs(id),
    project_id BIGINT REFERENCES projects(id),
    task_type TEXT NOT NULL,
    title TEXT NOT NULL,
    priority NUMERIC(8,3) NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'backlog',
    acceptance_criteria TEXT,
    evidence_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS applications (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT UNIQUE REFERENCES jobs(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'planned',
    applied_at TIMESTAMPTZ,
    response TEXT,
    next_action TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_feedback (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT REFERENCES jobs(id) ON DELETE CASCADE,
    stage TEXT,
    feedback TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_skill_demand (
    skill_id BIGINT PRIMARY KEY REFERENCES skills(id) ON DELETE CASCADE,
    jobs_count INTEGER NOT NULL DEFAULT 0,
    required_count INTEGER NOT NULL DEFAULT 0,
    demand_score NUMERIC(8,3) NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_learning_priority ON learning_tasks(status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_market_demand ON market_skill_demand(demand_score DESC);
