#!/usr/bin/env python3
"""Chromium DOM-geometry smoke for PUBLIC synthetic RQ7 SVGs.

Requires an explicitly installed Playwright+Chromium. This does NOT verify
screen-reader operation, perceptual legibility, human/AI cognitive benefits,
TEI Product Source closure, or runtime authorization.
"""
from __future__ import annotations

import argparse
import copy
import html
import json
from pathlib import Path

import rq7_pilot
import rq7_svg


def unique_cases() -> list[dict]:
    seen = set()
    result = []
    for dataset in ("v0", "v1"):
        inputs, gold = rq7_pilot.load(dataset)
        rq7_pilot.validate(inputs, gold)
        for case in inputs["cases"]:
            signature = json.dumps(case["declared"], sort_keys=True, ensure_ascii=False)
            if signature not in seen:
                seen.add(signature)
                result.append(case)
    return result


def document(case: dict) -> str:
    svg = rq7_svg.render_svg(case).split("?>", 1)[-1].strip()
    text = html.escape(rq7_pilot.declared_text(case))
    return (
        '<!doctype html><html lang="en"><head><meta charset="UTF-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        '<style>body{margin:0;font-family:sans-serif;}'
        '#diagram{width:100%;max-width:100%;overflow-x:auto;overflow-y:visible;'
        'border-bottom:1px solid #bbb;}#diagram svg{display:block;max-width:none;}'
        'pre{white-space:pre-wrap;padding:8px;}</style></head><body>'
        f'<main><div id="diagram">{svg}</div>'
        f'<pre id="declared-text">{text}</pre></main></body></html>'
    )


