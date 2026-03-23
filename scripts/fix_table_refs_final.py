from pathlib import Path

FILES = [
    Path(r"p:\workhub\Research station\Rutin-mini-review\critical-review-BITE-nature-based-wastewater.md"),
    Path(r"p:\workhub\Research station\Rutin-mini-review\critical-review-BITE-nature-based-wastewater-humanised.md"),
]

for path in FILES:
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "Table 1 reframes each barrier in terms of measurable endpoints and decisive experiments, so that future work can distinguish observed evidence from conjecture; this conversion of our previous four-barrier concept [8] into an actionable validation roadmap is a central contribution of this review.",
        "Table 2 reframes each barrier and deployment route in terms of measurable endpoints, decisive experiments, and go/no-go criteria, so that future work can distinguish observed evidence from conjecture; this conversion of our previous four-barrier concept [8] into an actionable validation roadmap is a central contribution of this review.",
    )
    text = text.replace(
        "The four-barrier framework (Sustainability [8]) is reframed as a validation roadmap (Table 1) with measurable endpoints per barrier.",
        "The four-barrier framework (Sustainability [8]) is reframed as a validation roadmap (Table 2) with measurable endpoints per barrier and deployment route.",
    )
    text = text.replace(
        "Benchmarking should be readiness-based and matrix-aware; compare against chlorine, UV, ozone, and membranes where appropriate (Table 1).",
        "Benchmarking should be readiness-based and matrix-aware; compare against chlorine, UV, ozone, and membranes where appropriate (Table 2).",
    )
    path.write_text(text, encoding="utf-8")

print("Fixed remaining table references in both manuscripts.")
