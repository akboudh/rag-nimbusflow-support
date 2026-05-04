from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendStaticTests(unittest.TestCase):
    def test_custom_query_not_rendered_as_selected_prompt(self) -> None:
        app_js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('activeExample = allExamples.find((example) => example.query === selectedExampleQuery)', app_js)
        self.assertIn("Custom question", app_js)
        self.assertIn("aria-pressed", app_js)

    def test_workspace_rail_uses_viewport_aware_height(self) -> None:
        styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertNotIn("height: 930px", styles)
        self.assertIn("minmax(280px, 50vh)", styles)
        self.assertIn("transition: none !important", styles)
        self.assertIn("animation: none !important", styles)

    def test_removed_markup_selectors_are_not_kept_in_css(self) -> None:
        styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

        for selector in (
            "logo-cloud",
            "cloud-ring",
            "cloud-core",
            "usage-chart",
            "usage-center",
            "usage-legend",
            "legend-",
            "tool-pill",
            "beta-tag",
            "new-query",
            "spark",
            "show-more",
            "example-toggle",
        ):
            self.assertNotIn(selector, styles)


if __name__ == "__main__":
    unittest.main()
