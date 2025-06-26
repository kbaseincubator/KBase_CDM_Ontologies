# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔄 DUAL REPOSITORY SYNC REQUIREMENT 🔄

**CRITICAL: This repository is maintained in TWO locations and MUST be kept in sync:**

- **Personal**: https://github.com/jplfaria/KBase_CDM_Ontologies
- **KBase Org**: https://github.com/kbaseincubator/KBase_CDM_Ontologies

**ALWAYS push changes to BOTH repositories:**
```bash
# After any commit, ALWAYS run both:
git push origin <branch>
git push kbase <branch>

# Example for dev branch:
git push origin dev && git push kbase dev

# Example for main branch:
git push origin main && git push kbase main
```

**Before making ANY changes, verify remotes are configured:**
```bash
git remote -v
# Should show both:
# origin  https://github.com/jplfaria/KBase_CDM_Ontologies.git
# kbase   https://github.com/kbaseincubator/KBase_CDM_Ontologies.git
```

**NEVER push to only one repository - both must stay identical.**

## ⚠️ DOCKER-ONLY EXECUTION ⚠️

**IMPORTANT: This pipeline MUST be executed using Docker containers only. Do not attempt to run scripts locally on the host system.**

All pipeline execution should use the containerized environment which includes all required tools (ROBOT, relation-graph, SemanticSQL) with proper memory configuration.

## Essential Commands

### Docker Execution (REQUIRED)
```bash
# Run with test dataset (6 ontologies)
make docker-test

# Run with production dataset 
make docker-run-large

# Build Docker image
make docker-build
```

### Development Commands (Docker-based)
```bash
# Show all available commands
make help

# Build and test in Docker
make docker-build
make docker-test
```

### Direct Docker Usage
```bash
# Run pipeline with Docker Compose
docker-compose up

# Start Jupyter notebook for analysis
docker-compose up notebook
```

## Containerized Tool Dependencies

All external tools are pre-installed in the Docker container:

1. **ROBOT v1.9.8** - Java-based ontology manipulation tool
   - Used for ontology merging, reasoning, and axiom removal
   - Pre-installed in container with optimized memory configuration

2. **SemanticSQL (semsql)** - For creating semantic SQL databases
   - Used to convert OWL ontologies to SQLite format
   - Pre-installed with rdftab.rs dependency

3. **relation-graph v2.3.2** - Java tool for computing entailed relationships
   - Used for materializing inferred relationships in ontologies
   - Pre-installed with memory-optimized JVM settings

## High-Level Architecture

### Workflow Pipeline
The repository implements a sequential pipeline for processing biological ontologies:

1. **Analyze Core Ontologies** (`analyze_core_ontologies.py`)
   - Processes ontologies listed in `ontologies_source.txt`
   - Creates "base" versions by removing external axioms using ROBOT
   - Stores results in `ontology_data_owl/`

2. **Analyze Non-Core Ontologies** (`analyze_non_core_ontologies.py`)
   - Downloads and processes additional ontologies from OBO Foundry
   - Filters based on size constraints and processing feasibility
   - Adds to `ontology_data_owl/non-base-ontologies/`

3. **Merge Ontologies** (`merge_ontologies.py`)
   - Combines multiple ontologies into unified files
   - Uses ROBOT for merging with various strategies
   - Memory-intensive operation (can use >1TB RAM for large merges)
   - Creates multiple merge variants in `outputs/`

4. **Create Semantic SQL Database** (`create_semantic_sql_db.py`)
   - Converts merged OWL files to SQLite databases
   - Uses SemanticSQL for transformation
   - Outputs to `outputs/*.db`

5. **Extract Tables to TSV** (`extract_sql_tables_to_tsv.py`)
   - Exports database tables to TSV/Parquet formats
   - Creates directories under `outputs/tsv_tables_*/`

### Key Data Flow
```
Raw OWL files → Base versions → Merged ontologies → SQLite DB → TSV/Parquet
```

### Important Configuration Files
- `ontologies_source.txt` - List of core ontologies to process
- `ontologies_merged.txt` - Ontologies to include in merges
- `prefix_mapping.txt` - URI prefix mappings for ontologies
- `custom_prefixes/` - Custom prefix configurations
- `semsql_custom_prefixes/` - SemanticSQL-specific prefix mappings

### Memory and Performance Considerations
- Large ontology merges can require >1TB of RAM
- Scripts include configurable memory limits for Java processes
- Processing can take several hours for complete workflow
- Individual ontology downloads may fail due to size/network constraints

## Containerized Environment

### Docker Setup
The repository now includes a complete Docker-based solution:
- **Dockerfile**: Multi-stage build with all dependencies pre-installed
- **docker-compose.yml**: Local development orchestration
- **High-memory configuration**: Optimized for large dataset processing
- **k8s/**: Kubernetes manifests for production deployment

### Container Features
- Pre-installed tools: ROBOT v1.9.8, relation-graph v2.3.2, SemanticSQL with rdftab.rs
- Non-root user execution (avoids permission issues)
- **Ultra-high memory configuration**: 1.5TB container limits for 680GB+ peak usage
- Memory usage monitoring and logging in outputs/utils/
- Volume mounts for data persistence
- Complete isolation from host system dependencies

### Memory Requirements
**⚠️ MASSIVE MEMORY REQUIREMENTS FOR PRODUCTION DATASETS ⚠️**

Production datasets require enormous memory allocation:
- **ROBOT merge operations**: Peak usage up to 680GB+ for large ontology merges
- **SemanticSQL processing**: Can take 19+ hours for database creation
- **Container memory**: 1.5TB allocated (1536GB) to handle peak usage with headroom
- **Recommended host memory**: 2TB+ for comfortable production processing

Test datasets use the same memory limits but will only consume what they need.

### Test Mode File Isolation
Test mode ensures complete isolation from production files:
- **Source file**: Uses `ontologies_source_test.txt` instead of `ontologies_source.txt`
- **Merged list**: Creates `ontologies_merged_test.txt` instead of `ontologies_merged.txt`
- **Output directories**: Uses `ontology_data_owl_test/` and `outputs_test/`
- **No production modifications**: Test mode never modifies production source files

### Python CLI Module
- **cdm_ontologies/cli.py**: Unified command-line interface
- Supports running complete workflow or individual steps
- Proper error handling and logging
- Progress tracking and memory monitoring

## 📚 Documentation Maintenance

### ⚠️ CRITICAL REMINDER: Always Review Documentation Before Commits

**Before any commit/push, ALWAYS verify that documentation reflects current repository state:**

1. **After moving/removing files**: Update all path references in docs/
2. **After script changes**: Verify CLI examples and API references
3. **After config changes**: Update CONFIGURATION.md and examples
4. **After removing features**: Remove outdated documentation sections

### Key Files to Check:
- **README.md**: Main user-facing documentation
- **docs/GETTING_STARTED.md**: Entry point for new users  
- **docs/API_REFERENCE.md**: CLI and Python API documentation
- **docs/CONFIGURATION.md**: Configuration file paths and examples
- **docs/TROUBLESHOOTING.md**: Commands and file references
- **docs/VERSION_TRACKING.md**: Version manager usage

### Common Issues After Changes:
- References to deleted files (run_test.sh, test_validation.py, etc.)
- Incorrect paths (files moved to config/, scripts/, etc.)
- Outdated CLI examples and command syntax
- Missing updates to troubleshooting commands

**Documentation accuracy is critical for user experience - broken examples frustrate users!**