MEASURE_JS = r"""() => {
  const svg = document.querySelector('#diagram svg');
  const frame = document.querySelector('#diagram');
  if (!svg || svg.getAttribute('role') !== 'img' ||
      !svg.querySelector('title') || !svg.querySelector('desc')) {
    throw new Error('SVG missing accessible image role/name/description');
  }
  const labels = [];
  for (const group of svg.querySelectorAll('g.declared-node')) {
    const r = group.querySelector('rect');
    const texts = [...group.querySelectorAll('text')];
    if (!r || texts.length !== 2) throw new Error('visible node labels missing');
    for (const t of texts) {
      const b = t.getBBox();
      labels.push({
        node: group.getAttribute('data-id'),
        text: t.textContent,
        x: b.x, y: b.y, w: b.width, h: b.height,
        overflow: b.x < -0.1 || b.y < -0.1 ||
          b.x + b.width > 180.1 || b.y + b.height > 60.1,
      });
    }
  }
  const obstacles = [...svg.querySelectorAll('g.declared-node')].map(g => ({
    id: g.getAttribute('data-id'), box: g.querySelector('rect').getBoundingClientRect()
  }));
  const hitTests = [];
  for (const e of svg.querySelectorAll('line.declared-edge, path.declared-edge')) {
    const from = e.getAttribute('data-from');
    const to = e.getAttribute('data-to');
    const count = 120;
    for (let i = 1; i < count; i++) {
      let p;
      if (e.tagName.toLowerCase() === 'path') {
        p = e.getPointAtLength(e.getTotalLength() * i / count);
      } else {
        const f = i / count;
        p = svg.createSVGPoint();
        p.x = (+e.getAttribute('x1')) * (1-f) + (+e.getAttribute('x2')) * f;
        p.y = (+e.getAttribute('y1')) * (1-f) + (+e.getAttribute('y2')) * f;
      }
      const screen = p.matrixTransform(e.getScreenCTM());
      for (const o of obstacles) {
        if (o.id === from || o.id === to) continue;
        const b = o.box;
        if (screen.x > b.left + 2 && screen.x < b.right - 2 &&
            screen.y > b.top + 2 && screen.y < b.bottom - 2) {
          hitTests.push({edge: from + '->' + to, node: o.id, x: screen.x, y: screen.y});
        }
      }
    }
  }
  const title = svg.querySelector('title').textContent;
  return {
    nodeCount: obstacles.length,
    edgeCount: svg.querySelectorAll('line.declared-edge, path.declared-edge').length,
    labelCount: labels.length,
    labelOverflows: labels.filter(l=>l.overflow),
    edgeHits: hitTests.slice(0, 10),
    accessibleTitle: title,
    contentWidth: frame.scrollWidth, viewportWidth: frame.clientWidth,
    svgWidth: svg.getBoundingClientRect().width,
  };
}"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshots", type=Path, help="optional output directory for public synthetic PNGs")
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Install Playwright/Chromium explicitly for browser smoke") from exc

    cases = unique_cases()
    if len(cases) != 3:
        raise RuntimeError(f"public DAG inventory changed: expected 3, got {len(cases)}")
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)
    checked = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for viewport_name, width, height, scale in (
            ("desktop", 1280, 900, 1),
            ("mobile", 390, 780, 2),
        ):
            context = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=scale, offline=True,
                reduced_motion="reduce",
            )
            page = context.new_page()
            requests = []
            page.on("request", lambda r: requests.append(r.url) if r.url.startswith(("http:", "https:")) else None)
            for case in cases:
                rq7_svg.check_public_pair(case)
                page.set_content(document(case), wait_until="load")
                page.evaluate("document.fonts.ready")
                result = page.evaluate(MEASURE_JS)
                expected = case["declared"]
                if result["nodeCount"] != len(expected["nodes"]) or result["edgeCount"] != len(expected["edges"]):
                    raise AssertionError(f"{case['id']} {viewport_name}: browser rendered wrong graph: {result}")
                if result["labelOverflows"]:
                    raise AssertionError(f"{case['id']} {viewport_name}: visible node text leaves its rectangle: {result['labelOverflows']}")
                if result["edgeHits"]:
                    raise AssertionError(f"{case['id']} {viewport_name}: drawn edge crosses unrelated node: {result['edgeHits']}")
                if not result["accessibleTitle"].startswith("Declared graph for "):
                    raise AssertionError("missing title in browser DOM")
                if width < result["svgWidth"]:
                    if result["contentWidth"] <= result["viewportWidth"]:
                        raise AssertionError("wide SVG cannot be reached by horizontal scroll")
                    page.evaluate("document.querySelector('#diagram').scrollLeft = 10000")
                    moved = page.evaluate("document.querySelector('#diagram').scrollLeft")
                    if moved <= 0:
                        raise AssertionError("wide SVG cannot be scrolled")
                if requests:
                    raise AssertionError("external HTTP(S) request in public synthetic browser smoke")
                if args.screenshots:
                    page.locator("#diagram").screenshot(
                        path=str(args.screenshots / f"{case['id']}-{viewport_name}.png")
                    )
                checked.append({"case": case["id"], "viewport": viewport_name, **result})
            if viewport_name == "desktop":
                # A deliberately long label exposes the known single-line
                # layout limitation. Detect it, never count it as a PASS.
                mutant = copy.deepcopy(cases[0])
                mutant["declared"]["nodes"][0]["label"] = "A deliberately long synthetic label that should be outside the narrow card"
                page.set_content(document(mutant))
                negative = page.evaluate(MEASURE_JS)
                if not negative["labelOverflows"]:
                    raise AssertionError("long-label overflow negative control was not detected")
            context.close()
        browser.close()

    print(json.dumps({
        "status": "PUBLIC_SYNTHETIC_CHROMIUM_GEOMETRY_SMOKE_ONLY",
        "distinct_graphs": len(cases),
        "viewport_checks": len(checked),
        "edge_crossing_checks": "sampled actual SVG paths/lines via Chromium screen CTM",
        "label_overflows_in_original_three_graphs": 0,
        "known_long_label_limitation": "DETECTED_NEGATIVE_CONTROL_NOT_SUPPORTED",
        "real_browser_dom_geometry": "CHECKED",
        "independent_visual_human_review": "NOT_RUN",
        "screen_reader_and_keyboard_a11y": "NOT_RUN",
        "human_ai_cognition": "NOT_RUN",
        "tei_product_source_policy": "NOT_RUN",
        "independent_holdout": False,
    }, indent=2))


if __name__ == "__main__":
    main()
