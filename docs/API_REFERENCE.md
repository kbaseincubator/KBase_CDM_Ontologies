# API Reference

Complete reference for the CDM Ontologies Pipeline command-line interface, Python modules, and programmatic usage.

## Command Line Interface

### Main CLI Module

```bash
python -m cdm_ontologies [OPTIONS] COMMAND [ARGS]
```

#### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--verbose, -v` | Enable verbose logging | `False` |
| `--config FILE` | Configuration file path | `.env` |
| `--dry-run` | Show what would be done without executing | `False` |
| `--help, -h` | Show help message | - |

#### Commands

##### `run-all`
Run the complete pipeline workflow

```bash
python -m cdm_ontologies run-all [OPTIONS]
```

**Options:**
- `--skip-download`: Skip download steps if files exist
- `--force-rebuild`: Force rebuild even if outputs exist
- `--steps STEPS`: Comma-separated list of steps to run

**Example:**
```bash
python -m cdm_ontologies run-all --verbose --steps "1,2,3"
```

##### `analyze-core`
Download and analyze core ontologies

```bash
python -m cdm_ontologies analyze-core [OPTIONS]
```

**Options:**
- `--source-file FILE`: Path to ontologies source file
- `--output-dir DIR`: Output directory for analysis results
- `--parallel N`: Number of parallel downloads

**Example:**
```bash
python -m cdm_ontologies analyze-core --parallel 10 --source-file config/ontologies_source_test.txt
```

##### `analyze-non-core`
Process non-core dependency ontologies

```bash
python -m cdm_ontologies analyze-non-core [OPTIONS]
```

**Options:**
- `--input-dir DIR`: Directory containing core analysis results
- `--obo-only`: Only process OBO Foundry ontologies
- `--max-size MB`: Maximum ontology size in MB

##### `create-base`
Create pseudo-base versions of ontologies

```bash
python -m cdm_ontologies create-base [OPTIONS]
```

**Options:**
- `--input-dir DIR`: Directory containing ontology files
- `--output-dir DIR`: Output directory for base versions
- `--robot-args ARGS`: Additional ROBOT arguments

##### `merge`
Merge ontologies into unified files

```bash
python -m cdm_ontologies merge [OPTIONS]
```

**Options:**
- `--merge-config FILE`: Merge configuration file
- `--output-dir DIR`: Output directory for merged files
- `--collapse-imports`: Collapse import statements

##### `create-db`
Create semantic SQL databases

```bash
python -m cdm_ontologies create-db [OPTIONS]
```

**Options:**
- `--input-dir DIR`: Directory containing OWL files
- `--output-dir DIR`: Output directory for databases
- `--create-views`: Create materialized views

##### `extract-tables`
Export database tables to files

```bash
python -m cdm_ontologies extract-tables [OPTIONS]
```

**Options:**
- `--input-dir DIR`: Directory containing database files
- `--output-dir DIR`: Output directory for exported tables
- `--format FORMAT`: Export format (tsv, parquet, json)

### Make Commands

#### Workflow Commands

```bash
make run-workflow           # Complete pipeline (production)
make test-workflow          # Complete pipeline (test dataset)
```

#### Individual Steps

```bash
make analyze-core           # Download and analyze ontologies
make analyze-non-core       # Process dependency ontologies
make create-base           # Generate base versions
make merge                 # Merge into unified files
make create-db             # Create SQLite databases
make extract-tables        # Export to TSV/Parquet
```

#### Test-Specific Commands

```bash
make test-analyze-core      # Analyze core with test dataset
make test-create-base       # Create base versions (test)
make test-merge            # Merge ontologies (test)
make test-create-db        # Create databases (test)
make test-extract-tables   # Export tables (test)
```

#### Docker Commands

```bash
make docker-build          # Build container image
make docker-run-small      # Run with small dataset
make docker-run-large      # Run with large dataset
make docker-test           # Run with test dataset
```

#### Utility Commands

```bash
make setup                 # Create directories
make install               # Install Python dependencies
make clean                 # Clean output files
make clean-all             # Clean everything including downloads
make help                  # Show all available targets
```

