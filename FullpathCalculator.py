"""

@author: andrewscott, with some code from http://online.rice.edu/courses/principles-of-computing-2/

"""

import random
import poc_grid
import poc_queue
import poc_zombie_gui
import time

try:
    import codeskulptor
    #codeskulptor.set_timeout(20)
except ImportError as exp:
#except Error as exp:
    #print "Codeskulptor not found"
    #print exp
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

# global constants
EMPTY = 0
FULL = 1
FOUR_WAY = 0
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7

class Apocalypse(poc_grid.Grid):
    """
    Class for simulating zombie pursuit of human on grid with
    obstacles
    """

    def __init__(self, grid_height, grid_width, obstacle_list = None,
                 zombie_list = None, human_list = None):
        """
        Create a simulation of given size with given obstacles,
        humans, and zombies
        """
        poc_grid.Grid.__init__(self, grid_height, grid_width)
        if obstacle_list != None:
            for cell in obstacle_list:
                self.set_full(cell[0], cell[1])
        if zombie_list != None:
            self._zombie_list = list(zombie_list)
        else:
            self._zombie_list = []
        if human_list != None:
            self._human_list = list(human_list)
        else:
            self._human_list = []

        self._z_side_list = []
        self._z_side_hall_list = {}
        self._z_side_coord_list = {}
        self._forbidden_list = {}
        self._distance_field = None
        
        
        #these should contain the dictionary items of cabinet lists, not their individual key / value pairs
        self._all_hall_cabinet_list = []
        self._all_hall_reverse_cabinet_list = []

    def clear(self):
        """
        Set cells in obstacle grid to be empty
        Reset zombie and human lists to be empty
        """
        poc_grid.Grid.clear(self)
        self._zombie_list = []
        self._human_list = []

    def set_aside(self, row, col):
        """
        Set A-Side to the given coordinate (zombie list)
        """
        #self._cells[row][col] = ZOMBIE
        self._zombie_list =[(row, col)]
        if DEBUG_SA:
            print "\nset_aside()"
            a_side = self._zombie_list[0]
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
            self.set_forbidden(self.get_cabinet_number(self._human_list[0])) 
        except:
            print "error setting z-side"
        
        if DEBUG_SZ:
            print "\nset_zside()"
            z_side = self._human_list[0]
            print z_side
            self.get_cabinet_number(z_side)
        if len(self._zombie_list) > 1:
            self._zombie_list = self._zombie_list[:1]
        
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
        hall_reverse_cabinets = self._all_hall_reverse_cabinet_list[hall_id]
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
        return len(self._zombie_list)

    def zombies(self):
        """
        Generator that yields the zombies in the order they were
        added.
        """
        # replace with an actual generator
        index = 0
        len_zombie_list = len(self._zombie_list)
        #while index < len_zombie_list:
        while index < len(self._zombie_list):
            try:
                if DEBUG_Z:
                    print len(self._zombie_list)
                    print self._zombie_list
                    print index
                yield self._zombie_list[index]
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
            for entity in self._zombie_list:
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
        while len(self._boundary_list)>0:
            #if DEBUG_CDF:
            #    print "len(self._boundary_list)", len(self._boundary_list)
            boundary = self._boundary_list.dequeue()
            if boundary == None:
                return self._distance_field
            self._visited.set_full(boundary[0], boundary[1])
            #self._distance_field[boundary[0], boundary[1]] = distance
            neighbors = self.four_neighbors(boundary[0], boundary[1])
            for neighbor in neighbors:
                #check if already iterated over tile this calculation, if not add distance calculation
                #if self._visited.is_empty(neighbor[0], neighbor[1]) and self.is_empty(neighbor[0], neighbor[1]):
                #modified version, checks if neighbor distance > current cell distance and also adds it to the calculation
                if self._visited.is_empty(neighbor[0], neighbor[1]) and self.is_empty(neighbor[0], neighbor[1]) \
                        or self._distance_field[neighbor[0]][neighbor[1]] > self._distance_field[boundary[0]][boundary[1]] and self.is_empty(neighbor[0], neighbor[1]):
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

        #Why is this here again?!
        """
        try:
            best_moves = list(moves_list[-1])
        except TypeError as exp:
            print "best_move() exception"
            print type(moves_list)
            print moves_list
            print exp
        """

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
                if self.is_empty(move[0], move[1]) and self.get_weight(move[0], move[1]) != float('inf') and move not in self._zombie_list:
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
            entity_list = self._zombie_list
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
        if len(self._zombie_list) > 0:
            current_trace_end = self._zombie_list[-1]
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
            self._zombie_list.append(next_trace_move)
            time.sleep(0.06)

            #update end of list
            current_trace_end = self._zombie_list[-1]
            return True

    def get_a_side(self):
        """
        Returns the coordinate of the current a-side
        A should be Zombies        
        """
        return self._zombie_list[0]
        #return self._human_list[0]

    def get_z_side(self):
        """
        Returns the coordinate of the current a-side
        Z should be Humans        
        """
        return self._human_list[0]
        #return self._zombie_list[0]

    def get_trace_end(self):
        """
        Returns the current end of a trace between a-z
        """
        return self._zombie_list[-1]

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
        if self.is_empty(row, col):
            self._cells[row][col] = weight
            if DEBUG_SW:
                print "(", row, ",", col, ") =", weight
        else:
            print "Trying to set weight of a non-traversable location"
            assert False

    def set_forbidden(self, z_side):
        """
        Takes a string name of the z-side cabinet
        Checks againsta dictionary of pre-defined locations as forbidden to traverse for that z-side
        Sets the forbidden tiles' weight to inf
        """
        if DEBUG_SF:
            print "sf z_side:", z_side
        #First, reset all weights to default of 1
        for row in range(self.get_grid_height()):
            for col in range(self.get_grid_width()):
                if self.is_empty(row, col):
                    self.set_weight(row, col, 1)
                    
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
        #inverted = dict([v, k] for k, tuple(v) in dictionary.iteritems())
        inverted = {v: k for k, v in dictionary.items()}        
        return inverted
        
    def get_hall_number(self, coordinate):
        """
        Use when coordinate already known
        Takes a grid coordinate and returns the hall ID
        """
        hall1_offset = (1, 1)
        hall1_dim = (28, 73)
        
        hall_list = ((hall1_offset, hall1_dim), )
        
        #Set the return variable 'hall' to empty string in case coordinate is not fount
        hall = ""
        for dummy_x in range(len(hall_list)):
            this_hall_offset = hall_list[dummy_x][0]
            this_hall_dim = hall_list[dummy_x][1]
            if coordinate[0] >= this_hall_offset[0] and coordinate[0] <= this_hall_offset[0]+this_hall_dim[0] and \
            coordinate[1] >= this_hall_offset[1] and coordinate[0] <= this_hall_offset[1]+this_hall_dim[1]:
                hall=dummy_x
        return hall
        
        
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
                #print "Cabinet", cabinet
                return cabinet
            except KeyError as e:
                #print "Cabinet not mapped at this coordinate"
                pass
        return ""


