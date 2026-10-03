# Independent publisher preparation — NOT LIVE

The current library mirrors are static. The Codex replenisher needs its local host. This directory is a tested foundation, not a deployed service, not an independently researching AI, and not a guarantee of continuous operation.

## Deployment requirements still unresolved

- A user-authorized X developer app with posting access, secure user-token storage/refresh and confirmed account identity. No API token is present in this repository.
- An always-on host with a persistent disk, budget approval, monitoring and an independent caretaker. Do not run this with ephemeral storage.
- An independently reviewed approved queue, including relevant recent published history in validation and exclusion of ALL native scheduled content. Do not automatically export the whole archive: many entries have already been posted.
- A tested cutover timestamp after the native queue ends, or a reconciled channel handover. Never run two independent publishers against separate databases.
- Media uploads/alt-text support and token refresh are not implemented in this initial text publisher. Live API account identity, access, rate/length constraints and billing require validation before activation.

The worker is off by default. It reads explicit UTC hourly slots, requires exact quotation and source text, rejects consecutive authors, limits Dhammapada to once per 24 hours, and requires four authors/three traditions for each complete eight-item window. The curator must also review women’s representation, meaning and source-use limits; validation cannot establish spiritual benefit or authentic attribution.

A durable SQLite claim is committed before sending. If a request times out or returns an invalid response, the channel remains blocked for manual reconciliation. It does not retry uncertain sends. A successful X post ID is recorded durably. Expired slots are not replayed in a burst. Database loss is a stop condition, not permission to initialize an empty failover history.

## Run checks without X access

`python3 -m unittest discover -s publisher -v`

Initialize a new deployment only after reconciling prior/native history: add `--initialize-state` to a non-sending inspection. This exclusively creates a new database and refuses to overwrite one. Never use it as automatic recovery after disk loss. Normal runs reject missing, empty or invalid databases.

Default inspection: `python3 publisher/worker.py --queue /secure/approved.json --db /persistent/events.sqlite`

Only after completing the deployment requirements, supply `X_USER_ACCESS_TOKEN`, `PUBLISHER_ENABLED=yes`, `PUBLISHER_CUTOVER_UTC`, and `--send` through the host’s secret manager. Never put tokens on command lines, in logs or in Git. Schedule one invocation each UTC hour, using one shared persistent database. A disabled/empty publisher is not healthy coverage; monitor the next approved slot and last confirmed post externally.

## Recovery and acceptance

1. Test restart with the same database; confirm no duplicate sends.
2. Test a simulated timeout; confirm later sends remain blocked.
3. Test publisher restart after the native queue handover; reconcile real post IDs.
4. Turn off the laptop and Wi-Fi. An independent observer must confirm at least two hosted hourly posts and durable receipts before calling deployment independent.
5. Retain checksummed library exports on independent hosts. A caretaker must handle expiring tokens, billing, source corrections, queue depletion, and platform changes.

An unreviewed research candidate must never reach `approved.json`. Existing `scripts/research.py` remains discovery-only. GitHub Actions schedules can be delayed or disabled after inactivity, so an untested workflow alone is not a perpetual publisher. No workflow activation or paid hosting purchase has occurred.