## Version Manager CLI

### Commands

#### `status`
Show current version status of all ontologies

```bash
python scripts/version_manager.py status [OPTIONS]
```

**Options:**
- `--format FORMAT`: Output format (text, json, csv)
- `--filter STATUS`: Filter by status (current, outdated, error)
- `--ontology NAME`: Show status for specific ontology

**Example:**
```bash
python scripts/version_manager.py status --format json --filter outdated
```

#### `report`
Generate detailed version report

```bash
python scripts/version_manager.py report [OPTIONS]
```

**Options:**
- `--output FILE`: Output file path
- `--format FORMAT`: Report format (markdown, html, text)
- `--include-history`: Include download history

**Example:**
```bash
python scripts/version_manager.py report --output version_report.md --include-history
```

#### `validate`
Validate file checksums and integrity

```bash
python scripts/version_manager.py validate [OPTIONS]
```

**Options:**
- `--fix`: Attempt to fix validation errors
- `--ontology NAME`: Validate specific ontology
- `--verbose`: Show detailed validation results

**Example:**
```bash
python scripts/version_manager.py validate --verbose --ontology bfo.owl
```

#### `history`
Show download history

```bash
python scripts/version_manager.py history [OPTIONS]
```

**Options:**
- `--limit N`: Show last N entries
- `--ontology NAME`: Show history for specific ontology
- `--since DATE`: Show entries since date (YYYY-MM-DD)
- `--status STATUS`: Filter by status (success, failed, skipped)

**Example:**
```bash
python scripts/version_manager.py history --limit 20 --since 2025-06-01
```

#### `clean`
Clean old backup files

```bash
python scripts/version_manager.py clean [OPTIONS]
```

**Options:**
- `--keep N`: Keep N most recent backups
- `--days N`: Keep backups from last N days
- `--all`: Remove all backups (use with caution)
- `--dry-run`: Show what would be deleted

**Example:**
```bash
python scripts/version_manager.py clean --keep 5 --dry-run
```

#### `force-update`
Force update specific ontologies

```bash
python scripts/version_manager.py force-update ONTOLOGY [ONTOLOGY ...]
```

**Example:**
```bash
python scripts/version_manager.py force-update bfo.owl iao.owl
```

#### `check-updates`
Check for available updates

```bash
python scripts/version_manager.py check-updates [OPTIONS]
```

**Options:**
- `--exit-code`: Exit with code 0 if updates available, 1 if not
- `--ontology NAME`: Check specific ontology
- `--threshold MB`: Only report updates larger than threshold

**Example:**
```bash
python scripts/version_manager.py check-updates --exit-code --threshold 1
```

## Python API

### Core Modules

#### `cdm_ontologies.core`

```python
from cdm_ontologies.core import Pipeline, Config

# Initialize pipeline
config = Config.from_file('.env.large')
pipeline = Pipeline(config)

# Run complete workflow
pipeline.run_all()

# Run individual steps
pipeline.analyze_core()
pipeline.create_base()
pipeline.merge_ontologies()
```

#### `cdm_ontologies.version_tracker`

```python
from cdm_ontologies.version_tracker import VersionTracker

# Initialize tracker
tracker = VersionTracker('ontology_versions.json')

# Check for updates
has_updates = tracker.check_for_updates('bfo.owl', 'http://example.com/bfo.owl')

# Get version info
version_info = tracker.get_version_info('bfo.owl')

# Update version
tracker.update_version('bfo.owl', 'http://example.com/bfo.owl', '/path/to/file.owl')
```

#### `cdm_ontologies.downloader`

```python
from cdm_ontologies.downloader import EnhancedDownloader

# Initialize downloader
downloader = EnhancedDownloader(max_retries=3, timeout=30)

# Download with version tracking
result = downloader.download_with_version_tracking(
    url='http://example.com/ontology.owl',
    output_path='/path/to/ontology.owl'
)

# Batch download
urls = ['http://example.com/ont1.owl', 'http://example.com/ont2.owl']
results = downloader.batch_download(urls, '/output/dir/')
```

