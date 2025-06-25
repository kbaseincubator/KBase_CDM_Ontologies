# Test Ontology Data Directory

This directory contains ontology data when running the test pipeline with `ontologies_source_test.txt`.

## What gets stored here:

- Downloaded test ontology files (.owl)
- Base versions of test ontologies
- A smaller subset of ontologies for testing the complete pipeline

## Test Dataset

The test `ontologies_source_test.txt` includes 6 carefully selected ontologies:
- **BFO** (Basic Formal Ontology) - Small foundational ontology
- **IAO** (Information Artifact Ontology) - Small, tests information entities
- **RO** (Relations Ontology) - Essential for relationship testing
- **PATO** (Phenotype And Trait Ontology) - Moderate size, tests qualities
- **ENVO** (Environment Ontology) - Larger OBO ontology for integration testing
- **CRediT** (Contributor Roles) - Small PyOBO vocabulary

This test set covers all pipeline aspects while remaining manageable in size.

## Purpose

The test dataset allows users to:
- Verify the pipeline works correctly
- See example outputs without processing large datasets
- Test modifications to the pipeline quickly
- Understand the expected output structure

## Note

This directory is excluded from git. Run the test pipeline with:
```bash
make docker-test
```