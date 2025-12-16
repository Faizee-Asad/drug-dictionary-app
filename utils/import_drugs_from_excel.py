#!/usr/bin/env python3
"""
Drug Dictionary Excel Import Script
==================================

This script imports drug data from Excel files into the Drug Dictionary database.
It expects Excel files with 'Brand Name' and 'Manufacturer' columns.

Usage:
    python import_drugs_from_excel.py <path_to_excel_file.xlsx>

Example:
    python import_drugs_from_excel.py Book2.xlsx
"""

import pandas as pd
import sqlite3
import sys
import os
from datetime import datetime

def import_excel_to_database(excel_file_path):
    """
    Import drug data from Excel file to database.
    
    Args:
        excel_file_path (str): Path to the Excel file
        
    Returns:
        tuple: (success_count, total_rows, error_count)
    """
    # Validate input file
    if not os.path.exists(excel_file_path):
        print(f"Error: File '{excel_file_path}' not found.")
        return 0, 0, 1
    
    if not excel_file_path.endswith(('.xlsx', '.xls')):
        print(f"Error: File must be an Excel file (.xlsx or .xls)")
        return 0, 0, 1

    try:
        # Read the Excel file
        print(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        print(f"Excel file information:")
        print(f"  - Number of rows: {len(df)}")
        print(f"  - Column names: {df.columns.tolist()}")
        
        # Validate required columns
        required_columns = ['Brand Name', 'Manufacturer']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            print(f"Required columns: {required_columns}")
            print(f"Found columns: {df.columns.tolist()}")
            return 0, len(df), 1
        
        # Connect to the database
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'drug_dictionary.db')
        if not os.path.exists(db_path):
            print(f"Error: Database file not found at {db_path}")
            return 0, len(df), 1
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current record count
        cursor.execute("SELECT COUNT(*) FROM drug_dictionary")
        initial_count = cursor.fetchone()[0]
        print(f"Current database record count: {initial_count}")
        
        # Process the data and insert into database
        print("\nStarting data import...")
        
        # Counters
        success_count = 0
        error_count = 0
        
        # Process each row
        for index, row in df.iterrows():
            try:
                brand_name = row['Brand Name'].strip() if pd.notna(row['Brand Name']) else None
                manufacturer = row['Manufacturer'].strip() if pd.notna(row['Manufacturer']) else "N/A"
                
                # Only insert if we have a brand name
                if brand_name:
                    # Insert into database
                    cursor.execute("""
                        INSERT INTO drug_dictionary 
                        (brand_name, manufacturer, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (
                        brand_name,
                        manufacturer,
                        datetime.now(),
                        datetime.now()
                    ))
                    success_count += 1
                    
                    # Print progress every 100 records
                    if success_count % 100 == 0:
                        print(f"  Imported {success_count} records...")
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"Error inserting row {index}: {e}")
        
        # Commit changes
        conn.commit()
        
        # Check final record count
        cursor.execute("SELECT COUNT(*) FROM drug_dictionary")
        final_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"\nImport Summary:")
        print(f"  - Successfully imported: {success_count} records")
        print(f"  - Errors encountered: {error_count}")
        print(f"  - Initial database count: {initial_count}")
        print(f"  - Final database count: {final_count}")
        print(f"  - Net increase: {final_count - initial_count} records")
        
        return success_count, len(df), error_count
        
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return 0, 0, 1

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python import_drugs_from_excel.py <path_to_excel_file.xlsx>")
        print("Example: python import_drugs_from_excel.py Book2.xlsx")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    success_count, total_rows, error_count = import_excel_to_database(excel_file_path)
    
    if success_count > 0:
        print(f"\n✅ Import completed successfully!")
        print(f"   Imported {success_count} out of {total_rows} rows from {excel_file_path}")
    else:
        print(f"\n❌ Import failed with {error_count} errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()