# Literature Review: Vibrio natriegens Growth Optimization for Closed-Loop Bayesian Optimization

**Authors**: Srusti Sain, Keltoum Boukra
**Project**: Closed-Loop AI Scientist for Cell Culture Workcell
**Date**: March 2026
**Organism**: *Vibrio natriegens* (ATCC 14048 / Vmax)

---

## Table of Contents

1. [Organism Overview](#1-organism-overview)
2. [Growth Rate Records and Benchmarks](#2-growth-rate-records-and-benchmarks)
3. [Media Composition](#3-media-composition)
   - 3.1 Complex Media Formulations
   - 3.2 Defined/Minimal Media
   - 3.3 Low-Chloride Industrial Medium
   - 3.4 v2 Salts
4. [Sodium and Salt Requirements](#4-sodium-and-salt-requirements)
5. [Osmolality](#5-osmolality)
6. [pH and Buffering](#6-ph-and-buffering)
7. [Temperature](#7-temperature)
8. [Oxygen and Aeration](#8-oxygen-and-aeration)
9. [Carbon Sources](#9-carbon-sources)
10. [Nitrogen Sources and Amino Acids](#10-nitrogen-sources-and-amino-acids)
11. [Divalent Cations (Mg2+, Ca2+, K+)](#11-divalent-cations)
12. [Trace Metals](#12-trace-metals)
13. [Overflow Metabolism and Acid Sensitivity](#13-overflow-metabolism-and-acid-sensitivity)
14. [Unique Biology](#14-unique-biology)
15. [Novel Optimization Ideas](#15-novel-optimization-ideas)
16. [Bayesian Optimization Methodology](#16-bayesian-optimization-methodology)
17. [White Paper Strategy: Three Optimization Targets](#17-white-paper-strategy-three-optimization-targets)
18. [Recommended BO Parameter Space](#18-recommended-bo-parameter-space)
19. [References](#19-references)

---

## 1. Organism Overview

*Vibrio natriegens* is a Gram-negative, non-pathogenic, halophilic marine bacterium originally isolated from salt marsh mud (Paynter & Bungay, 1969). It holds the record as the **fastest-growing non-pathogenic bacterium known**, with a doubling time under 10 minutes in optimal rich media.

**Why it matters for biotech:**
- Doubling time of ~9.4 min in BHIN (vs. ~20 min for *E. coli*)
- Glucose uptake rate of **3.90 g/g/h** -- more than 2x faster than *E. coli*
- **115,000 ribosomes per cell** (vs. 70,000 in *E. coli*) -- 29% RNA by dry weight
- Naturally competent (efficient transformation without electroporation)
- Growing genetic toolbox: NT-CRISPR (up to 100% efficiency), Graded-CRISPRi, Vnat Collection of standardized genetic parts
- Can consume >60 carbon substrates including chitin derivatives (ecologically relevant marine nutrient)
- Demonstrated fed-batch cultivation to >60 g/L biomass
- Two chromosomes (3.2 Mb + 1.9 Mb) with dynamic ploidy -- up to 50 copies of origin regions during fast growth

---

## 2. Growth Rate Records and Benchmarks

| Medium | Temp | Growth Rate (h⁻¹) | Doubling Time | Source |
|--------|------|--------------------|---------------|--------|
| BHIN (BHI + NaCl) | 37°C | **4.43** (max) | **9.4 min** | Hoffart et al. 2017 |
| BHIN (routine) | 37°C | 2.70 ± 0.03 | 15.4 min | Hoffart et al. 2017 |
| LBv2 | 37°C | ~3.0 | ~14 min | SGI/Barrick Lab |
| LB + 2.5% NaCl | 37°C | ~3.1 | 13.6 min | Pfeifer et al. 2019 |
| M9 + 1.5% NaCl + Wolfe's | 37°C | 1.70 ± 0.02 | 24 min | Long et al. 2017 |
| VN minimal + glucose (aerobic) | 37°C | 1.48-1.66 | 25-28 min | Hoffart et al. 2017 |
| Wilms-MOPS optimized | 37°C | **1.97 ± 0.13** | **21 min** | Gericke et al. 2024 |
| Low-chloride VN10 (batch) | 30°C | 0.90-0.96 | 43-46 min | Stadler et al. 2023 |
| VN minimal (anaerobic) | 37°C | 0.92 ± 0.01 | 45 min | Hoffart et al. 2017 |

**Note**: The 1.97 h⁻¹ on Wilms-MOPS medium (Gericke et al. 2024) is the **highest growth rate ever reported on a chemically defined medium** for *V. natriegens*. This was achieved by independently optimizing NaCl and osmolality -- two parameters previously confounded in the literature.

**OD600 to dry weight**: 1.0 OD600 ≈ **0.27 g CDW/L** (*V. natriegens* specific)

---

## 3. Media Composition

### 3.1 Complex Media Formulations

**BHIN** (Hoffart et al. 2017) -- Fastest growth:
- Brain Heart Infusion: 37 g/L
- NaCl: 15 g/L
- Growth rate: up to 4.43 h⁻¹

**LBv2** (SGI-DNA / Synthetic Genomics) -- Standard lab medium:
- LB Broth Miller: 25 g/L
- Additional NaCl: 200 mM (~11.7 g/L, total NaCl ~22 g/L)
- MgCl₂: 23.14 mM (2.2 g/L)
- KCl: 4.2 mM (0.31 g/L)
- Doubling time: ~14 min

**LB3** (Church Lab) -- Simple alternative:
- LB-Miller + 2% additional NaCl (total 3% = 30 g/L)
- Lacks Mg²⁺ and K⁺ supplementation of LBv2

**Marine 2216E** -- Simulates natural environment:
- Peptone: 5 g/L, Yeast powder: 1 g/L, NaCl: 19.45 g/L
- Ferric citrate: 0.1 g/L, Na₂SO₄: 3.24 g/L, CaCl₂: 1.8 g/L
- MgCl₂: 5.98 g/L, KCl: 0.55 g/L, NaCO₃: 0.16 g/L
- Plus trace: KBr, SrCl₂, H₃BO₃, NaSiO₃, NaF, NH₄NO₃, Na₂HPO₄

### 3.2 Defined/Minimal Media

**VN Minimal Medium** (Hoffart et al. 2017):

| Component | Concentration |
|-----------|---------------|
| (NH₄)₂SO₄ | 5 g/L |
| NaCl | 15 g/L |
| KH₂PO₄ | 1 g/L |
| K₂HPO₄ | 1 g/L |
| MgSO₄ | 0.25 g/L |
| CaCl₂ | 0.01 g/L |
| FeSO₄·7H₂O | 16.4 mg/L |
| MnSO₄·H₂O | 10 mg/L |
| CuSO₄·5H₂O | 0.3 mg/L |
| ZnSO₄·7H₂O | 1 mg/L |
| NiCl₂·6H₂O | 0.02 mg/L |
| Glucose | 10-50 g/L |

Growth rate: 1.48-1.66 h⁻¹ (aerobic), 0.92 h⁻¹ (anaerobic)

**M9-based Semi-Defined** (Long et al. 2017):
- Standard M9 salts + 15 g/L NaCl
- 10 mL/L Wolfe's minerals + 10 mL/L Wolfe's vitamins
- 0.05 g/L yeast extract (eliminates lag phase)
- Growth rate: 1.70 ± 0.02 h⁻¹

**Wilms-MOPS Optimized** (Gericke et al. 2024):
- MOPS buffer: 280-350 mM (optimal)
- NaCl: 7.5-15 g/L
- Trace elements, glucose 10-20 g/L
- Growth rate: **1.97 ± 0.13 h⁻¹** (record on defined medium)

### 3.3 Low-Chloride Industrial Medium

**VN10 Medium** (Stadler et al. 2023) -- eliminates bioreactor corrosion:

| Component | Concentration |
|-----------|---------------|
| Glucose | 24 g/L |
| KH₂PO₄ | 3 g/L |
| Na₂HPO₄·2H₂O | 16.59 g/L |
| Na₂SO₄ | 8.10 g/L |
| Na₃-citrate·2H₂O | 9.84 g/L |
| MgSO₄·7H₂O | 0.74 g/L |
| NH₄Cl | 1 g/L |
| Trace elements | 2% (v/v) |

**Key results:**
- Chloride reduced from 12.65 g/L to **10.3 mg/L** (>1000-fold)
- Shake flask OD600: 20.8 ± 0.87
- Fed-batch bioreactor: **59-62.5 g/L CDW**
- Osmolality: 0.8-0.91 Osmol/kg

**Critical findings:**
- EDTA-containing trace element solutions **strongly inhibit** growth
- Citrate is essential -- prevents ammonium magnesium phosphate precipitate while serving as sodium source
- NaCl can be **fully replaced** by Na₂HPO₄ + Na₂SO₄ + Na₃-citrate at equivalent total Na⁺

### 3.4 v2 Salts Explained

The v2 salt supplement (developed by SGI-DNA for Vmax product line):

| Component | Concentration |
|-----------|---------------|
| NaCl | 204 mM (11.9 g/L) |
| KCl | 4.2 mM (0.31 g/L) |
| MgCl₂ | 23.14 mM (2.2 g/L) |

**Why v2 outperforms simple NaCl supplementation:** K⁺ and Mg²⁺ are essential for ribosome stability and translation fidelity. Cell-free extracts from LBv2-grown cells produce **196 ± 12.46 µg/mL** protein, outperforming LB3 extracts (Des Soye et al. 2018). Since *V. natriegens* has 29% RNA by dry weight (higher ribosome content than *E. coli*), its Mg²⁺ and K⁺ demands are proportionally higher.

---

## 4. Sodium and Salt Requirements

NaCl is the **single most critical parameter** for *V. natriegens* growth, but recent work has overturned long-standing assumptions.

### Classical Understanding (pre-2024)
- Optimal: 15-25 g/L NaCl (1.5-2.5%)
- Minimum: ~10-15 g/L for growth
- Below 5 g/L: almost no growth
- Above 58 g/L (1M): no growth
- Best in LB: 2.5% NaCl gave highest OD of 1.021 (Pfeifer et al. 2019)

### Revised Understanding (Gericke et al. 2024)
- **Global optimum: 7.5-15 g/L NaCl** -- lower than previously thought
- The classical 15-25 g/L "optimum" was confounded by osmolality effects
- When osmolality is independently controlled via MOPS buffer, optimal NaCl drops significantly
- Growth rate at 10 g/L NaCl + 280 mM MOPS: **1.97 h⁻¹** (highest on defined medium)
- **Sodium ions are specifically required** (not just osmolarity) -- they stabilize the membrane and drive Na⁺-dependent transport

### Sodium Source Flexibility
- NaCl replaceable with Na₂HPO₄, Na₂SO₄, Na₃-citrate at equivalent total Na⁺ (Stadler et al. 2023)
- Total Na⁺ concentration is what matters, not the specific anion
- This enables low-chloride industrial processes

### Compatible Solutes as Sodium Supplements
- Glycine betaine, dimethylglycine, sarcosine serve **dual roles**: osmoprotectant AND carbon/energy source
- Choline, glycine betaine, DMG, and DMSP are most effective at rescuing growth at low Na⁺ (recent 2025 finding)

---

## 5. Osmolality

This is a recently recognized critical parameter, previously confounded with NaCl effects.

| Osmolality (Osmol/kg) | Effect |
|------------------------|--------|
| 0.6-0.8 | Suboptimal growth |
| **1.0-1.6** | **Optimal range** |
| 1.0-1.4 | Optimal at pH 8.0 |
| 1.1-1.5 | Optimal at pH 7.5 |
| >2.0 | Growth impaired |

**Key insight:** Previously reported NaCl "optima" of 15-25 g/L were partly an osmolality artifact. When osmolality is maintained independently (via MOPS buffer), the true sodium optimum is lower. This means *V. natriegens* needs both: (1) specific sodium ions and (2) appropriate osmolality from any compatible solute.

At lowest tested osmolality (0.88 Osmol/kg, 200 mM MOPS, 0 g/L NaCl): growth rate only 0.81 h⁻¹. At optimized osmolality (1.2 Osmol/kg): up to 1.97 h⁻¹ and final OD up to 13.

---

## 6. pH and Buffering

### pH Range
| pH | Effect |
|----|--------|
| 5.5 | Virtually no growth |
| 6.0-6.5 | Poor to moderate |
| **7.0-8.5** | **Optimal** |
| 8.0 | Recommended initial pH for mineral media |
| 9.0-10.0 | Reduced but viable |

### Acid Sensitivity -- The #1 Growth Limitation

This is arguably the most important and underappreciated factor in *V. natriegens* cultivation:

- *V. natriegens* **lacks nearly all acid resistance mechanisms** present in *E. coli* (no glutamate-dependent, arginine-dependent, or lysine-dependent acid resistance systems)
- In unbuffered glucose fermentation, pH drops to ~5.3 from organic acid accumulation
- The organism reaches **extinction within 12 hours** after growth phase -- 3 days sooner than *E. coli*
- Up to 25% of carbon flux goes to acetate, plus lactate and formate under microaerobic conditions

### Buffering Requirements

| Glucose (g/L) | Minimum MOPS | Recommended MOPS |
|----------------|--------------|------------------|
| 10 | 180 mM | 180-300 mM |
| 20 | 300 mM | **450 mM** |
| Unbuffered | -- | Death within 12 h |

- 100 mM MOPS delays extinction by 24 h
- 200 mM MOPS prevents extinction over 100 h
- **450 mM MOPS at 10 g/L NaCl** recommended for time-efficient production (Gericke et al. 2024)
- MOPS preferred over phosphate buffer (doesn't interfere with phosphate metabolism)

---

## 7. Temperature

| Temperature | Effect |
|-------------|--------|
| ≤28°C | Significantly slowed; **avoid for routine work** |
| 30°C | Good growth; **preferred for fed-batch** (62% more biomass than 37°C) |
| **37°C** | **Maximum growth rate** |
| >37°C | Growth slows significantly |

**Critical nuance:** 37°C gives the fastest instantaneous growth rate, but 30°C gives higher final biomass in fed-batch. This is because lower temperature reduces overflow metabolism and acid accumulation. The choice depends on your objective: growth rate vs. biomass yield.

**Starter cultures**: Commonly grown overnight at 30°C, 225 rpm.

---

## 8. Oxygen and Aeration

*V. natriegens* has **exceptionally high oxygen demand** -- this is the rate-limiting factor in 96-well plates.

| Parameter | Value |
|-----------|-------|
| Specific O₂ uptake rate | 22-28 mmol/gCDW/h |
| Volumetric OUR (fed-batch peak) | Up to **500 mmol/L/h** |
| DO setpoint (bioreactor) | ≥30-40% saturation |
| Bioreactor aeration | 0.25-2 vvm + up to 60% O₂ enrichment |
| Bioreactor agitation | 500-1200 rpm (cascade) |

**Consequence of O₂ limitation:** Triggers mixed acid fermentation → acetate, lactate, formate accumulate → pH crash → rapid cell death (due to acid sensitivity).

**Plate-based cultivation:**
- BioLector XT with FlowerPlate MTPs: 582 rpm, 1 mm amplitude works well
- Standard 96-well: use **low fill volumes** (100-200 µL), high shaking speed, breathable membrane seals
- Measurement interval: every 5-10 min given fast doubling time

---

## 9. Carbon Sources

### Growth Rates by Carbon Source (VN minimal, aerobic, 37°C)

| Carbon Source | Growth Rate (h⁻¹) | Doubling Time | Notes |
|---------------|-------------------|---------------|-------|
| **Sucrose** | **1.79 ± 0.02** | 23.2 min | Best single carbon source |
| **N-acetylglucosamine** | **1.74 ± 0.01** | 23.9 min | Chitin monomer -- ecologically relevant |
| **Glucose** | **1.68 ± 0.02** | 24.8 min | Most commonly used |
| Fructose | 1.51 ± 0.08 | 27.5 min | |
| Maltose | 1.22 ± 0.01 | 34.1 min | |
| Glycerol | 0.86 ± 0.03 | 48.3 min | Lower overflow metabolism |
| Arabinose | 0.83 ± 0.02 | 50.1 min | |
| Glucosamine | 0.68 ± 0.02 | 61.2 min | |
| Rhamnose | 0.40 ± 0.01 | 104 min | |
| Galactose | 0.18 ± 0.01 | 231 min | Very slow |

**No growth on:** xylose, lactose, mannose, cellobiose, ethanol, methanol, formate (wild-type).

Source: Hoffart et al. 2017

### Substrate Uptake Rates
- **Aerobic glucose uptake**: 3.90 ± 0.08 g/g CDW/h (21.4 ± 1.3 mmol/gDW/h)
- **Anaerobic glucose uptake**: 7.81 ± 0.71 g/g CDW/h
- **Biomass yield**: 0.38-0.44 gDW/g glucose (aerobic)
- For comparison, *E. coli* aerobic glucose uptake is ~1.5-2.0 g/g/h

### Key Finding: Sucrose > Glucose
Sucrose gives ~7% higher growth rate than glucose. This is underexplored in the optimization literature and could be a quick win for BO.

### Seawater-Based Cultivation
- Seawater naturally provides ~3% NaCl plus trace minerals
- Growth in seawater-based VN medium was **better** than distilled water-based (Dong et al. 2022)
- No external NaCl needed; trace minerals from seawater contribute positively

---

## 10. Nitrogen Sources and Amino Acids

### Primary Nitrogen Source
- Standard: **(NH₄)₂SO₄ at 5 g/L** in VN minimal medium
- Fed-batch: NH₄Cl at 1 g/L (VN10 medium)
- Generally non-limiting in standard formulations

### Nitrogen Fixation
- *V. natriegens* possesses nif cluster genes
- Can fix atmospheric N₂ under nitrogen-limiting **anaerobic** conditions
- Not relevant for aerobic optimization but interesting biologically

### Amino Acid Supplementation

**Yeast extract:**
- 0.05 g/L in M9-based medium eliminates lag phase
- Provides vitamins, cofactors, and growth factors

**Casamino acids (CAA):**
- Low concentrations show strong positive influence on growth
- Provides free amino acids that bypass biosynthetic cost

**Aspartate and glutamate:**
- Positively influence growth
- Provide pH buffering (amino acid catabolism can release NH₃)
- Aspartate may serve as alternative energy source and protective osmolyte
- *V. natriegens* has elevated glutamate/glutamine levels compared to *E. coli*

### Biomass Composition (Long et al. 2017)
- **Protein: 47%** of dry weight
- **RNA: 29%** (very high -- reflects massive ribosome content)
- Lipids: 7%
- Glycogen: remaining

The 47% protein content and extreme growth rate imply massive amino acid biosynthetic demand. Amino acid supplementation could relieve this bottleneck.

---

## 11. Divalent Cations

### Magnesium (Mg²⁺)

| Context | Mg²⁺ Source | Concentration |
|---------|-------------|---------------|
| v2 salts | MgCl₂ | 23.14 mM (2.2 g/L) |
| VN minimal | MgSO₄ | ~2 mM (0.25 g/L) |
| VN10 low-chloride | MgSO₄·7H₂O | ~3 mM (0.74 g/L) |
| Cell-free (Des Soye) | Mg-glutamate | 3.5 mM |
| Cell-free (Failmezger) | Mg-glutamate | 18 mM |

Mg²⁺ is critical for ribosome stability. Given *V. natriegens* has 29% RNA by dry weight (vs. 21% for *E. coli*), its Mg²⁺ demand is proportionally higher. The wide range in cell-free Mg²⁺ optima (3.5 vs 18 mM) suggests this parameter is highly context-dependent.

### Potassium (K⁺)

| Context | K⁺ Source | Concentration |
|---------|-----------|---------------|
| v2 salts | KCl | 4.2 mM |
| VN minimal | KH₂PO₄ + K₂HPO₄ | ~14.7 mM total |
| Cell-free | K-glutamate | 80-160 mM |
| VN10 | KH₂PO₄ | 22 mM |

K⁺ is important for translation fidelity and ribosome function.

### Calcium (Ca²⁺)

| Context | Ca²⁺ Source | Concentration |
|---------|-------------|---------------|
| VN minimal | CaCl₂ | ~90 µM (0.01 g/L) |
| VN10 trace | CaCl₂·2H₂O | ~183 µM |

---

## 12. Trace Metals

Trace metals have a **"very strong influence"** on *V. natriegens* growth (Pfeifer et al. 2019).

### Standard Trace Element Concentrations

| Metal | VN Minimal | VN10 Trace (final) | Wolfe's Minerals (final) |
|-------|-----------|-------------------|-------------------------|
| Fe²⁺/Fe³⁺ | 59 µM (FeSO₄) | ~118 µM (FeSO₄) | ~3.6 µM (FeSO₄) |
| Mn²⁺ | 59 µM (MnSO₄) | ~118 µM (MnSO₄) | ~30 µM (MnSO₄) |
| Zn²⁺ | 3.5 µM (ZnSO₄) | ~7 µM (ZnSO₄) | ~3.5 µM (ZnSO₄) |
| Cu²⁺ | 1.2 µM (CuSO₄) | ~2.4 µM (CuSO₄) | - |
| Ni²⁺ | 0.08 µM (NiCl₂) | ~0.16 µM (NiCl₂) | ~0.8 µM (NiCl₂) |

### Critical Finding: EDTA Inhibits Growth
EDTA-containing trace element solutions **strongly inhibit** *V. natriegens* growth, even though EDTA is commonly used as a chelator in bacterial media. **Citrate is the preferred chelator** -- it keeps metals bioavailable while preventing precipitation (Stadler et al. 2023).

### Iron is Likely the Most Important Trace Metal
- *V. natriegens* can use iron and manganese oxides as electron acceptors anaerobically (extracellular electron transfer)
- Iron speciation matters: ferric citrate (0.1 g/L) is used in Marine 2216E medium
- Siderophore production is expected given marine origin (iron-limited marine environment)
- Wide variation in iron concentrations across formulations (3.6-118 µM) suggests this is underoptimized

---

## 13. Overflow Metabolism and Acid Sensitivity

This is the **central challenge** of *V. natriegens* cultivation and the most important factor for BO to address.

### The Problem
- Even under fully aerobic conditions with excess O₂, *V. natriegens* produces **0.8 mol acetate per mol glucose** consumed (Long et al. 2017)
- Up to 25% of carbon flux goes to acetate via the Pta-AckA pathway
- Additional byproducts under microaerobic conditions: succinate, formate, lactate, ethanol
- After glucose depletion, cells undergo an "acetate switch" -- upregulating ACS to re-assimilate acetate

### Why This Kills Cells
- *V. natriegens* lacks acid resistance mechanisms (no GAD, ADI, or CAD systems found in *E. coli*)
- pH drops to ~5.3 in unbuffered batch culture
- Cells reach **extinction within 12 hours** after growth phase
- *E. coli* survives 3 days longer under identical conditions

### Mitigation Strategies
1. **Heavy buffering**: 300-450 mM MOPS (see Section 6)
2. **Fed-batch glucose limitation**: Prevents overflow metabolism entirely
3. **Lower temperature**: 30°C reduces overflow vs. 37°C
4. **Carbon source engineering**: Glycerol produces less overflow than glucose
5. **Mixed carbon sources**: Glucose + glycerol blends could reduce peak acid production
6. **Slow-release carbon**: Enzymatic release (sucrose + invertase) could mimic fed-batch in plates

---

## 14. Unique Biology

### Two Chromosomes and Dynamic Ploidy
- Bipartite genome: Chr1 (3.2 Mb, 11 rRNA operons, ~103 tRNAs) + Chr2 (1.9 Mb, 1 rRNA operon, ~21 tRNAs)
- Origin copy numbers swing from **~50 copies in early exponential** to ~20 in mid-exponential to near-diploid in stationary phase
- This creates a **6-fold gene dosage asymmetry** near origins during fast growth
- A rationally designed chromosome fusion did NOT prevent rapid growth (Messerschmidt et al. 2024)

**Implication for BO:** The growth phase at which cells are harvested/measured matters enormously for any gene expression work. BO could optimize inoculation density and harvest time to exploit ploidy dynamics.

### Quorum Sensing
- Harveyi-type QS system (LuxR/HapR homologues)
- Controls EPS production, biofilm formation, metabolic shifts at high cell density
- QS-regulated CpsR controls exopolysaccharide production (up to 157 ± 20 mg/L EPS, causing 800-fold viscosity increase)

### Electroactivity
- Direct electron transfer to electrodes: 6.6 µA/cm²
- Mediated electron transfer: 196 µA/cm²
- Hybrid extracellular electron transfer pathway
- Can use iron and manganese oxides as terminal electron acceptors

### Catalase Activity
- Minimal/low compared to *E. coli* (Pfeifer et al. 2019)
- May explain sensitivity to oxidative stress during competence
- Overexpression of AhpCF increased viability by >15.7-fold

---

## 15. Novel Optimization Ideas

### 15.1 Parameters from Existing Literature (Underexplored)

**Glycine betaine as dual-function supplement** (0-10 mM):
- Acts as both osmoprotectant AND carbon/energy source
- Choline, betaine, DMG, and DMSP rescue growth at low Na⁺
- Largely unexplored as a deliberate growth optimization supplement
- Source: recent 2025 *Appl. Environ. Microbiol.* study

**Iron speciation optimization:**
- FeCl₃ vs. ferric citrate vs. FeSO₄ -- different bioavailability
- Citrate-complexed iron remains bioavailable; EDTA-complexed does not
- Iron has "very strong influence" on growth but optimal form/concentration is undercharacterized
- Consider siderophore supplementation (marine organism adapted to iron-limited environment)

**Sucrose instead of glucose:**
- 7% higher growth rate (1.79 vs 1.68 h⁻¹) -- a free improvement
- Underused in the field; most labs default to glucose

**N-acetylglucosamine (chitin monomer):**
- Nearly as fast as glucose (1.74 h⁻¹), ecologically natural substrate
- Could be explored as primary or supplemental carbon source

### 15.2 Novel Protocol-Level Parameters

**Seed culture growth phase at inoculation:**
- Ploidy varies 6-fold between early and late exponential phase
- Inoculating from early exponential (high ploidy, more ribosomes) vs. stationary phase could affect lag time and initial growth rate
- BO could optimize the OD at which seed culture is harvested

**Temperature shift protocol:**
- Start at 30°C (ribosome accumulation phase, less overflow metabolism)
- Shift to 37°C at specific OD (growth burst phase)
- Analogous to "carb-loading" -- accumulate biosynthetic machinery before maximizing growth
- Achievable in plate reader by moving plates between incubators

**Carbon source blending:**
- Glucose:glycerol ratios from 0:1 to 1:0
- Glycerol produces less overflow metabolism than glucose
- Mixed sources could prevent peak acid production while maintaining reasonable growth rate
- Sucrose + invertase co-addition for enzymatic slow-release (mimics fed-batch in 96-well)

**Fill volume in 96-well plates:**
- 50-250 µL range directly controls kₗa (oxygen transfer)
- Lower volume = better aeration but more evaporation
- Interaction with shaking speed and seal type

**Shaking intermittency:**
- Continuous vs. periodic (5 min on / 5 min off)
- Brief pauses may allow surface oxygen access via pellicle
- Periodic O₂ oscillations produce synchronized growth dynamics (RSC 2025)

**Conditioned medium fraction:**
- Add 0-30% spent medium from stationary-phase *V. natriegens*
- Contains autoinducers, quorum sensing molecules, secreted growth factors
- Could prime fresh cultures for faster growth initiation

### 15.3 Chemical Additives (Novel)

**Sub-inhibitory surfactants:**
- Tween-20, Tween-80, or Triton X-100 at 0.001-0.1%
- Increase membrane permeability → faster nutrient uptake
- *V. natriegens* MK3 naturally produces biosurfactants
- Overexpression of D,D-carboxypeptidase PBP5/6 caused 2.8x increase in outer membrane permeability

**Redox mediators:**
- Riboflavin (0-50 µM), methylene blue, neutral red
- *V. natriegens* is electroactive -- redox mediators could alter intracellular redox balance
- Almost entirely unexplored for growth optimization (vs. electricity generation)

**QS modulators:**
- Exogenous AI-2 autoinducer (or synthetic DPD) to manipulate density-dependent behavior
- QS inhibitors (furanone derivatives) to delay stationary phase entry and extend exponential growth
- Could decouple growth phase from actual cell density

**Amino acid cocktails:**
- Aspartate + glutamate (pH buffering + energy source)
- Specific amino acids that bypass expensive biosynthetic pathways
- Target the 47% protein content bottleneck

### 15.4 Advanced Biological Approaches

**Adaptive Laboratory Evolution (ALE):**
- Successfully applied: 89% growth rate increase on acetate (2025)
- ALE on raffinose generated efficient utilization (2024)
- Convergent oxyR mutations under oxidative stress (2020)
- Short-term ALE pre-conditioning (10-20 generations) in target medium could shift baseline before BO optimization
- Could BO-optimize ALE conditions themselves (transfer frequency, selection pressure)

**Conditioned medium / cross-feeding:**
- *V. natriegens* produces indole-3-acetic acid (IAA) at ~10 nM
- Tested in co-culture with *Euglena gracilis* (>20% biomass increase for algae)
- Self-conditioning: add back filtered spent medium at various ratios

---

## 16. Bayesian Optimization Methodology

### 16.1 Key Papers for BO in Microbial Growth

| Paper | Organism | Parameters | Improvement | Key Method |
|-------|----------|------------|-------------|------------|
| Lapierre 2025 | *S. pasteurii* | 21 media components | **+28% biomass** over DoE | Batch BO, RoboLector |
| Nature Comms 2025 | PBMCs, yeast | 4-9 factors | **10-30x fewer** experiments vs DoE | GP + categorical overlap kernel |
| Cosenza 2022 | C2C12 cells | 14 components | **+181% cells**, 38% fewer experiments | Multi-information source BO |
| CETCH 2022 | In vitro pathway | 27 enzymes | **10x productivity** in 1000 assays | Active learning, 8 rounds |
| *P. putida* 2025 | *P. putida* | 48 media components | +60-70% titer, +350% yield | ML + explainable AI |

### 16.2 Practical Configuration

**GP Kernel:** Matern 5/2 (slightly less smooth than RBF, more realistic for biology)

**Acquisition Function:**
- **Thompson Sampling** for initial rounds: hyperparameter-free, naturally balances exploration/exploitation, robust with sparse data
- Switch to **logEI** or **UCB** with more data
- For batch suggestions: Thompson Sampling naturally provides diverse batches

**Initial Design:**
- Allocate ~50% of total experiment budget to initial space-filling design
- Latin hypercube sampling or Sobol sequences
- Length scale priors: 1/4 to 1/2 of each parameter's total range

**Handling Noise in 96-Well Plates:**
- GP noise model handles biological + pipetting variability naturally
- **Against routine replication**: "such replication may represent a missed opportunity to extract maximal information about the response surface" (Siska et al. 2025)
- Randomize well positions to mitigate edge effects (temperature gradients, evaporation)
- Model positional bias explicitly if needed

**Objective Function Options:**
1. **Maximum OD600** -- simplest, directly from plate reader
2. **Growth rate (µ_max)** -- more informative, requires curve fitting
3. **Lag time** -- important for fast-turnaround applications
4. **Multi-objective Pareto**: growth rate vs. final OD vs. lag time (use qEHVI in BoTorch)
5. **Composite score**: weighted µ_max + final OD + R² of growth curve fit

**Recommended objective for your project:** Multi-objective with growth rate (µ_max) and final OD600 as primary objectives. These can trade off (e.g., high glucose → fast growth but acid crash → low final OD).

### 16.3 Growth Curve Analysis

Use **GP-based growth curve fitting** (AMiGA software) rather than simple max-OD:
- Handles non-standard curve shapes
- Explicitly accounts for experimental noise
- Extracts µ_max, lag time, carrying capacity from kinetic data
- Superior to traditional logistic curve fitting for fast-growing organisms

### 16.4 Software Tools

| Tool | Best For | Notes |
|------|----------|-------|
| **BayBE** (Merck) | Practitioner-friendly, built-in chemical encodings | Transfer learning, mixed continuous/categorical, multi-objective; designed for self-driving labs |
| **BoTorch/GPyTorch** (Meta) | Full flexibility, custom acquisition functions | Most published bioprocess papers use this |
| **scikit-optimize** | Quick prototyping | Used in several bio papers |
| **AMiGA** | Growth curve analysis from plate readers | GP-based, directly applicable to OD kinetic data |
| **SAASBO** (BoTorch) | High-dimensional (>10 params) | Discovers which dimensions actually matter via sparse subspaces |

**Recommendation:** BayBE for the main BO loop (built-in support for mixed parameters, batch suggestions, transfer learning). AMiGA for extracting growth metrics from plate reader data as objective function inputs.

### 16.5 Experiment Budget

Based on published precedent:
- Most successful papers converge in **4-8 rounds**
- With 96 wells: run 32-48 unique conditions per plate (2-3 replicates) or up to 96 unique (no replicates)
- The literature suggests **replicates are often not worth the opportunity cost** when GP provides uncertainty estimates
- Budget for **5-10 plates total** (480-960 unique conditions)
- *V. natriegens* doubling time of ~10 min means a full growth curve in **3-6 hours** -- enables **multiple BO rounds per day**

---

## 17. White Paper Strategy: Three Optimization Targets

This project is a white paper demonstrating a closed-loop AI scientist for cell culture optimization. The goal is not merely to find better growth conditions -- it is to show that an autonomous system can **discover things about *V. natriegens* that human researchers missed, faster and with fewer experiments**.

Parameter selection should prioritize: (1) areas where the literature is wrong or incomplete, so the AI can "discover" something; (2) hidden interactions humans haven't mapped, so closed-loop BO outperforms one-shot DOE; and (3) clear comparisons to traditional methods showing a BO efficiency win.

### Target 1: Growth Rate Optimization

**Objective:** Maximize µ_max (maximum specific growth rate during exponential phase).

This is the baseline result. Every media optimization paper reports growth rate, and it provides credibility and direct comparison to existing literature benchmarks. The current records are:
- Rich medium (BHIN): µ = 4.43 h⁻¹ (9.4 min doubling)
- Defined medium (Wilms-MOPS): µ = 1.97 h⁻¹ (21 min doubling)

The closed-loop system should aim to **match or exceed the defined medium record** by exploring a broader parameter space than Gericke et al. 2024, who used traditional DOE.

### Target 2: Multi-Objective Pareto Optimization (Growth Rate vs. Biomass Yield)

**Objectives:** Maximize µ_max AND maximize final OD600 simultaneously via Pareto optimization.

This is the novel result. Nobody has systematically mapped the growth rate vs. final biomass trade-off for *V. natriegens* using Bayesian optimization. The literature clearly shows these objectives conflict:

| Condition | Favors Growth Rate | Favors Final Biomass |
|-----------|-------------------|---------------------|
| Temperature | 37°C (µ = 4.43 h⁻¹) | 30°C (62% more CDW in fed-batch) |
| Glucose | High (fast uptake) | Low-moderate (less acid crash) |
| Buffer | Moderate (less osmotic load) | High (prevents acid death) |

A Pareto front mapping these trade-offs would reveal:
- **"Sprint" conditions**: maximum instantaneous growth rate
- **"Marathon" conditions**: maximum final cell density
- **Balanced conditions**: best compromise for practical applications

This has direct practical value -- different biotech applications need different strategies (e.g., rapid cloning vs. protein production vs. cell-free extract preparation). The Pareto front provides actionable guidance that a single-objective study cannot.

**BO methodology**: Use multi-objective BO with the qEHVI (q-Expected Hypervolume Improvement) acquisition function in BoTorch, or BayBE's built-in multi-target Pareto support. Each 96-well plate simultaneously maps both objectives since growth curves yield both µ_max and final OD.

### Target 3: Autonomous Discovery of the NaCl-Osmolality Confound

**Objective:** Demonstrate that the AI system can independently identify confounded variables and resolve them.

This is the headline result for the white paper. The entire *V. natriegens* field used 15-25 g/L NaCl for decades based on studies that confounded sodium ion requirements with osmolality effects. Gericke et al. (2024) was the first to decouple these, showing the true NaCl optimum is 7.5-15 g/L when osmolality is independently controlled via MOPS buffer.

**The experimental design:**
- Include both NaCl (5-25 g/L) and MOPS (100-500 mM) as independent BO dimensions
- Do NOT inform the system of the expected confound
- Let the GP surrogate model discover the NaCl × MOPS interaction organically
- After convergence, analyze the GP's learned length scales and interaction structure

**Expected outcome:** The BO should converge on lower NaCl + higher MOPS, contradicting the textbook 2.5% NaCl recommendation. This independently validates Gericke et al. 2024 while demonstrating that the AI system can navigate misleading prior knowledge.

**Why this matters for the white paper:** Most BO-for-biology papers apply optimization to well-characterized systems. Showing that BO can **resolve a confound** that misled human researchers for decades is a qualitatively different (and stronger) claim about AI-driven science.

### White Paper Narrative Structure

**Result 1: "The system autonomously identified that the established NaCl optimum is confounded with osmolality"**
- Show the BO exploring NaCl × MOPS space iteratively
- Show convergence on lower NaCl + higher MOPS vs. the textbook recommendation
- Compare to Gericke et al. 2024 as independent validation

**Result 2: "Multi-objective optimization revealed a Pareto front of growth strategies"**
- Present the trade-off surface between growth rate and final biomass
- Identify "sprint" vs. "marathon" vs. balanced condition clusters
- Show temperature and glucose as key trade-off drivers
- Discuss practical implications for different biotech applications

**Result 3: "The system discovered non-obvious parameter interactions in fewer experiments than traditional DOE"**
- Glycine betaine × NaCl interaction (betaine partially substituting for salt?)
- Iron × growth rate (iron rate-limiting at high growth rates?)
- Glucose × MOPS × temperature three-way interaction (overflow metabolism cascade)
- Efficiency comparison: X improvement in Y rounds vs. literature benchmarks
- Compare to Lapierre 2025 (28% improvement) and Nature Comms 2025 (10-30x fewer experiments)

### Differentiation From Existing BO-for-Media Papers

Most published BO media optimization papers (Lapierre 2025, Cosenza 2022, Nature Comms 2025) work with organisms where the biology is well-characterized. *V. natriegens* presents unique challenges that make this work distinct:

1. **Fastest-growing organism** -- time resolution of measurements matters; growth curves complete in 3-6 hours enabling multiple BO rounds per day
2. **Acid sensitivity cliff** -- the fitness landscape has sharp drop-offs (not smooth gradients), challenging GP surrogate models and testing BO robustness
3. **Actively misleading prior knowledge** -- the NaCl/osmolality confound means naive literature-based priors would hurt, not help. The system must overcome this.
4. **Hardware-constrained optimization** -- 96-well plate oxygen limitation creates a real physical constraint the BO must navigate, unlike bioreactor-based studies
5. **Multi-objective biological trade-offs** -- growth rate vs. biomass yield is a fundamental microbial trade-off that has never been Pareto-mapped for *V. natriegens*

### Full 9-Parameter Search Space

For the white paper, the parameter space should be broad enough that traditional DOE is impractical (that is the point of BO). Nine parameters at 3 levels would require 19,683 full factorial experiments. BO should find the optimum in **5-8 rounds × 96 wells = 480-768 experiments** while capturing full interaction structure.

| Parameter | Range | Type | White Paper Role |
|-----------|-------|------|-----------------|
| NaCl | 5-25 g/L | Continuous | Confound discovery (Target 3) |
| MOPS buffer | 100-500 mM | Continuous | Confound discovery + acid survival |
| Temperature | 30-37°C | Continuous | Growth vs. yield trade-off (Target 2) |
| Glucose | 5-30 g/L | Continuous | Overflow metabolism interaction |
| MgSO₄ | 0.5-25 mM | Continuous | Ribosome stability, no literature consensus |
| Casamino acids | 0-5 g/L | Continuous | Biosynthetic burden, interaction with growth rate |
| Fe (ferric citrate) | 0-200 µM | Continuous | "Very strong influence", wildly inconsistent in literature |
| Fill volume | 75-250 µL | Continuous | O₂ transfer (hardware constraint navigation) |
| Glycine betaine | 0-10 mM | Continuous | Novel 2025 finding, unexplored in optimization |

**Key interactions to capture:** NaCl × MOPS (the confound), glucose × MOPS × temperature (overflow metabolism cascade), NaCl × glycine betaine (osmolyte substitution), Fe × µ_max (iron limitation at high growth rates), fill volume × glucose (O₂ demand scales with carbon availability).

---

## 18. Recommended BO Parameter Space (Detailed)

### Tier 1 -- Highest Impact (include in every experiment)

| Parameter | Range | Rationale |
|-----------|-------|-----------|
| **NaCl concentration** | 5-25 g/L | Most critical; true optimum (7.5-15 g/L) is lower than classical literature |
| **MOPS buffer concentration** | 100-500 mM | Prevents acid death; interacts with osmolality |
| **Initial pH** | 7.0-8.5 | Interacts with buffer and overflow metabolism |
| **Temperature** | 30-37°C | Growth rate vs. biomass yield trade-off |
| **Carbon source concentration** | 5-30 g/L glucose (or sucrose) | Drives overflow metabolism at high concentrations |

### Tier 2 -- High Impact (include if dimensionality allows)

| Parameter | Range | Rationale |
|-----------|-------|-----------|
| **MgCl₂ / MgSO₄** | 0.5-25 mM | Ribosome stability; v2 salts use 23 mM |
| **Casamino acids** | 0-5 g/L | Relieve amino acid biosynthetic burden |
| **Fill volume** (96-well) | 50-250 µL | Controls oxygen transfer directly |
| **Glycine betaine** | 0-10 mM | Novel dual osmoprotectant + carbon source |
| **FeCl₃ / ferric citrate** | 0-200 µM | "Very strong influence"; underoptimized |

### Tier 3 -- Exploratory (for later rounds or high-dimensional BO)

| Parameter | Range | Rationale |
|-----------|-------|-----------|
| KCl | 0-10 mM | Required ion; interact with Na⁺ |
| Yeast extract | 0-2 g/L | Vitamins/cofactors; eliminates lag |
| Aspartate / glutamate | 0-5 g/L | pH buffering + growth enhancement |
| Glucose:glycerol ratio | 0:1 to 1:0 | Overflow metabolism management |
| Seed culture OD | 0.1-2.0 | Exploits ploidy dynamics |
| Tween-80 | 0-0.05% | Membrane permeability; novel |
| Shaking speed/pattern | Variable | Oxygen dynamics |
| Conditioned medium | 0-30% | QS priming; novel |
| Carbon source identity | Glucose/sucrose/GlcNAc | Categorical; sucrose may be best |

### Key Interactions to Capture
- **NaCl × MOPS** (sodium vs. osmolality -- the confound that fooled the field)
- **NaCl × temperature** (salt tolerance is temperature-dependent)
- **Carbon source × MOPS** (glucose → acid → pH crash if underbuffered)
- **NaCl × MgCl₂** (divalent cation interactions)
- **Fill volume × carbon concentration** (O₂ demand scales with growth rate)

### Suggested Starting Point: 7-Parameter Design

For the first BO round (Weekend 1-2), start with these 7 parameters as a balanced exploration:

1. NaCl (5-25 g/L)
2. MOPS (100-500 mM)
3. Initial pH (7.0-8.5)
4. Glucose (5-30 g/L)
5. MgSO₄ (0.5-25 mM)
6. Fill volume (75-250 µL)
7. Casamino acids (0-5 g/L)

Use Latin hypercube sampling for initial plate, then BO-guided suggestions for subsequent plates. Temperature fixed at 37°C initially (optimize later if needed).

---

## 19. References

### Core *V. natriegens* Papers

1. Eagon RG (1962). Pseudomonas natriegens, a marine bacterium with a generation time of less than 10 minutes. *J Bacteriol* 83:736-737.

2. Weinstock MT, Hesek ED, Wilson CM, Gibson DG (2016). Vibrio natriegens as a fast-growing host for molecular biology. *Nature Methods* 13:849-851.

3. Lee HH, Ostrov N, Wong BG, et al. (2016). Vibrio natriegens, a new genomic powerhouse. *bioRxiv* 058487.

4. Hoffart E, Grenz S, Lange J, et al. (2017). High Substrate Uptake Rates Empower Vibrio natriegens as Production Host for Industrial Biotechnology. *Appl Environ Microbiol* 83(22):e01614-17.

5. Long CP, Gonzalez JE, Cipolla RM, Antoniewicz MR (2017). Metabolism of the fast-growing bacterium Vibrio natriegens elucidated by ¹³C metabolic flux analysis. *Metab Eng* 44:191-197.

6. Pfeifer E, Gätgens C, Courtney T, et al. (2019). An analysis and optimization of growth condition requirements of the fast-growing bacterium Vibrio natriegens. *bioRxiv* 775437.

7. Stukenberg D, Hensel T, Giessen TW (2022). NT-CRISPR, combining natural transformation and CRISPR-Cas9 counterselection for markerless and scarless genome editing in Vibrio natriegens. *Commun Biol* 5:265.

### Growth Optimization & Physiology

8. Gericke A, Hoefgen S, Tiller J, et al. (2024). Unraveling the impact of pH, sodium concentration, and medium osmolality on Vibrio natriegens in batch processes. *BMC Biotechnol* 24:71.

9. Stadler C, Gelleszun R, Hoefgen S, et al. (2023). High-cell-density cultivation of Vibrio natriegens in a low-chloride chemically defined medium. *Appl Microbiol Biotechnol* 107:7385-7397.

10. Tatzelt C, Gelleszun R, Noack S, et al. (2021). High-cell-density fed-batch cultivations of Vibrio natriegens. *Biotechnol Lett* 43:1723-1733.

11. Tschirhart T, et al. (2025). Vibrio natriegens is sensitive to its own acidic fermentation products. *Appl Environ Microbiol* AEM.01745-25.

12. Dong C, et al. (2022). Non-sterilized seawater fermentation for Vibrio natriegens. *Front Bioeng Biotechnol* 10:955097.

### Metabolism & Genome-Scale Models

13. Carlson LC, et al. (2023). Genome-scale metabolic model of Vibrio natriegens (iLC858). *Mol Syst Biol* 19:e10523.

14. Thoma F, Giessen TW (2022). Anaerobic succinate production in Vibrio natriegens. *Microb Cell Fact* 21:100.

15. Ellis GA, et al. (2021). Metabolic engineering of Vibrio natriegens for biotechnological applications. *Essays Biochem* 65:761-769.

### Genetic Tools & Engineering

16. Dalia TN, et al. (2023). Multiplex genome engineering and natural transformation (MuGENT) in Vibrio natriegens. *Cell Rep* 42:112619.

17. Messerschmidt K, et al. (2024). Chromosome fusion does not prevent rapid growth in Vibrio natriegens. *Commun Biol* 7:702.

18. Expanding the V. natriegens genetic toolbox: the Vnat Collection (2025). *Nucleic Acids Res* 53(13):gkaf580.

### Cell-Free Systems

19. Des Soye BJ, et al. (2018). Establishing a high-yielding cell-free protein synthesis platform derived from Vibrio natriegens. *ACS Synth Biol* 7:2245-2255.

20. Failmezger J, et al. (2018). Cell-free protein synthesis from fast-growing Vibrio natriegens. *Front Microbiol* 9:1146.

### Bayesian Optimization for Bioprocess

21. Lapierre R, et al. (2025). Multi-cycle high-throughput growth media optimization using batch Bayesian optimization. *J Chem Technol Biotechnol* 100:1571-1583.

22. Siska et al. (2025). A Guide to Bayesian Optimization in Bioprocess Engineering. *Biotechnol Bioeng* (arxiv:2508.10642).

23. Gisperg V, et al. (2025). Bayesian Optimization in Bioprocess Engineering -- Where Do We Stand Today? *Biotechnol Bioeng*.

24. Cosenza Z, et al. (2022). Multi-information source Bayesian optimization of culture media. *Biotechnol Bioeng* 119:3261-3275.

25. Nature Communications (2025). Accelerating cell culture media development using Bayesian optimization-based iterative experimental design.

26. Rosa SS, et al. (2022). Bayesian optimization of mRNA concentration. *Biotechnol Bioeng*.

### Osmoprotectants & Stress

27. V. natriegens osmoprotectants serve dual roles (2025). *Appl Environ Microbiol* AEM.00619-25.

28. Phaneuf PV, et al. (2020). Convergent oxyR mutations during adaptive laboratory evolution. *Mol Biol Evol* 37:660-677.

### Electroactivity & Novel Biology

29. V. natriegens anodic respiration (2023). *ChemSusChem* 16:e202300181.

30. V. natriegens microbial fuel cell (2023). *PMC* 9961702.

### Protocols

31. Culturing the Rapidly Growing Bacterium Vibrio natriegens. *JoVE* 24216.

32. Barrick Lab. Working with Vibrio natriegens (Vmax). Protocol wiki.

### Software

33. BayBE -- Bayesian Back End for Design of Experiments. Merck KGaA. GitHub.

34. BoTorch -- Bayesian Optimization in PyTorch. Meta Research.

35. AMiGA -- Analysis of Microbial Growth Assays. *mSystems* 2021.

---

*This literature review was compiled for the Closed-Loop AI Scientist project to inform the Bayesian Optimization search space for Vibrio natriegens growth optimization using the Monomer Bio robotic workcell.*
