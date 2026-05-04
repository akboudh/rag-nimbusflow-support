# Preparing for NimbusFlow 4.2 Token Rotation

NimbusFlow 4.2 closes a long-standing security gap by adding expiration to personal API tokens. Many teams built internal scripts assuming personal tokens were effectively permanent, so support engineers should be ready for upgrade questions.

## What changes in 4.2

Personal API tokens now expire after **90 days**. Service account tokens remain **long-lived** unless a workspace policy says otherwise. Teams with unattended jobs should move those jobs off personal tokens before upgrade.

## Migration advice

If a customer says "our token used to last forever," they are probably describing pre-4.2 behavior. The right answer is not to disable the policy; it is to move automation onto a service account with explicit ownership and rotation.

## Support guidance

When there is a conflict between old forum answers and current product behavior, prefer the latest documentation or release notes, then use the blog only as explanatory context.
