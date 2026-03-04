import os
from bs4 import BeautifulSoup
import networkx as nx
from pyvis.network import Network

ROOT_DIR = "." # Run from ~/isrl/isrl-research.github.io/
BASE_URL_PATH = "/ifid/ency/"

def build_optimized_graph():
    # 1. THE INDEX: Map of { filename : full_rel_path }
    # Example: { 'apple.html': 'ency/fruits-veg-botanicals/apple.html' }
    file_index = {}
    all_html_files = []
    
    print("Indexing files...")
    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".html"):
                rel_path = os.path.relpath(os.path.join(root, file), ROOT_DIR).replace("\\", "/")
                file_index[file] = rel_path
                all_html_files.append(rel_path)

    # 2. THE SCAN: Parse each file ONCE and extract <main> links
    G = nx.DiGraph()
    print(f"Scanning {len(all_html_files)} files for links...")
    
    for source_node in all_html_files:
        G.add_node(source_node, label=os.path.basename(source_node))
        
        full_path = os.path.join(ROOT_DIR, source_node)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'lxml') # 'lxml' is faster than 'html.parser'
                main_content = soup.find('main')
                
                if main_content:
                    for a in main_content.find_all('a', href=True):
                        href = a['href']
                        # Extract the target filename (e.g., 'lactose.html')
                        target_filename = href.split('/')[-1].split('#')[0]
                        
                        # Use our Index to instantly find the target node
                        if target_filename in file_index:
                            target_node = file_index[target_filename]
                            if source_node != target_node:
                                G.add_edge(source_node, target_node)
        except Exception as e:
            print(f"Skipping {source_node}: {e}")

    # 3. VISUALIZE: With Force-Directed Physics
    net = Network(height="900px", width="100%", bgcolor="#111", font_color="white", select_menu=True)
    
    # Calculate PageRank (Size nodes by how many links point TO them)
    pagerank = nx.pagerank(G)
    for node in G.nodes:
        G.nodes[node]['size'] = pagerank[node] * 1000 + 10
        G.nodes[node]['color'] = '#ff4b2b' if 'additives' in node else '#4facfe'

    net.from_nx(G)
    net.toggle_physics(True)
    net.show("encyclopedia_optimized.html", notebook=False)
    print("Done! Open encyclopedia_optimized.html")

if __name__ == "__main__":
    build_optimized_graph()

