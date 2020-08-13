"""
Zombie Apocalypse mini-project
Click "Mouse click" button to toggle items added by mouse clicks
Zombies have four way movement, humans have eight way movement
"""
import time
import threading
from multiprocessing import Queue
try:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
except ImportError:
    import simplegui

# Global constants
CLS = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
#CLS = ""
EMPTY = 0
FULL = -1
HAS_ZOMBIE = 2
HAS_HUMAN = 4
FOUR_WAY = 0
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7
SLACK_LENGTH = 5.0
TRACING = False
TIMER_INTERVAL = float(0.3)
CELL_COLORS = {EMPTY: "Yellow",
               FULL: "Black",
               HAS_ZOMBIE: "Red",
               HAS_HUMAN: "Green",
               HAS_ZOMBIE|HAS_HUMAN: "Purple"}

NAME_MAP = {OBSTACLE: "Remove Path",
            HUMAN: "Z-Side",
            ZOMBIE: "A-Side",
            EMPTY: "Add Path: wt. 1"}

# GUI constants
CELL_SIZE = 10
LABEL_STRING = "Mouse Click : "
Z_SIDE_LIST_INDEX = 0
Z_SIDE_LIST_LENGTH = 0

DEBUG_TZ = False
DEBUG_STLK = True


class ApocalypseGUI:
    """
    Container for interactive content
    """

    def __init__(self, simulation):
        """
        Create frame and timers, register event handlers
        """
        self._simulation = simulation
        self._grid_height = self._simulation.get_grid_height()
        self._grid_width = self._simulation.get_grid_width()
        self._frame = simplegui.create_frame("Weighted Distance Calculator",
                                             self._grid_width * CELL_SIZE,
                                             self._grid_height * CELL_SIZE)
        self._frame.set_canvas_background("White")
        #self._frame.add_button("Clear all", self.clear, 200)
        self._item_type = ZOMBIE
        global Z_SIDE_LIST_LENGTH
        Z_SIDE_LIST_LENGTH = len(self._simulation.get_z_side_list())
        global Z_SIDE_LIST_INDEX
        Z_SIDE_LIST_INDEX = Z_SIDE_LIST_LENGTH-1

        label = LABEL_STRING + NAME_MAP[self._item_type]
        self._item_label = self._frame.add_button(label,
                                                  self.toggle_item, 200)
        #Some ugly code, consider reworking this.
        #Takes z_side_list from simulation, increments the GUIs index and modulos against the length of the list
        z_label = "Set Z to " + self._simulation.get_z_side_list()[(Z_SIDE_LIST_INDEX+1) % Z_SIDE_LIST_LENGTH]
        self._z_button_label = self._frame.add_button(z_label, self.toggle_z_side, 200)
        self._frame.add_button("Calculate Length", self.calculate, 200)
        self._frame.add_button("Trace Path", self.stalk, 200)
        self._text_a_hall = self._frame.add_input('A-Hall', self.input_aside_hall, 200)
        self._text_a_cabinet = self._frame.add_input('A-Cabinet', self.input_aside_cabinet, 200)
        self._text_z_hall = self._frame.add_input('Z-Hall', self.input_zside_hall, 200)
        self._text_z_cabinet = self._frame.add_input('Z-Cabinet', self.input_zside_cabinet, 200)
        self._frame.add_button("Input A+Z Sides", self.process_input_a_z_sides, 200)
        self._frame.set_mouseclick_handler(self.add_item)
        self._frame.set_draw_handler(self.draw)
        
        #queue for storing thread results
        self._result_queue = Queue()
        
        #flag to keep track if input is currently being processed
        self._processing_input = False
        
        #hopefully adding this is going to help tips
        #self._distance_field_thread = threading.Thread()


    def start(self):
        """
        Start frame
        """
        self._frame.start()


    def clear(self):
        """
        Event handler for button that clears everything
        """
        self._simulation.clear()
        
    def input_aside_hall(self):
        return self._text_a_hall.get_text()
    
    def input_aside_cabinet(self):
        return self._text_a_cabinet.get_text()
    
    def input_zside_hall(self):
        return self._text_z_hall.get_text()
    
    def input_zside_cabinet(self):
        return self._text_z_cabinet.get_text()

    def process_input_a_z_sides(self):
        """
        Takes the text box inputs for a + z side details and sets the grid coordinates accordingly
        """
        #Bool for checking valid inputs. Assume initually correct.
        print CLS
        valid_a = True
        valid_z = True
        a_hall = -1
        z_hall = -1
        error_string_a = ""
        error_string_z = ""
        number_of_halls = len(self._simulation.get_all_cabinet_lists())
        max_hall_ID = number_of_halls - 1

        #Takes text from the gui input box, converts to int, deduct 1 to align with list index
        try:
            a_hall = int(self.input_aside_hall()) - 1
        except ValueError as e:
            valid_a = False
        try:
            z_hall = int(self.input_zside_hall()) - 1
        except ValueError as e:
            valid_z = False

        #check if hall numbers are between 1 and the length of the number of cabinet lists
        #(one cabinet list exists per hall)
        if a_hall < 0 or a_hall > max_hall_ID:
            if a_hall == -1:
                a_hall = "Blank"
            #this is just for 'nice' error reporting for the user
            else:
                a_hall += 1
            error_string_a += ("Unknown a_hall: " + str(a_hall) + "\n")
            valid_a = False
        if z_hall < 0 or z_hall > max_hall_ID:
            if z_hall == -1:
                z_hall = "Blank"
            #this is just for 'nice' error reporting for the user
            else:
                z_hall += 1
            error_string_a += ("Unknown z_hall: " + str(z_hall) + "\n")
            valid_z = False

        #just takes text from the GUI input boxes
        a_cabinet = self.input_aside_cabinet()
        z_cabinet = self.input_zside_cabinet()

        if valid_a:
            try:
                a_coord = self._simulation.get_cabinet_list(a_hall)[a_cabinet]
            except KeyError as e:
                #error_string_a += str(e)
                valid_a = False

        if valid_z:
            try:
                z_coord = self._simulation.get_cabinet_list(z_hall)[z_cabinet]
            except KeyError as e:
                #error_string_z += str(e)
                valid_z = False

        if valid_a:
            self.set_a_side(a_coord)
        else:
            print "Unknown A-Side"
            print error_string_a

        if valid_z:
            self.set_z_side(z_coord)
        else:
            print "Unknown Z-Side"
            print error_string_z
    
    def set_a_side(self, coordinate):
        """
        Passes the coordinate to the program layer to set the a side
        Checks the coordinate for an existing hall / cabinet ID
        """
        self._simulation.set_aside(coordinate[0], coordinate[1])
        self._text_a_hall.set_text(str(self._simulation.get_hall_number(coordinate)+1))
        self._text_a_cabinet.set_text(str(self._simulation.get_cabinet_number(coordinate)))
    
    def set_z_side(self, coordinate):
        """
        Passes the coordinate to the program layer to set the a side
        Checks the coordinate for an existing hall / cabinet ID
        """
        self._simulation.set_zside(coordinate[0], coordinate[1])
        self._text_z_hall.set_text(str(self._simulation.get_hall_number(coordinate)+1))
        self._text_z_cabinet.set_text(str(self._simulation.get_cabinet_number(coordinate)))

    def calculate(self):
        distance_field = self._simulation.compute_distance_field(HUMAN)
        #print distance
        #print self._simulation._zombie_list[0]
        self_pos = self._simulation._zombie_list[0]
        #print self_pos
        distance = distance_field[self_pos[0]][self_pos[1]]
        print CLS
        print distance, "tiles"
        print float((distance)*0.6 + SLACK_LENGTH), "meters including", SLACK_LENGTH, "meters slack"

    def flee(self):
        """
        Event handler for button that causes humans to flee zombies by one cell
        Diagonal movement allowed
        """
        zombie_distance = self._simulation.compute_distance_field(ZOMBIE)
        self._simulation.move_humans(zombie_distance)


    def stalk(self):
        """
        Launch GUI thread to increment Z trace end position
        """
        #check first if we're already processing an input
        if self.is_processing():
            return
        #else, make note that we are processing an input
        else:
            self._processing_input = True
        
        #arguments for printout
        initial_string = "Calculating all possible routes"
        append_string = "."
        repeat_delay = 1
        display_thread = "Displaying trace"
        
        self._distance_field_thread = threading.Thread(target=self.distance_field_wrapper, args=(HUMAN, ))
        target_thread = self._distance_field_thread        
        self._waiting_display_thread = threading.Thread(target=self.wait_print_wrapper, args=(initial_string, append_string, repeat_delay, target_thread))
        self._distance_field_thread.start()
        self._waiting_display_thread.start()  
        self._distance_field_thread.join()
        
        
        human_distance = self._result_queue.get()

        #commenging this out to try threading instead
        #human_distance = self._simulation.compute_distance_field(HUMAN)
        print CLS
        print display_thread
        self._draw_trace_wrapper_thread = threading.Thread(target=self.draw_trace_wrapper, args=(human_distance, 0.03))      
        self._draw_trace_wrapper_thread.start()
        #self._processing_input = False for this function occurs in draw_trace_wrapper
            
    def wait_print_wrapper(self, initial_string, append_string, repeat_delay, target_thread):
        """
        Wrapper for threading with a printout while waiting on another thread
        """
        label = initial_string     
        while target_thread.is_alive():
            print CLS
            print label
            label += append_string
            time.sleep(repeat_delay)

    def distance_field_wrapper(self, entity):
        """
        wrapper for calculating the distance field with threads
        stores in threading queue
        """
        distance_field = self._simulation.compute_distance_field(entity)
        self._result_queue.put(distance_field)
    
    def draw_trace_wrapper(self, human_distance, delay):
        """
        wrapper function for tracing the path one cell at a time
        """
        proceed = True
        #reset a-path trace
        print CLS
        self.reset_trace_path()
        while self._simulation.get_z_side() != self._simulation.get_trace_end() and proceed:
            #trace_z will return false if no valid moves are returned
            proceed = self._simulation.trace_z(human_distance)
            time.sleep(delay)
        self._processing_input = False

    def reset_trace_path(self):
        if self._simulation.num_zombies()>1:
            a_side = self._simulation.get_a_side()
            self._simulation.set_aside(a_side[0], a_side[1])

    def toggle_item(self):
        """
        Event handler to toggle between new obstacles, humans and zombies
        """
        self.reset_trace_path()
        if self._item_type == ZOMBIE:
            self._item_type = HUMAN
            self._item_label.set_text(LABEL_STRING + NAME_MAP[HUMAN])
        elif self._item_type == HUMAN:
            self._item_type = OBSTACLE
            self._item_label.set_text(LABEL_STRING + NAME_MAP[OBSTACLE])
        elif self._item_type == OBSTACLE:
            self._item_type = EMPTY
            self._item_label.set_text(LABEL_STRING + NAME_MAP[EMPTY])
        elif self._item_type == EMPTY:
            self._item_type = ZOMBIE
            self._item_label.set_text(LABEL_STRING + NAME_MAP[ZOMBIE])

    def toggle_z_side(self):
        """
        Alternates the selected Z-Side on the grid out of a dictionary of pre-defined coordinates / cabinet IDs
        Slight hack - hardcoding the hall ID's coordinate for the moment
        """
        #check if we're processing an input before proceeding        
        if self.is_processing():
            return
        
        global Z_SIDE_LIST_INDEX
        #Z_SIDE_LIST_INDEX += 1
        #Z_SIDE_LIST_INDEX %= Z_SIDE_LIST_LENGTH
        #Work out the next cabinet number & coordinate, set simulation z-side to coordinate
        next_z_index = (Z_SIDE_LIST_INDEX+1) % Z_SIDE_LIST_LENGTH
        next_z_string = self._simulation.get_z_side_list()[next_z_index]
        next_z_hall = self._simulation.get_z_side_hall_list()[next_z_string]
        next_z_coord = self._simulation.get_cabinet_list(next_z_hall)[next_z_string]
        self.set_z_side(next_z_coord)        

        #since we're using the toggle, we can be assured that these are our cabinets
        #and have a preferred path.
        #Therfore: set the forbidden paths that will be avoided
        #self._simulation.set_forbidden(next_z_string)

        #Setup label for next toggle
        Z_SIDE_LIST_INDEX = (Z_SIDE_LIST_INDEX+1) % Z_SIDE_LIST_LENGTH
        next_z_index = (Z_SIDE_LIST_INDEX+1) % Z_SIDE_LIST_LENGTH
        next_z_string = self._simulation.get_z_side_list()[next_z_index]
        self._z_button_label.set_text("Set Z to " + next_z_string)

        if DEBUG_TZ:
            print "Z_SIDE_LIST_INDEX", Z_SIDE_LIST_INDEX
            print "Z_SIDE_LIST_LENGTH", Z_SIDE_LIST_LENGTH

    def add_item(self, click_position):
        """
        Event handler to add new obstacles, humans and zombies
        """
        #check if we're processing an input before proceeding        
        if self.is_processing():
            return
            
        row, col = self._simulation.get_index(click_position, CELL_SIZE)
        clicked_coordinate = (row, col)
        if self._item_type == OBSTACLE:
            if not self.is_occupied(row, col):
                self._simulation.set_full(row, col)
        elif self._item_type == ZOMBIE:
            if self._simulation.is_empty(row, col):
                self.set_a_side(clicked_coordinate)
        elif self._item_type == HUMAN:
            if self._simulation.is_empty(row, col):
                self.set_z_side(clicked_coordinate)
        elif self._item_type == EMPTY:
            if not self._simulation.is_empty(row, col):
                self._simulation.set_empty(row, col)
        

    def is_occupied(self, row, col):
        """
        Determines whether the given cell contains any humans or zombies
        """
        cell = (row, col)
        human = cell in self._simulation.humans()
        zombie = cell in self._simulation.zombies()
        return human or zombie


    def draw_cell(self, canvas, row, col, color="Cyan"):
        """
        Draw a cell in the grid
        """
        upper_left = [col * CELL_SIZE, row * CELL_SIZE]
        upper_right = [(col + 1) * CELL_SIZE, row * CELL_SIZE]
        lower_right = [(col + 1) * CELL_SIZE, (row + 1) * CELL_SIZE]
        lower_left = [col * CELL_SIZE, (row + 1) * CELL_SIZE]
        canvas.draw_polygon([upper_left, upper_right,
                             lower_right, lower_left],
                            1, "Black", color)

    def draw_grid(self, canvas, grid):
        """
        Draw entire grid
        """
        for col in range(self._grid_width):
            for row in range(self._grid_height):
                status = grid[row][col]
                if status in CELL_COLORS:
                    color = CELL_COLORS[status]
                    if color != "White":
                        self.draw_cell(canvas, row, col, color)
                else:
                    if status == (FULL | HAS_HUMAN):
                        raise ValueError, "human moved onto an obstacle"
                    elif status == (FULL | HAS_ZOMBIE):
                        raise ValueError, "zombie moved onto an obstacle"
                    elif status == (FULL | HAS_HUMAN | HAS_ZOMBIE):
                        raise ValueError, "human and zombie moved onto an obstacle"
                    else:
                        raise ValueError, "invalid grid status: " + str(status)

    def draw(self, canvas):
        """
        Handler for drawing obstacle grid, human queue and zombie queue
        """
        grid = [[FULL] * self._grid_width for
                dummy_row in range(self._grid_height)]
        for row in range(self._grid_height):
            for col in range(self._grid_width):
                if self._simulation.is_empty(row, col):
                    grid[row][col] = EMPTY
        for row, col in self._simulation.humans():
            grid[row][col] |= HAS_HUMAN
        for row, col in self._simulation.zombies():
            grid[row][col] |= HAS_ZOMBIE
        self.draw_grid(canvas, grid)
        
    def is_processing(self):
        if self._processing_input:
            print "Currently processing, please standby."            
            return True
        else:
            return False

# Start interactive simulation
def run_gui(sim):
    """
    Encapsulate frame
    """
    gui = ApocalypseGUI(sim)
    gui.start()