height = 33
width = 75
border = 1
#paths_list = set()
def difference_list(list1, list2):
    temp_list = []
    for item in list1:
        if item not in list2:
            temp_list.append(item)
        else:
            #print "excluding", item
            pass
    return temp_list

def panel_to_index(y, x):
    return (y-1, x-1)

def line(start_panel, end_panel):
    start = panel_to_index(start_panel[0], start_panel[1])
    end = panel_to_index(end_panel[0], end_panel[1])
    #print "start", start
    #print "end", end
    line = []
    increment = 1
    if start[0] > end[0]:
        increment = -1
    elif start[1] > end[1]:
        increment = -1
    #print "increment", increment
    if start[0] != end[0]:
        #print "vertical"
        line = [(y_pos, start[1]) for y_pos in range(start[0], end[0]+1, increment)]
    elif start[1] != end[1]:
        #print "horizontal"
        line = [(start[0], x_pos) for x_pos in range(start[1], end[1]+1, increment)]
    #print "line", line

    return line

def all_paths():
    #global paths_list
    paths = []
    
    #clear_cols and clear_rows depricated - doesn't work with changing grid size
    #full width / heigth areas
    #clear_rows = [2, 16, 29]
    clear_rows = []    
    #clear_cols = [2, 5, 8, 13, 16, 21, 24, 29, 32, 37, 40, 47, 50, 55, 58, 63, 66, 71, 74]
    clear_cols = []
    
                  #full-hall horizontal paths
    clear_lines = [((2, 2), (2, 74)),
                  ((16, 2), (16, 74)),
                  ((29, 2), (29, 74)),
                  #full-hall vertical paths
                  ((2, 2), (29, 2)),
                  ((2, 5), (29, 5)),
                  ((2, 8), (29, 8)),
                  ((2, 13), (29, 13)),
                  ((2, 16), (29, 16)),
                  ((2, 21), (29, 21)),
                  ((2, 24), (29, 24)),
                  ((2, 29), (29, 29)),
                  ((2, 32), (29, 32)),
                  ((2, 37), (29, 37)),
                  ((2, 40), (29, 40)),
                  ((2, 47), (29, 47)),
                  ((2, 50), (29, 50)),
                  ((2, 55), (29, 55)),
                  ((2, 58), (29, 58)),
                  ((2, 63), (29, 63)),
                  ((2, 66), (29, 66)),
                  ((2, 71), (29, 71)),
                  ((2, 74), (29, 74)),
                  #additional paths 
                  ((2, 69), (16, 69)),
                  ((2, 70), (16, 70)),
                  ((2, 73), (16, 73)),
                  ((2, 74), (16, 74)),
                  ((6, 69), (6, 74)),
                  ((9, 69), (9, 74)),
                  ((14, 69), (14, 74)),
                  ((15, 69), (15, 74)),
                  ((16, 69), (16, 74))]
    #inner methods to return coordinates
    def row_path(row):
        return [(row-1, x_pos) for x_pos in range(border, width-border)]
    def col_path(col):
        return [(y_pos, col-1) for y_pos in range(border, height-border)]
    for row in clear_rows:
        for coord in row_path(row):
            #print coord
            paths.append(coord)
    for col in clear_cols:
        for coord in col_path(col):
            paths.append(coord)
    for line_point in clear_lines:
        for coord in line(line_point[0], line_point[1]):
            paths.append(coord)
    #print paths
    #for cell in paths_list:
    #    yield cell
    #remove some extra cells
    #extra_paths = ((1, 74), (28, 74))
    #extra_paths = [(1, 74), (15, 74), (28, 74)]
    remove_paths = [panel_to_index(2, 75), panel_to_index(16, 75), panel_to_index(29, 75)]
    return difference_list(paths, remove_paths)

