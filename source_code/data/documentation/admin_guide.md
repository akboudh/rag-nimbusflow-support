# NimbusFlow Administration Guide

## Single Sign-On Overview

NimbusFlow supports SAML 2.0 single sign-on for Business and Enterprise workspaces. Administrators can configure SAML from **Settings > Security > Identity** and may keep password login enabled during rollout. The product signs authentication requests with the workspace certificate and supports IdP-initiated and SP-initiated login.

### Required SAML attributes

- `email` must match the NimbusFlow primary identity
- `first_name` and `last_name` are optional but recommended
- `groups` is optional and is only needed when role mapping is enabled

## Group and role mapping

NimbusFlow can map up to **50 IdP groups** to workspace roles. Common patterns are:

- `nimbus-admins` -> Workspace Admin
- `nimbus-operators` -> Operator
- `nimbus-viewers` -> Read Only

If a user matches multiple mapped groups, the highest privilege wins. Role mapping is evaluated at login and on every SCIM update.

## SCIM provisioning

SCIM 2.0 provisioning is available on Enterprise plans. New users, profile changes, and deprovision events are applied within **5 minutes** under normal conditions. Administrators can force a resync from **Settings > Security > SCIM > Retry Sync**.

### Deprovisioning behavior

When a user is deprovisioned from the identity provider:

1. active NimbusFlow sessions are revoked
2. API tokens owned by that user are disabled
3. queued background jobs keep running until completion, but the user cannot start new jobs

## Audit and security controls

Administrators can export audit events from **Settings > Security > Audit Export**. The default export window is the last 7 days. For longer retention, configure scheduled exports to object storage.
