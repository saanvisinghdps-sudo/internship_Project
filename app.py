import streamlit as st
import folium
from streamlit_folium import st_folium
from Maps import Sample_Data, Map, Location
import webbrowser
import os

st.set_page_config(page_title="France Route Finder", layout="wide")

st.title("France Route Finder (Dijkstra)")

countries = Sample_Data()  # builds the map + locations + neighbours
france = countries["France"]

city_names = sorted(france.locations.keys())

col1, col2 = st.columns([2, 2])

with col1:
    start = st.selectbox("Start city", city_names, index=city_names.index("Paris") if "Paris" in city_names else 0)

with col2:
    destination = st.selectbox("Destination city", city_names)

if st.button("Find route"):
    if start == destination:
        st.warning("Pick two different cities.")
    else:
        result = france.dijkstra(start, destination)
        if result is None:
            st.error("No route found (graph may be disconnected).")
        else:
            path, dist = result
            st.success(f"Route found: {' -> '.join(path)}")
            st.write(f"Total distance: **{dist/1000:.2f} km**")

            # Build a folium map with the highlighted path
            m = france.to_folium(output_html="temp.html", highlight_path=path)
            webbrowser.open("file://" + os.path.abspath("temp.html"))

