# Project Outline: WizERD

## Project Overview

**Project Name:** WizERD

**Project Type:** CLI tool / Library (with optional web interface)

**Core Functionality:** A PostgreSQL schema visualization tool that generates clean, readable ER diagrams from SQL dumps or database schemas. Prioritizes visual legibility over compactness—ensures no table overlap and minimal relationship line crossovers, regardless of canvas size.

## Problem Statement

Existing ER diagram generators fail when handling large databases (100+ tables). They:
- Overlap tables and relationship lines
- Prioritize size/small canvas over readability
- Produce "line messes" that are nearly impossible to parse
- Lack hierarchy or logical grouping

## Goals

1. **Zero table overlap** — Tables should never render on top of each other
2. **Minimal line crossovers** — Relationship arrows should cross as little as possible
3. **Readable at any scale** — Whether 100 tables or 500, diagrams remain navigable
4. **Flexible output** — Support various output formats and layout options

## Features

### Core Features
- Parse PostgreSQL schema from SQL dump files
- (Optional) Direct database connection for schema extraction
- Generate optimized ER diagrams with:
  - Automatic table positioning
  - Smart relationship line routing (minimal crossovers)
  - Color-coded elements for differentiation
  - Crow's foot or other relationship notation (configurable)

### Output Options
- **Single giant diagram** — Pan/zoom enabled for 100+ tables
- **Auto-grouped diagrams** — Clustered by schema, domain, or custom groups
- **Multiple sub-diagrams** — Separate diagrams by namespace/schema

### Output Formats
- SVG (recommended for scalability)
- PNG
- PDF
- Interactive HTML (optional web interface)

### Deployment Possibilities
- CLI tool for local dev usage
- Optional web interface (containerized if hosted)
- Package/library mode for programmatic use

## Technical Approach

### Language
- Python or JS/TS (or both) — whichever offers best libraries

### Key Technical Challenges
1. **Graph layout algorithm** — Force-directed or constraint-based layout that optimizes for readability over compactness
2. **Line routing** — A* or similar pathfinding for relationship lines that avoids table boxes or other lines where possible
3. **Large database handling** — Performance optimization for 100+ node graphs

### Libraries to Evaluate
- Graphviz (Python: graphviz, pydot)
- D3.js (for web/interactive)
- elkjs or dagre-d3 (layout engines)
- Mermaid.js (for reference, likely insufficient)

## Timeline
- **Goal:** ASAP (expedited)
- **Priority:** Quality over speed
- **Phase 1:** Core schema parsing + basic diagram generation
- **Phase 2:** Layout optimization (overlap/crossover reduction)
- **Phase 3:** Multiple output formats and deployment options
- **Phase 4:** Refinement based on real-world usage

## Future Considerations
- Open source if the tool proves valuable
- Add support for other databases (MySQL, SQLite) if needed
- Configuration options for colors, grouping, notation style
