"""

@author: andrewscott
"""

import random
import poc_grid
import poc_queue
import poc_zombie_gui
import time
import copy
import math
from multiprocessing import Queue

try:
    import codeskulptor
except ImportError as exp:
    pass

# debug vars
DEBUG_CDF = False
DEBUG_MZ = False
DEBUG_MH = False
DEBUG_ME = False
DEBUG_VM = False
DEBUG_GD = False
DEBUG_BM = False
DEBUG_SA = False
DEBUG_SZ = False
DEBUG_TZ = False
DEBUG_Z = False
DEBUG_WEIGHT = False
DEBUG_SF = False
DEBUG_SW = False
DEBUG_GHN = False
DEBUG_GCN = False
DEBUG_GRCL = False
DEBUG_CLR = True

# global constants
EMPTY = 0
FULL = 1
FOUR_WAY = 0
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7

class path_calculator(poc_grid.Grid):
    """
    Class for simulating zombie pursuit of human on grid with
    obstacles
    """

    def __init__(self, grid_height, grid_width, obstacle_list = None,
                 zombie_list = None, human_list = None, initial_weight_list = None, default_weight = None,
                 demo_weight_list = None, hall_list = None):
        """
        Create a simulation of given size with given obstacles,
        humans, and zombies
        """
        poc_grid.Grid.__init__(self, grid_height, grid_width)
        
        if obstacle_list != None:
            for cell in obstacle_list:
                self.set_full(cell[0], cell[1])
        
        if zombie_list != None:
            self._a_side_list = list(zombie_list)
        else:
            self._a_side_list = []
        
        if human_list != None:
            self._human_list = list(human_list)
        else:
            self._human_list = []

        if hall_list != None:
            self._hall_list = copy.deepcopy(hall_list)
        else:
            self.hall_list = {1: (grid_height, grid_width)}
        
        if default_weight != None:
            self._default_weight = default_weight
        else:
            self._default_weight = 1

        if demo_weight_list != None:
            self._demo_weight_list = copy.deepcopy(demo_weight_list)
        else:
            #self._grid_width
            self._demo_weight_list = self.generate_demo_weight_lists()

            
        #remove line below
        if initial_weight_list != None:
            self._initial_weight_list = initial_weight_list[:][:]
        else:
            self._initial_weight_list = [[self._default_weight for x in range(grid_width)] for y in range(grid_height)]
            
            

        self._z_side_list = []
        self._z_side_hall_list = {}
        self._z_side_coord_list = {}
        self._forbidden_list = {}
        self._max_traversable_weight = self._default_weight
        self._min_traversable_weight = self._default_weight
        
        #these should contain the dictionary items of cabinet lists, not their individual key / value pairs
        self._all_hall_cabinet_list = []
        self._all_hall_reverse_cabinet_list = []

        #keep track of which demo map has just been served up
        self._current_demo_weight_list = 0

        #instantiate boundary list queue
        self._boundary_list = poc_queue.Queue()

    def generate_demo_weight_lists(self):
        """
        Generate & store a series of gradiated weight lists
        :return: A list of 2d grid lists
        """
        demo_weight_list = []

        #horizontal
        demo_weight_list.append([[col for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])
        demo_weight_list.append([[(col+2)*-1 for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])

        #Vertical
        demo_weight_list.append([[row for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])
        demo_weight_list.append([[(row+2)*-1 for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])

        #Diagonal NW/SE
        demo_weight_list.append([[col+row for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])
        demo_weight_list.append([[(col+row)*-1 for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])

        #Diagonal NE/SW
        demo_weight_list.append([[self.get_grid_width()-col+row for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])
        demo_weight_list.append([[(self.get_grid_width()-col+row)*-1 for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])

        #Circular
        demo_weight_list.append([[math.sqrt((col-(self.get_grid_width()//2))**2 + (row-(self.get_grid_height()//2))**2)  for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])
        demo_weight_list.append([[(math.sqrt((col-(self.get_grid_width()//2))**2 + (row-(self.get_grid_height()//2))**2)+2)*-1  for col in range(self.get_grid_width())] for row in range(self.get_grid_height())])

        return demo_weight_list

    def clear(self):
        """
        Set cells in obstacle grid to be empty
        Reset zombie and human lists to be empty
        """
        if DEBUG_CLR:
            print "clear(self)"
        poc_grid.Grid.clear(self)
        self._a_side_list = []
        self._human_list = []

    def set_floorplan(self, floorplan):
        for cell in floorplan:
            self.set_full(cell[0], cell[1])

    def set_aside(self, row, col):
        """
        Set A-Side to the given coordinate (zombie list)
        """
        #self._cells[row][col] = ZOMBIE
        self._a_side_list =[(row, col)]
        if DEBUG_SA:
            print "\nset_aside()"
            a_side = self._a_side_list[0]
            print a_side
            self.get_cabinet_number(a_side)

        #clear the distance field - it's not accurate for the current simulation
        self._distance_field = None

    def set_zside(self, row, col):
        """
        set z-side to the given coordinate (human list)
        """
        self._human_list=[(row, col)]
        
        #try to set the forbidden coordinates for this z-side with the cabinet NAME (string)
        #for the given z-side coordinate
        try:
            cabinet_number = self.get_cabinet_number(self._human_list[0])
            self.set_forbidden(cabinet_number)
        except Exception as e:
            print "bork bork, you're doing me a frighten"
            print "cabinet_number", cabinet_number
            print "Exception", e
            print "self._human_list[0]", self._human_list[0]
        
        if DEBUG_SZ:
            print "\nset_zside()"
            z_side = self._human_list[0]
            print z_side
            self.get_cabinet_number(z_side)
        if len(self._a_side_list) > 1:
            self._a_side_list = self._a_side_list[:1]
        
        #break out to set forbidden function - avoid tiles defined in the forbidden dictionary
        #self.set_forbidden(self._human_list[0])
        
        #clear the distance field - it's not accurate for the current simulation
        self._distance_field = None

    def get_z_side_list(self):
        return self._z_side_list
        
    def get_z_side_hall_list(self):
        """
        Takes no arguments, returns the dictionary of z-side and their associated hall numbers
        Key: Z-Side - String, Value: Hall Number - int
        """
        return self._z_side_hall_list
        
    def get_z_side_coord_list(self):
        """
        Takes no arguments, returns the dictionary of z-side and their associated coordinate offsets
        """
        return self._z_side_coord_list

    def get_cabinet_list(self, hall_number):
        """
        Use when hall number already known
        Takes a coordinate and returns the associated hall's cabinet dictionary
        Key: Cabinet ID, Value: Coordinate
        """
        try:
            assert hall_number < len(self._all_hall_cabinet_list) and hall_number >= 0
        except AssertionError as e:
            print e
            print "hall_number", hall_number, "outside known halls"
            print "len(self._all_hall_cabinet_list)", len(self._all_hall_cabinet_list)
            assert hall_number < len(self._all_hall_cabinet_list)
        hall_cabinets = self._all_hall_cabinet_list[hall_number]
        return hall_cabinets

    def get_all_cabinet_lists(self):
        """
        Use when coordinate not known
        Returns the list of all cabinet dictionaries
        """
        return self._all_hall_cabinet_list
        
    def get_reverse_cabinet_list(self, coordinate):
        """
        Use when coordinate already known
        Takes a coordinate and returns the associated hall's cabinet ID dictionary
        Key: Coordinate, Value: Cabinet ID
        """
        hall_id = self.get_hall_number(coordinate)
        try:
            hall_reverse_cabinets = self._all_hall_reverse_cabinet_list[hall_id]
        except IndexError:
            if DEBUG_GRCL:
                print IndexError, "Hall not defined for this coordinate"
            hall_reverse_cabinets = 0
        return hall_reverse_cabinets

    def get_all_reverse_cabinet_lists(self):
        """
        Use when coordinate not known
        Returns the list of all cabinet dictionaries ID dictionaries

        """
        return self._all_hall_reverse_cabinet_list

    def num_zombies(self):
        """
        Return number of zombies
        """
        #todo: refactor code according to this name
        return len(self._a_side_list)
        
    def num_grid_a_sides(self):
        return len(self._a_side_list)
        
    def num_grid_z_sides(self):
        return len(self._human_list)

    def zombies(self):
        """
        Generator that yields the zombies in the order they were
        added.
        """
        # replace with an actual generator
        index = 0
        len_zombie_list = len(self._a_side_list)
        #while index < len_zombie_list:
        while index < len(self._a_side_list):
            try:
                if DEBUG_Z:
                    print len(self._a_side_list)
                    print self._a_side_list
                    print index
                yield self._a_side_list[index]
                index += 1
            except IndexError as e:
                print e
        return

    def num_humans(self):
        """
        Return number of humans
        """
        return len(self._human_list)

    def humans(self):
        """
        Generator that yields the humans in the order they were added.
        """
        # replace with an actual generator
        index = 0
        len_human_list = len(self._human_list)
        while index < len_human_list:
            yield self._human_list[index]
            index += 1
        return

    def get_distance_field(self, entity_type):
        """
        Returns previously stored distance field.
        If no stored distance field, calculate and then return the distance field
        """
        #Only calculate the distance field if it's not already being calculated,
        #and there isn't already a valid one
        if self._distance_field == None:
            return self.compute_distance_field(entity_type)
        else:
            return self._distance_field


    def compute_distance_field(self, entity_type):
        """
        Function computes and returns a 2D distance field
        Distance at member of entity_list is zero
        Shortest paths avoid obstacles and use four-way distances

        Actually sets some variables internally as well as returning the distance field
        """

        grid_width = poc_grid.Grid.get_grid_width(self)
        grid_height = poc_grid.Grid.get_grid_height(self)
        self._visited = poc_grid.Grid(grid_height, grid_width)
        self._distance_field = [[grid_width*grid_height for dummy_col in range(0, grid_width)] for dummy_row in range(0, grid_height)]
        self._boundary_list = poc_queue.Queue()
        if entity_type == ZOMBIE:
            for entity in self._a_side_list:
                self._boundary_list.enqueue(entity)
        elif entity_type == HUMAN:
            for entity in self._human_list:
                self._boundary_list.enqueue(entity)
        else:
            print "Invalid Entity"
            return


        #set all initial distance to 0
        for boundary in self._boundary_list:
            self._distance_field[boundary[0]][boundary[1]] = 0

        #each step outward of unoccupied space gets +1 distance to their
        #corresponding field position
        if DEBUG_CDF:
            current_boundary_size = len(self._boundary_list)
        while len(self._boundary_list)>0:

            if DEBUG_CDF:
                next_boundary_size = len(self._boundary_list)
                if next_boundary_size > current_boundary_size*1.1 or next_boundary_size < current_boundary_size/1.1:
                    current_boundary_size = next_boundary_size
                    print "len(self._boundary_list)", len(self._boundary_list)
            boundary = self._boundary_list.dequeue()
            if boundary == None:
                return self._distance_field
            self._visited.set_full(boundary[0], boundary[1])
            neighbors = self.four_neighbors(boundary[0], boundary[1])
            for neighbor in neighbors:
                #check if already iterated over tile this calculation, if not add distance calculation
                #Also checks if neighbor distance > current cell distance and also adds it to the calculation
                if (self._visited.is_empty(neighbor[0], neighbor[1]) and self.is_empty(neighbor[0], neighbor[1])) \
                or (self._distance_field[neighbor[0]][neighbor[1]] > self._distance_field[boundary[0]][boundary[1]] and self.is_empty(neighbor[0], neighbor[1])):
                    self._distance_field[neighbor[0]][neighbor[1]] =  self._distance_field[boundary[0]][boundary[1]] + self.get_weight(boundary[0], boundary[1])
                    self._boundary_list.enqueue(neighbor)
                    self._visited.set_full(neighbor[0], neighbor[1])
        if DEBUG_CDF:
            for line in self._distance_field:
                print line
        return self._distance_field


        #print "w", grid_width
        #print "h", grid_height
        #for line in self._visited:
        #    print line


    def best_move(self, entity_type, moves_list, distance_list):
        """
        Find and return the optimal coordinate to move to
        """
        if DEBUG_BM:
            print "best_move()"
            print "BM - entity_type", entity_type
            print "BM - moves_list", moves_list
            print "BM - distance_list", distance_list

        #make sure there are some move entries in the list to check
        if len(moves_list) < 1:
            return False

        #setup initial results for comparison and storing of best move / distance
        best_distance = float("-inf")
        best_moves = []

        #Zombies want to move closer, humans further
        if entity_type == ZOMBIE:
            for dummy_idx in range(0, len(distance_list)):
                distance_list[dummy_idx] *= -1

        #Create list containing all coordinates that are "best" distance away
        for dummy_idx in range(0,len(moves_list)):
            if DEBUG_BM:
                print "BM - moves_list[",dummy_idx,"]", moves_list[dummy_idx]
            move_distance = distance_list[dummy_idx]
            if move_distance > best_distance:
                best_distance = move_distance
                best_moves = [(moves_list[dummy_idx])]
            if move_distance == best_distance:
                best_moves.append(moves_list[dummy_idx])

        #if more than one best move, return random entry from list of moves
        if len(best_moves) > 1 and type(best_moves) == list:
            return_move = best_moves[(random.randrange(len(best_moves)))]
        #if only one move, return the only move
        elif len(best_moves) == 1:
            return_move = best_moves[0]
        #If we got here, there are no valid moves
        else:
            return False
        if DEBUG_BM:
            print "best_moves", best_moves
            print "DEBUG_BM RETURNING:", return_move
        assert type(return_move) == tuple
        return return_move


    def move_humans(self, distance_field):
        """
        Really just sends HUMAN + distance field to move_entity
        """
        self._human_list = self.move_entity(HUMAN, distance_field)


    def move_zombies(self, distance_field):
        """
        Really just sends ZOMBIE + distance field to move_entity
        """
        self._human_list = self.move_entity(HUMAN, distance_field)


    def valid_move_gen(self, neighbor_function, location):
            """
            Should take a coordinate and an entity type and work out the valid
            moves it can make
            """
            if DEBUG_VM:
                print "valid_moves()"
                print "neighbor_function", neighbor_function
                print "location", type(location), location
            moves = neighbor_function(location[0], location[1])
            #Make sure standing still is an option
            moves.append(location)
            #make sure move coordinate isn't full and return
            #list comprehension style
            #return [move for move in moves if self.is_empty(move[0], move[1])]
            #generator style
            for move in moves:
                if self.is_empty(move[0], move[1]) and self.get_weight(move[0], move[1]) != float('inf') and move not in self._a_side_list:
                    if DEBUG_VM:
                        print "VM - yielding move", move
                    yield move

    def move_entity(self, entity_type, distance_field):
        """
        Try to abstract move function to take zombie or human
        as an argument and work accordingly
        """


        if DEBUG_ME:
            print "move_entity()"
            print "ME - entity_type", entity_type
            print "ME - distance_field", distance_field
        new_entity_list = []
        neighbor_function = 0
        if entity_type == HUMAN:
            entity_list = self._human_list
            neighbor_function = self.eight_neighbors
        elif entity_type == ZOMBIE:
            entity_list = self._a_side_list
            neighbor_function = self.four_neighbors
        for entity in entity_list:
            if DEBUG_ME:
                print "ME -entity_list", entity_list
                print "ME - neighbor_function", neighbor_function
            valid_moves = [move for move in self.valid_move_gen(neighbor_function, entity)]
            if DEBUG_ME:
                print "ME - valid_moves", valid_moves
            #working... but want to eliminate distances method
            #new_entity_list.append(self.best_move(entity_type, valid_moves, [distance for distance in self.distances(valid_moves, distance_field)] ))
            new_entity_list.append(self.best_move(entity_type, valid_moves, [distance_field[move[0]][move[1]] for move in valid_moves ] ))
        if DEBUG_ME:
            print "ME - new_entity_list", new_entity_list
        return new_entity_list

    def trace_z(self, distance_field):
        #set default value that should never occur
        current_trace_end = (-1, -1)

        #use some common sense and error checking, set the current end to the last position
        #in zombie list array
        if len(self._a_side_list) > 0:
            current_trace_end = self._a_side_list[-1]
        if current_trace_end == (-1, -1):
            print "Z-Side not set, breaking"
            return

        #while the trace isn't complete, call move_zombies to increment the trace
        #change to 'if' if you want the loop handled by the caller
        if current_trace_end != self._human_list[0]:
            if DEBUG_TZ:
                print "TZ current_trace_end", current_trace_end

            #Logic goes in here
            #Get valid moves (four neighbours), find best move, append best move to zombie list
            valid_moves = [move for move in self.valid_move_gen(self.four_neighbors, current_trace_end)]
            next_trace_move = self.best_move(ZOMBIE, valid_moves, [distance_field[move[0]][move[1]] for move in valid_moves] )
            #this happens if there are no valid moves, return from valid_moves()
            if next_trace_move == False:
                print "Encountered Dead End or Forbidden Path"
                return next_trace_move
            self._a_side_list.append(next_trace_move)
            time.sleep(0.06)

            #update end of list
            current_trace_end = self._a_side_list[-1]
            return True

    def detrace_z(self):
        if len(self._a_side_list) > 1:
            self._a_side_list.pop(1)
            return True
        else:
            return False

    def get_a_side(self):
        """
        Returns the coordinate of the current a-side
        A should be Zombies        
        """
        try:
            return self._a_side_list[0]
        except IndexError:
            return (0, 0)

    def get_z_side(self):
        """
        Returns the coordinate of the current a-side
        Z should be Humans        
        """
        try:
            return self._human_list[0]
        except IndexError:
            return (0, 0)

    def get_trace_end(self):
        """
        Returns the current end of a trace between a-z
        """
        return self._a_side_list[-1]

    def get_weight(self, row, col):
        """
        Weighted value (cost) of traversal
        Default traversable (non-full) value is 1
        """
        if self.is_empty(row, col):
            return self._cells[row][col]
        else:
            return float("inf")

    def set_weight(self, row, col, weight):
        """
        Sets the weight (cost of traversal) for a given coordinate
        :param row: y coord, top = 0
        :param col: x coord, left = 0
        :param weight: cost of traversal
        :return: None
        """
        if self.is_empty(row, col):
            self._cells[row][col] = weight
            #adjust the known stored min / max weight values
            if weight != float('inf'):
                if weight > self._max_traversable_weight:
                    self._max_traversable_weight = weight
                if weight < self._min_traversable_weight:
                    self._min_traversable_weight = weight
            if DEBUG_SW:
                print "(", row, ",", col, ") =", weight
        else:
            print "Trying to set weight of a non-traversable location"
            assert False
            
    def get_weight_map(self):
        """
        Returns the weight map for this simulation
        :return: 2 dimensional list of weights mapped to grid coordinates
        """
        weight_map = [[self.get_weight(row, col) for col in range(self.get_grid_width())] for row in range(self.get_grid_height())]
        return weight_map
        
    def set_weight_map(self, weight_map):
        """
        Takes a weight map and sets the grid values accordingly
        :param weight_map: 2 dimensional list of weights mapped to grid coordinates
        :return:
        """
        self.reset_max_traversable_weight()
        self.reset_min_traversable_weight()
        try:
            for row in range(len(weight_map)):
                for col in range(len(weight_map[0])):
                    if self.is_empty(row, col):
                        self.set_weight(row, col, weight_map[row][col])
        except Exception as e:
            print "bad weight map"
            print e
            
    def store_current_weight_map(self):
        self._initial_weight_list = self.get_weight_map()
        
    def load_stored_weight_map(self):
        """
        Map the stored weight grid "_initial_weight_list" onto the current 
        display grid.
        """
        self.reset_max_traversable_weight()
        self.reset_min_traversable_weight()
        for row in range(self.get_grid_height()):
            for col in range(self.get_grid_width()):
                if self.is_empty(row, col):
                    self.set_weight(row, col, self._initial_weight_list[row][col])

    def load_stored_tile_weight(self, row, col):
        self.set_weight(row, col, self._initial_weight_list[row][col])

    def load_demo_tile_weight(self, row, col):
        self.set_weight(row, col, self._demo_weight_list[row][col])

    def get_random_demo_weight_list(self):
        self._current_demo_weight_list = random.randrange(len(self._demo_weight_list))
        #use even indexes only
        if self._current_demo_weight_list %2 == 1:
            self._current_demo_weight_list -= 1
        return self._demo_weight_list[self._current_demo_weight_list]
    
    def get_demo_weight_list(self, index):
        return self._demo_weight_list[index]
        
    def get_next_demo_weight_list(self):
        self._current_demo_weight_list += 3
        self._current_demo_weight_list %= len(self._demo_weight_list)
        return self._demo_weight_list[self._current_demo_weight_list]

    def get_number_of_weight_lists(self):
        return len(self._demo_weight_list)

    def get_default_weight(self):
        return self._default_weight
        
    def get_max_traversable_weight(self):
        return self._max_traversable_weight
        
    def get_min_traversable_weight(self):
        return self._min_traversable_weight
        
    def reset_max_traversable_weight(self):
        self._max_traversable_weight = self._default_weight
        
    def reset_min_traversable_weight(self):
        self._min_traversable_weight = self._default_weight
        
    def get_relative_traversable_weight(self, weight):
        relative_range = self.get_max_traversable_weight() - self.get_min_traversable_weight()
        if relative_range < 1:
            return 0.001
        else:
            result = float(weight) / float(relative_range)
            return result

    def set_default_weight(self, weight):
        self._default_weight = weight

    def set_forbidden(self, z_side):
        """
        Takes a string name of the z-side cabinet
        Checks against a dictionary of pre-defined locations as forbidden to traverse for that z-side
        Sets the forbidden tiles' weight to inf
        """
        if DEBUG_SF:
            print "sf z_side:", z_side
            
        #First, reset all weights to initial values
        for col in range(self.get_grid_width()):
            for row in range(self.get_grid_height()):
                if self.is_empty(row, col):
                    self.set_weight(row, col, (self._initial_weight_list[row][col]))
                    
        #look up list of forbidden tiles for this z-side
        try:
            forbidden_tiles = self._forbidden_list[z_side]
        except KeyError as e:
            forbidden_tiles = []
            if DEBUG_SF:
                print e
        #set the forbidden tiles weight to infinity
        for tile in forbidden_tiles:
            if DEBUG_SF:
                print "Current tile", tile
            if self.is_empty(tile[0], tile[1]):
                self.set_weight(tile[0], tile[1], float("inf"))

        if DEBUG_SF:
            print "forbidden_tiles", forbidden_tiles
            print "weight map"
            for row in range(self.get_grid_height()):
                this_row = ""
                for col in range(self.get_grid_width()):
                    if self.get_weight(row, col) < float("inf"):
                        this_row += " " + str(self.get_weight(row, col)) + "  "
                    else:
                        this_row += str(self.get_weight(row, col)) + " "
                print this_row
        
    def invert_dictionary(self, dictionary):
        inverted = {v: k for k, v in dictionary.items()}        
        return inverted
        
    def get_hall_number(self, coordinate):
        """
        Use when coordinate already known
        Takes a grid coordinate and returns the hall ID
        """
        hall1_offset = (1, 1)
        hall1_dim = (28, 73)
        
        self._hall_list = ((hall1_offset, hall1_dim), )

        if DEBUG_GHN:
            print "len(self._hall_list)", len(self._hall_list)

        #Set the return variable 'hall' to -1 in case coordinate is not found
        hall = -1
        for dummy_x in range(len(self._hall_list)):
            this_hall_offset = self._hall_list[dummy_x][0]
            this_hall_dim = self._hall_list[dummy_x][1]
            if coordinate[0] >= this_hall_offset[0] and coordinate[0] <= this_hall_offset[0]+this_hall_dim[0] and \
            coordinate[1] >= this_hall_offset[1] and coordinate[0] <= this_hall_offset[1]+this_hall_dim[1]:
                hall=dummy_x
        return hall


    def set_hall_number(self, hall_number, hall_offset, hall_dimensions):
        """

        :param hall_number: Int - ID number of the hall
        :param hall_offset: Tuple (int, int) - coordinate of starting position for the hall
        :param hall_dimensions: Tuple (int, int) - height, width of the hall
        :return: None
        """
        new_hall_start_row = hall_offset[0]
        new_hall_start_col = hall_offset[1]
        new_hall_height = hall_dimensions[0]
        new_hall_width = hall_dimensions[1]
        for hall in self._hall_list:
            overlap = False
            start_row = self._hall_list[hall][0][0]
            start_col = self._hall_list[hall][0][1]
            hall_height = self._hall_list[hall][1][0]
            hall_width = self._hall_list[hall][1][1]

            #check for vertical overlap
            if (new_hall_start_row <= start_row+hall_height and new_hall_start_row >= start_row) or \
            (new_hall_start_row+new_hall_height <= start_row+hall_height and new_hall_start_row+new_hall_height >= start_row):
                #check for horizontal overlap
                if (new_hall_start_col <= start_col+hall_width and new_hall_start_col >= start_col) or \
                (new_hall_start_col+new_hall_width <= start_col+hall_width and new_hall_start_col+new_hall_width >= start_col):
                    #overlap confirmed
                    overlap = True

            if not overlap:
                self._hall_list[hall_number] = ((hall_offset), (hall_dimensions))

        
    def get_cabinet_number(self, coordinate):
        """
        Use when coordinate already known
        Try to match a coordinate to a hall number
        Then match within that halls' dictionary to a distinct cabinet
        """
        hall_number = self.get_hall_number(coordinate)
        if type(hall_number) == int:
            this_cabinet_list = self.get_reverse_cabinet_list(coordinate)   
            try:
                cabinet = this_cabinet_list[coordinate]
                return cabinet
            except KeyError as e:
                if DEBUG_GCN:
                    print KeyError, "Cabinet not defined at this coordinate", coordinate
            except TypeError as e:
                if DEBUG_GCN:
                    print TypeError
        return ""

    def get_number_paths_calculated(self):
        #number_of_paths = len(self._boundary_list)
        return len(self._boundary_list)

    def difference_of_lists(self, list1, list2):
        temp_list = []
        for item in list1:
            if item not in list2:
                temp_list.append(item)
            else:
                pass
        return temp_list

    def all_paths(self, clear_lines, excluded_tiles=None):
        #global paths_list
        paths = []
        for line_point in clear_lines:
            for coord in self.line(line_point[0], line_point[1]):
                paths.append(coord)
        return self.difference_of_lists(paths, excluded_tiles)

    def panel_to_index(self, y, x):
        return (y-1, x-1)

    def line(self, start_panel, end_panel):
        start = self.panel_to_index(start_panel[0], start_panel[1])
        end = self.panel_to_index(end_panel[0], end_panel[1])
        line = []
        increment = 1
        if start[0] > end[0]:
            increment = -1
        elif start[1] > end[1]:
            increment = -1
        if start[0] != end[0]:
            line = [(y_pos, start[1]) for y_pos in range(start[0], end[0]+1, increment)]
        elif start[1] != end[1]:
            line = [(start[0], x_pos) for x_pos in range(start[1], end[1]+1, increment)]
        return line