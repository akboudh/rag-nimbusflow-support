# Example Queries and Responses

## Runtime

- openai_configured: True
- embedding_model: text-embedding-3-small
- response_model: gpt-5-mini
- embedding_status: ready

## 1. Do personal API tokens expire after NimbusFlow 4.2?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Documentation: NimbusFlow 4.2 introduces mandatory rotation for personal API tokens. **Personal tokens now expire after 90 days** and users receive reminders starting 14 days before expiration. Existing personal tokens created before 4
- Documentation: Service accounts Service account tokens do **not expire by default**, but administrators can opt into rotation policies at the workspace level. OpenOps recommends rotating service tokens every 180 days even when no hard
- Documentation: The public REST API allows **120 requests per minute per workspace token**. When the limit is exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header in seconds.

Contradictions detected:
- On `personal_token_expiry`, prefer documentation (90 days); conflicting evidence: documentation says 90 days, forum says no expiry.

Top citations:
- [documentation] NimbusFlow 4.2 Release Notes -> Security changes
- [documentation] NimbusFlow 4.2 Release Notes -> Security changes / Service accounts
- [documentation] NimbusFlow Troubleshooting Guide -> API rate limits
- [forum] Do API tokens expire? -> Forum post p3

### Source Usage

{
  "documentation": 3,
  "forum": 2,
  "blog": 0
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `documentation` NimbusFlow 4.2 Release Notes -> Security changes (retrieval=0.484704, rerank=0.601351)
- `forum` Do API tokens expire? -> Forum post p3 (retrieval=0.480528, rerank=0.501289)
- `documentation` NimbusFlow 4.2 Release Notes -> Security changes / Service accounts (retrieval=0.244079, rerank=0.473143)
- `documentation` NimbusFlow Troubleshooting Guide -> API rate limits (retrieval=0.184703, rerank=0.436605)
- `forum` Do API tokens expire? -> Forum post p1 (retrieval=0.470427, rerank=0.434069)

## 2. My desktop agent is stuck on verifying certificate behind a proxy. What should I check?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Forum: Post by openops_eli (support-engineer): The desktop agent uses the operating system trust store instead of a bundled CA file. Import the proxy root certificate into the macOS System keychain, mark it trusted, then restar
- Documentation: If the desktop sync agent shows **Verifying certificate** for longer than 30 seconds: 1. confirm the workspace URL matches the certificate common name 2. confirm the corporate proxy root certificate is present in the **s
- Forum: Post by maya_ops (customer): After adding a corporate HTTPS inspection proxy, the macOS desktop agent never gets past 'Verifying certificate'. Browser access still works.

Top citations:
- [forum] Desktop agent stuck on verifying certificate -> Forum post p2
- [documentation] NimbusFlow Troubleshooting Guide -> Desktop agent certificate errors
- [forum] Desktop agent stuck on verifying certificate -> Forum post p1
- [forum] Desktop agent stuck on verifying certificate -> Forum post p3

### Source Usage

{
  "documentation": 1,
  "forum": 3,
  "blog": 1
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `forum` Desktop agent stuck on verifying certificate -> Forum post p2 (retrieval=0.43129, rerank=0.519843)
- `documentation` NimbusFlow Troubleshooting Guide -> Desktop agent certificate errors (retrieval=0.389936, rerank=0.456595)
- `forum` Desktop agent stuck on verifying certificate -> Forum post p1 (retrieval=0.403025, rerank=0.433769)
- `forum` Desktop agent stuck on verifying certificate -> Forum post p3 (retrieval=0.34274, rerank=0.407893)
- `blog` Tuning NimbusFlow Desktop Sync for Large Repositories -> Proxy and certificate checks (retrieval=0.293827, rerank=0.383771)

## 3. How quickly does SCIM deprovision a removed contractor?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Documentation: SCIM 2.0 provisioning is available on Enterprise plans. New users, profile changes, and deprovision events are applied within **5 minutes** under normal conditions. Administrators can force a resync from **Settings > Sec
- Documentation: Audit exports include login events, role changes, restore operations, API token creation, and SCIM actions. Large exports are streamed and may take several minutes to complete.
- Forum: Post by oliver_admin (customer): If a contractor is removed from Okta, how quickly does NimbusFlow disable their access?

Contradictions detected:
- On `scim_sync_delay`, prefer documentation (5 minutes); conflicting evidence: forum says hourly, forum says hourly.

Top citations:
- [documentation] NimbusFlow Administration Guide -> SCIM provisioning
- [documentation] NimbusFlow Troubleshooting Guide -> Audit log exports
- [forum] How long does SCIM deprovisioning take? -> Forum post p1
- [forum] How long does SCIM deprovisioning take? -> Forum post p2

### Source Usage

{
  "documentation": 2,
  "forum": 3,
  "blog": 0
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `documentation` NimbusFlow Administration Guide -> SCIM provisioning (retrieval=0.264188, rerank=0.46626)
- `forum` How long does SCIM deprovisioning take? -> Forum post p1 (retrieval=0.414498, rerank=0.438435)
- `forum` How long does SCIM deprovisioning take? -> Forum post p2 (retrieval=0.240098, rerank=0.392124)
- `forum` How long does SCIM deprovisioning take? -> Forum post p3 (retrieval=0.204327, rerank=0.379339)
- `documentation` NimbusFlow Troubleshooting Guide -> Audit log exports (retrieval=0.049927, rerank=0.35794)

## 4. What is the API rate limit and how should a client react to 429 errors?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Documentation: The public REST API allows **120 requests per minute per workspace token**. When the limit is exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header in seconds.
- Documentation: Recommended client behavior - honor `Retry-After` exactly - retry with exponential backoff for bursty workloads - spread bulk sync jobs across minute boundaries
- Documentation: If the desktop sync agent shows **Verifying certificate** for longer than 30 seconds: 1. confirm the workspace URL matches the certificate common name 2. confirm the corporate proxy root certificate is present in the **s

Top citations:
- [documentation] NimbusFlow Troubleshooting Guide -> API rate limits
- [documentation] NimbusFlow Troubleshooting Guide -> API rate limits / Recommended client behavior
- [documentation] NimbusFlow Troubleshooting Guide -> Desktop agent certificate errors
- [blog] Preparing for NimbusFlow 4.2 Token Rotation -> What changes in 4.2

### Source Usage

{
  "documentation": 3,
  "forum": 0,
  "blog": 2
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `documentation` NimbusFlow Troubleshooting Guide -> API rate limits (retrieval=0.336375, rerank=0.506551)
- `documentation` NimbusFlow Troubleshooting Guide -> API rate limits / Recommended client behavior (retrieval=0.218038, rerank=0.445051)
- `documentation` NimbusFlow Troubleshooting Guide -> Desktop agent certificate errors (retrieval=0.056343, rerank=0.353097)
- `blog` Preparing for NimbusFlow 4.2 Token Rotation -> What changes in 4.2 (retrieval=0.050294, rerank=0.248392)
- `blog` Preparing for NimbusFlow 4.2 Token Rotation -> Preparing for NimbusFlow 4.2 Token Rotation (retrieval=0.048577, rerank=0.247632)

## 5. Can I restore a workspace from two weeks ago?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Documentation: Restore workflow 1. open **Workspace Settings > Restore** 2. choose a timestamp 3. create a preview workspace 4. validate the preview 5. promote the preview back to production
- Documentation: NimbusFlow stores continuous incremental backups and exposes self-service restore points for the last **30 days**. The target recovery point objective is **30 minutes**. Restores older than 30 days require OpenOps interv
- Documentation: NimbusFlow can map up to **50 IdP groups** to workspace roles. Common patterns are: - `nimbus-admins` -> Workspace Admin - `nimbus-operators` -> Operator - `nimbus-viewers` -> Read Only If a user matches multiple mapped

Contradictions detected:
- On `restore_rpo`, prefer documentation (30 minutes); conflicting evidence: documentation says 30 minutes, blog says 24 hours.
- On `restore_retention`, prefer documentation (30 days); conflicting evidence: documentation says 30 days, blog says nightly snapshots.

Top citations:
- [documentation] NimbusFlow Troubleshooting Guide -> Restore points and retention / Restore workflow
- [documentation] NimbusFlow Troubleshooting Guide -> Restore points and retention
- [documentation] NimbusFlow Administration Guide -> Group and role mapping
- [blog] What We Learned From Rebuilding the Restore Pipeline -> What We Learned From Rebuilding the Restore Pipeline

### Source Usage

{
  "documentation": 3,
  "forum": 0,
  "blog": 2
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `documentation` NimbusFlow Troubleshooting Guide -> Restore points and retention / Restore workflow (retrieval=0.404202, rerank=0.447032)
- `documentation` NimbusFlow Troubleshooting Guide -> Restore points and retention (retrieval=0.135277, rerank=0.314083)
- `documentation` NimbusFlow Administration Guide -> Group and role mapping (retrieval=0.114103, rerank=0.30479)
- `blog` What We Learned From Rebuilding the Restore Pipeline -> What We Learned From Rebuilding the Restore Pipeline (retrieval=0.175004, rerank=0.272184)
- `blog` What We Learned From Rebuilding the Restore Pipeline -> What support teams should remember (retrieval=0.142167, rerank=0.257651)

## 6. What changed for audit exports in NimbusFlow 4.2?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Documentation: Audit exports include login events, role changes, restore operations, API token creation, and SCIM actions. Large exports are streamed and may take several minutes to complete.
- Documentation: Administrators can export audit events from **Settings > Security > Audit Export**. The default export window is the last 7 days. For longer retention, configure scheduled exports to object storage.
- Documentation: Audit exports are now available in **NDJSON** in addition to CSV. NDJSON is recommended for downstream SIEM ingestion and incremental processing.

Top citations:
- [documentation] NimbusFlow Troubleshooting Guide -> Audit log exports
- [documentation] NimbusFlow Administration Guide -> Audit and security controls
- [documentation] NimbusFlow 4.2 Release Notes -> Audit export improvements
- [blog] What We Learned From Rebuilding the Restore Pipeline -> What changed

### Source Usage

{
  "documentation": 3,
  "forum": 0,
  "blog": 2
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `documentation` NimbusFlow Troubleshooting Guide -> Audit log exports (retrieval=0.529235, rerank=0.608706)
- `documentation` NimbusFlow Administration Guide -> Audit and security controls (retrieval=0.397834, rerank=0.554567)
- `documentation` NimbusFlow 4.2 Release Notes -> Audit export improvements (retrieval=0.364662, rerank=0.539068)
- `blog` What We Learned From Rebuilding the Restore Pipeline -> What changed (retrieval=0.105024, rerank=0.246213)
- `blog` Preparing for NimbusFlow 4.2 Token Rotation -> Preparing for NimbusFlow 4.2 Token Rotation (retrieval=0.030661, rerank=0.239703)

## 7. Should unattended jobs use personal tokens or service accounts?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Documentation: Service accounts Service account tokens do **not expire by default**, but administrators can opt into rotation policies at the workspace level. OpenOps recommends rotating service tokens every 180 days even when no hard
- Documentation: NimbusFlow 4.2 introduces mandatory rotation for personal API tokens. **Personal tokens now expire after 90 days** and users receive reminders starting 14 days before expiration. Existing personal tokens created before 4
- Documentation: Deprovisioning behavior When a user is deprovisioned from the identity provider: 1. active NimbusFlow sessions are revoked 2. API tokens owned by that user are disabled 3. queued background jobs keep running until comple

Contradictions detected:
- On `personal_token_expiry`, prefer documentation (90 days); conflicting evidence: documentation says 90 days, forum says no expiry.
- On `service_token_expiry`, prefer documentation (no expiry by default); conflicting evidence: documentation says no expiry by default, blog says long-lived.

Top citations:
- [documentation] NimbusFlow 4.2 Release Notes -> Security changes / Service accounts
- [documentation] NimbusFlow 4.2 Release Notes -> Security changes
- [documentation] NimbusFlow Administration Guide -> SCIM provisioning / Deprovisioning behavior
- [forum] Do API tokens expire? -> Forum post p3

### Source Usage

{
  "documentation": 3,
  "forum": 1,
  "blog": 1
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `blog` Preparing for NimbusFlow 4.2 Token Rotation -> What changes in 4.2 (retrieval=0.366983, rerank=0.438547)
- `documentation` NimbusFlow 4.2 Release Notes -> Security changes / Service accounts (retrieval=0.284549, rerank=0.391944)
- `forum` Do API tokens expire? -> Forum post p3 (retrieval=0.225168, rerank=0.368125)
- `documentation` NimbusFlow 4.2 Release Notes -> Security changes (retrieval=0.196167, rerank=0.342323)
- `documentation` NimbusFlow Administration Guide -> SCIM provisioning / Deprovisioning behavior (retrieval=0.142675, rerank=0.32179)

## 8. How many IdP groups can I map to NimbusFlow roles?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Documentation: NimbusFlow can map up to **50 IdP groups** to workspace roles. Common patterns are: - `nimbus-admins` -> Workspace Admin - `nimbus-operators` -> Operator - `nimbus-viewers` -> Read Only If a user matches multiple mapped
- Documentation: Required SAML attributes - `email` must match the NimbusFlow primary identity - `first_name` and `last_name` are optional but recommended - `groups` is optional and is only needed when role mapping is enabled
- Documentation: The public REST API allows **120 requests per minute per workspace token**. When the limit is exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header in seconds.

Top citations:
- [documentation] NimbusFlow Administration Guide -> Group and role mapping
- [documentation] NimbusFlow Administration Guide -> Single Sign-On Overview / Required SAML attributes
- [documentation] NimbusFlow Troubleshooting Guide -> API rate limits
- [blog] Preparing for NimbusFlow 4.2 Token Rotation -> Preparing for NimbusFlow 4.2 Token Rotation

### Source Usage

{
  "documentation": 3,
  "forum": 1,
  "blog": 1
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `documentation` NimbusFlow Administration Guide -> Group and role mapping (retrieval=0.395915, rerank=0.562116)
- `documentation` NimbusFlow Administration Guide -> Single Sign-On Overview / Required SAML attributes (retrieval=0.118435, rerank=0.398636)
- `documentation` NimbusFlow Troubleshooting Guide -> API rate limits (retrieval=0.097942, rerank=0.390655)
- `blog` Preparing for NimbusFlow 4.2 Token Rotation -> Preparing for NimbusFlow 4.2 Token Rotation (retrieval=0.078132, rerank=0.269045)
- `forum` How long does SCIM deprovisioning take? -> Forum post p2 (retrieval=0.009351, rerank=0.227825)

## 9. Does the desktop agent use a private CA bundle?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Documentation: If the desktop sync agent shows **Verifying certificate** for longer than 30 seconds: 1. confirm the workspace URL matches the certificate common name 2. confirm the corporate proxy root certificate is present in the **s
- Forum: Post by openops_eli (support-engineer): The desktop agent uses the operating system trust store instead of a bundled CA file. Import the proxy root certificate into the macOS System keychain, mark it trusted, then restar
- Forum: Post by maya_ops (customer): After adding a corporate HTTPS inspection proxy, the macOS desktop agent never gets past 'Verifying certificate'. Browser access still works.

Top citations:
- [documentation] NimbusFlow Troubleshooting Guide -> Desktop agent certificate errors
- [forum] Desktop agent stuck on verifying certificate -> Forum post p2
- [forum] Desktop agent stuck on verifying certificate -> Forum post p1
- [forum] Desktop agent stuck on verifying certificate -> Forum post p3

### Source Usage

{
  "documentation": 1,
  "forum": 3,
  "blog": 1
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `documentation` NimbusFlow Troubleshooting Guide -> Desktop agent certificate errors (retrieval=0.32159, rerank=0.455668)
- `forum` Desktop agent stuck on verifying certificate -> Forum post p2 (retrieval=0.204789, rerank=0.396074)
- `forum` Desktop agent stuck on verifying certificate -> Forum post p1 (retrieval=0.132586, rerank=0.285014)
- `forum` Desktop agent stuck on verifying certificate -> Forum post p3 (retrieval=0.110662, rerank=0.275488)
- `blog` Tuning NimbusFlow Desktop Sync for Large Repositories -> Tuning NimbusFlow Desktop Sync for Large Repositories (retrieval=0.103977, rerank=0.266417)

## 10. Why do older posts mention nightly snapshots?

### Response

OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer.

Evidence summary:
- Blog: Older forum posts and runbooks may still mention nightly snapshots. Those references describe the retired architecture, not the current restore model.
- Forum: Post by openops_mila (support-engineer): At the moment personal tokens do not expire automatically. If you need a safer setup, use a service account and rotate the token on your own schedule. Accepted answer.
- Forum: Post by rhea_c (customer): We use personal API tokens in a nightly integration. I cannot find anything in the older docs about expiration. Do tokens ever expire automatically?

Top citations:
- [blog] What We Learned From Rebuilding the Restore Pipeline -> What support teams should remember
- [forum] Do API tokens expire? -> Forum post p3
- [forum] Do API tokens expire? -> Forum post p1
- [documentation] NimbusFlow 4.2 Release Notes -> Security changes / Service accounts

### Source Usage

{
  "documentation": 1,
  "forum": 3,
  "blog": 1
}

### Runtime

{
  "retrieval_provider": "lexical-fallback",
  "answer_provider": "deterministic-fallback",
  "embedding_model": "text-embedding-3-small",
  "response_model": "gpt-5-mini",
  "openai_configured": true,
  "embedding_status": "ready",
  "cached_embeddings": 37,
  "total_chunks": 37,
  "warning": "OpenAI answer generation failed: Network error: [Errno 8] nodename nor servname provided, or not known",
  "embedding_usage": {},
  "response_usage": {}
}

### Top Chunks

- `blog` What We Learned From Rebuilding the Restore Pipeline -> What support teams should remember (retrieval=0.312607, rerank=0.396415)
- `forum` Do API tokens expire? -> Forum post p3 (retrieval=0.163494, rerank=0.341139)
- `forum` Do API tokens expire? -> Forum post p1 (retrieval=0.191922, rerank=0.290778)
- `documentation` NimbusFlow 4.2 Release Notes -> Security changes / Service accounts (retrieval=0.055483, rerank=0.274903)
- `forum` Do API tokens expire? -> Forum post p2 (retrieval=0.155291, rerank=0.274749)
