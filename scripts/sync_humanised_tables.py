# Sync humanised manuscript Tables+Figures with main manuscript
import pathlib

main = pathlib.Path(r"p:\workhub\Research station\Rutin-mini-review\critical-review-BITE-nature-based-wastewater.md")
human = pathlib.Path(r"p:\workhub\Research station\Rutin-mini-review\critical-review-BITE-nature-based-wastewater-humanised.md")

main_text = main.read_text(encoding="utf-8")
human_text = human.read_text(encoding="utf-8")

# Extract Tables + Figures from main (from "## Tables" through "---\n\n" before "## Abbreviations")
start = main_text.index("## Tables\n\n**Table 1.** Evidence-to-action roadmap for rutin")
end = main_text.index("\n\n## Abbreviations")
block = main_text[start:end]

# In humanised, replace from "## Tables" to "## Abbreviations" (exclusive)
h_start = human_text.index("## Tables\n\n**Table 1.** How this mini-review")
h_end = human_text.index("\n\n## Abbreviations")
new_human = human_text[:h_start] + block + human_text[h_end:]
human.write_text(new_human, encoding="utf-8")
print("Synced Tables and Figures to humanised manuscript.")
