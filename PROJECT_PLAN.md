# Project Plan

## Team

| Person | Owns |
|--------|------|
| **Srusti** | LLM literature review + experiment designer + Bayesian optimization + growth metrics |
| **Keltoum** | MCP workflows, data parser, webapp, integrations |

---

## Interfaces

So we can work independently, here's what each component outputs.

### LLM Literature Review → Experiment Designer: Search space

Srusti gathers a list of documents and references about the cell line of interest as well as papers of interest for optimizing growth conditions, feeds them to an LLM, and extracts what parameters BO should explore.

```json
{
  "parameters": [
    {"name": "cell_volume_uL", "range": [20, 80], "unit": "uL"},
    {"name": "mix_height_mm", "range": [1, 4], "unit": "mm"},
    {"name": "mix_reps", "range": [1, 5], "unit": "count"}
  ]
}
```

### Srusti → Keltoum: Routine parameters

CSV with one row per well, columns are the routine parameters.

```csv
source_well,destination_well,cell_volume_uL,media_volume_uL,mix_height_mm,mix_reps,mix_volume_uL
A2,A3,40,160,1,3,100
A2,B3,40,160,2,3,100
A2,C3,60,140,4,5,50
...
```

### Keltoum → Srusti: Parsed results

Links each well's parameters to its growth outcome.

```json
{
  "results": [
    {
      "well": "A3",
      "params": {"cell_volume_uL": 40, "mix_height_mm": 1, "mix_reps": 3},
      "growth_rate": 0.042,
      "doubling_time": 16.5
    }
  ]
}
```

---

## Schedule

### Weekend 0: Planning (now)

| Who | What |
|-----|------|
| Keltoum | Define system architecture, create project plan, set up project structure |

**Sync**: Agree on plans with Srusti.

### Weekend 1: Setup

| Who | What |
|-----|------|
| Srusti | Curate papers (cell line info + growth condition optimization), set up BO framework, generate mock CSV with 96 rows |
| Keltoum | Figure out which workcell routines we need, test them on workcell |

**Sync**: Agree on CSV/JSON formats above.

### Weekend 2: Build

| Who | What |
|-----|------|
| Srusti | Working LLM literature review pipeline, working BO that outputs routine parameters CSV |
| Keltoum | Build data parser (OD data → growth metrics JSON) |

**Sync**: Test each component with sample data.

### Weekend 3: Connect

| Who | What |
|-----|------|
| Srusti | BO consumes parsed results, computes growth metrics, test literature review pipeline |
| Keltoum | Build webapp dashboard (view iterations, OD curves) |

**Sync**: Run full loop with mock data.

### Weekend 4: Polish

| Who | What |
|-----|------|
| Srusti | Tune BO, add progress visualization, final testing + docs |
| Keltoum | Integration testing, dry run full system |

**Sync**: Ready for real experiment.

### Weekend 5: Run

| Who | What |
|-----|------|
| Srusti + Keltoum | Run first real experiment on workcell, gather data, evaluate results. Keltoum physically present with workcell |

**Sync**: Review first iteration results, decide next steps.

---

## Files

```
src/
├── literature/       # Srusti
├── designer/         # Srusti (planned / BO output)
├── design/           # Keltoum (reagent LHS, transfer_array, validation)
├── mcp/              # Keltoum
├── parser/           # Keltoum
└── webapp/           # Keltoum
```

---

## Comms

- **Routine**: Whatsapp
- **Monomer**: Slack
- **Weekly**: 30 min sync at end of each weekend to discuss outcomes of work, next steps. 
