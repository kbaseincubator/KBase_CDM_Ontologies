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
        semsql_lib_dir = f"{base_dir}/semsql/lib"
        
        # Set up environment variables
        os.environ['PATH'] = f"/scratch/jplfaria/bin:{os.environ.get('PATH', '')}"
        os.environ['PYTHONPATH'] = f"{base_dir}/semsql:{os.environ.get('PYTHONPATH', '')}"
        
        # Set CLASSPATH more explicitly
        classpath_items = []
        for jar_file in os.listdir(semsql_lib_dir):
            if jar_file.endswith('.jar'):
                classpath_items.append(os.path.join(semsql_lib_dir, jar_file))
        
        os.environ['CLASSPATH'] = f"{':'.join(classpath_items)}"
        os.environ['JAVA_OPTS'] = "-Xmx4000G"
        
        # Set working directory
        outputs_dir = os.path.join(repo_path, 'outputs')
        os.makedirs(outputs_dir, exist_ok=True)
        os.chdir(outputs_dir)
        
        db_filename = input_owl_filename.replace('.owl', '.db')
        
        print(f"Input OWL file: {input_owl_filename}")
        print(f"Output DB file: {db_filename}")
        print(f"Working directory: {outputs_dir}")
        print(f"CLASSPATH: {os.environ['CLASSPATH']}")
        
        # Modified command to include explicit classpath setup
        cmd = f"""
        export PATH="/scratch/jplfaria/bin:$PATH"
        source {base_dir}/setup_oak_env.sh
        export CLASSPATH="{':'.join(classpath_items)}:$CLASSPATH"
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