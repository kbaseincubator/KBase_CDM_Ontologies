"""Tests for create_semantic_sql_db module."""

import os
import pytest
from pathlib import Path
import sys
import sqlite3

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from create_semantic_sql_db import create_semantic_sql_db

# Helper functions tests removed - functions don't exist in the actual module

class TestCreateSemanticSQLDB:
    """Test the main create_semantic_sql_db function."""
    
    def test_create_db_test_mode(self, temp_repo, mock_environment, monkeypatch):
        """Test database creation in test mode."""
        # Mock semsql command
        def mock_run(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('args', [])
            if isinstance(cmd, list) and 'semsql' in str(cmd):
                # Find output database file
                for i, arg in enumerate(cmd):
                    if arg == 'make' and i + 1 < len(cmd):
                        db_file = cmd[i + 1]
                        # Create a minimal SQLite database
                        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
                        conn = sqlite3.connect(db_file)
                        conn.execute("CREATE TABLE test (id INTEGER)")
                        conn.close()
            
            class MockResult:
                returncode = 0
                stdout = b"Success"
                stderr = b""
            return MockResult()
        
        monkeypatch.setattr("subprocess.run", mock_run)
        
        # Create merged OWL file
        outputs_dir = temp_repo / "outputs_test"
        outputs_dir.mkdir(exist_ok=True)
        owl_file = outputs_dir / "cdm-ontology.simple.robot.owl"
        owl_file.write_text('<?xml version="1.0"?><rdf:RDF></rdf:RDF>')
        
        # Run database creation
        result = create_semantic_sql_db(str(temp_repo))
        assert result == True
        
        # Check database was created
        db_file = outputs_dir / "cdm-ontology.simple.semsql.db"
        assert db_file.exists()
    
    def test_create_db_missing_owl_file(self, temp_repo, mock_environment, monkeypatch):
        """Test database creation fails when OWL file is missing."""
        # Run without creating OWL file
        result = create_semantic_sql_db(str(temp_repo))
        assert result == False
    
    def test_create_db_with_prefixes(self, temp_repo, mock_environment, monkeypatch):
        """Test database creation with custom prefixes."""
        # Mock semsql command
        executed_commands = []
        
        def mock_run(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('args', [])
            executed_commands.append(cmd)
            
            if isinstance(cmd, list) and 'semsql' in str(cmd):
                # Check for prefix arguments
                assert any('--prefix' in str(arg) for arg in cmd)
                
                # Create dummy database
                for i, arg in enumerate(cmd):
                    if arg == 'make' and i + 1 < len(cmd):
                        db_file = cmd[i + 1]
                        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
                        conn = sqlite3.connect(db_file)
                        conn.execute("CREATE TABLE test (id INTEGER)")
                        conn.close()
            
            class MockResult:
                returncode = 0
            return MockResult()
        
        monkeypatch.setattr("subprocess.run", mock_run)
        
        # Create prefix files
        prefix_dir = temp_repo / "semsql_custom_prefixes"
        prefix_dir.mkdir()
        (prefix_dir / "prefixes.csv").write_text("GO,http://purl.obolibrary.org/obo/GO_")
        
        # Create OWL file
        outputs_dir = temp_repo / "outputs_test"
        outputs_dir.mkdir(exist_ok=True)
        owl_file = outputs_dir / "cdm-ontology.simple.robot.owl"
        owl_file.write_text('<?xml version="1.0"?><rdf:RDF></rdf:RDF>')
        
        # Run database creation
        result = create_semantic_sql_db(str(temp_repo))
        assert result == True
        
        # Verify prefix was included in command
        assert len(executed_commands) > 0
    
    def test_create_db_command_failure(self, temp_repo, mock_environment, monkeypatch):
        """Test handling of semsql command failure."""
        def mock_run_fail(*args, **kwargs):
            class MockResult:
                returncode = 1
                stdout = b"Error output"
                stderr = b"Error occurred"
            return MockResult()
        
        monkeypatch.setattr("subprocess.run", mock_run_fail)
        monkeypatch.setattr("create_semantic_sql_db.check_semsql_installation", lambda: True)
        
        # Create OWL file
        outputs_dir = temp_repo / "outputs_test"
        outputs_dir.mkdir(exist_ok=True)
        owl_file = outputs_dir / "cdm-ontology.simple.robot.owl"
        owl_file.write_text('<?xml version="1.0"?><rdf:RDF></rdf:RDF>')
        
        # Run database creation
        result = create_semantic_sql_db(str(temp_repo))
        assert result == False