# think of creating a city_grid as creating an area in which the DarkStore is going to serve 
# and where customers live
class CityGrid:
    #num_parallel_streets must me an odd number
    def __init__(self, side_km: int, num_parallel_streets: int):

        self.side = side_km
        self.num_parallel_streets = num_parallel_streets
        
        self.customer_locs = self.generate_locs()
        # the loc of the dark store is fixed at the center of the city grid
        self.dark_store_loc = (0.0, 0.0) 
        # to keep track of assigned locs to customers 
        self.assigned_locs = [] 
    
    #generate the list of all available locs in the city grid
    def generate_locs(self):
        locs = []
        min_length = self.side / self.num_parallel_streets

        i = (1 - self.num_parallel_streets) / 2
        while i != (self.num_parallel_streets + 1) / 2:
            
            j = (1 - self.num_parallel_streets) / 2
            while j != (self.num_parallel_streets + 1)/ 2:
                locs.append((i * min_length, j * min_length))
                j += 1
            i += 1

        # remove the loc of the dark store from the list of available locs for customer assignment
        locs.remove((0.0, 0.0))
        return locs
    
    # Sample a random locaton from the city grid; this can be used to assign a loc to a customer
    def sample_loc(self):
        # first sample a random loc from the list of locs
        r = random.Random()
        
        sampled_loc = r.choice(self.customer_locs)
        
        # then migrate it from "locs" to the "assigned_locs" list to keep track of it
        self.customer_locs.remove(sampled_loc)
        self.assigned_locs.append(sampled_loc)

        # then return the sampled loc
        return sampled_loc
    
    # return manhattan distance between two locs; treat it as the optimal route length.
    @classmethod
    def route_length(cls, loc1, loc2):
        return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
    
