from pathlib import Path


NEW_TABLES = """## Tables

**Table 1.** Evidence map for rutin at the water-plant-virus interface: representative study systems, endpoints, matrix relevance, and translational weight for wastewater applications.

| Evidence domain | Representative virus/model | Experimental context | Matrix realism | Rutin form | Endpoint | Core message for this review | Directness to water-treatment relevance | Key limitation | Translational weight | Ref(s). |
|-----------------|----------------------------|----------------------|----------------|------------|----------|------------------------------|-----------------------------------------|----------------|---------------------|---------|
| Direct aqueous virion evidence | MS2 and T4 bacteriophages (surrogates) | Aqueous infectivity experiments with in-silico support | Simplified aqueous laboratory systems | Purified rutin | Binding plus infectivity response | Only evidence domain that directly tests water-phase virion attenuation | Direct, but still proof-of-concept | Surrogate phages, simplified chemistry, no wastewater benchmarking | Direct proof-of-concept | [7] |
| Computational comparator evidence | Selected viral surface proteins | Docking and target-ranking studies | No environmental matrix | Purified rutin within mixed comparator sets | Docking affinity and target ranking | Useful for hypothesis prioritization, not for deployment claims | Indirect | No infectivity outcome or matrix realism | Hypothesis support | [6] |
| Intracellular or cell-based antiviral evidence | SARS-CoV-2 3CLpro and related intracellular targets; dengue virus type 2 in cell systems | Biochemical, cell-based, or computational antiviral studies | Non-environmental biological systems | Purified rutin or related flavonoids | Enzyme inhibition or intracellular antiviral context | Mechanistic context exists, but target accessibility in aqueous virions remains unresolved | Indirect | Intracellular targets are not equivalent to virion inactivation in water | Mechanistic context | [11-18, 54] |
| Extract-based antiviral evidence | Mixed viruses or biological systems | Plant-extract assays and host-response studies | Extract and cell systems, not wastewater matrices | Rutin-containing extracts or biomass | Antiviral activity or host-response modulation | Extract activity cannot be treated as pure-rutin evidence | Contextual only | Attribution to rutin is unresolved | Contextual support | [9] |

*Note (Table 1):* Translational weight distinguishes direct proof-of-concept evidence from hypothesis support, mechanistic context, and broader contextual support. It does not imply engineering readiness.

---

**Table 2.** Minimum evidence and benchmarking requirements for deploying rutin-related concepts in nature-based wastewater treatment.

| Translational unit | Hypothesized role or use case | Required measurands | Decisive experiment | Comparator/control | Minimum success criterion | Current readiness | Main uncertainty | Ref(s). |
|--------------------|-------------------------------|---------------------|---------------------|--------------------|---------------------------|------------------|------------------|---------|
| Barrier 1. Sorption and filtration | Rutin changes virus retention or local inactivation at roots, biofilms, or treatment solids | Virus partitioning, infectivity loss, and surface-bound parent/metabolites | Defined-surface assays with quantified rutin exposure under controlled matrix chemistry | Matched surface without rutin and hydraulic control | Attributable infectivity or partitioning shift beyond sorption alone | Hypothesis stage | Whether rutin changes surface interactions at realistic concentrations | [8, 30, 40-44] |
| Barrier 2. Rhizosphere-mediated attenuation | Dissolved rutin, metabolites, or rhizosphere microbiome shifts contribute to attenuation | Infectivity, parent/metabolite concentrations, rhizosphere chemistry, microbiome profile | Planted vs. unplanted rhizobox or wetland assays with coupled chemistry and infectivity measurements | Unplanted control and sterilized or microbiome-perturbed control | Concurrent infectivity change with measured chemical exposure | Partial but unvalidated | Whether chemistry or microbiome effects drive the signal | [8, 30, 43, 44, 53] |
| Barrier 3. Plant internalisation | Virus and rutin/metabolites co-localize within tissues and alter recoverable infectivity | Tissue virus signal, tissue parent/metabolites, compartment mapping | Time-resolved co-quantification in root and shoot compartments | Plant with virus only, plant with rutin only, and matrix control | Same-compartment co-localization linked to infectivity outcome | Hypothesis stage | Whether virus and active species ever meet inside tissues | [8, 30, 31, 39] |
| Barrier 4. Intracellular degradation or transformation | Plant metabolism forms more or less active antiviral species | Metabolite identity, abundance, and infectivity outcome | Metabolomics-linked attenuation assays with planted and sterile controls | Sterile matrix control and parent-rutin dosing control | Reproducible metabolite-linked infectivity change | Hypothesis stage | Active species may be transformed products rather than parent rutin | [8, 45, 50, 51] |
| Passive release from living roots | Plant-mediated delivery without external dosing | Rhizosphere rutin flux, metabolite profile, and adjacent-water infectivity | Candidate wetland plants quantified across stress and seasonal states | Unplanted cell and purified-rutin matched dose | Measurable release overlaps antiviral range and tracks infectivity | Hypothesis stage | Natural release may be too low or too transient | [30, 43, 44, 53] |
| Plant litter or senescing biomass | Delayed release from decaying material in treatment beds | Release kinetics, sorption to solids, transformation products, and infectivity | Decomposition microcosms linked to virus attenuation assays | Fresh-biomass control and no-biomass control | Reproducible attenuation with defined release chemistry | Hypothesis stage | Decomposition may destroy rather than deliver active species | [30, 36, 43, 53] |
| Added plant extracts or processed biomass | Externally amended phytochemical mixture | Extract composition, rutin-equivalent dose, co-metabolites, and infectivity | Matrix-aware dosing trials with chemistry and infectivity tracking | Solvent control and purified-rutin comparator | Effect exceeds solvent control and attribution to the rutin-equivalent fraction is justified | Discovery stage | Extract effects may not be caused by rutin alone | [9, 53] |
| Purified rutin amendment | Direct, benchmarkable dosing route | Parent concentration, transformation products, matrix demand, and infectivity response | Dose-response trials in realistic water or wastewater matrices with established comparators | No-rutin control and chlorine, UV, ozone, or membrane benchmark | Reproducible infectivity reduction under realistic matrices and benchmarking | Discovery stage | Most controllable route, but least representative of passive phytoremediation | [6, 7, 23, 26, 28, 29, 45, 47-49] |

*Note (Table 2):* This table merges barrier validation and deployment scenarios so that readers can see, in one place, what must be measured before any credible wastewater deployment claim can be made.
"""


