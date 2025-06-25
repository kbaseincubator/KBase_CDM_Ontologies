# Version Tracking System

The CDM Ontologies Pipeline includes a sophisticated version tracking system that prevents unnecessary downloads and maintains a complete audit trail of all ontology updates.

## How It Works

### SHA256 Checksums

Instead of relying on timestamps or file sizes, the system uses SHA256 checksums to detect actual content changes:

```python
# When downloading a file
new_checksum = calculate_sha256(downloaded_file)
previous_checksum = get_stored_checksum(filename)

if new_checksum == previous_checksum:
    print("✅ No changes detected - skipping")
else:
    print("🔄 Content changed - updating")
```

### Automatic Backup System

Before updating any file, the system automatically creates a backup:

```
ontology_versions[_test]/backups/
├── bfo.owl.2025-06-24T23:45:12.backup      # Previous version
├── iao.owl.2025-06-24T23:45:15.backup      # With timestamp
└── checksums.json                          # Backup checksums
```

## Version Registry

### Master Version File

The `ontology_versions.json` file tracks all ontologies:

```json
{
  "bfo.owl": {
    "url": "http://purl.obolibrary.org/obo/bfo.owl",
    "current_checksum": "ca399c2b8b79f4d1a23e4567890abcdef1234567",
    "previous_checksum": "b12345678901234567890abcdef1234567890abc",
    "last_updated": "2025-06-25T00:43:07.708999",
    "size_bytes": 161248,
    "download_attempts": 2,
    "status": "success"
  }
}
```

### Download History

The `download_history.log` provides a complete audit trail:

```
2025-06-25T00:43:07 | bfo.owl | SUCCESS | NEW | Size: 158KB | Checksum: ca399c2b...
2025-06-25T00:52:15 | bfo.owl | SKIPPED | NO_CHANGE | Checksum matches: ca399c2b...
2025-06-25T01:15:22 | bfo.owl | SUCCESS | UPDATED | Size: 162KB | New checksum: d4567890...
```

## Using the Version Manager

### Check Current Status

```bash
# Show status of all tracked ontologies
python version_manager.py status

# Example output:
# 📊 Ontology Version Status (TEST mode)
# 
# ✅ bfo.owl - Current (158 KB)
# ✅ iao.owl - Current (590 KB)
# 🔄 envo.owl - Update available (9.9 MB → 10.2 MB)
# ⚠️  credit.owl - Checksum mismatch
```

### Validate File Integrity

```bash
# Check all files match their stored checksums
python version_manager.py validate

# Example output:
# 🔍 Validating 9 ontology files...
# ✅ bfo.owl - Checksum valid
# ✅ iao.owl - Checksum valid
# ❌ envo.owl - Checksum mismatch! File may be corrupted.
```

### View Download History

```bash
# Show complete download history
python version_manager.py history

# Show only recent entries
python version_manager.py history --limit 10

# Show history for specific ontology
python version_manager.py history --ontology bfo.owl
```

### Generate Detailed Report

```bash
# Create comprehensive version report
python version_manager.py report

# Creates version_report.md with full details
```

### Clean Old Backups

```bash
# Remove old backups (keep 3 most recent)
python version_manager.py clean --keep 3

# Remove all backups (dangerous!)
python version_manager.py clean --all
```

## Test vs Production Environments

The version tracking system automatically handles multiple environments:

### Test Environment
- Files: `ontology_versions_test/ontology_versions.json`
- Backups: `ontology_versions_test/backups/`
- 9 curated ontologies

### Production Environment
- Files: `ontology_versions/ontology_versions.json`
- Backups: `ontology_versions/backups/`
- 30+ ontologies

### Environment Detection

```bash
# Automatically detects environment from source file
ONTOLOGIES_SOURCE_FILE=ontologies_source_test.txt python version_manager.py status
# Uses test environment

ONTOLOGIES_SOURCE_FILE=ontologies_source.txt python version_manager.py status
# Uses production environment
```

## Version Tracking in Pipeline

### During Download Process

```python
def download_with_version_tracking(url, filename):
    # 1. Check if file exists and get current checksum
    current_checksum = get_current_checksum(filename)
    
    # 2. Download to temporary location
    temp_file = download_to_temp(url)
    new_checksum = calculate_sha256(temp_file)
    
    # 3. Compare checksums
    if new_checksum == current_checksum:
        log("✅ No changes detected - skipping")
        return "skipped"
    
    # 4. Backup existing file
    if file_exists(filename):
        create_backup(filename, current_checksum)
    
    # 5. Move new file and update registry
    move_file(temp_file, filename)
    update_version_registry(filename, new_checksum, url)
    
    return "updated"
```

### Pipeline Integration

All download scripts automatically use version tracking:

- `enhanced_download.py` - Main download function
- `analyze_core_ontologies.py` - Core ontology downloads
- `analyze_non_core_ontologies.py` - Additional ontology downloads

## Benefits

### Efficiency
- **Skip unchanged files**: Avoid downloading identical content
- **Parallel processing**: Track multiple downloads simultaneously
- **Retry logic**: Handle network issues gracefully

### Reliability
- **Backup system**: Never lose previous versions
- **Integrity validation**: Detect file corruption
- **Complete audit trail**: Track all changes over time

### Maintenance
- **Automated cleanup**: Remove old backups based on policy
- **Status monitoring**: Easy overview of current state
- **Detailed reporting**: Generate comprehensive version reports

## Advanced Usage

### Custom Backup Retention

```bash
# Keep 5 most recent backups
python version_manager.py clean --keep 5

# Keep backups from last 30 days
python version_manager.py clean --days 30
```

### Selective Updates

```bash
# Force re-download specific ontology
python version_manager.py force-update bfo.owl

# Update only if size changed significantly
python version_manager.py update --size-threshold 1MB
```

### Integration with CI/CD

```bash
# Check if any ontologies have updates available
if python version_manager.py check-updates --exit-code; then
    echo "Updates available - running pipeline"
    make run-workflow
else
    echo "No updates - skipping pipeline"
fi
```

## Troubleshooting

### Checksum Mismatches

```bash
# Validate specific file
python version_manager.py validate --ontology bfo.owl

# Re-download corrupted file
rm ontology_data_owl/bfo.owl
make analyze-core
```

### Missing Version Data

```bash
# Rebuild version registry from existing files
python version_manager.py rebuild-registry

# Initialize version tracking for new files
python version_manager.py init
```

### Backup Recovery

```bash
# List available backups
python version_manager.py list-backups bfo.owl

# Restore from backup
python version_manager.py restore bfo.owl 2025-06-24T23:45:12
```

## Implementation Details

The version tracking system consists of:

- **`version_tracker.py`**: Core tracking functionality
- **`enhanced_download.py`**: Download with version integration
- **`version_manager.py`**: CLI tool for management
- **JSON registry**: Structured version data
- **Log files**: Human-readable audit trail
- **Backup system**: Automatic file preservation

This system ensures that the CDM Ontologies Pipeline only processes ontologies that have actually changed, making it efficient for regular updates while maintaining complete traceability of all changes.