# Test Pipeline Outputs Directory

This directory contains example outputs from running the test pipeline with `ontologies_source_test.txt`.

## What's included:

### Test Dataset
The test pipeline processes 6 carefully selected ontologies:
- BFO, IAO (small foundational ontologies)
- RO, PATO (essential relationships and traits)
- ENVO (moderate-sized environmental ontology)
- CRediT (small controlled vocabulary)

### Generated Files

#### Merged Ontology
- `ontology_data_owl.owl` - Merged ontology containing all 6 test ontologies
- Demonstrates the merge process without massive file sizes

#### Database
- `ontology_data_owl.db` - Semantic SQL database (manageable size)
- Shows the complete database schema and structure

#### Analysis Results
- `core_ontologies_analysis.json` - Analysis of test core ontologies
- `non_core_ontologies_analysis.json` - Analysis of test non-core ontologies
- Various TSV files with term analysis

#### Extracted Tables
- `tsv_tables_ontology_data_owl/` - All database tables in TSV format
- `parquet_tables_*/` - Parquet format for data analysis
- Includes key tables: statements, entailed_edge, prefix, etc.

## Purpose

This test output directory serves as:
1. **Demonstration** - Shows what the pipeline produces
2. **Validation** - Verifies correct pipeline operation
3. **Documentation** - Examples of expected output formats
4. **Testing** - Reference for comparing custom runs

## Running the Test Pipeline

To regenerate these outputs:
```bash
make docker-test
```

The test pipeline typically completes in minutes rather than hours/days.