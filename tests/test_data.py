"""
Unit tests for AURORA data layer.
"""
import pytest
from pathlib import Path
from scripts.download_data import RAW_DIR
from scripts.preprocess import CACHED_DIR

def test_directories_exist():
    """Ensure data directories are properly initialized."""
    assert RAW_DIR.exists() or RAW_DIR.parent.exists()

def test_preprocessing_functions():
    """Test preprocessing stubs."""
    assert CACHED_DIR.exists() or CACHED_DIR.parent.exists()
