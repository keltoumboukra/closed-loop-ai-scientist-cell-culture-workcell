# V. natriegens Growth Optimization: Parameter Research Summary

## Organism Background

Vibrio natriegens is the fastest-growing non-pathogenic bacterium known (~10 min doubling in rich media vs ~25 min for E. coli). It is a marine halophile with 12 rRNA operons, two chromosomes enabling parallel replication, and dynamic polyploidy (~50 genome copies during exponential phase).

**Critical sensitivity:** V. natriegens lacks acid resistance mechanisms. It metabolizes glucose so fast that acetate overflow crashes pH from 7.2 to 5.3 in ~4 hours if unbuffered. Below pH 5.5, growth stops and cells die within 12 hours.

### Key Growth Rates by Condition

| Condition | Growth rate (1/h) | Doubling time |
|-----------|-------------------|---------------|
| BHIN (37 g/L BHI + 15 g/L NaCl), 37°C | 4.43 | ~9.4 min |
| LBv2, 37°C | ~3.0–3.5 | ~12–14 min |
| Glucose minimal + salts, 37°C | 1.70 | ~24 min |
| Sucrose minimal + salts, 37°C | 1.79 | ~23 min |
| Optimized mineral medium (Gericke 2024) | 1.97 | ~21 min |

### Carbon Source Growth Rates (Hoffart et al. 2017, mineral medium, 37°C)

| Carbon Source | μ (1/h) |
|---------------|---------|
| Sucrose | 1.79 |
| N-acetylglucosamine | 1.74 |
| Glucose | 1.68 |
| Fructose | 1.51 |
| Succinate | 1.00 |
| Acetate | 0.45 |
| Xylose | No growth |

---

## Top 5 Parameters for Bayesian Optimization

These are per-well variables that the Monomer liquid handler can vary across 96 wells.

### 1. NaCl concentration — 5 to 15 g/L

V. natriegens is an obligate halophile — zero growth below ~5 g/L NaCl. The critical finding (Gericke et al. 2024) is that the optimum is 7.5–15 g/L, NOT the classical 25 g/L. The old recommendation was confounded by osmolality effects.

- 0 g/L → OD<2 after 10h
- 12–18 g/L → OD 20–24 after 10h (Stadler et al. 2021)

### 2. MOPS buffer concentration — 100 to 400 mM

In 96-well plates without active pH control, buffer capacity is the single most important variable for preventing growth arrest.

- 200 mM MOPS, pH 7.5: μ = 0.81 /h
- 280 mM MOPS, pH 8.0: μ = 1.97 /h (2.4x faster)
- 500 mM MOPS: μ = 0.53 /h (osmolality inhibition)

Sweet spot depends on glucose load — 180 mM for 10 g/L glucose, 300 mM for 20 g/L.

### 3. Glucose concentration — 5 to 20 g/L

Paradoxical effect — more glucose does NOT mean faster growth due to acid overflow:

- 10 g/L glucose + 280 mM MOPS → μ = 1.97 /h
- 20 g/L glucose + 300 mM MOPS → μ = 0.97 /h

Glucose uptake rate is 3.90 g/g/h — 2x faster than E. coli (Hoffart et al. 2017).

### 4. MgSO₄ / MgCl₂ — 1 to 25 mM

Essential for ribosome assembly, enzyme function, and high translation rate. LBv2 uses 23.14 mM MgCl₂; minimal media use 1–5 mM MgSO₄.

Caveat: Mg²⁺ precipitates as ammonium magnesium phosphate above pH 6.5. Citrate chelator prevents this (Stadler et al. 2023).

### 5. Casamino acids — 0 to 5 g/L

Triple function: (a) additional nitrogen/carbon source, (b) natural pH buffer, (c) reduces biosynthetic burden. Even 0.05 g/L yeast extract eliminates lag phase entirely (Hoffart et al. 2017).

---

