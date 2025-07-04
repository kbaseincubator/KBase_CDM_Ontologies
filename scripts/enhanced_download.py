"""
Enhanced download functionality with version tracking and robust error handling.
"""

import os
import requests
import gzip
import shutil
import time
from datetime import datetime
from urllib.parse import urlparse
from version_tracker import (
    should_download, get_file_checksum, backup_old_version,
    log_download_attempt, update_version_info, load_version_info
)


def get_output_directories(repo_path, test_mode=False):
    """Get appropriate output directories based on test mode."""
    # Check if we're in a workflow with a pre-created output directory
    workflow_output_dir = os.environ.get('WORKFLOW_OUTPUT_DIR')
    
    if workflow_output_dir:
        # Use the provided workflow output directory
        outputs_path = workflow_output_dir
        outputs_base = os.path.dirname(outputs_path)
    else:
        # Generate timestamp for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if test_mode:
            outputs_base = os.path.join(repo_path, 'outputs_test')
            outputs_path = os.path.join(outputs_base, f'run_{timestamp}')
        else:
            outputs_base = os.path.join(repo_path, 'outputs')
            outputs_path = os.path.join(outputs_base, f'run_{timestamp}')
        
        # Create the timestamped run directory
        os.makedirs(outputs_base, exist_ok=True)
        os.makedirs(outputs_path, exist_ok=True)
        
        # Create a symlink to the latest run for convenience
        latest_link = os.path.join(outputs_base, 'latest')
        if os.path.islink(latest_link):
            os.unlink(latest_link)
        elif os.path.exists(latest_link):
            # If it's not a symlink but exists, remove it
            if os.path.isdir(latest_link):
                shutil.rmtree(latest_link)
            else:
                os.remove(latest_link)
        os.symlink(os.path.basename(outputs_path), latest_link)
    
    # Set up other directories
    if test_mode:
        ontology_data_path = os.path.join(repo_path, 'ontology_data_owl_test')
        non_base_dir = os.path.join(ontology_data_path, 'non-base-ontologies')
        version_dir = os.path.join(repo_path, 'ontology_versions_test')
    else:
        ontology_data_path = os.path.join(repo_path, 'ontology_data_owl')
        non_base_dir = os.path.join(ontology_data_path, 'non-base-ontologies')
        version_dir = os.path.join(repo_path, 'ontology_versions')
    
    # Create directories
    os.makedirs(ontology_data_path, exist_ok=True)
    os.makedirs(non_base_dir, exist_ok=True)
    os.makedirs(version_dir, exist_ok=True)
    
    return ontology_data_path, non_base_dir, outputs_path, version_dir


def is_test_mode():
    """Check if we're in test mode based on environment variables."""
    source_file = os.environ.get('ONTOLOGIES_SOURCE_FILE', 'ontologies_source.txt')
    return 'test' in source_file.lower()


def download_with_retry(url, max_retries=3, timeout=30):
    """Download with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⚠️  Attempt {attempt + 1} failed for {url}, retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)
            else:
                raise e


def handle_compressed_file(response, output_path, url):
    """Handle compressed (.gz) file downloads."""
    if url.endswith('.gz'):
        # If output_path ends with .gz, remove it for the decompressed file
        if output_path.endswith('.gz'):
            decompressed_path = output_path[:-3]  # Remove .gz extension
        else:
            decompressed_path = output_path
            
        # Save compressed file temporarily
        gz_path = decompressed_path + '.gz'
        with open(gz_path, 'wb') as f:
            f.write(response.content)
        
        # Decompress
        with gzip.open(gz_path, 'rb') as f_in:
            with open(decompressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove compressed file
        os.remove(gz_path)
        print(f"✅ Downloaded and decompressed: {os.path.basename(decompressed_path)}")
    else:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded: {os.path.basename(output_path)}")


def download_ontology_with_versioning(url, output_path, repo_path, force_download=False):
    """
    Download ontology with comprehensive version tracking.
    
    Args:
        url: URL to download from
        output_path: Where to save the file
        repo_path: Repository root path
        force_download: Skip version checks and force download
    
    Returns:
        tuple: (success: bool, status: str, message: str)
    """
    test_mode = is_test_mode()
    _, _, _, version_dir = get_output_directories(repo_path, test_mode)
    version_file = os.path.join(version_dir, 'ontology_versions.json')
    
    filename = os.path.basename(output_path)
    
    try:
        # Check if download is needed (unless forced)
        if not force_download:
            needs_download, reason = should_download(output_path, url, version_file)
            if not needs_download:
                log_download_attempt(version_dir, filename, "skipped", None, url)
                return True, "skipped", f"File up to date: {filename}"
        
        # Get current checksum if file exists
        old_checksum = None
        if os.path.exists(output_path):
            old_checksum = get_file_checksum(output_path)
            backup_old_version(output_path, old_checksum, version_dir)
        
        # Download with retry logic
        print(f"📥 Downloading {filename}...")
        response = download_with_retry(url)
        
        # Calculate new checksum
        new_checksum = get_file_checksum(response.content)
        
        # Check if content actually changed
        if old_checksum == new_checksum and not force_download:
            log_download_attempt(version_dir, filename, "no_change", old_checksum, url)
            return True, "no_change", f"No changes detected: {filename}"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Handle compressed files
        if isinstance(response.content, bytes):
            # Create a mock response object for handle_compressed_file
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            
            handle_compressed_file(MockResponse(response.content), output_path, url)
        else:
            handle_compressed_file(response, output_path, url)
        
        # Update version tracking
        update_version_info(version_file, filename, url, old_checksum, new_checksum)
        
        # Log successful download
        status = "updated" if old_checksum else "new"
        log_download_attempt(version_dir, filename, status, new_checksum, url)
        
        return True, status, f"Successfully downloaded: {filename}"
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error downloading {filename}: {str(e)}"
        log_download_attempt(version_dir, filename, "error", None, url, str(e))
        return False, "error", error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error downloading {filename}: {str(e)}"
        log_download_attempt(version_dir, filename, "error", None, url, str(e))
        return False, "error", error_msg


def download_ontology_safe(url, output_path, repo_path, force_download=False):
    """
    Safe wrapper for ontology download that handles known problematic URLs.
    
    Returns:
        bool: True if successful, False if failed
    """
    # Known problematic ontologies to skip
    problematic_patterns = ['cp.owl', 'has.owl', 'is.owl', 'apollo.owl']
    
    filename = os.path.basename(output_path)
    if any(pattern in filename for pattern in problematic_patterns):
        print(f"⚠️  Skipping known problematic ontology: {filename}")
        return False
    
    success, status, message = download_ontology_with_versioning(
        url, output_path, repo_path, force_download
    )
    
    if success:
        if status != "skipped":
            print(f"   {message}")
    else:
        print(f"❌ {message}")
    
    return success


def get_file_checksum(content_or_path):
    """Calculate checksum from file content or file path."""
    import hashlib
    
    sha256_hash = hashlib.sha256()
    
    if isinstance(content_or_path, (bytes, bytearray)):
        # Content bytes
        sha256_hash.update(content_or_path)
    else:
        # File path
        with open(content_or_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()