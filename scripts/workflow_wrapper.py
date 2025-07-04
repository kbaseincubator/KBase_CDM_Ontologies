#!/usr/bin/env python3
"""
Wrapper script to run the CDM workflow with proper logging.
This ensures all output is captured to a log file with timestamp matching the output directory.
"""

import sys
import os
import subprocess
from datetime import datetime
import signal
import atexit

def setup_logging(repo_path):
    """Set up logging with timestamp matching output directory."""
    # Determine test mode
    test_mode = 'test' in os.environ.get('ONTOLOGIES_SOURCE_FILE', '').lower()
    
    # Get timestamp from environment or generate new one
    timestamp = os.environ.get('WORKFLOW_TIMESTAMP')
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.environ['WORKFLOW_TIMESTAMP'] = timestamp
    
    # Create log directory
    log_dir = os.path.join(repo_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Determine log file name
    log_type = 'test' if test_mode else 'prod'
    log_file = os.path.join(log_dir, f'cdm_ontologies_{log_type}_{timestamp}.log')
    
    return log_file, timestamp

def run_workflow_with_logging():
    """Run the workflow with output captured to log file."""
    # Get repository path
    repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Set up logging
    log_file, timestamp = setup_logging(repo_path)
    
    print(f"📝 Logging output to: {log_file}")
    print(f"⏰ Timestamp: {timestamp}")
    
    # Prepare the command
    cmd = [sys.executable, '-m', 'cdm_ontologies.cli', 'run-all'] + sys.argv[1:]
    
    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{os.path.join(repo_path, 'scripts')}:{env.get('PYTHONPATH', '')}"
    env['WORKFLOW_TIMESTAMP'] = timestamp
    
    # Open log file
    with open(log_file, 'w') as log:
        # Write header
        log.write(f"CDM Ontologies Workflow Log\n")
        log.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Command: {' '.join(cmd)}\n")
        log.write(f"Environment: {os.environ.get('ONTOLOGIES_SOURCE_FILE', 'default')}\n")
        log.write("=" * 80 + "\n\n")
        log.flush()
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env,
            cwd=repo_path
        )
        
        # Stream output to both console and log file
        try:
            for line in process.stdout:
                # Write to console
                sys.stdout.write(line)
                sys.stdout.flush()
                
                # Write to log file
                log.write(line)
                log.flush()
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nWorkflow interrupted by user")
            log.write("\n\nWorkflow interrupted by user\n")
            process.terminate()
            process.wait()
            return 130  # Standard shell exit code for SIGINT
        
        # Wait for process to complete
        return_code = process.wait()
        
        # Write footer
        log.write("\n" + "=" * 80 + "\n")
        log.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Exit code: {return_code}\n")
        
        if return_code == 0:
            print(f"\n✅ Workflow completed successfully! Log saved to: {log_file}")
        else:
            print(f"\n❌ Workflow failed with exit code {return_code}. Check log: {log_file}")
        
        return return_code

if __name__ == "__main__":
    sys.exit(run_workflow_with_logging())