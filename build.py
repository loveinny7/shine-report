#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
샤인영어 일간 학습 리포트 — 정적 페이지 빌더

사용법
    python3 build.py                # data/ 아래 모든 JSON을 페이지로 생성 + index.html 갱신
    python3 build.py data/xxx.json  # 특정 리포트만 다시 생성

새 리포트 추가
    1) data/ 폴더에서 기존 JSON 하나를 복사해 파일 이름을 바꾼다 (예: data/2026-11-28-kimseojun.json)
    2) 학생 이름·날짜·수업·숙제·한마디를 고친다
    3) python3 build.py
    4) 생성된 reports/<id>.html 을 열어 확인하고 커밋·푸시
"""

from __future__ import annotations

import html
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
TPL_DIR = ROOT / "templates"

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


# ----------------------------------------------------------------- 유틸


def esc(value) -> str:
    """HTML 이스케이프 (None → 빈 문자열)."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_date(iso: str) -> date:
    y, m, d = (int(part) for part in iso.split("-"))
    return date(y, m, d)


def date_labels(iso: str) -> tuple[str, str]:
    """('11월 27일 금요일', '2026.11.27') 형태로 돌려준다."""
    dt = parse_date(iso)
    long_label = f"{dt.month}월 {dt.day}일 {WEEKDAYS[dt.weekday()]}요일"
    short_label = f"{dt.year}.{dt.month:02d}.{dt.day:02d}"
    return long_label, short_label


def asset_prefix(output_rel: str) -> str:
    depth = len(Path(output_rel).parent.parts)
    return "../" * depth + "assets/style.css" if depth else "assets/style.css"


def fill(template: str, values: dict) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    leftover = [key for key in ("{{", ) if key in out]
    if leftover:
        for line in out.splitlines():
            if "{{" in line:
                raise SystemExit(f"[빌드 중단] 치환되지 않은 자리표시자: {line.strip()}")
    return out


# ----------------------------------------------------------------- 조각


def render_lessons(lessons: list[dict]) -> str:
    rows = []
    for item in lessons:
        tags = "".join(
            f'\n          <span class="chip">{esc(tag)}</span>' for tag in item.get("tags", [])
        )
        rows.append(
            '        <li class="lesson">\n'
            f'          <div class="lesson-book">{esc(item.get("book"))}</div>\n'
            f'          <div class="lesson-detail">{esc(item.get("detail"))}</div>'
            f"{tags}\n"
            "        </li>"
        )
    return "\n".join(rows)


def render_next_class(text: str | None) -> str:
    if not text:
        return ""
    return (
        '\n      <div class="next-class"><b>다음 시간</b><span>'
        + esc(text)
        + "</span></div>"
    )


def render_homework(items: list[dict]) -> str:
    rows = []
    for item in items:
        cls = "check is-done" if item.get("done") else "check"
        note = item.get("note")
        note_html = f'\n          <small>{esc(note)}</small>' if note else ""
        rows.append(
            f'        <li class="{cls}">\n'
            '          <span class="box" aria-hidden="true"></span>\n'
            f'          <span class="label">{esc(item.get("task"))}{note_html}</span>\n'
            "        </li>"
        )
    return "\n".join(rows)


def render_tests(items: list[dict]) -> str:
    tiles = []
    for item in items:
        unit = f'<span class="unit">{esc(item.get("unit"))}</span>' if item.get("unit") else ""
        note = f'\n          <span class="tile-note">{esc(item["note"])}</span>' if item.get("note") else ""
        tiles.append(
            '        <div class="tile">\n'
            f'          <div class="tile-value">{esc(item.get("value"))}{unit}</div>\n'
            f'          <div class="tile-label">{esc(item.get("label"))}</div>{note}\n'
            "        </div>"
        )
    return "\n".join(tiles)


def badge_class(tone: str | None) -> str:
    return {"gold": "badge", "soft": "badge badge--soft", "mint": "badge badge--mint"}.get(
        tone or "gold", "badge"
    )


# ----------------------------------------------------------------- 리포트 1장


