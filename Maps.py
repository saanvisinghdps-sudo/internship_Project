
import heapq
import math
import folium


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in meters."""
    R = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


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
        # Nearest-node cache (built on demand)
        self._nn_ids = None
        self._nn_lat_rad = None
        self._nn_lon_rad = None

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

    def edge_distance_m(self, u: str, v: str) -> float:
        """Geographic edge length in meters (computed from node coords)."""
        (lat1, lon1) = self.coords[u]
        (lat2, lon2) = self.coords[v]
        return haversine_m(lat1, lon1, lat2, lon2)

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

    def _reconstruct(self, parent: dict[str, str | None], start: str, goal: str):
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur)
        path.reverse()
        if not path or path[0] != start:
            return None
        return path

    def route(self, start: str, goal: str, mode: str = "cost"):
        """
        Compute a route using either:
          - mode="cost"     -> minimizes file edge weights (fastest, if weights represent time/cost)
          - mode="distance" -> minimizes geographic distance (meters)

        Returns (path_list, total_value).

        Notes:
          - For cost: uses Dijkstra (heuristic=0) to keep it correct even if costs aren't distances.
          - For distance: uses A* with straight-line heuristic for speed.
        """
        if start not in self.locations or goal not in self.locations:
            return None, float("inf")

        if mode not in ("cost", "distance"):
            raise ValueError("mode must be 'cost' or 'distance'")

        open_heap = []
        heapq.heappush(open_heap, (0.0, start))

        g_score = {start: 0.0}
        parent: dict[str, str | None] = {start: None}
        closed = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                return self._reconstruct(parent, start, goal), g_score[goal]

            for nb in self.neighbours.get(current, []):
                if nb in closed:
                    continue

                if mode == "cost":
                    w = self.edge_weights.get((current, nb))
                    if w is None:
                        continue
                    h = 0.0
                else:
                    w = self.edge_distance_m(current, nb)
                    h = self._heuristic(nb, goal)

                tentative = g_score[current] + w
                if tentative < g_score.get(nb, float("inf")):
                    g_score[nb] = tentative
                    parent[nb] = current
                    heapq.heappush(open_heap, (tentative + h, nb))

        return None, float("inf")

    def shortest_path(self, start: str, goal: str):
        """Backwards-compatible: treats the file weights as the thing to minimize."""
        return self.route(start, goal, mode="cost")

    def dijkstra(self, start: str, destination: str):
        return self.shortest_path(start, destination)

    def folium_route_map(self, path: list[str], zoom_start: int = 13, max_points: int = 2000) -> folium.Map:
        """Draw a single route."""
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

    def folium_compare_routes(
        self,
        fastest_path: list[str] | None,
        shortest_path: list[str] | None,
        zoom_start: int = 13,
        max_points: int = 2000,
    ) -> folium.Map:
        """Draw two routes on one map with different colors."""

        base_path = fastest_path or shortest_path
        if not base_path:
            return folium.Map(location=[52.52, 13.405], zoom_start=12, tiles="OpenStreetMap")

        def downsample(p: list[str] | None):
            if not p:
                return None
            if len(p) <= max_points:
                return p
            step = max(1, len(p) // max_points)
            p2 = p[::step]
            if p2[-1] != p[-1]:
                p2.append(p[-1])
            return p2

        fastest_ds = downsample(fastest_path)
        shortest_ds = downsample(shortest_path)

        lat0, lon0 = self.coords[base_path[0]]
        fmap = folium.Map(location=[lat0, lon0], zoom_start=zoom_start, tiles="OpenStreetMap")

        start = base_path[0]
        end = base_path[-1]

        lat_s, lon_s = self.coords[start]
        folium.Marker(
            location=[lat_s, lon_s],
            tooltip=f"Start: {start}",
            popup=f"Start: {start}",
            icon=folium.Icon(color="green"),
        ).add_to(fmap)

        lat_t, lon_t = self.coords[end]
        folium.Marker(
            location=[lat_t, lon_t],
            tooltip=f"Destination: {end}",
            popup=f"Destination: {end}",
            icon=folium.Icon(color="red"),
        ).add_to(fmap)

        all_coords = []

        if shortest_ds:
            coords = [[self.coords[n][0], self.coords[n][1]] for n in shortest_ds]
            folium.PolyLine(
                coords,
                color="blue",
                weight=6,
                opacity=0.85,
                tooltip="Shortest (distance)",
            ).add_to(fmap)
            all_coords.extend(coords)

        if fastest_ds:
            coords = [[self.coords[n][0], self.coords[n][1]] for n in fastest_ds]
            folium.PolyLine(
                coords,
                color="red",
                weight=6,
                opacity=0.85,
                tooltip="Fastest (cost)",
            ).add_to(fmap)
            all_coords.extend(coords)

        if all_coords:
            fmap.fit_bounds(all_coords)

        return fmap

    def _build_nearest_cache(self):
        """Build cached coordinate arrays for nearest-node lookup."""
        ids = list(self.coords.keys())
        self._nn_ids = ids
        self._nn_lat_rad = [math.radians(self.coords[i][0]) for i in ids]
        self._nn_lon_rad = [math.radians(self.coords[i][1]) for i in ids]

    def nearest_node(self, lat: float, lon: float) -> str:
        """
        Return the node id in this graph closest to the given (lat, lon).
        """
        if not self.coords:
            raise ValueError("No coordinates loaded; cannot find nearest node.")

        if self._nn_ids is None:
            self._build_nearest_cache()

        lat0 = math.radians(float(lat))
        lon0 = math.radians(float(lon))

        best_i = 0
        best_d2 = float("inf")

        for i, (lat_i, lon_i) in enumerate(zip(self._nn_lat_rad, self._nn_lon_rad)):
            x = (lon_i - lon0) * math.cos((lat_i + lat0) * 0.5)
            y = (lat_i - lat0)
            d2 = x * x + y * y
            if d2 < best_d2:
                best_d2 = d2
                best_i = i

        return str(self._nn_ids[best_i])


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




