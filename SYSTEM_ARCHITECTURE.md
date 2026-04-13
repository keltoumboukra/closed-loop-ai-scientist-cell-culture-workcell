# Closed-Loop AI Scientist for Cell Culture Optimization

## Objective

**Optimize growth conditions for a cell line** by combining Monomer's robotic workcell for automated experimentation with an AI scientist backend for intelligent experimental design.

## Document status

| Section | Status |
|---------|--------|
| System Architecture | ✅ Defined |
| Experiment Designer | 🔶 Partially Defined |
| LLM Literature Review | 🔶 Partially Defined |
| Monomer MCP Interface | 🔶 Partially Defined |
| Data Pipeline | 🔶 Partially Defined |
| Webapp | 🔶 Partially Defined |

**Legend**: ✅ Defined | 🔶 Partially Defined | ❓ To Be Determined

---

## 1. System Architecture

### Core Loop

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│   │  Experiment  │───▶│   Monomer    │───▶│   Monomer    │───▶│    Data      │ │
│   │   Designer   │    │     MCP      │    │   Workcell   │    │   Parser     │ │
│   └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘ │
│          ▲                                                          │          │
│          │                                                          │          │
│          └──────────────────────────────────────────────────────────┘          │
│                              Feedback Loop                                      │
│                                        │                                        │
│                                        ▼                                        │
│                                 ┌──────────────┐                               │
│                                 │    Webapp    │                               │
│                                 │  (Human View)│                               │
│                                 └──────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Full System Diagram

```mermaid
flowchart TB
    subgraph SETUP["⚙️ ONE-TIME SETUP"]
        ROUTINES["Available Routines<br/><i>Define via Monomer MCP</i><br/><br/>🔶 <b>Needs: Routine selection</b>"]
    end

    subgraph INPUTS["📥 ITERATION INPUTS"]
        direction TB
        LIT_REVIEW["📄 LLM Literature Review<br/><i>Papers on cell line +<br/>growth condition optimization</i><br/><br/>🔶 <b>Partially Defined</b>"]
        PREV_DATA["📊 Previous Iteration Data<br/><i>OD readings + design mapping</i>"]
        HUMAN_REAGENTS["👤 Human Action<br/><i>Physical reagent placement</i>"]
    end

    subgraph DESIGNER["🧠 EXPERIMENT DESIGNER"]
        direction TB
        BAYESIAN["Bayesian Optimization"]
        CONSTRAINTS["Apply Physical Constraints"]
        DESIGN_OUTPUT["Generate 96 Designs<br/><i>1 per well</i>"]
        
        BAYESIAN --> CONSTRAINTS --> DESIGN_OUTPUT
    end

    subgraph OUTPUT_FILES["📄 EXPERIMENT FILES"]
        direction TB
        ROUTINE_PARAMS["Routine Parameters"]
        ROUTINES_TO_RUN["Routines to Run"]
        WELL_MAP["Well-to-Design Mapping"]
    end

    subgraph MCP["🔌 MONOMER MCP"]
        MCP_TRANSLATE["Translate to<br/>Workcell Commands"]
    end

    subgraph WORKCELL["🤖 MONOMER WORKCELL"]
        direction TB
        STEP1["<b>Step 1: Setup</b><br/>Configure each well<br/>per design parameters"]
        STEP2["<b>Step 2: Monitor Loop</b>"]
        
        subgraph MONITOR_LOOP["Repeat for N hours"]
            INCUBATE["Incubate"]
            READ_OD["Read OD"]
            INCUBATE --> READ_OD --> INCUBATE
        end
        
        STEP1 --> STEP2
        STEP2 --> MONITOR_LOOP
    end

    subgraph DATA_OUT["📈 RAW DATA"]
        RAW_OD["OD Readings<br/><i>96 wells × time series</i>"]
    end

    subgraph PARSER["🔄 DATA PARSER"]
        direction TB
        LINK["Link: Well → Design → OD"]
        METRICS["Calculate Growth Metrics"]
        STRUCTURE["Structure for Storage"]
        
        LINK --> METRICS --> STRUCTURE
    end

    subgraph WEBAPP["🌐 WEBAPP"]
        direction TB
        WEBAPP_VIEW["Human Dashboard<br/><i>• View iteration data</i><br/><i>• Monitor workcell status</i><br/><i>• Browse design results</i>"]
    end

    %% Setup flow (one-time)
    ROUTINES -->|"Informs constraints"| DESIGNER

    %% Iteration flow
    LIT_REVIEW -->|"Early iterations"| DESIGNER
    PREV_DATA -->|"Later iterations"| DESIGNER
    HUMAN_REAGENTS -->|"Places reagents<br/>specified by literature review"| DESIGNER
    
    DESIGNER --> OUTPUT_FILES
    OUTPUT_FILES --> MCP
    MCP --> WORKCELL
    WORKCELL --> DATA_OUT
    DATA_OUT --> PARSER
    PARSER --> PREV_DATA
    PARSER --> WEBAPP

    %% Transition decision
    HUMAN_DECISION{{"👤 Human Decision:<br/>Fix reagents?"}}
    WEBAPP -.->|"Human reviews data"| HUMAN_DECISION
    HUMAN_DECISION -->|"Yes"| FIXED_MODE["Fixed Reagent Mode"]
    HUMAN_DECISION -->|"No"| EXPLORATION["Continue Exploration"]

    style LIT_REVIEW fill:#ffe6cc,stroke:#d79b00
    style ROUTINES fill:#ffe6cc,stroke:#d79b00
    style HUMAN_DECISION fill:#e1d5e7,stroke:#9673a6
    style MCP fill:#dae8fc,stroke:#6c8ebf
    style WEBAPP fill:#d5e8d4,stroke:#82b366
```

