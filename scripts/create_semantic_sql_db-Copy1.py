import sys
import os
import subprocess
import traceback
from pathlib import Path

def create_semantic_sql_db(
    repo_path: str,
    input_owl_filename: str = 'CDM_merged_ontologies.owl'
) -> bool:
    """
    Create a semantic SQL database from the merged ontologies OWL file.
    """
    try:
        base_dir = "/home/jplfaria/scratch/install_stuff"
        sqlite_path = "/scratch/jplfaria/bin/sqlite3"
        semsql_path = f"{base_dir}/semsql/bin/semsql"
        
        # Set up environment variables
        os.environ['PATH'] = f"/scratch/jplfaria/bin:{os.environ.get('PATH', '')}"
        os.environ['PYTHONPATH'] = f"{base_dir}/semsql:{os.environ.get('PYTHONPATH', '')}"
        os.environ['JAVA_OPTS'] = "-Xmx4000G"
        
        # Set working directory
        outputs_dir = os.path.join(repo_path, 'outputs')
        os.makedirs(outputs_dir, exist_ok=True)
        os.chdir(outputs_dir)
        
        db_filename = input_owl_filename.replace('.owl', '.db')
        
        print(f"Input OWL file: {input_owl_filename}")
        print(f"Output DB file: {db_filename}")
        print(f"Working directory: {outputs_dir}")
        
        # Add the sqlite3 path to the command environment
        cmd = f"""
        export PATH="/scratch/jplfaria/bin:$PATH"
        source {base_dir}/setup_oak_env.sh
        {semsql_path} make {db_filename}
        """
        
        print("\nExecuting command:")
        print(cmd)
        
        result = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True)
        
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
            
        return not bool(result.stderr)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    repo_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    create_semantic_sql_db(repo_path)