### Configuration Classes

#### `Config`

```python
from cdm_ontologies.config import Config

# Load from file
config = Config.from_file('.env.large')

# Load from environment
config = Config.from_environment()

# Create programmatically
config = Config(
    robot_java_args='-Xmx32g',
    parallel_downloads=10,
    dataset_size='large'
)

# Access settings
print(config.robot_java_args)
print(config.parallel_downloads)
```

#### `Environment`

```python
from cdm_ontologies.environment import Environment

# Detect environment
env = Environment.detect()

print(env.mode)          # 'test' or 'production'
print(env.data_dir)      # 'ontology_data_owl_test' or 'ontology_data_owl'
print(env.output_dir)    # 'outputs_test' or 'outputs'
```

### Utility Functions

#### File Operations

```python
from cdm_ontologies.utils import (
    calculate_checksum,
    create_backup,
    ensure_directory,
    get_file_size
)

# Calculate file checksum
checksum = calculate_checksum('/path/to/file.owl')

# Create backup
backup_path = create_backup('/path/to/file.owl')

# Ensure directory exists
ensure_directory('/path/to/directory')

# Get file size
size_bytes = get_file_size('/path/to/file.owl')
```

#### Logging

```python
from cdm_ontologies.logging import setup_logging, get_logger

# Setup logging
setup_logging(level='INFO', log_file='pipeline.log')

# Get logger
logger = get_logger('pipeline')

logger.info('Starting pipeline')
logger.error('An error occurred')
```

### Error Handling

#### Exception Classes

```python
from cdm_ontologies.exceptions import (
    PipelineError,
    DownloadError,
    ProcessingError,
    ValidationError
)

try:
    # Pipeline operations
    pipeline.run_all()
except DownloadError as e:
    print(f"Download failed: {e}")
except ProcessingError as e:
    print(f"Processing failed: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Exit Codes

The pipeline uses standard exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Download error |
| 4 | Processing error |
| 5 | Validation error |
| 6 | Out of memory |
| 7 | Permission denied |

## Environment Variables

### Core Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ONTOLOGIES_SOURCE_FILE` | Path to ontology source file | `config/ontologies_source.txt` |
| `DATASET_SIZE` | Dataset size (test/small/large) | `small` |
| `ROBOT_JAVA_ARGS` | Java arguments for ROBOT | `-Xmx16g` |
| `PARALLEL_DOWNLOADS` | Concurrent downloads | `10` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Advanced Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TIMEOUT_SECONDS` | Network timeout | `30` |
| `MAX_RETRIES` | Download retry attempts | `3` |
| `ENABLE_REASONING` | Enable ontological reasoning | `true` |
| `CREATE_VIEWS` | Create database views | `true` |
| `EXPORT_PARQUET` | Export Parquet format | `true` |

## Return Values and Data Structures

### Version Info Structure

```python
{
    "url": "http://purl.obolibrary.org/obo/bfo.owl",
    "current_checksum": "ca399c2b8b79f4d1...",
    "previous_checksum": "b12345678901234...",
    "last_updated": "2025-06-25T00:43:07.708999",
    "size_bytes": 161248,
    "download_attempts": 2,
    "status": "success"
}
```

### Download Result Structure

```python
{
    "filename": "bfo.owl",
    "url": "http://purl.obolibrary.org/obo/bfo.owl",
    "status": "success",  # success, skipped, failed
    "size_bytes": 161248,
    "checksum": "ca399c2b8b79f4d1...",
    "download_time": 2.34,
    "attempts": 1
}
```

### Validation Result Structure

```python
{
    "step": 1,
    "status": "passed",  # passed, failed, warning
    "checks": [
        {
            "name": "File exists",
            "status": "passed",
            "message": "core_ontologies_analysis.json exists"
        }
    ],
    "summary": {
        "passed": 5,
        "failed": 0,
        "warnings": 1
    }
}
```

This API reference provides comprehensive documentation for all interfaces to the CDM Ontologies Pipeline. Use it to integrate the pipeline into your workflows or build custom applications on top of the pipeline infrastructure.