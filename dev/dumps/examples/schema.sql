-- DevOps CI/CD Pipeline & Operations Platform
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE organizations(
    org_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_name varchar(255) NOT NULL,
    plan_tier varchar(50),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE teams(
    team_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id uuid NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    team_name varchar(255) NOT NULL,
    team_type varchar(50)
);

CREATE TABLE projects(
    project_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id uuid NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    project_name varchar(255) NOT NULL,
    description text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repositories(
    repo_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id uuid NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    repo_name varchar(255) NOT NULL,
    git_url text,
    default_branch varchar(100) DEFAULT 'main'
);

CREATE TABLE branches(
    branch_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    repo_id uuid NOT NULL REFERENCES repositories(repo_id) ON DELETE CASCADE,
    branch_name varchar(255) NOT NULL,
    is_protected boolean DEFAULT FALSE,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE commits(
    commit_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id uuid NOT NULL REFERENCES branches(branch_id) ON DELETE CASCADE,
    commit_hash varchar(40) UNIQUE NOT NULL,
    author_email varchar(255),
    commit_message text,
    committed_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pull_requests(
    pr_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_branch_id uuid NOT NULL REFERENCES branches(branch_id) ON DELETE CASCADE,
    target_branch_id uuid NOT NULL REFERENCES branches(branch_id) ON DELETE RESTRICT,
    head_commit_id uuid REFERENCES commits(commit_id),
    title varchar(500),
    description text,
    status varchar(20) CHECK (status IN ('open', 'merged', 'closed', 'draft')),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE code_reviews(
    review_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    pr_id uuid NOT NULL REFERENCES pull_requests(pr_id) ON DELETE CASCADE,
    reviewer_email varchar(255),
    status varchar(20) CHECK (status IN ('pending', 'approved', 'changes_requested', 'commented')),
    reviewed_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE builds(
    build_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    commit_id uuid NOT NULL REFERENCES commits(commit_id) ON DELETE CASCADE,
    build_number integer NOT NULL,
    status varchar(20) CHECK (status IN ('queued', 'running', 'success', 'failed', 'cancelled')),
    started_at timestamp,
    completed_at timestamp,
    duration_seconds integer
);

CREATE TABLE build_artifacts(
    artifact_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    build_id uuid NOT NULL REFERENCES builds(build_id) ON DELETE CASCADE,
    artifact_name varchar(255),
    artifact_type varchar(50),
    file_size_bytes bigint,
    storage_url text
);

CREATE TABLE test_runs(
    test_run_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    build_id uuid NOT NULL REFERENCES builds(build_id) ON DELETE CASCADE,
    test_suite_name varchar(255),
    total_tests integer,
    passed_tests integer,
    failed_tests integer,
    skipped_tests integer,
    started_at timestamp,
    completed_at timestamp
);

CREATE TABLE test_cases(
    test_case_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_run_id uuid NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    test_name varchar(500),
    status varchar(20) CHECK (status IN ('passed', 'failed', 'skipped', 'error')),
    duration_ms integer,
    error_message text
);

CREATE TABLE environments(
    env_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id uuid NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    env_name varchar(100) CHECK (env_name IN ('development', 'staging', 'production', 'qa')),
    cluster_name varchar(255),
    region varchar(100)
);

CREATE TABLE deployments(
    deployment_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    artifact_id uuid NOT NULL REFERENCES build_artifacts(artifact_id) ON DELETE RESTRICT,
    env_id uuid NOT NULL REFERENCES environments(env_id) ON DELETE RESTRICT,
    deployed_by varchar(255),
    deployment_strategy varchar(50),
    status varchar(20) CHECK (status IN ('pending', 'in_progress', 'success', 'failed', 'rolled_back')),
    started_at timestamp DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp
);

CREATE TABLE deployment_logs(
    log_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    deployment_id uuid NOT NULL REFERENCES deployments(deployment_id) ON DELETE CASCADE,
    log_level varchar(20),
    log_message text,
    logged_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE monitoring_metrics(
    metric_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    deployment_id uuid NOT NULL REFERENCES deployments(deployment_id) ON DELETE CASCADE,
    metric_name varchar(255),
    metric_value DECIMAL(15, 4),
    unit varchar(50),
    recorded_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE alerts(
    alert_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_id uuid NOT NULL REFERENCES monitoring_metrics(metric_id) ON DELETE CASCADE,
    severity varchar(20) CHECK (severity IN ('info', 'warning', 'critical')),
    alert_message text,
    triggered_at timestamp DEFAULT CURRENT_TIMESTAMP,
    acknowledged boolean DEFAULT FALSE
);

CREATE TABLE incidents(
    incident_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id uuid NOT NULL REFERENCES alerts(alert_id) ON DELETE RESTRICT,
    incident_number varchar(50) UNIQUE NOT NULL,
    title varchar(500),
    severity varchar(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status varchar(20) CHECK (status IN ('open', 'investigating', 'resolved', 'closed')),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE incident_updates(
    update_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id uuid NOT NULL REFERENCES incidents(incident_id) ON DELETE CASCADE,
    update_message text,
    updated_by varchar(255),
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE incident_resolutions(
    resolution_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id uuid NOT NULL REFERENCES incidents(incident_id) ON DELETE CASCADE,
    resolution_notes text,
    root_cause text,
    resolved_by varchar(255),
    resolved_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post_mortems(
    post_mortem_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    resolution_id uuid NOT NULL REFERENCES incident_resolutions(resolution_id) ON DELETE CASCADE,
    document_url text,
    lessons_learned text,
    action_items text,
    published_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE team_members(
    member_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id uuid NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    email varchar(255) NOT NULL,
    role VARCHAR(100),
    joined_at timestamp DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE code_reviews
    ADD COLUMN reviewer_member_id uuid REFERENCES team_members(member_id);

CREATE TABLE deployment_approvals(
    approval_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    deployment_id uuid NOT NULL REFERENCES deployments(deployment_id) ON DELETE CASCADE,
    approver_member_id uuid NOT NULL REFERENCES team_members(member_id),
    approved_at timestamp DEFAULT CURRENT_TIMESTAMP,
    approval_status varchar(20) CHECK (approval_status IN ('approved', 'rejected'))
);

CREATE TABLE incident_assignments(
    assignment_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id uuid NOT NULL REFERENCES incidents(incident_id) ON DELETE CASCADE,
    assigned_member_id uuid NOT NULL REFERENCES team_members(member_id),
    assigned_at timestamp DEFAULT CURRENT_TIMESTAMP,
    role_in_incident varchar(100)
);

CREATE TABLE tags(
    tag_id serial PRIMARY KEY,
    tag_name varchar(100) UNIQUE NOT NULL,
    color varchar(7)
);

CREATE TABLE project_tags(
    project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
    tag_id integer REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (project_id, tag_id)
);

CREATE TABLE commit_tags(
    commit_id uuid REFERENCES commits(commit_id) ON DELETE CASCADE,
    tag_id integer REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (commit_id, tag_id)
);

CREATE TABLE incident_tags(
    incident_id uuid REFERENCES incidents(incident_id) ON DELETE CASCADE,
    tag_id integer REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (incident_id, tag_id)
);

-- Indexes
CREATE INDEX idx_teams_org ON teams(org_id);

CREATE INDEX idx_projects_team ON projects(team_id);

CREATE INDEX idx_repos_project ON repositories(project_id);

CREATE INDEX idx_branches_repo ON branches(repo_id);

CREATE INDEX idx_commits_branch ON commits(branch_id);

CREATE INDEX idx_prs_source ON pull_requests(source_branch_id);

CREATE INDEX idx_prs_target ON pull_requests(target_branch_id);

CREATE INDEX idx_reviews_pr ON code_reviews(pr_id);

CREATE INDEX idx_builds_commit ON builds(commit_id);

CREATE INDEX idx_artifacts_build ON build_artifacts(build_id);

CREATE INDEX idx_test_runs_build ON test_runs(build_id);

CREATE INDEX idx_test_cases_run ON test_cases(test_run_id);

CREATE INDEX idx_environments_project ON environments(project_id);

CREATE INDEX idx_deployments_artifact ON deployments(artifact_id);

CREATE INDEX idx_deployments_env ON deployments(env_id);

CREATE INDEX idx_logs_deployment ON deployment_logs(deployment_id);

CREATE INDEX idx_metrics_deployment ON monitoring_metrics(deployment_id);

CREATE INDEX idx_alerts_metric ON alerts(metric_id);

CREATE INDEX idx_incidents_alert ON incidents(alert_id);

CREATE INDEX idx_updates_incident ON incident_updates(incident_id);

CREATE INDEX idx_resolutions_incident ON incident_resolutions(incident_id);

CREATE INDEX idx_postmortems_resolution ON post_mortems(resolution_id);

