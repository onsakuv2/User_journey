# Autonomous Wake

When activated in headless mode, complete the requested Azure Boards task without conversational prompting.

## Outcome

Produce a read result or publish result using available runtime inputs, while defaulting to safe behavior when write intent is ambiguous.

## Headless Behavior

- Resolve organization, project, and PAT from explicit arguments first, then environment variables.
- For publish operations, default to dry-run unless an explicit apply flag is present.
- Fail fast when required Azure settings or input files are missing.
- Return a concise operational summary that includes whether changes were applied or only previewed.

## Supported Task Shapes

- `-H:read` or `--headless:read` for board retrieval
- `-H:publish` or `--headless:publish` for create/update/link operations
- `-H:link` or `--headless:link` when only relations need to be established

## Good Result

- No interactive dependencies
- No silent writes
- Clear machine-usable summary of created, reused, linked, skipped, and failed items