racetrack =  all_paths()
no_path = []
for grid_y in range(0, height):
    for grid_x in range(0, width):
        #no_path.add((grid_y, grid_x))
        no_path.append((grid_y, grid_x))
#print no_path

floorplan = difference_list(no_path, racetrack)

#instantiate the simulation
#simulation = Apocalypse(height, width, list(floorplan), zlist, hlist)
simulation = Apocalypse(height, width, list(floorplan))


#define coord dictionaries
simulation._z_side_list = ("001-A", "001-B", "002-A", "002-B")
simulation._z_side_coord_list = {'001-A': (1, 1), '001-B': (1, 1), '002-A': (1, 1), '002-B': (1, 1)}
simulation._z_side_hall_list = {'001-A': 0, '001-B': 0, '002-A': 0, '002-B': 0}
hall_1_cabinet_list = {'001-A': (13, 70), '001-B': (12, 70), '002-B': (5, 70), '002-A': (4, 70)}

#this forbidden list only blocks the entrance areas
simulation._forbidden_list = {'001-A': ((1, 66), (1, 67), (28, 66), (28, 67)),
                                '001-B': ((1, 66), (1, 67), (28, 66), (28, 67)),
                                '002-A': ((15, 66), (15, 67)),
                                '002-B': ((15, 66), (15, 67))}

#create and add the midpoint to the forbidden list of cabinets that don't use
#the midpoint as an access path: traces should run around the outside of the track                                
midpoint = tuple(line((16, 2), (16, 68)))
two_one_six_a = simulation._forbidden_list['002-A']
two_one_six_b = simulation._forbidden_list['002-B']
simulation._forbidden_list['002-A'] = midpoint + two_one_six_a
simulation._forbidden_list['002-B'] = midpoint + two_one_six_b 

#using coordinate for cabinet 801                                
offset = (27, 46)
row_800 = {'801': (offset[0]-0, offset[1]), 
           '802': (offset[0]-1, offset[1]), 
           '803': (offset[0]-2, offset[1]), 
           '804': (offset[0]-3, offset[1]), 
           '805': (offset[0]-4, offset[1]), 
           '806': (offset[0]-5, offset[1]), 
           '807': (offset[0]-6, offset[1]), 
           '808': (offset[0]-7, offset[1]), 
           '809': (offset[0]-8, offset[1]),
           '810': (offset[0]-9, offset[1]), 
           '811': (offset[0]-10, offset[1]), 
           '812': (offset[0]-11, offset[1]), 
           '813': (offset[0]-12, offset[1]), 
           '814': (offset[0]-13, offset[1]), 
           '815': (offset[0]-14, offset[1]), 
           '816': (offset[0]-15, offset[1]), 
           '817': (offset[0]-16, offset[1]), 
           '818': (offset[0]-17, offset[1]), 
           '819': (offset[0]-18, offset[1]), 
           '820': (offset[0]-19, offset[1]), 
           '821': (offset[0]-20, offset[1]), 
           '822': (offset[0]-21, offset[1]), 
           '823': (offset[0]-22, offset[1]), 
           '824': (offset[0]-23, offset[1]), 
           '825': (offset[0]-24, offset[1]), 
           '826': (offset[0]-25, offset[1])}

