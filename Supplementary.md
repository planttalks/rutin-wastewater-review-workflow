# Supplementary Information

**Rutin at the Water–Plant–Virus Interface: A Critical Mini-Review for Nature-Based Wastewater Treatment**

This file provides supplementary data and reproducibility information for the computational workflow described in Section 2 and cited in Sections 3–4 of the main manuscript.

---

## S1. Data and code availability

No primary wet-lab datasets were generated.

**Public code repository (scripts and this Supplementary file).**  
[https://github.com/planttalks/rutin-wastewater-review-workflow](https://github.com/planttalks/rutin-wastewater-review-workflow) (branch `main`). A tagged release (e.g. `v1.0.0`) should be created at submission or acceptance for citation stability.

**Processed outputs and logs (Tables S2–S4, manifests).**  
The paths below refer to the local analysis bundle used to build this mini-review. For submission, archive the `workflow_outputs/02_analysis/` tree (and docking logs under `workflow_outputs/02_analysis/docking/rutin_1MSC_multiligand/`) as a **Zenodo** upload (or equivalent) and cite the **DOI** here and in the main manuscript Data/Code availability statement. The GitHub repository may contain code only; large or binary outputs are often better on Zenodo.


| Item                             | Location                                                                                                                                             |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Descriptor and workflow scripts  | `scripts/rutin_insilico_descriptors_core.py`, `scripts/rutin_vina_docking_prep.py`, `scripts/rutin_multiligand_vina_1MSC.py`                         |
| BioTransformer merge helpers     | `scripts/biotransformer_fetch_rutin.py`, `scripts/biotransformer_merge_jar_csv_to_descriptors.py`, `scripts/biotransformer_merge_products_to_csv.py` |
| Vina logs and docking summary    | `workflow_outputs/02_analysis/docking/rutin_1MSC_multiligand/` (e.g. `*_vina.log`, `summary.csv`, `manifest.json`)                                   |
| BioTransformer outputs           | `workflow_outputs/02_analysis/` (JSON/CSV from environmental microbial mode)                                                                         |
| Descriptor and metabolite tables | `workflow_outputs/02_analysis/rutin_metabolites_descriptors.csv`, `rutin_local_ENVMICRO_1.csv`                                                       |
| Optional Python dependencies     | `requirements-optional-insilico.txt` (RDKit, httpx, numpy, scipy)                                                                                    |


AutoDock Vina (v1.2.7) and Open Babel are used as external executables; versions are logged in run manifests where applicable.

---

## Table S1. Computational parameters (Section 2)


| Parameter              | Value                                                     |
| ---------------------- | --------------------------------------------------------- |
| Receptor               | MS2 coat protein, PDB ID: 1MSC                            |
| Docking software       | AutoDock Vina v1.2.7                                      |
| Grid center (Å)        | *x* = 39.26, *y* = 19.10, *z* = 19.08                     |
| Grid dimensions        | 24 × 24 × 24 Å                                            |
| Exhaustiveness         | 8                                                         |
| Ligand 3D generation   | RDKit (ETKDG), then PDBQT via Open Babel                  |
| BioTransformer mode    | Environmental microbial metabolism, single enzymatic step |
| SMILES standardisation | RDKit                                                     |


---

## Table S2. Molecular descriptors (selected species)

Representative descriptors from the workflow underlying Section 3.1 and 3.3. Full set: `workflow_outputs/02_analysis/rutin_metabolites_descriptors.csv`.


| Species                      | MolLogP | TPSA (Å²) | Note                         |
| ---------------------------- | ------- | --------- | ---------------------------- |
| Rutin (parent)               | ≈ −1.69 | ≈ 269     | Parent glycoside             |
| Quercetin                    | ≈ 2.0   | ≈ 131     | Aglycone                     |
| Protocatechuic acid          | ≈ 0.8   | ≈ 78      | Illustrative small phenolic  |
| BT env disaccharide fragment | ≈ −4.37 | ≈ 169     | Most water-polar in ensemble |


MolLogP, octanol–water partition coefficient (log P); TPSA, topological polar surface area. Values rounded for display; exact values in the CSV.

---

## Table S3. BioTransformer 3.0 environmental microbial single-step products (intact rutin and quercetin)

Single enzymatic step, environmental microbial metabolism mode [59]. Species carried forward to the 1MSC capsid docking screen (Table S4) are indicated.


| Substrate      | Product type                      | Approx. mass (Da) or description | Carried to capsid screen  |
| -------------- | --------------------------------- | -------------------------------- | ------------------------- |
| Rutin (intact) | Disaccharide-range fragment       | ~326                             | Yes (BT_env_disaccharide) |
| Rutin (intact) | Quercetin (aglycone)              | ~302                             | Yes (quercetin)           |
| Rutin (intact) | C15H10O6 scaffold                 | ~286                             | Yes (BT_env_scaffold_286) |
| Quercetin      | Epimerization product             | ~302                             | Yes (BT_Q_epimer)         |
| Quercetin      | Benzopyran-dione isomer           | ~302                             | Yes (BT_Q_benzopyran)     |
| Quercetin      | Dicarboxylic derivative           | —                                | Yes (BT_Q_dicarboxy)      |
| Quercetin      | Aldehyde–acid (neutral acid form) | —                                | Yes (BT_Q_aldehyde_acid)  |


Source: BioTransformer 3.0 [59], environmental microbial mode; RDKit-standardized SMILES inputs. Full outputs: `workflow_outputs/02_analysis/`.

---

## Table S4. Docking results: best affinity per ligand (1MSC global search)

Best binding affinity (kcal mol−1) from the whole-protomer search used in Section 3.3. Full logs and poses are under `workflow_outputs/02_analysis/docking/rutin_1MSC_multiligand/`


| Ligand              | Label                                                     | Best affinity (kcal mol−1) |
| ------------------- | --------------------------------------------------------- | -------------------------- |
| rutin_parent        | Rutin (parent glycoside)                                  | −6.785                     |
| quercetin           | Quercetin (aglycone)                                      | −6.187                     |
| BT_env_disaccharide | ENVMICRO rutin → disaccharide fragment (~326 Da)          | −5.126                     |
| BT_env_scaffold_286 | ENVMICRO rutin → C15H10O6 scaffold (~286 Da)              | −6.116                     |
| BT_Q_epimer         | ENVMICRO quercetin → epimerization product                | −6.110                     |
| BT_Q_benzopyran     | ENVMICRO quercetin → benzopyran-dione isomer              | −5.997                     |
| BT_Q_dicarboxy      | ENVMICRO quercetin → dicarboxylic derivative              | −5.767                     |
| BT_Q_aldehyde_acid  | ENVMICRO quercetin → aldehyde–acid                        | −5.684                     |
| protocatechuic      | Protocatechuic acid (illustrative ring-cleavage phenolic) | −4.483                     |


These values are hypothesis-generating only and are not directly comparable to site-targeted or other receptor setups in Zure et al. [6, 7] (see main text Section 3.3 and 4).