#!/usr/bin/env python3
"""Test validation script to check pipeline outputs at each step."""

import os
import sys
import sqlite3
from pathlib import Path

def check_directory_exists(path, description):
    """Check if a directory exists."""
    if os.path.exists(path):
        print(f"✅ {description}: {path} exists")
        return True
    else:
        print(f"❌ {description}: {path} NOT found")
        return False

def check_file_exists(path, description):
    """Check if a file exists and show its size."""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✅ {description}: {path} exists ({size:,} bytes)")
        return True
    else:
        print(f"❌ {description}: {path} NOT found")
        return False

def count_files_in_directory(path, pattern="*"):
    """Count files matching pattern in directory."""
    if not os.path.exists(path):
        return 0
    files = list(Path(path).glob(pattern))
    return len(files)

def check_sqlite_tables(db_path):
    """Check SQLite database and list tables."""
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"✅ Database has {len(tables)} tables:")
        for table in tables[:5]:  # Show first 5 tables
            print(f"   - {table[0]}")
        if len(tables) > 5:
            print(f"   ... and {len(tables) - 5} more tables")
        return True
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def validate_step1_analyze_core():
    """Validate step 1: Analyze core ontologies."""
    print("\n🔍 Validating Step 1: Analyze Core Ontologies")
    print("-" * 50)
    
    # Check test mode
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    test_mode = 'test' in source_file.lower()
    
    # Check for downloaded ontology files
    owl_dir = "ontology_data_owl_test" if test_mode else "ontology_data_owl"
    check_directory_exists(owl_dir, f"Ontology data directory ({'TEST' if test_mode else 'PROD'})")
    
    # Count OWL files
    owl_count = count_files_in_directory(owl_dir, "*.owl")
    print(f"📊 Found {owl_count} OWL files in {owl_dir}")
    
    # Check for specific test ontologies
    test_ontologies = ["bfo.owl", "iao.owl", "uo.owl", "envo.owl", "go.owl"]
    for onto in test_ontologies:
        check_file_exists(os.path.join(owl_dir, onto), f"Test ontology {onto}")

def validate_step2_analyze_non_core():
    """Validate step 2: Analyze non-core ontologies."""
    print("\n🔍 Validating Step 2: Analyze Non-Core Ontologies")
    print("-" * 50)
    
    # Check test mode
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    test_mode = 'test' in source_file.lower()
    
    # Check non-base ontologies directory
    base_dir = "ontology_data_owl_test" if test_mode else "ontology_data_owl"
    non_base_dir = f"{base_dir}/non-base-ontologies"
    check_directory_exists(non_base_dir, f"Non-base ontologies directory ({'TEST' if test_mode else 'PROD'})")
    
    # Count files in non-base directory
    non_base_count = count_files_in_directory(non_base_dir, "*.owl")
    print(f"📊 Found {non_base_count} files in non-base directory")

def validate_step3_create_base():
    """Validate step 3: Create pseudo-base ontologies."""
    print("\n🔍 Validating Step 3: Create Pseudo-Base Ontologies")
    print("-" * 50)
    
    # Check test mode
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    test_mode = 'test' in source_file.lower()
    
    # Check for -base.owl files
    owl_dir = "ontology_data_owl_test" if test_mode else "ontology_data_owl"
    base_count = count_files_in_directory(owl_dir, "*-base.owl")
    print(f"📊 Found {base_count} base ontology files")
    
    # Check for specific base files
    base_ontologies = ["ro-base.owl", "pato-base.owl", "cl-base.owl"]
    for onto in base_ontologies:
        check_file_exists(os.path.join(owl_dir, onto), f"Base ontology {onto}")

def validate_step4_merge():
    """Validate step 4: Merge ontologies."""
    print("\n🔍 Validating Step 4: Merge Ontologies")
    print("-" * 50)
    
    # Check test mode
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    test_mode = 'test' in source_file.lower()
    
    # Check outputs directory
    outputs_dir = "outputs_test" if test_mode else "outputs"
    check_directory_exists(outputs_dir, f"Outputs directory ({'TEST' if test_mode else 'PROD'})")
    
    # Check for merged ontology file
    merged_files = list(Path(outputs_dir).glob("*.owl"))
    if merged_files:
        for merged_file in merged_files:
            check_file_exists(str(merged_file), f"Merged ontology")
    else:
        print("❌ No merged ontology files found in outputs/")
    
    # Check for ontologies_merged.txt
    check_file_exists("ontologies_merged.txt", "Merged ontologies list")

