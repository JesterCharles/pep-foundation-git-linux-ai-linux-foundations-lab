# Runbook: status-page

The status-page service shows teammates which deployment a build talks to.

- It must listen on `http://localhost:8080` and answer on the `/status` path.
  `localhost` (127.0.0.1) is this machine itself: the service and its health
  check run on the same computer and never leave it.
- The health check calls `http://localhost:8080/status` every 30 seconds.
- `bin/status.sh` prints one status line. The on-call person runs it directly
  as `./bin/status.sh`, so it must be executable by the owner and the on-call
  group, and not open to anyone else: permission mode `750`.
- The deployment name comes from the `DEPLOY_ENV` environment variable, loaded
  from `env/deploy.env`. That file holds deployment settings, so only its owner
  may read or change it: permission mode `600`. Start from `env/deploy.env.example`.
- Triage results go into the `triage/` folder; the launch checklist that the
  release manager keeps in the `release notes` folder is copied there first.
