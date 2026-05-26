import json
import subprocess
import sys
from pathlib import Path

import fitz
import pytest

CLI = Path(__file__).parent / "pdf_chunker_cli.py"


@pytest.fixture(scope="session")
def test_pdf(tmp_path_factory):
    pdf_path = tmp_path_factory.mktemp("data") / "test.pdf"
    doc = fitz.open()
    for i in range(1, 11):
        page = doc.new_page()
        page.insert_text((50, 50), f"page {i}", fontsize=12)
    doc.set_toc([
        [1, "第一章", 1],
        [2, "第一章第一節", 2],
        [2, "第一章第二節", 3],
        [1, "第二章", 4],
        [2, "第二章第一節", 5],
        [2, "第二章第二節", 6],
        [1, "第三章", 7],
        [2, "第三章第一節", 8],
        [2, "第三章第二節", 9],
        [1, "附錄", 10],
    ])
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
    )


def test_inspect_json_schema(test_pdf):
    r = run_cli("inspect", str(test_pdf), "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["total_pages"] == 10
    assert len(data["toc"]) == 10
    first = data["toc"][0]
    assert set(first.keys()) == {
        "index", "level", "title", "page", "span_pages", "children",
    }
    assert first["title"] == "第一章"
    assert first["span_pages"] == 3
    assert first["children"] == 2


def test_plan_by_level(test_pdf, tmp_path):
    r = run_cli("plan", str(test_pdf), "--level", "1", "-o", str(tmp_path), "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["total_chunks"] == 4
    titles = [c["title"] for c in data["chunks"]]
    assert titles == ["第一章", "第二章", "第三章", "附錄"]
    assert data["total_pages"] == 10


def test_plan_by_select_range(test_pdf, tmp_path):
    r = run_cli("plan", str(test_pdf), "--select", "0,3-4", "-o", str(tmp_path), "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert [c["title"] for c in data["chunks"]] == ["第一章", "第二章", "第二章第一節"]


def test_plan_by_match(test_pdf, tmp_path):
    r = run_cli("plan", str(test_pdf), "--match", "^第.章$", "-o", str(tmp_path), "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert [c["title"] for c in data["chunks"]] == ["第一章", "第二章", "第三章"]


def test_chunk_writes_files(test_pdf, tmp_path):
    r = run_cli("chunk", str(test_pdf), "--level", "1", "-o", str(tmp_path), "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["total_chunks"] == 4
    for chunk in data["chunks"]:
        out = Path(chunk["output"])
        assert out.exists()
        doc = fitz.open(str(out))
        assert doc.page_count == chunk["pages"]
        doc.close()


def test_error_select_out_of_range(test_pdf, tmp_path):
    r = run_cli("plan", str(test_pdf), "--select", "99", "-o", str(tmp_path))
    assert r.returncode == 1
    assert "index out of range" in r.stderr


def test_error_missing_selection(test_pdf, tmp_path):
    r = run_cli("plan", str(test_pdf), "-o", str(tmp_path))
    assert r.returncode == 2
