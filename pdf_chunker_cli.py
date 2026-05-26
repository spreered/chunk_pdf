#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["pymupdf>=1.22.3"]
# ///
"""CLI for pdf_chunker — inspect / plan / chunk with --json output for AI agents."""
import argparse
import json
import os
import re
import sys

from pdf_chunker import PDFChunker


def compute_inspect(chunker):
    toc = chunker.toc
    total_pages = chunker.doc.page_count
    items = []
    for i, item in enumerate(toc):
        level = item["level"]
        page = item["page"]
        end_page = total_pages
        children = 0
        for j in range(i + 1, len(toc)):
            nxt = toc[j]
            if nxt["level"] <= level:
                end_page = nxt["page"] - 1
                break
            children += 1
        start_page = max(1, page)
        end_page = max(start_page, min(end_page, total_pages))
        items.append({
            "index": i,
            "level": level,
            "title": item["title"],
            "page": page,
            "span_pages": end_page - start_page + 1,
            "children": children,
        })
    return {
        "pdf": chunker.pdf_path,
        "total_pages": total_pages,
        "toc": items,
    }


def parse_select(spec, toc_len):
    indices = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            indices.update(range(int(a), int(b) + 1))
        else:
            indices.add(int(part))
    out_of_range = [i for i in indices if i < 0 or i >= toc_len]
    if out_of_range:
        raise ValueError(
            f"index out of range: {sorted(out_of_range)} (toc has {toc_len} items)"
        )
    return sorted(indices)


def resolve_selection(chunker, args):
    toc = chunker.toc
    if args.select is not None:
        chosen = set(parse_select(args.select, len(toc)))
    elif args.level is not None:
        chosen = {i for i, item in enumerate(toc) if item["level"] == args.level}
    elif args.match is not None:
        pattern = re.compile(args.match)
        chosen = {i for i, item in enumerate(toc) if pattern.search(item["title"])}
    else:
        raise ValueError("must provide one of --select / --level / --match")
    if not chosen:
        raise ValueError("no toc items matched the selection")
    return [{**item, "selected": i in chosen} for i, item in enumerate(toc)]


def build_plan(chunker, selections, output_dir):
    ranges = chunker.determine_chunk_ranges(selections)
    original = os.path.splitext(os.path.basename(chunker.pdf_path))[0]
    out_dir = output_dir or os.path.dirname(chunker.pdf_path) or os.getcwd()
    enriched = []
    for r in ranges:
        sanitized = chunker._sanitize_filename(r["title"])
        enriched.append({
            "title": r["title"],
            "start_page": r["start_page"],
            "end_page": r["end_page"],
            "pages": r["end_page"] - r["start_page"] + 1,
            "output": os.path.join(out_dir, f"{original}_{sanitized}.pdf"),
        })
    return ranges, {
        "chunks": enriched,
        "total_chunks": len(enriched),
        "total_pages": sum(c["pages"] for c in enriched),
    }


def cmd_inspect(args):
    chunker = PDFChunker()
    chunker.load_pdf(args.pdf)
    chunker.extract_toc()
    if not chunker.toc:
        result = {"pdf": args.pdf, "total_pages": chunker.doc.page_count, "toc": []}
    else:
        result = compute_inspect(chunker)
    chunker.close()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_inspect_human(result)


def print_inspect_human(result):
    print(f"PDF: {result['pdf']}")
    print(f"Total pages: {result['total_pages']}")
    if not result["toc"]:
        print("(no table of contents)")
        return
    print(f"ToC ({len(result['toc'])} items):")
    for item in result["toc"]:
        indent = "  " * (item["level"] - 1)
        print(
            f"  [{item['index']:3d}] {indent}L{item['level']} "
            f"p.{item['page']:>4d} ({item['span_pages']:>3d}p) {item['title']}"
        )


def cmd_plan(args):
    chunker = PDFChunker()
    chunker.load_pdf(args.pdf)
    chunker.extract_toc()
    if not chunker.toc:
        raise SystemExit("error: PDF has no table of contents")
    selections = resolve_selection(chunker, args)
    _, plan = build_plan(chunker, selections, args.output_dir)
    chunker.close()
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print_plan_human(plan)


def print_plan_human(plan):
    print(f"Plan: {plan['total_chunks']} chunks, {plan['total_pages']} pages total")
    for c in plan["chunks"]:
        print(f"  p.{c['start_page']}-{c['end_page']} ({c['pages']}p)  {c['title']}")
        print(f"    -> {c['output']}")


def cmd_chunk(args):
    chunker = PDFChunker()
    chunker.load_pdf(args.pdf)
    chunker.extract_toc()
    if not chunker.toc:
        raise SystemExit("error: PDF has no table of contents")
    selections = resolve_selection(chunker, args)
    ranges, _ = build_plan(chunker, selections, args.output_dir)
    created = chunker.create_chunks(ranges, output_dir=args.output_dir)
    chunker.close()
    result_chunks = [
        {
            "title": r["title"],
            "start_page": r["start_page"],
            "end_page": r["end_page"],
            "pages": r["end_page"] - r["start_page"] + 1,
            "output": path,
        }
        for r, path in zip(ranges, created)
    ]
    result = {
        "chunks": result_chunks,
        "total_chunks": len(result_chunks),
        "total_pages": sum(c["pages"] for c in result_chunks),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Created {len(result_chunks)} chunks:")
        for c in result_chunks:
            print(f"  {c['output']} ({c['pages']}p)")


def add_common(parser):
    parser.add_argument("--json", action="store_true", help="emit JSON to stdout")


def add_selection(parser):
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--select", help="comma-separated indices, e.g. 0,2,5-7")
    g.add_argument("--level", type=int, help="select all ToC items at this level")
    g.add_argument("--match", help="regex matched against titles")
    parser.add_argument(
        "-o", "--output-dir", help="output directory (default: same dir as PDF)"
    )


def main():
    parser = argparse.ArgumentParser(
        prog="pdf_chunker_cli", description="Chunk a PDF by its ToC"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_inspect = sub.add_parser("inspect", help="show PDF structure and ToC")
    p_inspect.add_argument("pdf")
    add_common(p_inspect)

    p_plan = sub.add_parser("plan", help="preview chunks without writing files")
    p_plan.add_argument("pdf")
    add_selection(p_plan)
    add_common(p_plan)

    p_chunk = sub.add_parser("chunk", help="write chunked PDF files")
    p_chunk.add_argument("pdf")
    add_selection(p_chunk)
    add_common(p_chunk)

    args = parser.parse_args()
    try:
        if args.cmd == "inspect":
            cmd_inspect(args)
        elif args.cmd == "plan":
            cmd_plan(args)
        elif args.cmd == "chunk":
            cmd_chunk(args)
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
