"""Tests for resource_check module."""

import os
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from resource_check import (
    check_system_resources, get_dataset_size,
    format_bytes, check_disk_space, check_memory
)

class TestResourceCheckHelpers:
    """Test resource check helper functions."""
    
    def test_format_bytes(self):
        """Test byte formatting."""
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
        assert format_bytes(1.5 * 1024 * 1024 * 1024) == "1.5 GB"
        assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.0 TB"
    
    def test_get_dataset_size(self, monkeypatch):
        """Test dataset size detection."""
        # Test mode
        monkeypatch.setenv("DATASET_SIZE", "test")
        assert get_dataset_size() == "test"
        
        # Large mode
        monkeypatch.setenv("DATASET_SIZE", "large")
        assert get_dataset_size() == "large"
        
        # Default
        monkeypatch.delenv("DATASET_SIZE", raising=False)
        assert get_dataset_size() == "large"

class TestDiskSpaceCheck:
    """Test disk space checking."""
    
    def test_check_disk_space_sufficient(self, monkeypatch):
        """Test when sufficient disk space is available."""
        # Mock disk usage
        mock_usage = Mock()
        mock_usage.free = 500 * 1024**3  # 500GB free
        
        monkeypatch.setattr("shutil.disk_usage", lambda path: mock_usage)
        
        success, available, required = check_disk_space("/test/path", 100 * 1024**3)
        
        assert success == True
        assert available == 500 * 1024**3
        assert required == 100 * 1024**3
    
    def test_check_disk_space_insufficient(self, monkeypatch):
        """Test when insufficient disk space."""
        # Mock disk usage
        mock_usage = Mock()
        mock_usage.free = 50 * 1024**3  # 50GB free
        
        monkeypatch.setattr("shutil.disk_usage", lambda path: mock_usage)
        
        success, available, required = check_disk_space("/test/path", 100 * 1024**3)
        
        assert success == False
        assert available == 50 * 1024**3
        assert required == 100 * 1024**3

class TestMemoryCheck:
    """Test memory checking."""
    
    def test_check_memory_sufficient(self, monkeypatch):
        """Test when sufficient memory is available."""
        # Mock memory info
        mock_memory = Mock()
        mock_memory.total = 32 * 1024**3  # 32GB total
        mock_memory.available = 20 * 1024**3  # 20GB available
        
        monkeypatch.setattr("psutil.virtual_memory", lambda: mock_memory)
        
        success, total, available, required = check_memory(8 * 1024**3)
        
        assert success == True
        assert total == 32 * 1024**3
        assert available == 20 * 1024**3
        assert required == 8 * 1024**3
    
    def test_check_memory_insufficient(self, monkeypatch):
        """Test when insufficient memory."""
        # Mock memory info
        mock_memory = Mock()
        mock_memory.total = 16 * 1024**3  # 16GB total
        mock_memory.available = 4 * 1024**3  # 4GB available
        
        monkeypatch.setattr("psutil.virtual_memory", lambda: mock_memory)
        
        success, total, available, required = check_memory(8 * 1024**3)
        
        assert success == False
        assert total == 16 * 1024**3
        assert available == 4 * 1024**3
        assert required == 8 * 1024**3

class TestCheckSystemResources:
    """Test the main system resource check function."""
    
    def test_check_system_resources_test_mode(self, monkeypatch):
        """Test resource check in test mode."""
        # Set test mode
        monkeypatch.setenv("DATASET_SIZE", "test")
        
        # Mock disk and memory checks
        mock_disk_usage = Mock()
        mock_disk_usage.free = 50 * 1024**3  # 50GB free
        
        mock_memory = Mock()
        mock_memory.total = 16 * 1024**3  # 16GB total
        mock_memory.available = 10 * 1024**3  # 10GB available
        
        monkeypatch.setattr("shutil.disk_usage", lambda path: mock_disk_usage)
        monkeypatch.setattr("psutil.virtual_memory", lambda: mock_memory)
        
        success, message = check_system_resources()
        
        assert success == True
        assert "Resources OK for test dataset" in message
    
    def test_check_system_resources_large_mode_success(self, monkeypatch):
        """Test resource check in large mode with sufficient resources."""
        # Set large mode
        monkeypatch.setenv("DATASET_SIZE", "large")
        
        # Mock sufficient resources
        mock_disk_usage = Mock()
        mock_disk_usage.free = 2000 * 1024**3  # 2TB free
        
        mock_memory = Mock()
        mock_memory.total = 2000 * 1024**3  # 2TB total
        mock_memory.available = 1600 * 1024**3  # 1.6TB available
        
        monkeypatch.setattr("shutil.disk_usage", lambda path: mock_disk_usage)
        monkeypatch.setattr("psutil.virtual_memory", lambda: mock_memory)
        
        success, message = check_system_resources()
        
        assert success == True
        assert "Resources OK for large dataset" in message
    
    def test_check_system_resources_insufficient_disk(self, monkeypatch):
        """Test resource check with insufficient disk space."""
        # Set large mode
        monkeypatch.setenv("DATASET_SIZE", "large")
        
        # Mock insufficient disk
        mock_disk_usage = Mock()
        mock_disk_usage.free = 100 * 1024**3  # 100GB free (not enough)
        
        mock_memory = Mock()
        mock_memory.total = 2000 * 1024**3
        mock_memory.available = 1600 * 1024**3
        
        monkeypatch.setattr("shutil.disk_usage", lambda path: mock_disk_usage)
        monkeypatch.setattr("psutil.virtual_memory", lambda: mock_memory)
        
        success, message = check_system_resources()
        
        assert success == False
        assert "Insufficient disk space" in message
    
    def test_check_system_resources_insufficient_memory(self, monkeypatch):
        """Test resource check with insufficient memory."""
        # Set large mode
        monkeypatch.setenv("DATASET_SIZE", "large")
        
        # Mock insufficient memory
        mock_disk_usage = Mock()
        mock_disk_usage.free = 2000 * 1024**3
        
        mock_memory = Mock()
        mock_memory.total = 32 * 1024**3  # 32GB total (not enough)
        mock_memory.available = 20 * 1024**3
        
        monkeypatch.setattr("shutil.disk_usage", lambda path: mock_disk_usage)
        monkeypatch.setattr("psutil.virtual_memory", lambda: mock_memory)
        
        success, message = check_system_resources()
        
        assert success == False
        assert "Insufficient memory" in message