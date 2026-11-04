#!/usr/bin/env bash
# Plant a scenario on the Pi by replacing the app's config.json.
# Usage (from ~/bring-up-bot): scenarios/seed.sh healthy|wrong_address|gage_range|no_wait
set -euo pipefail
name="${1:?usage: scenarios/seed.sh <scenario>}"
scp -q "scenarios/${name}.json" bringup-pi:abp2_app/config.json
echo "Seeded '${name}' on the Pi."
