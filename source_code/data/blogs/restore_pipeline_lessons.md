# What We Learned From Rebuilding the Restore Pipeline

Last year our restore pipeline relied on **nightly snapshots**. That design was easy to reason about but painful for customers who needed finer recovery windows.

## Why the old design hurt

With nightly snapshots, the practical recovery point objective was roughly **24 hours**. Customers running integrations overnight could lose a full business day when they needed a restore at noon.

## What changed

We replaced the nightly-only model with continuous incremental backups and preview workspaces. The migration reduced restore time and made validation safer because teams could inspect a preview before promotion.

## What support teams should remember

Older forum posts and runbooks may still mention nightly snapshots. Those references describe the retired architecture, not the current restore model.
