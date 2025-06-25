#!/bin/bash
# Quick test script to demonstrate the CDM Ontologies Pipeline

set -e  # Exit on any error

echo "🧪 CDM Ontologies Pipeline - Quick Test"
echo "========================================"
echo

# Show help
echo "📚 Available commands:"
make help
echo

# Test CLI help
echo "📚 CLI help:"
python -m cdm_ontologies --help
echo

# Option 1: Run individual steps for testing
echo "🎯 Option 1: Test individual steps with version tracking"
echo "To test each step individually, run:"
echo "  make test-analyze-core           # Download and analyze 9 test ontologies"
echo "  python test_validation.py 1     # Validate step 1 outputs"
echo "  python version_manager.py status # Check version tracking"
echo "  make test-create-base            # Create base versions"
echo "  python test_validation.py 3     # Validate step 3 outputs"
echo "  make test-merge                  # Merge ontologies"
echo "  python test_validation.py 4     # Validate step 4 outputs"
echo "  # ... and so on"
echo

# Option 2: Run complete workflow
echo "🚀 Option 2: Test complete workflow"
echo "To test the complete pipeline:"
echo "  make test-workflow               # Run all steps with test dataset"
echo "  python test_validation.py all   # Validate all outputs"
echo "  python test_validation.py version # Check version tracking"
echo

# Option 3: Docker test
echo "🐳 Option 3: Test with Docker"
echo "To test in Docker environment:"
echo "  make docker-test                 # Run complete workflow in Docker"
echo

# Option 4: Version management
echo "🗂️  Option 4: Version management"
echo "To manage ontology versions:"
echo "  python version_manager.py status    # Show current status"
echo "  python version_manager.py validate  # Verify checksums"
echo "  python version_manager.py history   # Show download log"
echo "  python version_manager.py clean     # Clean old backups"
echo

echo "💡 Tips:"
echo "- Test ontologies are in ontologies_source_test.txt (9 ontologies)"
echo "- Test data isolated in *_test directories (ontology_data_owl_test/, outputs_test/)"
echo "- Version tracking prevents unnecessary re-downloads"
echo "- All downloads logged with checksums and timestamps"
echo "- Memory requirement for test: ~8GB (vs 1TB+ for full dataset)"
echo "- Run test twice to see version tracking skip unchanged files"
echo

echo "🎯 Ready to test! Choose your option above."