def build_report(data: dict, tpl: str) -> tuple[str, dict]:
    student = data.get("student", {})
    note = data.get("note", {})
    iso = data["date"]
    long_label, short_label = date_labels(iso)

    output = data.get("output") or f"reports/{data['id']}.html"
    year = parse_date(iso).year

    description = (
        f"{student.get('name', '')} 학생 {long_label} 학습 리포트 — "
        f"{data.get('summary', '오늘의 수업·숙제·테스트 기록')}"
    )

    page_title = f"{student.get('name', '학생')} · {long_label} 학습 리포트 | 샤인영어"

    values = {
        "ASSET": asset_prefix(output),
        "PAGE_TITLE": esc(page_title),
        "DESCRIPTION": esc(description),
        "DATE_LABEL": esc(f"{long_label} · {year}"),
        "BADGE": esc(data.get("badge", {}).get("text", "잘했어요")),
        "INITIAL": esc(student.get("initial") or (student.get("name") or "?")[:1]),
        "STUDENT_NAME": esc(student.get("name")),
        "SCHOOL": esc(student.get("school")),
        "GRADE": esc(student.get("grade")),
        "LESSONS": render_lessons(data.get("lessons", [])),
        "NEXT_CLASS": render_next_class(data.get("next_class")),
        "HOMEWORK": render_homework(data.get("homework", [])),
        "HOMEWORK_NOTE": esc(data.get("homework_note", "")),
        "TESTS": render_tests(data.get("tests", [])),
        "NOTE_LEAD": esc(note.get("lead")),
        "NOTE_BODY": esc(note.get("body")).replace("\n", "<br>"),
        "SIGN_NAME": esc(note.get("name", "이정인 원장")),
        "SIGN_SUB": esc(note.get("sub", "서울대 영어교육과")),
        "FOOTER_NOTE": esc(data.get("footer_note", "본 리포트는 샤인영어(대구 수성구)에서 발송했습니다.")),
    }

    html_out = fill(tpl, values)

    meta = {
        "output": output,
        "student": student,
        "badge": data.get("badge", {}),
        "summary": data.get("summary", ""),
        "date": iso,
        "short": short_label,
        "listed": data.get("listed", True),
        "name": student.get("name", ""),
    }
    return html_out, meta


# ----------------------------------------------------------------- index


def render_rows(meta_list: list[dict]) -> str:
    rows = []
    for meta in meta_list:
        student = meta["student"]
        badge = meta.get("badge", {})
        rows.append(
            f'    <a class="report-row" href="{esc(meta["output"])}">\n'
            f'      <span class="avatar" aria-hidden="true">{esc(student.get("initial") or (student.get("name") or "?")[:1])}</span>\n'
            '      <span class="row-main">\n'
            f'        <span class="row-name">{esc(student.get("name"))} '
            f'<em>{esc(student.get("school"))} · {esc(student.get("grade"))}</em></span>\n'
            f'        <span class="row-meta">{esc(meta.get("summary"))}</span>\n'
            "      </span>\n"
            '      <span class="row-side">\n'
            f'        <span class="{badge_class(badge.get("tone"))}">{esc(badge.get("text"))}</span>\n'
            f'        <span class="row-date">{esc(meta.get("short"))}</span>\n'
            "      </span>\n"
            "    </a>"
        )
    return "\n".join(rows)


def build_index(meta_list: list[dict], tpl: str) -> str:
    listed = [m for m in meta_list if m.get("listed")]
    listed.sort(key=lambda m: (m["date"], m["name"]), reverse=True)
    if not listed:
        listed = meta_list
    values = {"REPORT_ROWS": render_rows(listed) if listed else '    <p class="hint">아직 등록된 리포트가 없습니다.</p>'}
    return fill(tpl, values)


# ----------------------------------------------------------------- main


def main(argv: list[str]) -> int:
    report_tpl = (TPL_DIR / "report.html").read_text(encoding="utf-8")
    index_tpl = (TPL_DIR / "index.html").read_text(encoding="utf-8")

    if len(argv) > 1:
        paths = [Path(arg) if Path(arg).is_absolute() else ROOT / arg for arg in argv[1:]]
    else:
        paths = sorted(p for p in DATA_DIR.glob("*.json") if not p.name.startswith("_"))

    if not paths:
        raise SystemExit("[빌드 중단] data/*.json 이 없습니다.")

    metas: list[dict] = []
    for path in paths:
        data = read_json(path)
        page, meta = build_report(data, report_tpl)
        out_path = ROOT / meta["output"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page, encoding="utf-8")
        metas.append(meta)
        print(f"  ✓ {out_path.relative_to(ROOT)}  ({meta['student'].get('name')} · {meta['date']})")

    # index 는 data/ 전체를 스캔해 만든다 (한 건만 빌드해도 목록은 항상 최신)
    all_metas: list[dict] = []
    for path in sorted(p for p in DATA_DIR.glob("*.json") if not p.name.startswith("_")):
        data = read_json(path)
        _, meta = build_report(data, report_tpl)
        all_metas.append(meta)

    index_html = build_index(all_metas, index_tpl)
    (ROOT / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  ✓ index.html  (목록 {len([m for m in all_metas if m['listed']])}건)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
