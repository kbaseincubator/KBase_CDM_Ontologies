# SemsQL Custom Prefixes

## Purpose

This directory contains custom prefixes that are added to SemsQL during the Docker build process. These prefixes are essential for properly handling URIs from various biological databases in our merged ontology, which combines 30+ different ontologies.

## Custom Prefixes

The `custom_prefixes.csv` file contains the following custom prefixes:

- **KEGG** (Kyoto Encyclopedia of Genes and Genomes)
  - `kegg.reaction` - For KEGG reaction entries
  - `kegg.pathway` - For KEGG pathway entries

- **SEED** (Model SEED Database)
  - `seed.compound` - For SEED compound entries
  - `seed.reaction` - For SEED reaction entries

- **MetaCyc** (Metabolic Pathway Database)
  - `metacyc.reaction` - For MetaCyc reactions
  - `metacyc.pathway` - For MetaCyc pathways

- **Reactome** (Pathway Database)
  - `Reactome` - For Reactome pathway details

## How It Works

1. **During Docker Build**: The `custom_prefixes.csv` file is copied into the Docker image and appended to SemsQL's main `prefixes.csv` file.

2. **In SemsQL Database Creation**: When SemsQL creates a database from our merged ontology, it imports all prefixes (including our custom ones) into the database's `prefix` table.

3. **Result**: All URIs from KEGG, SEED, MetaCyc, and Reactome are properly prefixed in the resulting SemsQL database.

## Integration with Main Workflow

The custom prefixes are automatically integrated when:
- Building the Docker image (`make docker-build`)
- Running the production pipeline (`make docker-run-prod`)
- The merged ontology contains terms from 30+ ontologies including KEGG, SEED, MetaCyc, and Reactome

## File Format

The `custom_prefixes.csv` file follows the standard SemsQL prefix format:
```csv
prefix,base
prefix_name,base_uri
```

Multiple prefixes can map to different base URIs for the same database (e.g., different KEGG entry types).