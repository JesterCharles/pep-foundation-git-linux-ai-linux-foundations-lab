#!/bin/sh
# Prints one status line for the status-page service.
# Deployment settings load from env/deploy.env when it exists.
here="$(dirname "$0")"
env_file="$here/../env/deploy.env"
if [ -f "$env_file" ]; then
  . "$env_file"
fi
deployment="${DEPLOY_ENV:-development}"
port="$(grep '^port=' "$here/../app/config/app.conf" | cut -d= -f2)"
echo "status-page ($deployment) expects http://localhost:$port/status"
