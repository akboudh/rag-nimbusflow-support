# NimbusFlow Troubleshooting Guide

## API rate limits

The public REST API allows **120 requests per minute per workspace token**. When the limit is exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header in seconds.

### Recommended client behavior

- honor `Retry-After` exactly
- retry with exponential backoff for bursty workloads
- spread bulk sync jobs across minute boundaries

## Desktop agent certificate errors

If the desktop sync agent shows **Verifying certificate** for longer than 30 seconds:

1. confirm the workspace URL matches the certificate common name
2. confirm the corporate proxy root certificate is present in the **system trust store**
3. restart the agent after importing the certificate
4. on macOS, run `nimbus-agent doctor`

The agent does not use a private certificate bundle. It reads from the **system trust store** so proxy or inspection certificates must be installed at the OS level.

## Restore points and retention

NimbusFlow stores continuous incremental backups and exposes self-service restore points for the last **30 days**. The target recovery point objective is **30 minutes**. Restores older than 30 days require OpenOps intervention and are not covered by the standard SLA.

### Restore workflow

1. open **Workspace Settings > Restore**
2. choose a timestamp
3. create a preview workspace
4. validate the preview
5. promote the preview back to production

## Audit log exports

Audit exports include login events, role changes, restore operations, API token creation, and SCIM actions. Large exports are streamed and may take several minutes to complete.
