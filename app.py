import streamlit as st
from streamlit_folium import st_folium
from Maps import Sample_Data, Map, Location


st.set_page_config(page_title="France Route Finder", layout="wide")

st.title("France Route Finder (Dijkstra)")

countries = Sample_Data()  # builds the map + locations + neighbours
france = countries["France"]

city_names = sorted(france.locations.keys())

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    start = st.selectbox("Start city", city_names, index=city_names.index("Paris") if "Paris" in city_names else 0)

with col2:
    destination = st.selectbox("Destination city", city_names)

with col3:
    k = st.number_input("k-nearest links", min_value=1, max_value=10, value=3, step=1)

# Optional: rebuild neighbours when k changes
# (This is simple but re-running Sample_Data() every time can be slow.
# If you want this polished, we can cache it.)
if st.button("Find route"):
    # Rebuild graph with chosen k
    # easiest approach: recreate and rebuild neighbours
    countries = Sample_Data()
    france = countries["France"]

    # Clear neighbours and rebuild using selected k
    # (Only do this if you want k to actually change)
    france.neighbours = {name: [] for name in france.locations.keys()}
    france.connect_nearest_loc(k=int(k))

    if start == destination:
        st.warning("Pick two different cities.")
    else:
        result = france.dijkstra(start, destination)
        if result is None:
            st.error("No route found (graph may be disconnected). Try a larger k.")
        else:
            path, dist = result
            st.success(f"Route found: {' -> '.join(path)}")
            st.write(f"Total distance: **{dist:.2f} km**")

            # Build a folium map with the highlighted path
            m = france.to_folium(output_html="temp.html", highlight_path=path)

            # france.to_folium returns a filename, but we want the folium map object.
            # Quick workaround: recreate the folium map in-memory here:

            import folium

            avg_lat = sum(loc.lat for loc in france.locations.values()) / len(france.locations)
            avg_lon = sum(loc.long for loc in france.locations.values()) / len(france.locations)
            folium_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=6, tiles="OpenStreetMap")

            # markers
            for loc in france.locations.values():
                folium.Marker(
                    location=[loc.lat, loc.long],
                    popup=f"{loc.name} ({loc.lat}, {loc.long})",
                    tooltip=loc.name
                ).add_to(folium_map)

            # edges
            drawn = set()
            for a, nbrs in france.neighbours.items():
                for b in nbrs:
                    edge = tuple(sorted((a, b)))
                    if edge in drawn:
                        continue
                    drawn.add(edge)
                    loc1 = france.locations[a]
                    loc2 = france.locations[b]
                    folium.PolyLine(
                        locations=[[loc1.lat, loc1.long], [loc2.lat, loc2.long]],
                        weight=3,
                        opacity=0.6,
                    ).add_to(folium_map)

            # highlight path
            path_coords = [[france.locations[name].lat, france.locations[name].long] for name in path]
            folium.PolyLine(
                locations=path_coords,
                weight=6,
                opacity=0.9,
            ).add_to(folium_map)

            # fit bounds
            folium_map.fit_bounds([[loc.lat, loc.long] for loc in france.locations.values()])

            st_folium(folium_map, width=1100, height=650)
