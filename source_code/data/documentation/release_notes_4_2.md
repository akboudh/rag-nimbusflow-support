# NimbusFlow 4.2 Release Notes

## Security changes

NimbusFlow 4.2 introduces mandatory rotation for personal API tokens. **Personal tokens now expire after 90 days** and users receive reminders starting 14 days before expiration. Existing personal tokens created before 4.2 are migrated onto the same policy when first used after upgrade.

### Service accounts

Service account tokens do **not expire by default**, but administrators can opt into rotation policies at the workspace level. OpenOps recommends rotating service tokens every 180 days even when no hard expiry is enforced.

## Audit export improvements

Audit exports are now available in **NDJSON** in addition to CSV. NDJSON is recommended for downstream SIEM ingestion and incremental processing.

## Restore preview improvements

Preview workspaces now load faster and preserve user role mappings during validation. No retention or RPO changes were made in 4.2.
