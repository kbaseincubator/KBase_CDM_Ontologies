import os
import sqlite3
import pandas as pd
import traceback
from pathlib import Path
from enhanced_download import get_output_directories, is_test_mode

def create_parquet_files(repo_path: str) -> bool:
    """
    Export all tables from the CDM_merged_ontologies.db database to Parquet files.
    
    Args:
        repo_path (str): Path to the repository root directory
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        # Setup paths - support test configuration
        test_mode = is_test_mode()
        ontology_data_path, _, outputs_path, version_dir = get_output_directories(repo_path, test_mode)
        
        outputs_dir = outputs_path
        db_file = os.path.join(outputs_dir, 'CDM_merged_ontologies.db')
        parquet_dir = os.path.join(outputs_dir, 'parquet_files')
        
        print(f"🔧 Mode: {'TEST' if test_mode else 'PRODUCTION'}")
        print(f"📁 Database file: {db_file}")
        print(f"📁 Parquet output directory: {parquet_dir}")
        
        # Verify database file exists
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"Database file not found: {db_file}")
        
        # Create parquet output directory
        os.makedirs(parquet_dir, exist_ok=True)
        
        print(f"\n📖 Reading database from: {db_file}")
        print(f"💾 Saving Parquet files to: {parquet_dir}")
        
        # Connect to database
        conn = sqlite3.connect(db_file)
        
        # Get list of all tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        tables_df = pd.read_sql(tables_query, conn)
        table_names = tables_df['name'].tolist()
        
        print(f"\n📋 Found {len(table_names)} tables to export:")
        
        total_files = 0
        total_size = 0
        
        for table_name in table_names:
            try:
                print(f"Processing table: {table_name}")
                
                # Read table data
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                
                # Define output file path
                parquet_file = os.path.join(parquet_dir, f"{table_name}.parquet")
                
                # Save as Parquet
                df.to_parquet(parquet_file, index=False, compression='snappy')
                
                # Get file size for reporting
                file_size = os.path.getsize(parquet_file)
                total_size += file_size
                total_files += 1
                
                print(f"✅ Exported '{table_name}' to '{parquet_file}'")
                print(f"   📊 {len(df):,} rows, {len(df.columns)} columns, {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
                
            except Exception as table_error:
                print(f"⚠️ Error processing table '{table_name}': {str(table_error)}")
                continue
        
        conn.close()
        
        print(f"\n✅ Export completed successfully!")
        print(f"📁 Created {total_files} Parquet files")
        print(f"📏 Total size: {total_size:,} bytes ({total_size / (1024*1024):.1f} MB)")
        print(f"📂 Files saved in: {parquet_dir}")
        
        # Show compression comparison if TSV directory exists
        tsv_dir = os.path.join(outputs_dir, 'tsv_tables')
        if os.path.exists(tsv_dir):
            try:
                # Calculate TSV directory size
                tsv_size = sum(os.path.getsize(os.path.join(tsv_dir, f)) 
                             for f in os.listdir(tsv_dir) 
                             if os.path.isfile(os.path.join(tsv_dir, f)))
                
                compression_ratio = (tsv_size - total_size) / tsv_size * 100
                print(f"\n📊 Compression Analysis:")
                print(f"   TSV files: {tsv_size:,} bytes ({tsv_size / (1024*1024):.1f} MB)")
                print(f"   Parquet files: {total_size:,} bytes ({total_size / (1024*1024):.1f} MB)")
                print(f"   Space saved: {compression_ratio:.1f}% ({(tsv_size - total_size) / (1024*1024):.1f} MB)")
                
            except Exception as comp_error:
                print(f"📊 Could not calculate compression ratio: {str(comp_error)}")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Error occurred: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    repo_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    success = create_parquet_files(repo_path)
    if success:
        print("\n🎉 Parquet export completed successfully!")
    else:
        print("\n💥 Parquet export failed!")
        exit(1)