---

## 2. Components

### 2.1 Experiment Designer

**Status**: 🔶 Partially Defined

The "brain" of the system. Uses Bayesian Optimization to generate experimental designs based on available data and physical constraints.

| Aspect | Decision |
|--------|----------|
| Core Algorithm | Bayesian Optimization |
| Agent Extension | Lower priority (future) |

**Inputs**

| Input | Source | When |
|-------|--------|------|
| Literature parameters | LLM Literature Review | Early iterations |
| Experimental results | Data Parser | Later iterations |
| Available routines | Monomer MCP | One-time setup |
| Reagent specification | LLM Literature Review | Early iterations |
| Physical reagent placement | Human | Early iterations (places what literature review specifies) |

**Outputs**

| Output | Description |
|--------|-------------|
| Routine parameters | Parameters for each routine to execute |
| Routines to run | Sequence of Monomer workcell routines |
| Well-to-design mapping | Links each of 96 wells to its design |

**Constraint**: All iterations must end with OD measurement.

---

### 2.2 LLM Literature Review

**Status**: 🔶 Partially Defined

Provides literature-based guidance for early iterations before sufficient experimental data exists. Papers are fed to an LLM, that extracts parameter ranges and reagent recommendations for the experiment designer.

| Question | Priority |
|----------|----------|
| Which papers to include (cell line-specific + general growth optimization)? | High |
| How to structure the LLM prompt for extracting search space parameters? | High |
| What output schema should the LLM produce? | High |

---

### 2.3 Monomer MCP Interface

**Status**: 🔶 Partially Defined

Translates experiment files into Monomer workcell commands and retrieves data.

**What's Defined**
- MCP connection is established and working
- Basic tools are available for querying plates and cultures

**Known Routines**

| Routine | Purpose |
|---------|---------|
| Measure Absorbance | OD600 reading (required every iteration) |
| Same Plate Passage | Cell passaging with configurable parameters |

**Available MCP Tools** (from current setup)

- `list_plates`, `get_plate_details`, `get_plate_observations`
- `list_cultures`, `get_culture_details`

**Remaining Work**

| Question | Priority |
|----------|----------|
| Which routines are available for our use case? | High |
| Which routines do we want to define/request? | High |
| Define MCP workflow for experiment submission to Monomer workcell | Medium |
| Define MCP workflow for OD data retrieval from Monomer workcell | Medium |

---

### 2.4 Monomer Workcell Execution

**Two-Phase Execution**

