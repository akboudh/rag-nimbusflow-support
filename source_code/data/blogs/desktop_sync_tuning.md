# Tuning NimbusFlow Desktop Sync for Large Repositories

When support teams troubleshoot slow syncs, the default instinct is to increase everything. In practice, the desktop agent performs best when administrators first confirm whether the bottleneck is CPU, disk, or a proxy doing TLS inspection.

## Worker tuning

The desktop agent defaults to **4 workers** per workspace profile. That is usually enough for repositories under 200k files. Increasing to 6 or 8 workers can help on high-core machines, but it also increases memory usage and can make certificate failures noisier because more connections fail in parallel.

## Proxy and certificate checks

Teams behind interception proxies should validate that the proxy root certificate is trusted by the operating system. The agent reads the system trust store, so a browser succeeding does not prove the agent has the same trust path on every platform.

## Practical advice

Start with certificate validation, then measure CPU, then raise workers if CPU remains under 60 percent. Most support escalations that look like sync slowness are actually trust-store or proxy issues.