## Fixed Conditions (Plate-Wide)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Temperature | 37°C | Optimal for growth rate across all studies |
| Initial pH | 8.0 | 2.4x growth rate vs pH 7.5 (Gericke 2024) |
| Shaking | Max RPM | V. natriegens has extreme O₂ demand |
| Trace elements | 1x Hoffart recipe | Strong effect but binary (present/absent) |
| CaCl₂ | 1 mM | Standard supplement |
| NH₄Cl | Standard | Nitrogen source |

---

## Excluded Parameters and Rationale

| Candidate | Verdict | Reasoning |
|-----------|---------|-----------|
| Temperature | Fix at 37°C | Plate-wide, can't vary per-well |
| Initial pH | Fix at 8.0 | Plate-wide |
| Shaking speed | Fix at max | Plate-wide |
| KCl | Exclude | Minor effect (4.2 mM in LBv2), not independently significant |
| Yeast extract | Exclude | Subsumed by casamino acids; similar function |
| Osmolality | Exclude | Emergent property of NaCl + MOPS + glucose; correlated parameters confuse GP |
| Trace elements | Fix at 1x | Hard to vary meaningfully per-well |
| Aspartate/glutamate | Exclude | Overlaps with casamino acids |

---

## Key Parameter Interactions

| Interaction | Expected Effect |
|-------------|----------------|
| Glucose × MOPS | Dominant interaction. More glucose needs more buffer |
| NaCl × MgCl₂ | Both contribute to ionic strength/osmolality |
| NaCl × MOPS | Both contribute to osmolality. Combined >2.0 Osmol/kg inhibits growth |
| Casamino acids × MOPS | CAA provides additional buffering, may reduce MOPS requirement |

---

## BO Search Space

| Parameter | Low | High | Unit | Stock prep |
|-----------|-----|------|------|------------|
| NaCl | 5 | 15 | g/L | Concentrated brine |
| MOPS (pH 8.0) | 100 | 400 | mM | 1M MOPS stock, pH'd to 8.0 with NaOH |
| Glucose | 5 | 20 | g/L | 200 g/L stock, filter-sterilized |
| MgSO₄ | 1 | 25 | mM | 1M stock |
| Casamino acids | 0 | 5 | g/L | 50 g/L stock, filter-sterilized |

---

## Plate Layout Recommendations

- Randomize conditions across wells
- Sacrifice edge wells (rows A/H, cols 1/12) to water/PBS for evaporation mitigation → ~60 usable wells
- Initial round: 60-well Latin Hypercube design for 5 parameters
- BO rounds: 20–30 new conditions + 5–10 anchor conditions per plate
- Total: 3–5 plates (180–300 experiments)
- No triplicates needed — let the GP model noise (Siska et al. 2025)

---

## Key References

1. Weinstock et al. (2016) — "V. natriegens, a new genomic powerhouse" (bioRxiv)
2. Lee et al. (2016) — "V. natriegens as a fast-growing host" (Nature Methods)
3. Hoffart et al. (2017) — "High Substrate Uptake Rates" (Appl Environ Microbiol)
4. Pfeifer et al. (2019) — "Analysis and optimization of growth conditions" (bioRxiv 775437)
5. Stadler et al. (2021) — "High-cell-density fed-batch cultivations" (Biotechnol Lett)
6. Stadler et al. (2023) — "Low-chloride chemically defined medium" (Appl Microbiol Biotechnol)
7. Gericke/Forsten et al. (2024) — "Impact of pH, Na, osmolality" (BMC Biotechnology)
8. Lapierre et al. (2025) — "Multi-cycle batch BO for media" (J Chem Tech Biotech)
9. Siska et al. (2025) — "A Guide to BO in Bioprocess Engineering" (arXiv)
10. Gisperg et al. (2025) — "BO in Bioprocess Engineering: Where Do We Stand?" (PMC)
11. V. natriegens acid sensitivity (AEM 2025)