```mermaid
flowchart LR
    subgraph PHASE1["Phase 1: Setup"]
        SETUP["Configure 96 wells<br/>per design parameters"]
    end
    
    subgraph PHASE2["Phase 2: Monitor"]
        direction TB
        INC["Incubate"] --> OD["Read OD"]
        OD --> INC
    end
    
    PHASE1 --> PHASE2
    PHASE2 -->|"After N hours"| DONE["Complete"]
```

**Hardware**
- Tecan Infinite Platereader (OD measurement)
- Opentrons OT-2 (liquid handling)
- Liconic incubators (temperature control)
- PAA KX-2 robot arm (plate transport)

---

### 2.5 Data Parser

**Status**: 🔶 Partially Defined

Transforms raw OD data into structured datasets linking designs to outcomes. The platereader CSVs only contain OD readings -- they have no knowledge of what experimental parameters were used in each well. The parser joins the OD data with the well-to-design mapping so the Bayesian optimizer can learn which parameter combinations produce faster growth.

**Inputs**

| Input | Source | Description |
|-------|--------|-------------|
| Per-well absorbance CSVs | Monomer platereader | One CSV per well (`well_A1_absorbance.csv`, etc.) with columns: `timestamp`, `absorbance_od600`, `cell_concentration_cells_per_ml`, `parent_well`, `consider_data` |
| Well-to-design mapping | Experiment Designer | JSON mapping each well to its design parameters (e.g. `cell_volume_uL`, `mix_height_mm`, `mix_reps`) |

**Processing Steps**

```mermaid
flowchart LR
    RAW["Per-well OD CSVs<br/>from platereader"] --> FILTER["Filter to<br/>consider_data=True"]
    DESIGN["Well-to-Design<br/>Mapping JSON"] --> LINK
    FILTER --> LINK["Link well →<br/>design params"]
    LINK --> CALC["Fit exponential<br/>growth curve"]
    CALC --> STORE["Write<br/>growth_metrics.json"]
    STORE --> OUT1["→ Experiment Designer (BO)"]
    STORE --> OUT2["→ Webapp"]
```

**Output**

Growth metrics JSON linking each well's design parameters to its growth outcome. Stored at `data/iterations/iter_NNN/analysis/growth_metrics.json`.

**Core Data Structure**

```
Iteration N
├── input/
│   └── well_to_design_mapping.json   (from Experiment Designer)
├── output/
│   └── well_*_absorbance.csv         (from platereader, 96 files)
└── analysis/
    └── growth_metrics.json           (produced by this parser)
```

**Calculated Metrics** (per well)

Cells go through a lag phase (slow/no growth), an exponential phase (dividing at a constant rate), and a stationary phase (growth stops). We fit the exponential phase to extract growth speed.

| Metric | Definition | Purpose |
|--------|------------|---------|
| Growth rate (`growth_rate`, 1/hour) | Slope of ln(OD) vs time during exponential phase. From the model OD(t) = OD_0 * e^(mu*t), mu is the growth rate. | **Primary optimization target**: higher = faster cell division. This is the number the Bayesian optimizer maximizes. |
| Max OD (`max_od`) | Highest OD600 reading observed during the valid data window. Represents peak cell density achieved. | **Second optimization target** for multi-objective BO: higher = more total biomass. Can trade off against growth rate (e.g., high glucose may give fast initial growth but acid crash lowers final OD). |
| Doubling time (`doubling_time_hours`) | ln(2) / growth_rate. How long it takes the population to double. | Human-interpretable equivalent of growth rate. Useful for sanity-checking against known literature values. |
| R-squared (`r_squared`, 0-1) | Coefficient of determination for the linear regression on ln(OD) vs time. | **Data quality indicator**. Above ~0.95 = reliable estimate. Below ~0.8 = suspect (well may not have entered exponential phase). Lets the optimizer down-weight unreliable wells. |

---

### 2.6 Webapp

**Status**: 🔶 Partially Defined

Dashboard for humans to monitor the system and review results.

**Features**

| Feature | Description | Priority |
|---------|-------------|----------|
| Iteration view | 96-well heatmap + OD curves for each well | High |
| Design details | View parameters for any well | High |
| Workcell status | Live updates from Monomer workcell | High |
| History | Browse past iterations | Medium |
| Comparison | Compare designs across iterations | Lower |

---

### 2.7 Transition Logic

**Status**: ✅ Defined