#using coordinate for cabinet 701   
offset = (27, 49)          
row_700 = {'701': (offset[0]-0, offset[1]), 
           '702': (offset[0]-1, offset[1]), 
           '703': (offset[0]-2, offset[1]), 
           '704': (offset[0]-3, offset[1]), 
           '705': (offset[0]-4, offset[1]), 
           '706': (offset[0]-5, offset[1]), 
           '707': (offset[0]-6, offset[1]), 
           '708': (offset[0]-7, offset[1]), 
           '709': (offset[0]-8, offset[1]),
           '710': (offset[0]-9, offset[1]), 
           '711': (offset[0]-10, offset[1]), 
           '712': (offset[0]-11, offset[1]), 
           '713': (offset[0]-12, offset[1]), 
           '714': (offset[0]-13, offset[1]), 
           '715': (offset[0]-14, offset[1]), 
           '716': (offset[0]-15, offset[1]), 
           '717': (offset[0]-16, offset[1]), 
           '718': (offset[0]-17, offset[1]), 
           '719': (offset[0]-18, offset[1]), 
           '720': (offset[0]-19, offset[1]), 
           '721': (offset[0]-20, offset[1]), 
           '722': (offset[0]-21, offset[1]), 
           '723': (offset[0]-22, offset[1]), 
           '724': (offset[0]-23, offset[1]), 
           '725': (offset[0]-24, offset[1]), 
           '726': (offset[0]-25, offset[1])}
           
#using coordinate for cabinet 601   
offset = (27, 54)          
row_600 = {'601': (offset[0]-0, offset[1]), 
           '602': (offset[0]-1, offset[1]), 
           '603': (offset[0]-2, offset[1]), 
           '604': (offset[0]-3, offset[1]), 
           '605': (offset[0]-4, offset[1]), 
           '606': (offset[0]-5, offset[1]), 
           '607': (offset[0]-6, offset[1]), 
           '608': (offset[0]-7, offset[1]), 
           '609': (offset[0]-8, offset[1]),
           '610': (offset[0]-9, offset[1]), 
           '611': (offset[0]-10, offset[1]), 
           '612': (offset[0]-11, offset[1]), 
           '613': (offset[0]-12, offset[1]), 
           '614': (offset[0]-13, offset[1]), 
           '615': (offset[0]-14, offset[1]), 
           '616': (offset[0]-15, offset[1]), 
           '617': (offset[0]-16, offset[1]), 
           '618': (offset[0]-17, offset[1]), 
           '619': (offset[0]-18, offset[1]), 
           '620': (offset[0]-19, offset[1]), 
           '621': (offset[0]-20, offset[1]), 
           '622': (offset[0]-21, offset[1]), 
           '623': (offset[0]-22, offset[1]), 
           '624': (offset[0]-23, offset[1]), 
           '625': (offset[0]-24, offset[1]), 
           '626': (offset[0]-25, offset[1])}
           
#using coordinate for cabinet 501   
offset = (27, 57)          
row_500 = {'501': (offset[0]-0, offset[1]), 
           '502': (offset[0]-1, offset[1]), 
           '503': (offset[0]-2, offset[1]), 
           '504': (offset[0]-3, offset[1]), 
           '505': (offset[0]-4, offset[1]), 
           '506': (offset[0]-5, offset[1]), 
           '507': (offset[0]-6, offset[1]), 
           '508': (offset[0]-7, offset[1]), 
           '509': (offset[0]-8, offset[1]),
           '510': (offset[0]-9, offset[1]), 
           '511': (offset[0]-10, offset[1]), 
           '512': (offset[0]-11, offset[1]), 
           '513': (offset[0]-12, offset[1]), 
           '514': (offset[0]-13, offset[1]), 
           '515': (offset[0]-14, offset[1]), 
           '516': (offset[0]-15, offset[1]), 
           '517': (offset[0]-16, offset[1]), 
           '518': (offset[0]-17, offset[1]), 
           '519': (offset[0]-18, offset[1]), 
           '520': (offset[0]-19, offset[1]), 
           '521': (offset[0]-20, offset[1]), 
           '522': (offset[0]-21, offset[1]), 
           '523': (offset[0]-22, offset[1]), 
           '524': (offset[0]-23, offset[1]), 
           '525': (offset[0]-24, offset[1]), 
           '526': (offset[0]-25, offset[1])}
           
