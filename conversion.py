import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

SUPPORTED_EXTENSIONS = {
    '.csv',
    '.docx',
    '.html',
    '.json',
    '.pdf',
    '.pptx',
    '.txt',
    '.xlsx',
}


def iter_supported_files(source: Path, recursive: bool):
    if source.is_file():
        if source.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield source, source.parent
        else:
            logging.warning("Skipping unsupported file: %s", source)
        return

    pattern = "**/*" if recursive else "*"
    for file_path in source.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield file_path, source


def resolve_output_path(output_root: Path, file_path: Path, base_path: Path) -> Path:
    relative_parent = file_path.parent.relative_to(base_path)
    target_dir = output_root / relative_parent
    target_dir.mkdir(parents=True, exist_ok=True)

    candidate = target_dir / f"{file_path.stem}.md"
    counter = 2
    while candidate.exists():
        candidate = target_dir / f"{file_path.stem}-{counter}.md"
        counter += 1
    return candidate


def convert_documents(sources, output_folder, recursive=False):
    output_root = Path(output_folder)
    output_root.mkdir(parents=True, exist_ok=True)

    try:
        from markitdown import MarkItDown
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "markitdown is not installed. Install it in the active environment before running conversions."
        ) from error

    md_converter = MarkItDown()
    converted = []
    failed = []

    for raw_source in sources:
        source = Path(raw_source)
        if not source.exists():
            logging.error("Source does not exist: %s", source)
            failed.append({"source": str(source), "error": "Path does not exist"})
            continue

        found_supported_file = False
        for file_path, base_path in iter_supported_files(source, recursive):
            found_supported_file = True
            output_file = resolve_output_path(output_root, file_path, base_path)
            logging.info("Converting %s -> %s", file_path, output_file)
            try:
                result = md_converter.convert(str(file_path))
                output_file.write_text(result.text_content, encoding='utf-8')
                converted.append({"source": str(file_path), "output": str(output_file)})
            except Exception as error:
                logging.error("Failed to convert %s: %s", file_path, error)
                failed.append({"source": str(file_path), "error": str(error)})

        if source.is_dir() and not found_supported_file:
            logging.warning("No supported files found in %s", source)

    return {
        "converted": converted,
        "failed": failed,
        "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="Convert one or more documents or folders into markdown using MarkItDown."
    )
    parser.add_argument(
        "sources",
        nargs='+',
        help="One or more files or folders to convert.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Folder where markdown files will be written.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action='store_true',
        help="Recursively scan folders for supported documents.",
    )
    return parser


def main():
    args = build_parser().parse_args()
    try:
        summary = convert_documents(args.sources, args.output, recursive=args.recursive)
    except RuntimeError as error:
        logging.error(str(error))
        return 1

    logging.info(
        "Conversion complete: %s succeeded, %s failed.",
        len(summary["converted"]),
        len(summary["failed"]),
    )
    return 0 if not summary["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())