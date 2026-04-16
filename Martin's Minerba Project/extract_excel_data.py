#!/usr/bin/env python3
"""
Extract trade data from Excel files and convert to JSON
"""
import pandas as pd
import json
import os
from pathlib import Path

os.chdir("/Users/martinhutauruk/Downloads/Martin's Minerba Project")

# Define which Excel files map to which data types
excel_mapping = {
    'ekspor indonesia secara nilai (satuan ribu dolar) tiap hs code per tahun.xlsx': 'indonesiaExportValue',
    'ekspor indonesia secara kuantitas (satuan ton) tiap hs code per tahun.xlsx': 'indonesiaExportQty',
    'impor indonesia secara nilai (satuan ribu dolar) tiap hs code per tahun.xlsx': 'indonesiaImportValue',
    'impor indonesia secara kuantitas (satuan ton) tiap hs code per tahun.xlsx': 'indonesiaImportQty',
    'import dunia secara nilai (satuan ribu dolar) tiap hs code per tahun.xlsx': 'worldImportValue',
    'import dunia secara kuantitas (satuan ton) tiap hs code per tahun.xlsx': 'worldImportQty',
    'harga tiap hs code per tahun.xlsx': 'price'
}

# Navigate to Downloads folder where the Excel files are
os.chdir("/Users/martinhutauruk/Downloads")

# HS Codes list from user
hs_codes = [
    '2606', '281810', '281820', '281830', '282530', '282612', '282732', '283322', '321290',
    '7601', '760110', '760120', '7602', '760200', '7603', '760310', '760320',
    '7604', '760410', '760421', '760429', '7605', '760511', '760519', '760521', '760529',
    '7606', '760611', '760612', '760691', '760692', '7607', '760711', '760719', '760720',
    '7608', '760810', '760820', '7609', '760900', '7610', '761010', '761090',
    '7611', '761100', '7612', '761210', '761290', '7613', '761300', '7614', '761410', '761490',
    '7615', '761510', '761511', '761519', '761520', '7616', '761610', '761691', '761699'
]

trade_data = {}

# Initialize data structure for all HS codes
for hs in hs_codes:
    trade_data[f'hs_{hs}'] = {
        'hsCode': hs,
        'data': {}
    }

print("🔍 Reading Excel files...\n")

for excel_file, data_key in excel_mapping.items():
    if not os.path.exists(excel_file):
        print(f"⚠️  File not found: {excel_file}")
        continue
    
    try:
        df = pd.read_excel(excel_file, sheet_name=0)
        print(f"✅ Reading: {excel_file}")
        print(f"   Columns: {df.columns.tolist()}")
        print(f"   Rows: {len(df)}")
        
        # Try to parse the data
        # Assuming first column is HS Code, rest are years with data
        if len(df.columns) > 1:
            # Get years from column headers (typically numeric)
            year_cols = [col for col in df.columns[1:] if isinstance(col, (int, float)) or (isinstance(col, str) and col.isdigit())]
            
            print(f"   Year columns found: {year_cols}\n")
        
    except Exception as e:
        print(f"❌ Error reading {excel_file}: {e}\n")

print("\n📊 Data structure initialized for conversion")
print(f"   Total HS codes: {len(trade_data)}")
print("\nNext: Use the web interface to upload or manually verify data")
