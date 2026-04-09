# Retrieve Board Context

Retrieve requirements or hierarchy context from Azure Boards so the user can ground BMad planning in live board data.

## Outcome

Return the relevant Azure Boards work items and relationships in a form the user can inspect, summarize, or feed into downstream BMad planning without losing source traceability.

## What to Clarify

Ask only for missing inputs:

- Azure organization and project
- Which work item scope matters: requirements, epics, features, stories, or a WIQL selection
- Whether the user wants raw JSON, a concise summary, or both

## Deterministic Path

Use `python ./scripts/azure_boards_sync.py --help` to inspect supported commands, then run one of the read operations.

Prefer script-driven retrieval for:

- WIQL-based discovery
- Fetching specific work items by ID
- Pulling enough fields to preserve hierarchy context

## Good Result

- Returned items clearly identify source work-item IDs and types
- Parent-child relationships are preserved when available
- Missing items, inaccessible boards, or auth failures are reported plainly

## Fallback

If the script cannot run, explain the blocker, avoid pretending the board was queried, and help the user prepare the WIQL, IDs, or export shape needed for the next run.
