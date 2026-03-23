# Replace Tables section in critical-review-BITE-nature-based-wastewater.md
# Single Table 1, add Table 2, add Figures section with Figure 1
import pathlib

path = pathlib.Path(r"p:\workhub\Research station\Rutin-mini-review\critical-review-BITE-nature-based-wastewater.md")
text = path.read_text(encoding="utf-8")

# Marker: start of Tables section
start_marker = "## Tables\n\n**Table 1.** Evidence-to-action roadmap: evidence domains (A), four-barrier"
end_marker = "\n\n**Supplementary material.** Positioning and deployment (how this review differs from prior work; deployment modes for rutin) are provided as **Supplementary Table S1**.\n\n---"

if start_marker not in text:
    raise SystemExit("Start marker not found")
if end_marker not in text:
    raise SystemExit("End marker not found")

new_section = r"""## Tables

**Table 1.** Evidence-to-action roadmap for rutin at the water–plant–virus interface: evidence domains, four-barrier validation, readiness comparison, and minimal pilot checklist in one reference for study design, benchmarking, and pilot design.

| Category | Item | Description / endpoint / specification | Status or next step | Ref(s). |
|----------|------|----------------------------------------|---------------------|---------|
| **Evidence** | Direct aqueous virion | Pure rutin, MS2/T4 phages; relevance to water-phase: moderate | Surrogate phages, simplified conditions only | [7] |
| **Evidence** | Computational | Docking to viral surface proteins; relevance: low | No infectivity benchmark in realistic matrices | [6] |
| **Evidence** | Intracellular/cell-based | Rutin vs. 3CLpro and related targets; indirect relevance | Target not accessible in water-phase virions | [11-18] |
| **Evidence** | Extract-based | Rutin-containing plant extracts; low to indirect relevance | Rutin not isolated as sole active species | [9] |
| **Barrier** | 1. Sorption and filtration | Endpoint: virus partitioning or infectivity at surfaces with quantified rutin | Compare retention and infectivity with/without rutin under controlled matrix | [8, 30, 40-44] |
| **Barrier** | 2. Rhizosphere-mediated | Endpoint: infectivity in rhizosphere water with parent/metabolite measurement | Planted vs. unplanted; rhizosphere chemistry, microbiome, infectivity | [8, 30, 43, 44] |
| **Barrier** | 3. Plant internalisation | Endpoint: virus and rutin/metabolites in same tissue | Quantify virus and rutin in same compartments over time | [8, 30, 31, 39] |
| **Barrier** | 4. Intracellular degradation | Endpoint: metabolites linked to infectivity outcome | Metabolomics-linked attenuation in planted vs. sterile | [8, 45, 50, 51] |
| **Readiness** | Purified rutin | Candidate virion interaction; limited proof-of-concept | Discovery stage | [6, 7] |
| **Readiness** | Rutin-rich biomass | Mixed phytochemical; not water-validated | Discovery stage | [9] |
| **Readiness** | Chlorination, UV, ozone, membranes | Established disinfection or removal | Deployment ready | [23, 26, 28, 29, 45, 47-49] |
| **Pilot** | Objective | Separate phytochemical-mediated attenuation from hydraulic, sorptive, and microbial removal | — | — |
| **Pilot** | Design | Paired cells: planted vs. unplanted or rutin-dosed vs. control; defined HRT, hydraulic loading, virus spike or natural load | — | — |
| **Pilot** | Measurands | Virus partitioning and infectivity; parent rutin and key metabolites in porewater and tissue (see Table 2 for deployment modes) | — | — |
| **Pilot** | Success criteria | Attributable infectivity or partitioning change with concurrent rutin/metabolite data; comparison with established technologies | — | — |

*Note:* Evidence "relevance" denotes whether the domain informs water-phase virion attenuation (not engineering readiness). Readiness does not imply equivalence between rutin and validated technologies; it shows current asymmetry in evidence maturity.

---

**Table 2.** Positioning and deployment: how this review differs from prior work (A) and deployment modes for rutin (B).

**A. How this mini-review differs from prior reviews**

| Review or article focus | Main evidence domain | Water-treatment relevance | Rutin-specific? | Gap addressed here | Ref(s). |
|-------------------------|----------------------|---------------------------|-----------------|--------------------|---------|
| Antiviral medicinal plants and metabolomics | Plant extracts, host responses, broad antiviral context | Mostly indirect | No | Limited treatment-train and matrix-specific translation | [9] |
| Constructed wetlands and pathogen removal | System-level wastewater and wetland attenuation | High | No | Phytochemical identity and compound-specific virus mechanisms rarely resolved | [30, 36] |
| Conventional wastewater virus disinfection | Validated environmental treatment processes | High | No | Does not address plant-derived compounds as candidate modifiers | [23] |
| Antiviral phytoremediation framework | Conceptual four-barrier framing | Moderate | Partly | Barrier logic stronger than direct rutin evidence base | [8] |
| This mini-review | Direct virion, intracellular, and extract evidence separated explicitly | Targeted | Yes | Minimum evidence required before environmental translation claims | This article |

**B. Deployment modes for rutin: what must be measured and current readiness**

| Deployment mode | Source compartment | What must be measured directly | Main uncertainty | Readiness | Ref(s). |
|-----------------|--------------------|---------------------------------|------------------|-----------|---------|
| Passive release from living roots | Root tissues and rhizosphere exudates | Root or rhizosphere rutin concentration, metabolite profile, infectivity in adjacent water | Whether plants release enough rutin or active metabolites to matter virologically | Hypothesis stage | [30, 43, 44, 53] |
| Plant litter or senescing biomass | Decaying shoots, roots, associated solids | Temporal release profile, sorption to solids, transformation products, virus attenuation | Whether decomposition increases local exposure or accelerates loss | Hypothesis stage | [30, 36, 43, 53] |
| Added plant extracts or processed biomass | External amendment to treatment system | Extract composition, rutin fraction, co-metabolites, matrix stability, infectivity endpoint | Attribution: extract effects may not be rutin alone | Discovery stage | [9, 53] |
| Purified rutin amendment | Direct dosing to water or treatment unit | Parent concentration, transformation products, matrix demand, infectivity response | Most controllable; least representative of passive phytoremediation | Discovery stage | [6, 7] |

*Note (Table 2):* Plant-mediated delivery (B, rows 1–2) differs from direct compound addition (rows 3–4) in translational questions, fate pathways, and engineering implications.

---

## Figures

**Figure 1.** Conceptual framework for rutin at the water–plant–virus interface: evidence scales (molecular → assay → technology) and four potential barriers (sorption/filtration, rhizosphere, internalisation, intracellular). Rutin currently sits at discovery/hypothesis stage; readiness comparison with established virus-control technologies is in Table 1 (Readiness rows). *File:* `figures/fig1_three_scales_four_barriers.svg`.

---
"""

start_i = text.index(start_marker)
end_i = text.index(end_marker) + len(end_marker)
new_text = text[:start_i] + new_section + text[end_i:]
path.write_text(new_text, encoding="utf-8")
print("Replaced Tables section successfully.")
