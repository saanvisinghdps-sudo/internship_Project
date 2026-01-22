from geopy.distance import geodesic    
import webbrowser
import collections
import heapq
import folium
import os

class Location:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.lat = latitude
        self.long = longitude
    
    def check_invariants(self):
        if not isinstance(self.name,str):
            raise TypeError(f"The location name should be a string, got {type(self.name).__name__}")
        if len(self.name) == 0:
            raise ValueError(f"The location name can't be empty")
        if not isinstance(self.lat,(int)) and not isinstance(self.lat,(float)):
            raise TypeError(f"The latitude should be an integer or float, got {type(self.lat).__name__}")
        if not isinstance(self.long,(int)) and not isinstance(self.long,(float)):
            raise TypeError(f"The longitude should be a integer or float, got {type(self.long).__name__}")

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"({self.name}, {self.lat}, {self.long})"

class Map:
    def __init__(self, name):
        self.name = name
        self.locations = {}          
        self.neighbours = {}   

    def connect_nearest_loc(map_obj, k = 3):
        names = list(map_obj.locations.keys())
        k = max(0, min(k, len(names) - 1))
        for name in names:
            loc = map_obj.locations[name]
            dists = []

            for other_name in names:
                if other_name == name:
                    continue
                other_loc = map_obj.locations[other_name]
                d = map_obj.calculate_distance(loc, other_loc)
                dists.append((d,other_name))

            dists.sort(key=lambda x: x[0])
            nearest = dists[:k]

            for _, other_name in nearest:
                map_obj.add_neighbours(loc, map_obj.locations[other_name])     

    def to_folium(self, output_html = "map.html", highlight_path = None): 
        avg_lat = sum(loc.lat for loc in self.locations.values()) / len(self.locations)
        avg_lon = sum(loc.long for loc in self.locations.values()) / len(self.locations)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6, tiles="OpenStreetMap")

        #Add markers       
        for loc in self.locations.values():
            folium.Marker(
                location=[loc.lat, loc.long],
                popup=f"{loc.name} ({loc.lat}, {loc.long})",
                tooltip=loc.name
            ).add_to(m)
        bounds = [[loc.lat, loc.long] for loc in self.locations.values()]
        m.fit_bounds(bounds)    

        #Creating a line between two locations in a map
        drawn = set()
        for a, nbrs in self.neighbours.items():
            for b in nbrs:
                edge = tuple(sorted((a, b)))
                if edge in drawn:
                    continue
                drawn.add(edge)

                loc1 = self.locations[a]
                loc2 = self.locations[b]

                folium.PolyLine(
                    locations=[[loc1.lat,loc1.long], [loc2.lat,loc2.long]],
                    weight = 3,
                    opacity = 0.7,
                ).add_to(m)

        if highlight_path:
            path_coords = []
            for name in highlight_path:
                loc = self.locations[name]
                path_coords.append([loc.lat, loc.long])    

            folium.PolyLine(
                locations=path_coords,
                color="#FF0000",
                weight=6,
                opacity=0.9,
            ).add_to(m)    

        m.save(output_html)
        print("Saved map to:", os.path.abspath(output_html))  
        return output_html


    def check_invariants(self):
        for key,location in self.locations.items():
            if not isinstance(location, Location):
                raise TypeError(f"All values must be Location objects, got {type(location).__name__}")
            if key != location.name:
                raise ValueError(f"Location key '{key}' does not match location name '{location.name}'")
        for loc in self.neighbours:
            if loc not in self.locations.keys():
                raise ValueError(f"there are no {loc} present in {self.locations.keys()}")
            for loc2 in self.neighbours[loc]:
                if loc2 not in self.neighbours :
                    raise ValueError(f"there is no {loc2} present in {self.neighbours.keys()}") 
                if loc not in self.neighbours[loc2]:
                    raise ValueError(f"there is no {loc} present in {self.neighbours[loc2]}")

    def add_location(self, location):
        if isinstance(location, Location):
            self.locations[location.name] = location
            if location.name not in self.neighbours:
                self.neighbours[location.name] = []

    def display_locations(self):
        if not self.locations:
            print(f"No locations found for {self.name}")
        else:
            for location in self.locations.values():
                print(location)

    def add_neighbours(self, location1, location2):
        if not (isinstance(location1, Location) and isinstance(location2, Location)):
            raise ValueError("Invalid Location type")

        name1, name2 = location1.name, location2.name

        if name1 not in self.neighbours or name2 not in self.neighbours:
            raise ValueError("Nonexistent location for adding neighbours")

        if name2 not in self.neighbours[name1]:
            self.neighbours[name1].append(name2)
        if name1 not in self.neighbours[name2]:
            self.neighbours[name2].append(name1)

    def display_neighbours(self, location):
        if isinstance(location, Location):
            key = location.name
        else:
            # This doesn't look solid
            key = location

        if key not in self.neighbours:
            raise ValueError(f"There is no neighbouring location for {key}")

        print(f"Neighbours of {key}: {', '.join(self.neighbours[key])}")


    # creating a function to calculate the distance from one location to another location while considering its latitude and longitude 
    # Using Geopy
    # parameters: location1,location2,dist ---> its lat and long
    def calculate_distance(self, location1, location2):
        coord_1 = (location1.lat,location1.long)
        coord_2 = (location2.lat,location2.long)

        distance = geodesic(coord_1,coord_2).meters
        return distance 

    # The Dijkstra Function-- which has 2 parameters containg starting and ending point
    def dijkstra(self, start, destination):
        graph = {}

        # A location name and its neighbour name should be present in the graph using for loop
        for loc_name in self.neighbours.keys():
            graph[loc_name] = {}

            for neighbour_name in self.neighbours[loc_name]:
                loc1 = self.locations[loc_name]
                loc2 = self.locations[neighbour_name]
 
                #Implementing weights(distances) into the graph from one node to another
                distances = self.calculate_distance(loc1,loc2)
                graph[loc_name][neighbour_name] = distances

        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        parent = {start: None}
        queue = [(0, start)]   


        while queue:  
            # inside the queue there should be a construction of a path and then provide the distances    
            # printing the current node as it has the smallest distance    
            current_distance, current_node = heapq.heappop(queue)      

            if current_node == destination:
                path = []
                current = destination
                while current is not None:  
                    path.append(current)
                    current = parent.get(current) 
                path.reverse()
                return path, distances[destination]
        

            # Skip if the current distance is already the shortest path
            if current_distance > distances[current_node]:
                continue

            # Update if the new distance is shorter than the previous distance
            for neighbor, weight in graph[current_node].items():
                alt_distance = current_distance + weight
                if alt_distance < distances[neighbor]:
                    distances[neighbor] = alt_distance
                    parent[neighbor] = current_node
                    heapq.heappush(queue, (alt_distance, neighbor))



    # When it reaches the destination it. will stop 
    # Shortest path in an unweighted graph
    def bfs(self, root, destination):
        visited = set([root])
        queue = collections.deque([root]) 
        parent = {root: None}

        while queue:
            vertex = queue.popleft()                               
            if vertex == destination:
                path = []
                current = destination
                while current is not None:  
                    path.append(current)
                    current = parent.get(current) 
                path.reverse()
                return path
            for neighbour in self.neighbours.get(vertex, []):
                if neighbour not in visited: 
                    visited.add(neighbour)
                    parent[neighbour] = vertex  
                    queue.append(neighbour) 