def validate_step5_create_db():
    """Validate step 5: Create semantic SQL database."""
    print("\n🔍 Validating Step 5: Create Semantic SQL Database")
    print("-" * 50)
    
    # Check test mode
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    test_mode = 'test' in source_file.lower()
    
    # Check for database files
    outputs_dir = "outputs_test" if test_mode else "outputs"
    db_files = list(Path(outputs_dir).glob("*.db"))
    
    if db_files:
        for db_file in db_files:
            check_file_exists(str(db_file), f"SQLite database")
            check_sqlite_tables(str(db_file))
    else:
        print("❌ No database files found in outputs/")

def validate_step6_extract_tables():
    """Validate step 6: Extract SQL tables to TSV."""
    print("\n🔍 Validating Step 6: Extract SQL Tables to TSV")
    print("-" * 50)
    
    # Check test mode
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    test_mode = 'test' in source_file.lower()
    
    # Check for TSV output directory
    outputs_dir = "outputs_test" if test_mode else "outputs"
    tsv_dirs = list(Path(outputs_dir).glob("tsv_tables*"))
    
    if tsv_dirs:
        for tsv_dir in tsv_dirs:
            check_directory_exists(str(tsv_dir), f"TSV tables directory")
            tsv_count = count_files_in_directory(str(tsv_dir), "*.tsv")
            print(f"📊 Found {tsv_count} TSV files in {tsv_dir}")
    else:
        print("❌ No TSV tables directories found")
    
    # Check for Parquet files if they exist
    parquet_dirs = list(Path(outputs_dir).glob("parquet_tables*"))
    if parquet_dirs:
        for parquet_dir in parquet_dirs:
            check_directory_exists(str(parquet_dir), f"Parquet tables directory")
            parquet_count = count_files_in_directory(str(parquet_dir), "*.parquet")
            print(f"📊 Found {parquet_count} Parquet files in {parquet_dir}")


def validate_version_tracking():
    """Validate version tracking system."""
    print("\n🔍 Validating Version Tracking System")
    print("-" * 50)
    
    # Check test mode
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    test_mode = 'test' in source_file.lower()
    
    # Check version tracking directory
    version_dir = "ontology_versions_test" if test_mode else "ontology_versions"
    check_directory_exists(version_dir, f"Version tracking directory ({'TEST' if test_mode else 'PROD'})")
    
    # Check for version tracking files
    version_file = os.path.join(version_dir, "ontology_versions.json")
    if check_file_exists(version_file, "Version tracking file"):
        try:
            import json
            with open(version_file, 'r') as f:
                version_data = json.load(f)
            print(f"📊 Tracking {len(version_data)} ontologies")
            
            # Show some statistics
            updated_count = sum(1 for info in version_data.values() if info.get('previous_checksum'))
            print(f"📊 {updated_count} ontologies have update history")
        except Exception as e:
            print(f"❌ Error reading version file: {e}")
    
    # Check for download history log
    log_file = os.path.join(version_dir, "download_history.log")
    check_file_exists(log_file, "Download history log")
    
    # Check for backups directory
    backup_dir = os.path.join(version_dir, "backups")
    if os.path.exists(backup_dir):
        backup_count = count_files_in_directory(backup_dir, "*")
        print(f"📦 Found {backup_count} backup files")

def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python test_validation.py <step>")
        print("Steps: 1=analyze-core, 2=analyze-non-core, 3=create-base, 4=merge, 5=create-db, 6=extract-tables, version=version-tracking, all=all-steps")
        sys.exit(1)
    
    step = sys.argv[1].lower()
    
    print("🧪 CDM Ontologies Pipeline - Test Validation")
    print("=" * 60)
    
    # Show current mode
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    test_mode = 'test' in source_file.lower()
    print(f"🔧 Validation Mode: {'TEST' if test_mode else 'PRODUCTION'}")
    print(f"📄 Source File: {source_file}")
    
    if step in ["1", "analyze-core", "all"]:
        validate_step1_analyze_core()
    
    if step in ["2", "analyze-non-core", "all"]:
        validate_step2_analyze_non_core()
    
    if step in ["3", "create-base", "all"]:
        validate_step3_create_base()
    
    if step in ["4", "merge", "all"]:
        validate_step4_merge()
    
    if step in ["5", "create-db", "all"]:
        validate_step5_create_db()
    
    if step in ["6", "extract-tables", "all"]:
        validate_step6_extract_tables()
    
    if step in ["version", "version-tracking", "all"]:
        validate_version_tracking()
    
    print("\n✅ Validation complete!")

if __name__ == "__main__":
    main()