import streamlit as st
from neo4j import GraphDatabase

# -------------------------------
# CONFIG
# -------------------------------

URI = "bolt://127.0.0.1:7687"

driver = GraphDatabase.driver(
    "bolt://127.0.0.1:7687",
    auth=("neo4j", "neo4j123")
)

st.set_page_config(page_title="GOT Graph Explorer", layout="wide")

st.title("🐉 Game of Thrones Knowledge Graph Explorer")

# -------------------------------
# SEARCH INPUT
# -------------------------------
search = st.text_input("🔍 Search Character / Entity")

# -------------------------------
# QUERY FUNCTION
# -------------------------------
def query_graph(name):
    with driver.session() as session:
        result = session.run("""
            MATCH (n)-[r]-(x)
            WHERE toLower(n.name) CONTAINS toLower($name)
            RETURN n.name AS source, type(r) AS relation, x.name AS target
            LIMIT 50
        """, name=name)
        return [record.data() for record in result]

# -------------------------------
# DISPLAY RESULTS
# -------------------------------

from pyvis.network import Network
import streamlit.components.v1 as components

def visualize_graph(data):
    net = Network(height="500px", width="100%", bgcolor="#222", font_color="white")

    for row in data:
        source = row["source"]
        target = row["target"]
        relation = row["relation"]

        net.add_node(source, label=source)
        net.add_node(target, label=target)
        net.add_edge(source, target, label=relation)

    net.save_graph("graph.html")
    HtmlFile = open("graph.html", "r", encoding="utf-8")
    components.html(HtmlFile.read(), height=500)


if search:
    data = query_graph(search)

    if data:
        st.subheader("🔗 Graph View")
        visualize_graph(data)
    else:
        st.warning("No results found")

# -------------------------------
# ALL NODES VIEW
# -------------------------------
st.sidebar.header("Explore")

if st.sidebar.button("Show random nodes"):
    with driver.session() as session:
        result = session.run("""
            MATCH (n)
            RETURN n.name AS name
            LIMIT 20
        """)
        nodes = [r["name"] for r in result]

    st.subheader("📊 Sample Nodes")
    for n in nodes:
        st.write(n)