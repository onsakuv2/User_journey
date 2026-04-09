# Publish Board Hierarchy

Publish BMad-generated epics, features, stories, and hierarchy links back to Azure Boards without creating duplicate items or breaking parent-child structure.

## Outcome

Translate the user-approved BMad planning output into Azure Boards work items and links, with a dry-run preview available before any write is applied.

## What to Clarify

Ask only for information that blocks a safe publish:

- Azure organization and project if not already available
- The artifact or JSON input that defines the intended hierarchy
- Whether the run should be dry-run only or apply changes
- Any area path, iteration path, or parent root constraints the board requires

## Deterministic Path

Use `python ./scripts/azure_boards_sync.py --help` to inspect supported publish operations.

Prefer script-driven publishing for:

- Validating the input JSON shape
- Looking up existing items by title and type
- Creating missing epics, features, and stories
- Linking children to parents after creation

## Good Result

- The user sees a dry-run plan or applied change summary with created, reused, and linked work items
- Existing matches are reused instead of duplicated when the script can determine a safe match
- Hierarchy problems are surfaced before writes complete

## Safety Standard

Do not apply writes until the requested hierarchy is concrete enough to validate. If duplicate risk remains ambiguous, surface the ambiguity and ask for the missing discriminator instead of guessing.
