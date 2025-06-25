# KBase CDM Ontologies Pipeline

A containerized pipeline for processing and merging biological ontologies at scale with comprehensive version tracking and multi-environment support.

## Overview

This pipeline processes biological ontologies from sources like OBO Foundry, Gene Ontology, CHEBI, and others, creating unified knowledge bases for computational analysis. It transforms heterogeneous ontology formats into structured databases while maintaining provenance and version control.

**Key Features:**
- Processes 30+ major biological ontologies
- Handles datasets requiring >1TB RAM for production workloads
- Creates semantic SQL databases for efficient querying
- Exports to multiple formats (OWL, SQLite, TSV, Parquet)
- Comprehensive version tracking with SHA256 checksums
- Docker-based deployment with all dependencies included

## Quick Start

### Test Mode (Recommended First Step)

```bash
# Build and run with test dataset (6 ontologies)
make docker-build
make docker-test
```

### Production Mode

```bash
# Requires 1.5TB+ available RAM
make docker-run-large
```

## Installation

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- 8GB RAM (test mode) or 1.5TB RAM (production mode)

### Setup

```bash
git clone https://github.com/jplfaria/KBase_CDM_Ontologies.git
cd KBase_CDM_Ontologies
make docker-build
```

## Pipeline Architecture

The pipeline consists of 5 sequential steps:

1. **Analyze Core Ontologies** - Downloads and processes primary ontologies
2. **Analyze Non-Core Ontologies** - Processes additional OBO ontologies
3. **Merge Ontologies** - Combines all ontologies using ROBOT
4. **Create Semantic SQL Database** - Converts to queryable SQLite format
5. **Extract Tables** - Exports database tables to TSV/Parquet

## Configuration

### Test Dataset (6 ontologies)
- Quick execution (~10 minutes)
- Demonstrates full pipeline
- Uses `config/ontologies_source_test.txt`

### Production Dataset (30+ ontologies)
- Extended execution (hours to days)
- Requires massive memory allocation
- Uses `config/ontologies_source.txt`

## Output Structure

```
outputs/              # Production outputs (git-ignored)
outputs_test/         # Test outputs (included as examples)
├── ontology_data_owl.owl     # Merged ontology file
├── ontology_data_owl.db      # SQLite database
└── tsv_tables_*/             # Exported data tables
```

## Memory Requirements

| Mode | Ontologies | RAM Required | Processing Time |
|------|------------|--------------|-----------------|
| Test | 6 | 8GB | ~10 minutes |
| Small | 15 | 64GB | ~2 hours |
| Large | 30+ | 1.5TB | 24+ hours |

## Documentation

- [Getting Started Guide](docs/GETTING_STARTED.md)
- [Pipeline Architecture](docs/PIPELINE_ARCHITECTURE.md)
- [Configuration Options](docs/CONFIGURATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## CLI Usage

```bash
# Run complete workflow
python -m cdm_ontologies run-workflow --env-file .env.test

# Run individual steps
python -m cdm_ontologies analyze-core
python -m cdm_ontologies merge-ontologies
python -m cdm_ontologies create-db

# Check pipeline status
python -m cdm_ontologies status
```

## External Tools

The Docker container includes all required tools:
- **ROBOT v1.9.8** - Ontology manipulation
- **relation-graph v2.3.2** - Relationship inference
- **SemanticSQL** - OWL to SQL conversion

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests with `make docker-test`
4. Submit a pull request

## License

This project is licensed under the MIT License - see [LICENSE.txt](LICENSE.txt) for details.

## Support

- Issues: [GitHub Issues](https://github.com/jplfaria/KBase_CDM_Ontologies/issues)
- Documentation: [docs/](docs/)

## Acknowledgments

This pipeline processes ontologies from:
- [OBO Foundry](http://obofoundry.org/)
- [Gene Ontology](http://geneontology.org/)
- [ChEBI](https://www.ebi.ac.uk/chebi/)
- [NCBI Taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy)
- And many other biological ontology providers