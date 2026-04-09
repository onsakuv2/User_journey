# Convert Documents

Convert the user-provided document set into markdown using `{project-root}/conversion.py`.

## Outcome

Produce markdown files for the requested source files or folders, place them in the requested output folder, and give the user a concise report covering converted files, skipped inputs, and failures.

## What to Clarify

Only ask for details that are missing or ambiguous:

- Source paths: one or more files or folders
- Output folder
- Whether folder inputs should be scanned recursively

If the user already supplied those items, proceed without re-asking.

## Tool Use

Prefer the deterministic project tool:

```text
python {project-root}/conversion.py -o {output_dir} {source_1} {source_2}
```

Add `--recursive` when the user wants nested files included.

The tool supports these source types when MarkItDown can process them: `.csv`, `.docx`, `.html`, `.json`, `.pdf`, `.pptx`, `.txt`, `.xlsx`.

## Good Result

- The output folder exists and contains markdown files for each successful conversion.
- The user can see which sources succeeded and where the markdown landed.
- Failures are reported with enough detail to retry or fix the source.
- Unsupported files or empty folders are called out clearly instead of being silently treated as success.

## Failure Handling

If `{project-root}/conversion.py` is missing or cannot run:

- State the blocker plainly.
- Do not claim conversion succeeded.
- Offer the next practical step, such as fixing the tool path, installing the required dependency, or narrowing the source set.