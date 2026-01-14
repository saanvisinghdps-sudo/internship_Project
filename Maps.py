class Location:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.lat = latitude
        self.long = longitude

    def __str__(self):
        return f"the following location is: {self.name} and the latitude is {self.lat} and the longitude is {self.long}."


class Map:
    def __init__(self, name):
        self.name = name
        self.locations = {}          
        self.neighbours = {}        

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


class Neighbours:
    neighbours = {
        "Paris": ["Lyon", "Marseille"],
        "Lyon": ["Paris", "Marseille"],
        "Marseille": ["Paris", "Lyon"],

        "Tokyo": ["Satiama", "Kyoto"],
        "Satiama": ["Tokyo", "Kyoto"],
        "Kyoto": ["Satiama", "Tokyo"],

        "Seattle": ["Portland", "San Francisco"],
        "Portland": ["Seattle", "San Francisco"],
        "San Francisco": ["Seattle", "Portland"],
    }

    def __init__(self, location1, location2):
        self.__location1 = location1
        self.__location2 = location2

    def get_location1(self):
        return self.__location1

    def get_location2(self):
        return self.__location2

    def __str__(self):
        return f"Neighbours: {self.__location1} and {self.__location2}."

def Sample_Data():
    countries = {}

    # France
    france = Map("France")
    paris = Location("Paris", 48.8566, 2.3522)
    lyon = Location("Lyon", 45.7640, 4.8357)
    marseille = Location("Marseille", 43.2965, 5.3698)
    
    for loc in [paris, lyon, marseille]:
        france.add_location(loc)
    
    france.add_neighbours(paris, lyon)
    france.add_neighbours(paris, marseille)
    france.add_neighbours(lyon, marseille)
    
    countries["France"] = france

    # Japan
    japan = Map("Japan")
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
    
    countries["USA"] = usa

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
