class Map:
    def __init__(self, name):
        self.name = name
        self.locations={}
        self.neighbours= {}
    def add_location(self, location):
        if isinstance(location,Location):
            self.locations[location] = location
            self.neighbours[location] = [] 

    def display_locations(self): 
        if not self.locations:
            print(f"No locations found for {self.name}")
        else:
            for location in self.locations:
                print(location)
#Class invariants need to be added
    def add_neighbours(self, location1, location2):

        self.neighbours[location1].append(location2)
        self.neighbours[location2].append(location1)
                    


    def display_neighbours(self, location):
        if location not in self.neighbours.keys():
            print(f"There is no neighbouring location for {location}")
            return
        else:
            print(f"Neighbours: {str(self.neighbours[location])}")




class Location:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.lat = latitude
        self.long = longitude

    def __str__(self):
        return f"the following location is: {self.name} and the latitude is {self.lat} and the longitude is {self.long}."
    


def Sample_Data():
    countries = {}  
    france = Map("France")
    paris=Location("Paris", 48.8566, 2.3522)
    france.add_location(paris)
    lyon =Location("Lyon", 45.7640, 4.8357)
    france.add_location(lyon)
    marseille = Location("Marseille", 43.2965, 5.3698)
    france.add_location(marseille)
    countries["France"] = france
    france.add_neighbours(paris,lyon)
    france.display_neighbours(paris)
    japan = Map("Japan")
    tokyo = Location("Tokyo", 35.6762, 139.6503)
    japan.add_location(tokyo)
    kyoto=Location("Kyoto", 35.0116, 135.7681)
    japan.add_location(kyoto)
    satiama=Location("Satiama",35.8857, 139.6682)
    japan.add_location(satiama)
    countries["Japan"] = japan
    usa = Map("USA")
    seattle= Location("Seattle", 47.6062, 122.3321)
    usa.add_location(seattle)
    portland=Location("Portland",45.5152, 122.6748)
    usa.add_location(portland)
    san_francisco = Location("San Francisco",37.7749, 122.4194)
    usa.add_location(san_francisco)
    countries["USA"] = usa
    for k,v in countries.items():
        v.display_locations()
        
    return countries

if __name__ == "__main__":
    data = Sample_Data() 

    #print(data)
    neighbours={
    "Paris":["Lyon", "Marseille"],
    "Lyon":["Paris","Marseille"],
    "Marseille":["Paris","Lyon"],

    "Tokyo":["Satiama","Kyoto"],
    "Satiama":["Tokyo","Kyoto"],
    "Kyoto":["Satiama","Tokyo"],

    "Seattle":["Portland","San Franscisco"], # pyright: ignore[reportUndefinedVariable]
    "Portland":["Seattle", "San Francisco"],
    "San Francisco":["Seattle", "Portland"]
}
    