#!/usr/bin/env python3
"""
Extract trade data from Excel files and convert to JavaScript JSON format
"""
import pandas as pd
import json
import os

os.chdir("/Users/martinhutauruk/Downloads")

# HS Codes from user's aluminum, nickel, copper, tin, silica list
all_hs_codes = {
    # Aluminum
    '2606', '281810', '281820', '281830', '282530', '282612', '282732', '283322', '321290',
    '7601', '760110', '760120', '7602', '760200', '7603', '760310', '760320',
    '7604', '760410', '760421', '760429', '7605', '760511', '760519', '760521', '760529',
    '7606', '760611', '760612', '760691', '760692', '7607', '760711', '760719', '760720',
    '7608', '760810', '760820', '7609', '760900', '7610', '761010', '761090',
    '7611', '761100', '7612', '761210', '761290', '7613', '761300', '7614', '761410', '761490',
    '7615', '761510', '761511', '761519', '761520', '7616', '761610', '761691', '761699',
    # Nickel
    '2604', '7501', '7502', '7503', '7504', '7505', '7506', '7507', '7508',
    '282540', '283324', '750110', '750120', '750210', '750220',
    '750511', '750512', '750521', '750522', '750610', '750620', '750810', '750890',
    '850730', '850740', '850750', '850760', '720260',
    '750711', '750712', '750720',
    # Copper
    '2603', '7401', '7402', '7403', '7404', '7405', '7406', '7407', '7408',
    '7409', '7410', '7411', '7412', '7413', '7415', '7418', '7419',
    '262030', '282550', '282741', '283325', '854411',
    '740100', '740110', '740120', '740311', '740312', '740313', '740319',
    '740321', '740322', '740323', '740329', '740400', '740500',
    '740610', '740620', '740711', '740721', '740722', '740729',
    '740811', '740819', '740821', '740822', '740829',
    '740911', '740919', '740921', '740929', '740931', '740939', '740940', '740990',
    '741011', '741012', '741021', '741022',
    '741110', '741121', '741122', '741129',
    '741210', '741220', '741300', '741420', '741490',
    '741510', '741521', '741529', '741531', '741532', '741533', '741539',
    '741600', '741700', '741810', '741811', '741819', '741820',
    '741910', '741920', '741980', '741991', '741999',
    # Tin
    '2609', '8001', '8002', '8003', '8004', '8005', '8006', '8007',
    '260900', '800110', '800120', '800200', '800300', '800400', '800500', '800600', '800700',
    # Silica
    '250510', '250590', '250610', '250620', '251200', '251710', '281122', '381800',
    '690220', '7001', '700100', '7005', '701090', '7019', '701911',
    '7202', '720221', '720229', '854231', '900190'
}

trade_data = {}

print("🔍 Reading Excel files from /Users/martinhutauruk/Downloads/\n")

# Read each Excel file
excel_files = {
    'ekspor indonesia secara nilai (satuan ribu dolar) tiap hs code per tahun.xlsx': 'indonesiaExportValue',
    'ekspor indonesia secara kuantitas (satuan ton) tiap hs code per tahun.xlsx': 'indonesiaExportQty',
    'impor indonesia secara nilai (satuan ribu dolar) tiap hs code per tahun.xlsx': 'indonesiaImportValue',
    'impor indonesia secara kuantitas (satuan ton) tiap hs code per tahun.xlsx': 'indonesiaImportQty',
    'import dunia secara nilai (satuan ribu dolar) tiap hs code per tahun.xlsx': 'worldImportValue',
    'import dunia secara kuantitas (satuan ton) tiap hs code per tahun.xlsx': 'worldImportQty',
}

for file_name, data_type in excel_files.items():
    if not os.path.exists(file_name):
        print(f"⚠️  {file_name} not found")
        continue
    
    try:
        df = pd.read_excel(file_name, sheet_name=0, header=None)
        print(f"✅ {file_name}")
        print(f"   Rows: {len(df)}, Columns: {len(df.columns)}")
        
        # Try to get year headers from first or second row
        header_row = None
        for row_idx in [0, 1]:
            if row_idx < len(df):
                potential_header = df.iloc[row_idx]
                # Check if this row contains year-like values
                year_values = [col for col in potential_header if isinstance(col, (int, float)) or (isinstance(col, str) and col.isdigit() and 2000 <= int(col) <= 2030)]
                if len(year_values) > 0:
                    header_row = row_idx
                    break
        
        if header_row is not None:
            df_data = df.iloc[header_row:].reset_index(drop=True)
            df_data.columns = df_data.iloc[0]
            df_data = df_data.iloc[1:].reset_index(drop=True)
            
            print(f"   Years detected: {list(df_data.columns[1:])[:5]}...")
            
            # Extract data for HS codes we need
            for hs_code in all_hs_codes:
                hs_key = f'hs_{hs_code}'
                # Initialize data structure if not exists
                if hs_key not in trade_data:
                    trade_data[hs_key] = {
                        'hsCode': hs_code,
                        'data': {}
                    }
                
                # Find matching row for this HS code
                matching_rows = df_data[df_data[df_data.columns[0]].astype(str) == hs_code]
                if len(matching_rows) > 0:
                    row_data = matching_rows.iloc[0]
                    # Extract year values
                    values = []
                    for col in df_data.columns[1:]:
                        try:
                            val = float(row_data[col]) if pd.notna(row_data[col]) else 0
                            values.append(round(val, 2))
                        except:
                            values.append(0)
                    
                    if len(values) > 0:
                        trade_data[hs_key]['data'][data_type] = values
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}\n")

# Save to JSON file
output_file = "/Users/martinhutauruk/Downloads/Martin's Minerba Project/trade_data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    # Output as JavaScript constant
    f.write("// Auto-generated trade data from Excel files\n")
    f.write("const importedTradeData = ")
    json.dump(trade_data, f, indent=2, ensure_ascii=False)
    f.write(";\n")

print(f"\n✨ Data exported to: {output_file}")
print(f"   Total HS codes with data: {len(trade_data)}")
print(f"   Total HS codes expected: {len(all_hs_codes)}")

# Show sample
sample_key = list(trade_data.keys())[0]
print(f"\n📋 Sample (first HS code):")
print(f"   Key: {sample_key}")
print(f"   Data: {trade_data[sample_key]}")
