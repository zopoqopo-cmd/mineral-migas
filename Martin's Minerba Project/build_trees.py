#!/usr/bin/env python3
"""
Build new industrialTrees from experiment.xlsx
"""
import pandas as pd
import json
import re

# Read experiment.xlsx
df = pd.read_excel('experiment.xlsx')

# Read price data
price_df = pd.read_excel('harga tiap hs code 2025.xlsx')
price_dict = {}
for _, row in price_df.iterrows():
    hs = str(row['Kode HS']).strip()
    price = row['Harga ($/kg)']
    if pd.notna(price):
        price_dict[hs] = float(price)

# Read trade data
with open('trade_data.json', 'r') as f:
    content = f.read()
json_str = content.replace('// Auto-generated from Excel files', '').replace('const importedTradeData = ', '').replace(';', '').strip()
trade_data = json.loads(json_str)

# Function to parse HS codes from text
def parse_hs_codes(text):
    if pd.isna(text):
        return []
    matches = re.findall(r'\((\d+)\)|\b(\d{4,6})\b', str(text))
    hs_codes = []
    for match in matches:
        hs = match[0] or match[1]
        if len(hs) >= 4:
            hs_codes.append(hs)
    return list(set(hs_codes))

# Build tree for each commodity
industrial_trees = {}

commodities = df['Komoditas'].unique()

for comm in commodities:
    comm_clean = comm.strip().lower().replace(' ', '_')
    comm_df = df[df['Komoditas'] == comm]
    
    nodes = {}
    for _, row in comm_df.iterrows():
        hs = str(row['Kode HS']).strip()
        if hs:
            nodes[hs] = {
                'id': f'hs_{hs}',
                'name': str(row['Nama Senyawa / Barang']).strip(),
                'type': 'unknown',
                'desc': str(row['Nama Senyawa / Barang']).strip(),
                'price': price_dict.get(hs, 0),
                'tradeData': trade_data.get(f'hs_{hs}', {}).get('data', {}),
                'children': []
            }
    
    # Build relationships
    for _, row in comm_df.iterrows():
        hs = str(row['Kode HS']).strip()
        if hs not in nodes:
            continue
            
        children = parse_hs_codes(row['Menghasilkan'])
        for child_hs in children:
            if child_hs in nodes and child_hs != hs:
                if child_hs not in [c['id'].replace('hs_', '') for c in nodes[hs]['children']]:
                    nodes[hs]['children'].append(nodes[child_hs])
    
    # Find root nodes
    roots = []
    for hs, node in nodes.items():
        has_parent = False
        for other_hs, other_node in nodes.items():
            if hs in [c['id'].replace('hs_', '') for c in other_node['children']]:
                has_parent = True
                break
        if not has_parent:
            roots.append(node)
    
    def assign_types(node, level=0):
        if level == 0:
            node['type'] = 'hulu'
        elif level == 1:
            node['type'] = 'antara'
        elif level == 2:
            node['type'] = 'hilir'
        else:
            node['type'] = 'aplikasi'
        
        for child in node['children']:
            assign_types(child, level + 1)
    
    for root in roots:
        assign_types(root)
    
    def add_edge_explanations(node):
        for child in node['children']:
            if node['price'] > 0 and child['price'] > 0:
                ratio = child['price'] / node['price']
                if ratio >= 3:
                    explanation = f"Harga naik {ratio:.1f}x dari {node['name']} (${node['price']:.3f}/kg ke ${child['price']:.3f}/kg)"
                    child['edgeExplanation'] = explanation
            add_edge_explanations(child)
    
    for root in roots:
        add_edge_explanations(root)
    
    industrial_trees[comm_clean] = {
        'title': f'Rantai Nilai {comm.strip()}',
        'desc': f'Hilirisasi komprehensif {comm.strip().lower()}',
        'tree': roots[0] if roots else None
    }

with open('industrial_trees_new.json', 'w') as f:
    json.dump(industrial_trees, f, indent=2, ensure_ascii=False)

print('Generated industrial_trees_new.json')