def update_file(path_str: str) -> None:
    path = Path(path_str)
    text = path.read_text(encoding="utf-8")

    replacements = {
        "Table 2 summarises how this mini-review differs from prior treatments and states these questions explicitly.": "Tables 1 and 2 summarise the current evidence base and the minimum translational requirements that follow from it.",
        "Table 2 summarises how this mini-review differs from prior treatments and spells out these questions; Table 1 gives the evidence-to-action roadmap and pilot checklist.": "Tables 1 and 2 summarise the current evidence base and the minimum translational requirements that follow from it.",
        "First, we provide an evidence-graded, rutin-specific account that no prior treatment provides (Table 2). Second, we separate evidence explicitly into three domains (direct virion, cell-based, extract-based) with distinct relevance to water-phase attenuation (Table 1). Third, we translate our previous four-barrier model [8] into a validation roadmap with measurable endpoints and decisive experiments per barrier (Section 4, Table 1). Fourth, we make physicochemical fate, hydraulic context, and deployment modes explicit for nature-based treatment design (Table 1, Table 3, Section 5).": "First, we provide an evidence-graded, rutin-specific account of the current evidence base (Table 1). Second, we separate evidence explicitly into three domains (direct virion, cell-based, extract-based) with distinct relevance to water-phase attenuation (Table 1). Third, we translate our previous four-barrier model [8] into a validation roadmap with measurable endpoints and decisive experiments per barrier (Section 4, Table 2). Fourth, we make physicochemical fate, deployment scenarios, and benchmarking requirements explicit for nature-based treatment design (Table 2, Section 5).",
        "First, we provide an evidence-graded, rutin-specific account that no prior treatment provides (Table 2). Second, we separate evidence explicitly into three domains (direct virion, cell-based, extract-based) with distinct relevance to water-phase attenuation. Third, we translate our previous four-barrier model [8] into a validation roadmap with measurable endpoints and decisive experiments per barrier (Section 4, Table 1). Fourth, we make physicochemical fate, hydraulic context, and deployment modes explicit for nature-based treatment design (Table 1, Table 3, Section 5).": "First, we provide an evidence-graded, rutin-specific account of the current evidence base (Table 1). Second, we separate evidence explicitly into three domains (direct virion, cell-based, extract-based) with distinct relevance to water-phase attenuation. Third, we translate our previous four-barrier model [8] into a validation roadmap with measurable endpoints and decisive experiments per barrier (Section 4, Table 2). Fourth, we make physicochemical fate, deployment scenarios, and benchmarking requirements explicit for nature-based treatment design (Table 2, Section 5).",
        "Table 3 therefore separates plant-linked delivery modes from direct compound application;": "Table 2 therefore separates plant-linked delivery modes from direct compound application;",
        "Table 1 and Table 3 specify suggested measurands (virus partitioning, infectivity, parent and transformation product concentrations) and deployment modes; target ranges for HRT, dosing concentration, or contact time would require data from the staged experiments outlined in the research agenda. Table 1 (continued) summarises a minimal pilot and design checklist for quick reference.": "Table 2 specifies suggested measurands, decisive experiments, deployment routes, and benchmarking controls; target ranges for HRT, dosing concentration, or contact time would require data from the staged experiments outlined in the research agenda. A minimal pilot can therefore be derived directly from the go/no-go structure in Table 2.",
        "Accordingly, Figure 1 and Table 1 (Readiness rows) should be read as evidence-readiness tools.": "Accordingly, Figure 1 and Table 2 should be read as evidence-to-deployment tools.",
        "(Table 1, Table 3).": "(Table 2).",
        "(see Table 3 for deployment modes)": "(see Table 2 for deployment routes and go/no-go criteria)",
        "Figure 1 presents the conceptual framework; see the Figures section for the full caption and file reference.": "Figure 1 presents the integrated evidence-to-deployment framework; see the Figures section for the full caption and file reference.",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    start = text.index("## Tables")
    end = text.index("## Figures")
    text = text[:start] + NEW_TABLES + "\n\n---\n\n" + text[end:]

    old_figure = "**Figure 1.** Conceptual framework proposed in this review for rutin at the water–plant–virus interface: evidence scales (molecular → assay → technology) and four potential barriers (sorption/filtration, rhizosphere, internalisation, intracellular). Readiness versus established technologies is given in Table 1. *File:* `figures/fig1_three_scales_four_barriers.svg`."
    new_figure = "**Figure 1.** From rutin antiviral signal to wastewater relevance: current evidence domains, translation gates, and barrier-resolved deployment logic for nature-based systems. Only direct aqueous virion evidence currently reaches the wastewater-relevant bridge; cell-based and extract evidence remain indirect or contextual. Established technologies (chlorine, UV, ozone, membranes) are benchmark comparators rather than peers in readiness. *File:* `figures/fig1_three_scales_four_barriers.svg`."
    text = text.replace(old_figure, new_figure)

    path.write_text(text, encoding="utf-8")


for file_path in [
    r"p:\workhub\Research station\Rutin-mini-review\critical-review-BITE-nature-based-wastewater.md",
    r"p:\workhub\Research station\Rutin-mini-review\critical-review-BITE-nature-based-wastewater-humanised.md",
]:
    update_file(file_path)

print("Updated display items in both manuscripts.")