def Sample_Data():
    countries = {}
    # France
    france = Map("France")
    paris = Location("Paris", 48.8566, 2.3522)
    marseille = Location("Marseille", 43.2965, 5.3698)
    lyon = Location("Lyon", 45.7640, 4.8357)
    toulouse = Location("Toulouse", 43.6047, 1.4442)
    nice = Location("Nice", 43.7102, 7.2620)
    nantes = Location("Nantes", 47.2184, -1.5536)
    montpellier = Location("Montpellier", 43.6108, 3.8767)
    strasbourg = Location("Strasbourg", 48.5734, 7.7521)
    bordeaux = Location("Bordeaux", 44.8378, -0.5792)
    lille = Location("Lille", 50.6292, 3.0573)
    rennes = Location("Rennes", 48.1173, -1.6778)
    reims = Location("Reims", 49.2583, 4.0317)
    le_havre = Location("Le Havre", 49.4944, 0.1079)
    saint_etienne = Location("Saint-Étienne", 45.4397, 4.3872)
    toulon = Location("Toulon", 43.1242, 5.9280)
    grenoble = Location("Grenoble", 45.1885, 5.7245)
    dijon = Location("Dijon", 47.3220, 5.0415)
    angers = Location("Angers", 47.4784, -0.5632)
    nimes = Location("Nîmes", 43.8367, 4.3601)
    villeurbanne = Location("Villeurbanne", 45.7667, 4.8833)
    clermont_ferrand = Location("Clermont-Ferrand", 45.7772, 3.0870)
    le_mans = Location("Le Mans", 48.0061, 0.1996)
    aix_en_provence = Location("Aix-en-Provence", 43.5297, 5.4474)
    brest = Location("Brest", 48.3904, -4.4861)
    tours = Location("Tours", 47.3941, 0.6848)
    amiens = Location("Amiens", 49.8941, 2.2957)
    limoges = Location("Limoges", 45.8336, 1.2611)
    annecy = Location("Annecy", 45.8992, 6.1294)
    perpignan = Location("Perpignan", 42.6887, 2.8948)
    metz = Location("Metz", 49.1193, 6.1757)
    besancon = Location("Besançon", 47.2378, 6.0241)
    orleans = Location("Orléans", 47.9029, 1.9093)
    caen = Location("Caen", 49.1829, -0.3707)
    mulhouse = Location("Mulhouse", 47.7508, 7.3359)
    rouen = Location("Rouen", 49.4432, 1.0993)
    nancy = Location("Nancy", 48.6921, 6.1844)
    saint_denis = Location("Saint-Denis", 48.9362, 2.3574)
    montauban = Location("Montauban", 44.0180, 1.3550)
    avignon = Location("Avignon", 43.9493, 4.8055)
    poitiers = Location("Poitiers", 46.5802, 0.3404)
    dunkirk = Location("Dunkerque", 51.0344, 2.3768)
    rochelle = Location("La Rochelle", 46.1591, -1.1517)
    chambery = Location("Chambéry", 45.5646, 5.9178)
    bayonne = Location("Bayonne", 43.4929, -1.4748)
    pau = Location("Pau", 43.2951, -0.3708)
    valence = Location("Valence", 44.9334, 4.8924)
    cannes = Location("Cannes", 43.5528, 7.0174)
    ajaccio = Location("Ajaccio", 41.9192, 8.7386)
    colmar = Location("Colmar", 48.0795, 7.3585)
    beziers = Location("Béziers", 43.3442, 3.2158)

    cities = [
        paris, marseille, lyon, toulouse, nice, nantes, montpellier, strasbourg, bordeaux, lille,
        rennes, reims, le_havre, saint_etienne, toulon, grenoble, dijon, angers, nimes, villeurbanne,
        clermont_ferrand, le_mans, aix_en_provence, brest, tours, amiens, limoges, annecy, perpignan, metz,
        besancon, orleans, caen, mulhouse, rouen, nancy, saint_denis, montauban, avignon, poitiers,
        dunkirk, rochelle, chambery, bayonne, pau, valence, cannes, ajaccio, colmar, beziers
    ]
    
    for loc in cities:
       france.add_location(loc)
    

    france.connect_nearest_loc(k=3)  
    france.check_invariants()
    countries["France"] = france
    path_bfs = france.bfs("Paris", "Rochelle")
    path_dij,dist = france.dijkstra("Paris", "Rennes")

    france.to_folium("france_network.html")
    france.to_folium("france_bfs.html", highlight_path = path_bfs)
    france.to_folium("france_dijkstra.html", highlight_path = path_dij)

    print("Maps created!")
    # Now display all
    
    for country_name, country_map in countries.items():
        print(f"\n{country_name}:")
        country_map.display_locations()
        
        print("\nNeighbours:")
        for loc_name in country_map.neighbours.keys():
            country_map.display_neighbours(loc_name)

    return countries
    
if __name__=="__main__":    
    Sample_Data()