```mermaid
stateDiagram
    [*] --> Exploration
    
    state Exploration {
        [*] --> LiteratureGuided
        LiteratureGuided: Exploration Phase
        LiteratureGuided: • LLM literature review specifies reagents to explore
        LiteratureGuided: • Human places specified reagents on workcell
        LiteratureGuided: • Broader parameter space
    }
    
    Exploration --> HumanDecision: Human decides
    HumanDecision --> Exploitation: Fix reagents
    HumanDecision --> Exploration: Continue exploring
    
    state Exploitation {
        [*] --> FixedReagents
        FixedReagents: Optimization Phase
        FixedReagents: • Reagents locked
        FixedReagents: • BO focuses on parameters
    }
    
    Exploitation --> [*]: Complete
```

**Trigger**: Human operator decides when to transition to fixed reagents (via webapp review). Once transitioned, reagents are locked and no longer need to be placed.

---

## 3. Data Flow

### Per-Iteration Sequence

```mermaid
sequenceDiagram
    participant ED as Experiment Designer
    participant MCP as Monomer MCP
    participant WC as Monomer Workcell
    participant DP as Data Parser
    participant WA as Webapp
    
    ED->>ED: Generate 96 designs
    ED->>MCP: Submit experiment files
    MCP->>WC: Execute setup
    
    loop Monitor (N hours)
        WC->>WC: Incubate
        WC->>WC: Read OD
        WC-->>WA: Status update
    end
    
    WC-->>DP: Final OD dataset
    DP->>DP: Link + calculate metrics
    DP->>WA: Push results
    DP->>ED: Ready for next iteration
```

### File Organization

```
data/
└── iterations/
    └── iter_001/
        ├── input/
        │   ├── routine_parameters.json
        │   ├── routines_to_run.json
        │   ├── well_to_design_mapping.json
        │   └── transfer_array.json   # Monomer dispense list (optional vs routine JSON)
        ├── output/
        │   └── od_readings.csv
        └── analysis/
            └── growth_metrics.json
```

Reagent LHS designs (mapping + `transfer_array.json` + `*_design_summary.md`) are produced by **`src/design`**; run **`scripts/generate_reagent_design.py`** from the repo root. Details: **`src/design/README.md`**.

**Plate layout for liquid handling:** a single **24-well source plate** (`source_24w`, max 8.5 mL per well) holds all six reagent stocks (`A1`-`A6`) and the bacterial inoculum (`B1`). All transfers land in a **96-well experiment plate** (`experiment`) that starts empty. The generated `*_design_summary.md` includes the full workcell setup table with aspirated volumes per source well.

---

## 4. Action Items

### High Priority

| Component | Action |
|-----------|--------|
| LLM Literature Review | Curate relevant papers (cell line + growth optimization) |
| LLM Literature Review | Define LLM prompt structure and output schema |
| Monomer MCP | Determine which routines are available |
| Monomer MCP | Define which routines we need for experiments |
| Monomer MCP | Define experiment submission workflow |
| Data Parser | Implement well-to-design linking |

### Medium Priority

| Component | Action |
|-----------|--------|
| Experiment Designer | Implement Bayesian Optimization |
| Webapp | Build iteration dashboard |
| Data Parser | Implement metric calculations |

### Lower Priority

| Component | Action |
|-----------|--------|
| Transition | System-proposed transition |
| Experiment Designer | Agent-based wrapper |
| Webapp | Cross-iteration comparison |

---

## 5. Open Questions

| ID | Question | Component |
|----|----------|-----------|
| Q1 | Which papers to include and how to structure the LLM prompt for extracting search space? | LLM Literature Review |
| Q2 | Which available routines fit our experimental needs? | Monomer MCP |
| Q3 | Do we need to define custom routines, or use existing ones? | Monomer MCP |
| Q4 | How long should each monitoring phase run? | Experiment Designer |

---

## Glossary

| Term | Definition |
|------|------------|
| Iteration | One complete cycle: design → execute → measure → analyze |
| Design | Experimental parameters for one well |
| OD | Optical Density at 600nm (cell density proxy) |
| Routine | A Monomer workcell operation |
| Transition | Switch from reagent exploration to fixed-reagent optimization |

---
