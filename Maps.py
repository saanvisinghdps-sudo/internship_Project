

import heapq
import math
import folium


class Location:
    def __init__(self, name, latitude, longitude):
        self.name = str(name)
        self.lat = float(latitude)
        self.long = float(longitude)

    def __repr__(self):
        return f"({self.name}, {self.lat}, {self.long})"


class Map:
    """
    Graph map for DIMACS-like data:
      - locations: node_id -> Location
      - neighbours: node_id -> list of neighbour node_ids
      - edge_weights: (u, v) -> cost (from file)
      - coords: node_id -> (lat, lon)
    """

    def __init__(self, name):
        self.name = name
        self.locations = {}
        self.neighbours = {}
        self.edge_weights = {}
        self.coords = {}

    def add_location(self, loc: Location):
        self.locations[loc.name] = loc
        self.coords[loc.name] = (loc.lat, loc.long)
        if loc.name not in self.neighbours:
            self.neighbours[loc.name] = []

    def add_edge(self, u: str, v: str, cost: float, add_reverse: bool = True):
        if u not in self.locations or v not in self.locations:
            return

        if v not in self.neighbours[u]:
            self.neighbours[u].append(v)
        self.edge_weights[(u, v)] = float(cost)

        if add_reverse:
            if u not in self.neighbours[v]:
                self.neighbours[v].append(u)
            self.edge_weights[(v, u)] = float(cost)

    # ---------- Fast shortest path (A*; Dijkstra when heuristic=0) ----------

    def _heuristic(self, a: str, b: str) -> float:
        """
        Straight-line distance heuristic in meters (rough).
        Helps A* run much faster than plain Dijkstra on big graphs.
        """
        (lat1, lon1) = self.coords[a]
        (lat2, lon2) = self.coords[b]

        dlat = (lat2 - lat1) * 111_320.0
        mean_lat = (lat1 + lat2) * 0.5
        dlon = (lon2 - lon1) * (111_320.0 * math.cos(math.radians(mean_lat)))
        return math.hypot(dlat, dlon)

    def shortest_path(self, start: str, goal: str):
        """
        Returns (path_list, total_cost).
        Uses A* for speed with file edge costs.
        """
        if start not in self.locations or goal not in self.locations:
            return None, float("inf")

        open_heap = []
        heapq.heappush(open_heap, (0.0, start))

        g_score = {start: 0.0}
        parent = {start: None}
        closed = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                path = []
                cur = goal
                while cur is not None:
                    path.append(cur)
                    cur = parent.get(cur)
                path.reverse()
                return path, g_score[goal]

            for nb in self.neighbours.get(current, []):
                if nb in closed:
                    continue

                w = self.edge_weights.get((current, nb))
                if w is None:
                    continue

                tentative = g_score[current] + w
                if tentative < g_score.get(nb, float("inf")):
                    g_score[nb] = tentative
                    parent[nb] = current
                    f = tentative + self._heuristic(nb, goal)
                    heapq.heappush(open_heap, (f, nb))

        return None, float("inf")

    # keep your old method name
    def dijkstra(self, start: str, destination: str):
        return self.shortest_path(start, destination)

    # ---------- Folium route map (ONLY draws the route) ----------

    def folium_route_map(self, path: list[str], zoom_start: int = 13, max_points: int = 2000) -> folium.Map:
        """
        Draw only the route (fast). Also downsample to keep the map responsive.

        max_points: limit number of points in polyline for performance.
        """
        # Downsample if path is huge
        if len(path) > max_points:
            step = max(1, len(path) // max_points)
            path = path[::step]
            if path[-1] != path[-1]:
                path.append(path[-1])

        lat0, lon0 = self.coords[path[0]]
        fmap = folium.Map(location=[lat0, lon0], zoom_start=zoom_start, tiles="OpenStreetMap")

        lat_s, lon_s = self.coords[path[0]]
        folium.Marker(
            location=[lat_s, lon_s],
            tooltip=f"Start: {path[0]}",
            popup=f"Start: {path[0]}",
            icon=folium.Icon(color="green"),
        ).add_to(fmap)

        lat_t, lon_t = self.coords[path[-1]]
        folium.Marker(
            location=[lat_t, lon_t],
            tooltip=f"Destination: {path[-1]}",
            popup=f"Destination: {path[-1]}",
            icon=folium.Icon(color="red"),
        ).add_to(fmap)

        coords = [[self.coords[n][0], self.coords[n][1]] for n in path]
        folium.PolyLine(coords, weight=6, opacity=0.9).add_to(fmap)
        fmap.fit_bounds(coords)
        return fmap


# ------------------ Parsing functions ------------------

def parse_dimacs_coords(coords_path: str) -> dict[str, tuple[float, float]]:
    """
    coords lines: v <id> <x> <y>

    In your dataset:
      x = encoded longitude
      y = encoded latitude

    Decode:
      lon = x*360/2^32 - 180
      lat = y*360/2^32 -  90
    """
    TWO32 = 2 ** 32
    coords = {}

    with open(coords_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("v "):
                continue

            parts = line.split()
            if len(parts) < 4:
                continue

            _, node_id, x_str, y_str = parts[:4]
            node_id = str(int(node_id))

            x = int(x_str)  # lon encoded
            y = int(y_str)  # lat encoded

            lon = (x * 360.0) / TWO32 - 180.0
            lat = (y * 360.0) / TWO32 - 90.0

            coords[node_id] = (lat, lon)

    return coords


def load_dimacs_map(graph_path: str, coords_path: str, name: str = "Graph", add_reverse_edges: bool = True) -> Map:
    """
    graph lines: a <from> <to> <cost>
    We'll use <cost> as edge weight.
    """
    m = Map(name)

    coords = parse_dimacs_coords(coords_path)
    for node_id, (lat, lon) in coords.items():
        m.add_location(Location(node_id, lat, lon))

    with open(graph_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line[0] in ("c", "p"):
                continue
            if not line.startswith("a "):
                continue

            parts = line.split()
            if len(parts) < 4:
                continue

            _, u_str, v_str, cost_str = parts[:4]
            u = str(int(u_str))
            v = str(int(v_str))

            try:
                cost = float(cost_str)
            except ValueError:
                continue

            m.add_edge(u, v, cost, add_reverse=add_reverse_edges)

    return m




