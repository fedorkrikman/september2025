# chat_export.py

import argparse
from pathlib import Path
import sys

from chat_html_parser import parse_chat_html_to_text


def convert_html_chat_to_txt(html_path: Path, txt_path: Path) -> None:
    """
    Обёртка над парсером: читает HTML, получает готовый текст
    и пишет его в *.txt.
    """
    text = parse_chat_html_to_text(html_path)
    txt_path.write_text(text, encoding="utf-8")


def find_html_files_to_process(
    base_dir: Path,
    explicit_files: list[str] | None
) -> list[tuple[Path, Path]]:
    # как было ранее — без изменений
    pairs: list[tuple[Path, Path]] = []

    if explicit_files:
        for name in explicit_files:
            html_path = (base_dir / name).resolve()
            if not html_path.is_file():
                print(f"[WARN] HTML not found: {html_path}", file=sys.stderr)
                continue
            if html_path.suffix.lower() != ".html":
                print(f"[WARN] Not an .html file: {html_path}", file=sys.stderr)
                continue

            txt_path = html_path.with_suffix(".txt")
            if txt_path.exists():
                print(f"[SKIP] TXT already exists: {txt_path}")
                continue

            pairs.append((html_path, txt_path))
    else:
        for html_path in base_dir.glob("*.html"):
            txt_path = html_path.with_suffix(".txt")
            if txt_path.exists():
                continue
            pairs.append((html_path, txt_path))

    return pairs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert exported ChatGPT HTML files to plain text STEP/Q/A format."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help=(
            "Список HTML-файлов для обработки. "
            "Если не указаны или указан один аргумент '*' — "
            "обрабатываются все *.html без соответствующих .txt."
        ),
    )
    parser.add_argument(
        "-d", "--dir",
        type=str,
        default=".",
        help="Рабочая директория (по умолчанию текущая).",
    )

    args = parser.parse_args(argv)
    base_dir = Path(args.dir).resolve()

    if not args.files or (len(args.files) == 1 and args.files[0] == "*"):
        explicit_files = None
    else:
        explicit_files = args.files

    pairs = find_html_files_to_process(base_dir, explicit_files)

    if not pairs:
        print("[INFO] Nothing to do: no HTML files without TXT.")
        return 0

    for html_path, txt_path in pairs:
        print(f"[PROCESS] {html_path.name} -> {txt_path.name}")
        try:
            convert_html_chat_to_txt(html_path, txt_path)
        except Exception as e:
            print(f"[ERROR] Failed to process {html_path}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