#using coordinate for cabinet 401   
offset = (27, 62)          
row_400 = {'407': (offset[0]-6, offset[1]), 
           '408': (offset[0]-7, offset[1]), 
           '409': (offset[0]-8, offset[1]),
           '410': (offset[0]-9, offset[1]), 
           '411': (offset[0]-10, offset[1]), 
           '412': (offset[0]-11, offset[1]), 
           '413': (offset[0]-12, offset[1]), 
           '414': (offset[0]-13, offset[1]), 
           '415': (offset[0]-14, offset[1]), 
           '416': (offset[0]-15, offset[1]), 
           '417': (offset[0]-16, offset[1]), 
           '418': (offset[0]-17, offset[1]), 
           '419': (offset[0]-18, offset[1]), 
           '420': (offset[0]-19, offset[1]), 
           '421': (offset[0]-20, offset[1]), 
           '422': (offset[0]-21, offset[1]), 
           '423': (offset[0]-22, offset[1]), 
           '424': (offset[0]-23, offset[1]), 
           '425': (offset[0]-24, offset[1]), 
           '426': (offset[0]-25, offset[1])}
          
#using coordinate for cabinet 301   
offset = (27, 65)          
row_300 = {'307': (offset[0]-6, offset[1]), 
           '308': (offset[0]-7, offset[1]), 
           '309': (offset[0]-8, offset[1]),
           '310': (offset[0]-9, offset[1]), 
           '311': (offset[0]-10, offset[1]), 
           '312': (offset[0]-11, offset[1]), 
           '313': (offset[0]-12, offset[1]), 
           '314': (offset[0]-13, offset[1]), 
           '315': (offset[0]-14, offset[1]), 
           '316': (offset[0]-15, offset[1]), 
           '317': (offset[0]-16, offset[1]), 
           '318': (offset[0]-17, offset[1]), 
           '319': (offset[0]-18, offset[1]), 
           '320': (offset[0]-19, offset[1]), 
           '321': (offset[0]-20, offset[1]), 
           '322': (offset[0]-21, offset[1]), 
           '323': (offset[0]-22, offset[1]), 
           '324': (offset[0]-23, offset[1]), 
           '325': (offset[0]-24, offset[1]), 
           '326': (offset[0]-25, offset[1])}
           
#combine all lists of cabinet coordinates           
hall_1_cabinet_list.update(row_300)
hall_1_cabinet_list.update(row_400)
hall_1_cabinet_list.update(row_500)
hall_1_cabinet_list.update(row_600)
hall_1_cabinet_list.update(row_700)
hall_1_cabinet_list.update(row_800)

#create the reverse-lookup cabinet list
hall1_reverse_cabinet_list = simulation.invert_dictionary(hall_1_cabinet_list)

#add the hall dictionaries to the 'all' lists
simulation._all_hall_cabinet_list.append(hall_1_cabinet_list)
simulation._all_hall_reverse_cabinet_list.append(hall1_reverse_cabinet_list)
           
#Starting points for a + z sides
starting_a = [27, 54]
starting_z = simulation._all_hall_cabinet_list[0][simulation._z_side_list[-1]]
simulation.set_aside(starting_a[0], starting_a[1])
simulation.set_zside(starting_z[0], starting_z[1])          

poc_zombie_gui.run_gui(simulation)
#try:
#    poc_zombie_gui.run_gui(Apocalypse(30, 40))
#except:
#    print "gui initialization failed"
#test = Apocalypse(30, 40)
"""
(27, 46) (2, 46) = 801 - 826
(27, 49) (2, 49) = 701 - 726
(27, 54) (2, 54) = 601 - 626
(27, 57) (2, 57) = 501 - 526
(14, 62) (2, 62) = 414 - 426
(14, 65) (2, 65) = 314 - 326

(27, 70) (16, 70) = 201 - 209 (9 cabinets / 12 tiles)
(27, 73) (16, 73) = 101 - 109 (9 cabinets / 12 tiles)

(14, 73) (3, 73) = 111 - 118 (8 cabinets / 12 tiles)
(13, 70) = 001-B
(12, 70) = 001-A
(5, 70) = 002-B
(4, 70) = 002-A
"""