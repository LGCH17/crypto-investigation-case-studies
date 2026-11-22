import pandas as pd
import networkx as nx

def short_name(label):
    """'Bybit Exploiter 2 (0xA4B2...)' -> 'Bybit Exploiter 2'
       '0x6BB0... (Velora/ParaSwap Augustus)' -> 'Velora/ParaSwap Augustus'"""
    label = str(label).strip()
    if label.startswith("0x") and "(" in label:
        return label.split("(", 1)[1].rstrip(")")
    return label.split(" (")[0]

df = pd.read_csv("bybit_trace.csv", encoding="cp1252")
df = df.dropna(subset=["From", "To"])

G = nx.DiGraph()
for _, row in df.iterrows():
    sender, receiver = short_name(row["From"]), short_name(row["To"])
    if G.has_edge(sender, receiver):
        G[sender][receiver]["transfers"] += 1
    else:
        G.add_edge(sender, receiver, transfers=1)

print("Wallets/contracts (nodes):", G.number_of_nodes())
print("Connections (edges):", G.number_of_edges())
print("Transfers (rows):", len(df))

print("\nMost connections OUT (fan-out):")
for node, n in sorted(G.out_degree(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {node}: sends to {n}")

print("\nMost connections IN (consolidation):")
for node, n in sorted(G.in_degree(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {node}: receives from {n}")

print("\nRoute from Exploiter 1 to Exploiter 45:")
print("  " + " -> ".join(nx.shortest_path(G, "Bybit Exploiter 1", "Bybit Exploiter 45")))
import matplotlib.pyplot as plt

# Which wallets are on the FBI list? Read it from your own CSV column.
#print(df["In FBI list?"].value_counts(dropna=False))
fbi_listed = {short_name(to) for to, flag in zip(df["To"], df["In FBI list?"])
              if str(flag).strip().upper().startswith("YES")}
#print("Recipients marked YES:", sorted(fbi_listed))

# Put each wallet in a column by how many hops it is from Exploiter 1
layers = nx.single_source_shortest_path_length(G, "Bybit Exploiter 1")
for node in G.nodes():
    G.nodes[node]["layer"] = layers.get(node, 0)
pos = nx.multipartite_layout(G, subset_key="layer")

# Colour each node by what it is
colors = []
for node in G.nodes():
    if node in fbi_listed:
        colors.append("tab:red")
    elif node.startswith("Bybit Exploiter"):
        colors.append("tab:orange")
    elif node.startswith("Null"):
        colors.append("black")
    else:
        colors.append("lightgrey")

# Thicker arrows for edges carrying more transfers
widths = [1 + G[u][v]["transfers"] for u, v in G.edges()]
labels = {(u, v): G[u][v]["transfers"] for u, v in G.edges() if G[u][v]["transfers"] > 1}

plt.figure(figsize=(16, 9))
nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=900)
nx.draw_networkx_edges(G, pos, width=widths, arrowsize=15, edge_color="grey",
                       connectionstyle="arc3,rad=0.1", node_size=900)
label_pos = {node: (x, y - 0.06) for node, (x, y) in pos.items()}
nx.draw_networkx_labels(G, label_pos, font_size=8)
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8)
plt.title("Bybit hack: traced slice\n"
          "red = in FBI list | orange = attacker wallet, not confirmed on FBI list | "
          "grey = DEX/protocol | black = burn")
plt.axis("off")
plt.tight_layout()
plt.savefig("wallet_graph.png", dpi=150)
print("Saved wallet_graph.png; FBI-listed nodes:", len(fbi_listed))