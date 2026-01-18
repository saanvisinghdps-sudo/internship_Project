class Location:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.lat = latitude
        self.long = longitude
        self.check_invariants()
    
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
        return f"the following location is: {self.name} and the latitude is {self.lat} and the longitude is {self.long}."

    def __repr__(self):
        return str(self)
import collections

class Map:
    def __init__(self, name):
        self.name = name
        self.locations = {}          
        self.neighbours = {}   
        self.check_invariants()  


    def check_invariants(self):
        for key ,location in self.locations.items():
            if not isinstance(location, Location):
                raise TypeError(f"All values must be Location objects, got {type(location).__name__}")
            if key != location.name:
                raise ValueError(f"Location key '{key}' does not match location name '{location.name}'")
        for loc in self.neighbours.keys():
            if loc not in self.locations.keys():
                raise ValueError(f"there are no {loc} present in {self.locations.keys()}")
            for loc2 in self.neighbours[loc]:
                if loc2 not in self.neighbours.keys() :
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
            print("No neighbours for this location")
            return

        name1, name2 = location1.name, location2.name

        if name1 not in self.neighbours or name2 not in self.neighbours:
            print("Both locations must be added to the map first")
            return

        if name2 not in self.neighbours[name1]:
            self.neighbours[name1].append(name2)
        if name1 not in self.neighbours[name2]:
            self.neighbours[name2].append(name1)

    def display_neighbours(self, location):
        if isinstance(location, Location):
            key = location.name
        else:
            key = location

        if key not in self.neighbours:
            print(f"There is no neighbouring location for {key}")
            return

        print(f"Neighbours of {key}: {', '.join(self.neighbours[key])}")
  
#When it reaches the destination it. will stop 
#Shortest path in an unweighted graph
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
                print(f"Shortest path from {root} to {destination}: {' -> '.join(path)}")
                print(f"the locations visited from Paris is: {visited}")
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
    lyon = Location("Lyon", 45.7640, 4.8357)
    marseille = Location("Marseille", 43.2965, 5.3698)
    bordeaux = Location("Bordeaux", 44.8361, -0.58081)
    toulouse = Location("Toulouse", 43.60045, 1.44400)
    rochelle = Location("Rochelle", 46.1591, -1.1517)
    rennes = Location("Rennes", 48.1147, -1.6794)
    strasbourg = Location("Strasbourg", 48.5800, 7.7500)
    lille = Location("Lille", 50.6292, 3.05725)
    amiens = Location("Amiens", 49.894066, 2.2957)

    cities = [paris, lyon, marseille, bordeaux, toulouse, rochelle, rennes, strasbourg, lille, amiens]


    for loc in cities:
       france.add_location(loc)

        
    france.add_neighbours(paris, lyon)
    france.add_neighbours(lyon, marseille)
    france.add_neighbours(paris, strasbourg)
    france.add_neighbours(lille, amiens)
    france.add_neighbours(paris, lille)
    france.add_neighbours(paris, bordeaux)
    france.add_neighbours(bordeaux, toulouse)
    france.add_neighbours(rochelle, bordeaux)
    france.add_neighbours(rochelle, rennes)   
    france.check_invariants()
    countries["France"] = france
    france.bfs("Paris", "Rochelle")
   
    graph = {"Paris":["Lille","Lyon","Bordeaux","Strasbourg"], 
            "Lille":["Amiens"], 
            "Lyon": ["Paris", "Marseille"],
            "Bordeaux": ["Toulouse","Rochelle"], 
            "Rochelle":["Rennes","Bordeaux"], 
            "Amiens":["Lille"],
            "Strasbourg":["Paris"],
            "Marseille":["Lyon"],
            "Toulouse":["Bordeaux"],
            "Rennes":["Rochelle"]}    

    
    # Japan
    '''japan = Map("Japan")
    tokyo = Location("Tokyo", 35.6762, 139.6503)
    kyoto = Location("Kyoto", 35.0116, 135.7681)
    saitama = Location("Saitama", 35.8857, 139.6682)  
    
    for loc in [tokyo, kyoto, saitama]:
        japan.add_location(loc)
    
    japan.add_neighbours(tokyo, kyoto)
    japan.add_neighbours(tokyo, saitama)
    japan.add_neighbours(kyoto, saitama)
    
    countries["Japan"] = japan

    # USA
    usa = Map("USA")
    seattle = Location("Seattle", 47.6062, -122.3321)
    portland = Location("Portland", 45.5152, -122.6748)
    sf = Location("San Francisco", 37.7749, -122.4194)
    
    for loc in [seattle, portland, sf]:
        usa.add_location(loc)
    
    usa.add_neighbours(seattle, portland)
    usa.add_neighbours(seattle, sf)
    usa.add_neighbours(portland, sf)
    
    countries["USA"] = usa'''

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
    
    