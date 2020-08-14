"""
Zombie Apocalypse mini-project
Click "Mouse click" button to toggle items added by mouse clicks
Zombies have four way movement, humans have eight way movement
"""
import time
import threading
import math
import random
from decimal import *
from multiprocessing import Queue
try:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
except ImportError:
    import simplegui

# Global constants
CLS = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
CLS = "\n"
EMPTY = 0
#full value can't be used as a tile weight
FULL = -1
HAS_ZOMBIE = 2
HAS_HUMAN = 4
FOUR_WAY = 3
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7
INSPECT = ''
METERS_PER_TILE = 0.6
FEET_PER_METER = 3.28084

#color wheel setup, putting red at 0 degrees
R_OFFSET = 0
G_OFFSET = 120
B_OFFSET = 240
ROTATION_OFFSET = 90
INTENSITY = 255
#ADJUSTMENT_SPEED = 6

#Global variable for demo mode status
RUN_DEMO = True
DEMO_STATUS = "START"
#DEMO_STATUS = "RIGHT"
#DEMO_STATUS = "RESTORE_ORIGINAL_WEIGHT_DOWN"
DEMO_LOOPS = 3

TIMER_INTERVAL = float(0.3)
CELL_COLORS = {EMPTY: "Yellow",
               FULL: "Black",
               HAS_ZOMBIE: "Red",
               HAS_HUMAN: "Green",
               HAS_ZOMBIE|HAS_HUMAN: "Purple"}

NAME_MAP = {OBSTACLE: "Delete Path",
            HUMAN: "Place Z-Side",
            ZOMBIE: "Place A-Side",
            EMPTY: "Add Path",
            INSPECT: "Inspect Cell"}

# GUI constants
CELL_SIZE = 10
LABEL_STRING = "Mouse Click : "
Z_SIDE_LIST_INDEX = 0
Z_SIDE_LIST_LENGTH = 0

DEBUG_TZ = False
DEBUG_STLK = False
DEBUG_WPR = False
DEBUG_GWI2S = False
DEBUG_RFT = False
DEBUG_DEMO = False
DEBUG_INIT = False
DEBUG_DRAW = False
DEBUG_COT = False
DEBUG_CLH = False
DEBUG_TZW = False

class ApocalypseGUI:
    """
    Container for interactive content
    """

    def __init__(self, simulation, metric=True, slack_length=5.0, tile_size=10, adjustment_speed = 6):
        """
        Create frame and timers, register event handlers
        """
        #simulation variables
        self._metric = metric
        self._slack_length = slack_length
        #CELL_SIZE = tile_size
        self._tile_size = tile_size
        
        self._simulation = simulation
        self._grid_height = self._simulation.get_grid_height()
        self._grid_width = self._simulation.get_grid_width()
        self._grid_width_pixels = self._grid_width * self._tile_size
        self._grid_height_pixels = max(340, ((self._grid_height+4) * self._tile_size))
        self._frame = simplegui.create_frame("Weighted Distance Calculator",
                                             self._grid_width_pixels,
                                             self._grid_height_pixels)
        self._frame.set_canvas_background("Black")                                   
        #self._frame.add_button("Clear all", self.clear, 200)
        self._item_type = ZOMBIE
        global Z_SIDE_LIST_LENGTH
        Z_SIDE_LIST_LENGTH = len(self._simulation.get_z_side_list())
        global Z_SIDE_LIST_INDEX
        Z_SIDE_LIST_INDEX = Z_SIDE_LIST_LENGTH-1

        label = LABEL_STRING + NAME_MAP[self._item_type]
        self._item_label = self._frame.add_button(label,
                                                  self.toggle_item, 200)

        #Takes z_side_list from simulation, increments the GUIs index and modulos against the length of the list
        try:
            z_label = "Set Z to " + str(self._simulation.get_z_side_list()[(Z_SIDE_LIST_INDEX+1) % Z_SIDE_LIST_LENGTH])
        except ZeroDivisionError:
            z_label = ""
        if len(self._simulation.get_z_side_list()) > 0:
            self._z_button_label = self._frame.add_button(z_label, self.toggle_z_side, 200)
        self._frame.add_button("Calculate Length", self.calculate_length_handler, 200)
        self._frame.add_button("Trace Path", self.trace_z_handler, 200)
        self._text_a_hall = self._frame.add_input('A-Hall', self.input_aside_hall, 200)
        self._text_a_cabinet = self._frame.add_input('A-Cabinet', self.input_aside_cabinet, 200)
        self._text_z_hall = self._frame.add_input('Z-Hall', self.input_zside_hall, 200)
        self._text_z_cabinet = self._frame.add_input('Z-Cabinet', self.input_zside_cabinet, 200)
        self._text_cell_weight = self._frame.add_input('Weight', self.input_cell_weight, 200)
        self._frame.add_button("Input A+Z Sides", self.process_input_a_z_sides, 200)
        self._frame.set_mouseclick_handler(self.add_item)
        self._frame.set_draw_handler(self.draw)
        
        #queue for storing thread results
        self._result_queue = Queue()
        self._trace_result_queue = Queue()
        
        #flag to keep track if input is currently being processed
        self._processing_input = False
        
        self._output_text = ""

        #Putting this here to avoid attribute errors when checking if it's running        
        self._display_for_seconds_thread = threading.Thread()
        
        #color setup
        #run through the whole spectrum if range = 360
        self._color_range = 360
        #start at red if start = 0
        self._color_start = 0
        #take some variables from the global constants
        self._default_r_offset = R_OFFSET
        self._default_g_offset = G_OFFSET
        self._default_b_offset = B_OFFSET
        self._current_r_offset = R_OFFSET
        self._current_g_offset = G_OFFSET
        self._current_b_offset = B_OFFSET
        self._default_rotation_offset = ROTATION_OFFSET
        self._current_rotation_offset = ROTATION_OFFSET
        self._default_intensity = INTENSITY
        self._current_intensity = INTENSITY
        self._default_adjustment_speed = adjustment_speed
        self._current_adjustment_speed = adjustment_speed
        self._rotation_modulo = 360**2/self._color_range
        if DEBUG_INIT:
            print "self._rotation_modulo", self._rotation_modulo

        #demo mode settings
        mac_fps = 15
        if DEBUG_DEMO:
            self._demo_mode_timeout = 30
        else:
            self._demo_mode_timeout = mac_fps*60*5
        self._demo_mode_timer = 0
        self._color_direction_list = [-1, 1]
        self._color_direction = self._color_direction_list[random.randrange(len(self._color_direction_list))]
        #self._color_direction = 1


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
        """
        Takes text from frame input box and returns the value
        """
        return self._text_a_hall.get_text()
    
    def input_aside_cabinet(self):
        """
        Takes text from frame input box and returns the value
        """
        return self._text_a_cabinet.get_text()
    
    def input_zside_hall(self):
        """
        Takes text from frame input box and returns the value
        """
        return self._text_z_hall.get_text()
    
    def input_zside_cabinet(self):
        """
        Takes text from frame input box and returns the value
        """
        return self._text_z_cabinet.get_text()

    def input_cell_weight(self):
        """
        Returns the value from the weighting input box
        :return:
        """
        return self._text_cell_weight.get_text()

    def process_input_a_z_sides(self):
        """
        Takes the text box inputs for a + z side details and sets the grid coordinates accordingly
        """
        self._demo_mode_timer = 0
        #Bool for checking valid inputs. Assume initually correct.
        print CLS
        valid_a = True
        valid_z = True
        a_hall = -1
        z_hall = -1
        error_string_a = ""
        error_string_z = ""
        a_cabinet = ""
        z_cabinet = ""
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
                a_hall = "(blank)"
            #this is just for 'nice' error reporting for the user
            else:
                a_hall += 1
            error_string_a += ("Unknown A-Hall: " + str(a_hall))
            
            valid_a = False
        if z_hall < 0 or z_hall > max_hall_ID:
            if z_hall == -1:
                z_hall = "(blank)"
            #this is just for 'nice' error reporting for the user
            else:
                z_hall += 1
            error_string_z += ("Unknown Z-Hall: " + str(z_hall))
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
                if len(a_cabinet) == 0 or a_cabinet == "":
                    a_cabinet = "(blank)"
                error_string_a += ("Unknown A-Cabinet: " + a_cabinet)

        if valid_z:
            try:
                z_coord = self._simulation.get_cabinet_list(z_hall)[z_cabinet]
            except KeyError as e:
                print e
                #error_string_z += str(e)
                valid_z = False
                if len(z_cabinet) == 0 or z_cabinet == "":
                    z_cabinet = "(blank)"
                error_string_z += ("Unknown Z-Cabinet: " + z_cabinet)

        if valid_a:
            self.set_a_side(a_coord)
        else:
            self.display_for_seconds_wrapper(error_string_a, 3, self._display_for_seconds_thread)
            #print "Unknown A-Side"
            #print error_string_a

        if valid_z:
            self.set_z_side(z_coord)
        else:
            self.display_for_seconds_wrapper(error_string_z, 3, self._display_for_seconds_thread)
            #print "Unknown Z-Side"
            #print error_string_z
    
    def set_a_side(self, coordinate):
        """
        Passes the coordinate to the program layer to set the a side
        Checks the coordinate for an existing hall / cabinet ID
        """
        self._simulation.set_aside(coordinate[0], coordinate[1])
        self._text_a_hall.set_text(str(self._simulation.get_hall_number(coordinate)+1))
        self._text_a_cabinet.set_text(str(self._simulation.get_cabinet_number(coordinate)))
        self.clear_output_text()
        
        #generate new distance information
        #self._simulation.compute_distance_field(HUMAN)
    
    def set_z_side(self, coordinate):
        """
        Passes the coordinate to the program layer to set the a side
        Checks the coordinate for an existing hall / cabinet ID
        """
        self._simulation.set_zside(coordinate[0], coordinate[1])
        self._text_z_hall.set_text(str(self._simulation.get_hall_number(coordinate)+1))
        self._text_z_cabinet.set_text(str(self._simulation.get_cabinet_number(coordinate)))
        self.clear_output_text()
        
        #generate new distance information
        #self._simulation.compute_distance_field(HUMAN)

    def inspect_cell(self, coordinate):
        """
        :param coordinate:
        :return:
        Handler for GUI, inspects the grid cell clicked on
        """
        cell_contents = self.get_cell_details(coordinate)

    def get_cell_details(self, coordinate):
        """
        :param coordinate:
        :return:
        Passes call on to the program layer to retrieve the cell details for the given coordinate
        """

    def set_inspection_details(self):
        """
        :return:
        Set the GUI layer fields with the relevant details from a cell inspection
        """
        
    def calculate_length_handler(self):
        """
        Calculate and display to GUI + Command line the distance between the A & Z Sides
        """

        #reset demo mode timeout
        self._demo_mode_timer = 0

        #end demo mode if it's running
        if RUN_DEMO:
            self.end_demo()

        #don't proceed if another set of instructions is being processed
        if self.is_processing():
            return
            
        elif not self.is_a_and_z_set():
            self.display_for_seconds_wrapper("Please set A and Z sides on the grid", 5)
            return

        else:
            self._processing_input = True

            self._calculate_distance_field_wrapper_thread = threading.Thread(target=self.calculate_distance_field_wrapper, args=())
            self._calculate_distance_field_wrapper_thread.start()

            self._display_calculated_distance_thread = threading.Thread(target=self.display_calculated_distance_wrapper, args=())
            self._display_calculated_distance_thread.start()
            
            
    def display_calculated_distance_wrapper(self):
        distance_field = self._result_queue.get()        
        self_pos = self._simulation.get_a_side()
        distance = distance_field[self_pos[0]][self_pos[1]]
        print CLS
        output = ""
        if self._metric:
            output = "Distance: " + str(distance) + " tiles - " + str(float((distance)*METERS_PER_TILE + self._slack_length)) + " meters including " + str(self._slack_length) + " meters slack"
        else:
            output = "Distance: " + str(distance) + " tiles - " + str(float((distance)*METERS_PER_TILE*FEET_PER_METER + self._slack_length)) + " feet including " + str(self._slack_length)*FEET_PER_METER + " feet slack"
        
        #self._waiting_display_thread.join()            
        self.set_output_text_handler(output)
        #self.display_for_seconds("output", 5)
        print self._output_text

    def flee(self):
        """
        Event handler for button that causes humans to flee zombies by one cell
        Diagonal movement allowed
        """
        zombie_distance = self._simulation.compute_distance_field(ZOMBIE)
        self._simulation.move_humans(zombie_distance)
        
    def is_a_and_z_set(self):
        """
        Sanity check - do we have a single a and a single z side to calculate the length of / trace
        """
        try:
            self.set_a_side(self._simulation.get_a_side())
        except Exception:
            pass
        
        try:
            self.set_z_side(self._simulation.get_z_side())
        except Exception:
            pass
        
        if self._simulation.num_grid_a_sides() == 1 and self._simulation.num_grid_z_sides() == 1:
            return True
        else:
            return False

    def calculate_distance_field_wrapper(self):
        initial_string = "Calculating all possible routes"
        append_string = "."
        repeat_delay = 1

        self._distance_field_thread = threading.Thread(target=self.distance_field_wrapper, args=(HUMAN, ))
        target_thread = self._distance_field_thread
        self._waiting_display_thread = threading.Thread(target=self.wait_print_wrapper, args=(initial_string, append_string, repeat_delay, target_thread), kwargs={'suffix_method': self.get_number_paths_calculated})
        self._distance_field_thread.start()
        self._waiting_display_thread.start()

    def get_number_paths_calculated(self):
        return "{:.2E}".format(Decimal(self._simulation.get_number_paths_calculated()))
        
    def trace_z_handler(self):
        self._demo_mode_timer = 0
        if self.is_processing():
            if RUN_DEMO:
                self.end_demo()
            else:
                return
        elif not self.is_a_and_z_set():
            self.display_for_seconds_wrapper("Please set A and Z sides on the grid", 5)
            return
        
        #else, make note that we are processing an input
        else:
            self.trace_z_thread = threading.Thread(target=self.trace_z_wrapper, args=())
            self.trace_z_thread.start()
        

    def trace_z_wrapper(self):
        """
        Launch GUI thread to increment Z trace end position
        """
        #check first if we're already processing an input
        self._demo_mode_timer = 0
        if self.is_processing():
            if RUN_DEMO:
                self.end_demo()
            else:
                return
        #else, make note that we are processing an input
        else:
            self._processing_input = True

        self.calculate_distance_field_wrapper()

        self._distance_field_thread.join()
        
        human_distance = self._result_queue.get()
        
        #PART 2: Display the Trace
        #arguments for printout
        initial_string = "Tracing optimal route"
        append_string = "."
        repeat_delay = 0.2

        print CLS
        
        self._draw_trace_wrapper_thread = threading.Thread(target=self.draw_trace_wrapper, args=(human_distance, 0.03))      
        target_thread = self._draw_trace_wrapper_thread
        self._tracing_display_thread = threading.Thread(target=self.wait_print_wrapper, args=(initial_string, append_string, repeat_delay, target_thread))           
        self._draw_trace_wrapper_thread.start()
        self._tracing_display_thread.start()
        
        #Check if there was a dead-end or unpassable trace scenario for UI output
        self._check_for_broken_path_wrapper_thread = threading.Thread(target=self.check_for_broken_path_wrapper)
        self._check_for_broken_path_wrapper_thread.start()
        
        #join all threads and set processing = false
        if DEBUG_TZW:
            print "1"
        if self._draw_trace_wrapper_thread.is_alive():
            self._draw_trace_wrapper_thread.join()
        if DEBUG_TZW:
            print "2"
        if self._tracing_display_thread.is_alive():
            self._tracing_display_thread.join()
        if DEBUG_TZW:
            print "3"
        if self._tracing_display_thread.is_alive():
            self._tracing_display_thread.join()
        if DEBUG_TZW:
            print "4"
        if self._check_for_broken_path_wrapper_thread.is_alive():
            self._check_for_broken_path_wrapper_thread.join()
        if DEBUG_TZW:
            print "5"
        
        #clear output text
        self.clear_output_text()
        if DEBUG_TZW:
            print "6"
        
        self._processing_input = False
        if DEBUG_TZW:
            print "7"
        
    def check_for_broken_path_wrapper(self):
        """
        Checks if the path was completed, passes failure text to display_for_seconds_wrapper as thread if 
        path failed
        """
        trace_result = self._trace_result_queue.get()
        if trace_result == False:
            display_string = "Encountered dead-end or forbidden path"
            time = 5
            self._display_text_thread = threading.Thread(target=self.display_for_seconds_wrapper, args=(display_string, time, self._tracing_display_thread))    
            self._display_text_thread.start()
            
    def display_for_seconds_wrapper(self, display_string, display_time, wait_for_this_thread_first = None):
        #check if anything else is being displayed for seconds first
        #todo: implement a way of doing a join here if another copy of this thread is running that doesn't hold up the current thread
        self._display_for_seconds_thread = threading.Thread(target = self.display_for_seconds, args=(display_string, display_time, wait_for_this_thread_first))
        self._display_for_seconds_thread.start()

    def set_output_text_handler(self, output_text):
        """
        Waits on any text being used through 'display_for_seconds()', then sets the output text 
        as the argument passed 'output_text'
        """
        #todo: make this wait for a PRE-EXISTING self._display_for_seconds_thread, not the one calling it
        #if self._display_for_seconds_thread.is_alive():
        #    self._display_for_seconds_thread.join()
        #while self._display_for_seconds_thread.is_alive():
        #    pass
        self._output_text = output_text         
        
    def display_for_seconds(self, display_string, display_time, wait_for_this_thread_first = None):
        """
        Thread to output to gui and command line a string for a number of seconds.
        Optional argument = wait for this thread to be completed before outputting text
        """
        #todo: as with other threading - find a way to pass this to the handler
        #that will check if another (not the same) display_for_seconds thread is running 
        if wait_for_this_thread_first:
            while wait_for_this_thread_first.is_alive():
                time.sleep(0.1)       
        print CLS        
        self._output_text = display_string
        print self._output_text
        time.sleep(display_time)
        self.clear_output_text()
        print CLS
        
    def wait_print_wrapper(self, initial_string, append_string, repeat_delay, target_thread, suffix_string=None, suffix_method=None):
        """
        Wrapper for threading with a printout while waiting on another thread
        """
        if DEBUG_WPR:
            print "start wpr"
        self._output_text = initial_string
        current_repeats = 1
        max_repeats = 4
        append_this_time = True
        while target_thread.is_alive():
            self._output_text = initial_string + (current_repeats-1)*append_string
            if suffix_string:
                self._output_text += suffix_string
            if suffix_method:
                self._output_text += (2*max_repeats - current_repeats) * " "
                self._output_text += str(suffix_method())
            print CLS            
            print self._output_text

            if append_this_time:
                current_repeats += 1
                if current_repeats == max_repeats:
                    append_this_time = False
                else:
                    current_repeats %= max_repeats
            else:
                append_this_time = True
            #only sleep and loop while target thread is still running
            if target_thread.is_alive():
                time.sleep(repeat_delay)
            else:
                break
        #self.clear_output_text()
        print CLS        
        if DEBUG_WPR:
            print "end wpr"
        self._processing_input = False

    def distance_field_wrapper(self, entity):
        """
        wrapper for calculating the distance field with threads
        stores in threading queue
        """
        distance_field = self._simulation.get_distance_field(entity)
        self._result_queue.put(distance_field)
    
    def draw_trace_wrapper(self, human_distance, delay):
        """
        wrapper function for tracing the path one cell at a time
        """
        self._processing_input = True
        proceed = True
        #reset a-path trace
        print CLS
        self.reset_trace_path()
        while self._simulation.get_z_side() != self._simulation.get_trace_end() and proceed:
            #trace_z will return false if no valid moves are returned
            proceed = self._simulation.trace_z(human_distance)
            time.sleep(delay)
        self._processing_input = False
        
        #store the result of the trace from logic layer
        #if it returned false then the trace wasn't complete
        self._trace_result_queue.put(proceed)
        

    def reset_trace_path(self):
        if self._simulation.num_zombies()>1:
            a_side = self._simulation.get_a_side()
            self._simulation.set_aside(a_side[0], a_side[1])
        
    def clear_output_text(self):
        if DEBUG_COT:
            print "Clearing"
        self.set_output_text_handler("")

    def toggle_item(self):
        """
        Event handler to toggle between new obstacles, humans and zombies
        """
        if RUN_DEMO:
            self.end_demo()
        self._demo_mode_timer = 0

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
            self._item_type = INSPECT
            self._item_label.set_text(LABEL_STRING + NAME_MAP[INSPECT])
        elif self._item_type == INSPECT:
            self._item_type = ZOMBIE
            self._item_label.set_text(LABEL_STRING + NAME_MAP[ZOMBIE])

    def toggle_z_side(self):
        """
        Alternates the selected Z-Side on the grid out of a dictionary of pre-defined coordinates / cabinet IDs
        Slight hack - hardcoding the hall ID's coordinate for the moment
        """

        #Kill the dmeo if it's running
        if RUN_DEMO:
            self.end_demo()
        self._demo_mode_timer = 0

        #check if we're processing an input before proceeding        
        if self.is_processing():
            return
        
        global Z_SIDE_LIST_INDEX
        #Work out the next cabinet number & coordinate, set simulation z-side to coordinate
        next_z_index = (Z_SIDE_LIST_INDEX+1) % Z_SIDE_LIST_LENGTH
        next_z_string = self._simulation.get_z_side_list()[next_z_index]
        try:
            next_z_hall = self._simulation.get_z_side_hall_list()[next_z_string]
        except KeyError as e:
            print "KeyError", e
            print "Key=",next_z_string
            print "len(self._simulation.get_z_side_hall_list())", len(self._simulation.get_z_side_hall_list())
            print "self._simulation.get_z_side_hall_list()", self._simulation.get_z_side_hall_list()
        next_z_coord = self._simulation.get_cabinet_list(next_z_hall)[next_z_string]
        self.set_z_side(next_z_coord)

        #Setup label for next toggle
        Z_SIDE_LIST_INDEX = (Z_SIDE_LIST_INDEX+1) % Z_SIDE_LIST_LENGTH
        next_z_index = (Z_SIDE_LIST_INDEX+1) % Z_SIDE_LIST_LENGTH
        next_z_string = self._simulation.get_z_side_list()[next_z_index]
        self._z_button_label.set_text("Set Z to " + next_z_string)

        if DEBUG_TZ:
            print "Z_SIDE_LIST_INDEX", Z_SIDE_LIST_INDEX
            print "Z_SIDE_LIST_LENGTH", Z_SIDE_LIST_LENGTH
            
    def validate_coordinate(self, coordinate):
        if coordinate[0] < self._grid_height and coordinate[1] < self._grid_width:
            return True
        else:
            return False

    def reset_forbidden_tiles(self):
        #a_side = self._simulation.get_cabinet_number(self._simulation.get_a_side())
        z_side = self._simulation.get_cabinet_number(self._simulation.get_z_side())
        if DEBUG_RFT:
            #print "a_side", a_side
            print "z_side", z_side
        self._simulation.set_forbidden(z_side)
        #self._simulation.set_forbidden(a_side)

    def add_item(self, click_position):
        """
        Event handler to add / move / remove items / inspect
        """

        #reset demo mode timer
        self._demo_mode_timer = 0

        #kill the demo if it's running
        if RUN_DEMO:
            self.end_demo()

        #check if we're processing an input before proceeding        
        if self.is_processing():
            return

        row, col = self._simulation.get_index(click_position, self._tile_size)
        clicked_coordinate = (row, col)

        #check if this is inside the actual grid as we've extended the board 
        #area with a text field
        if not self.validate_coordinate(clicked_coordinate):
            return
            
        #if there's already a trace drawn
        if self._simulation.num_zombies()>1:
            #clear the trace
            self.reset_trace_path()
                
        #clear the ourput text
        self.clear_output_text()
        
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
            #set the coordinates weight to the simulation's default
            self._simulation.set_weight(row, col, self._simulation.get_default_weight())
        elif self._item_type == INSPECT:
            self.inspect_cell(clicked_coordinate)
        

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
        upper_left = [col * self._tile_size, row * self._tile_size]
        upper_right = [(col + 1) * self._tile_size, row * self._tile_size]
        lower_right = [(col + 1) * self._tile_size, (row + 1) * self._tile_size]
        lower_left = [col * self._tile_size, (row + 1) * self._tile_size]
        canvas.draw_polygon([upper_left, upper_right,
                             lower_right, lower_left],
                            1, "Black", color)

    def draw_grid(self, canvas, grid):
        """
        Draw entire grid
        """
        #default color
        color = "Black"
        for col in range(self._grid_width):
            for row in range(self._grid_height):
                status = grid[row][col]
                if status in CELL_COLORS:
                    weight = self._simulation.get_weight(row, col)
                    color = CELL_COLORS[status]
                    #logic specifically for working with non-standard weight open paths
                    #if weight != self._simulation.get_default_weight() and status == EMPTY:
                    if status == EMPTY:
                        if weight == float('inf'):
                            gray_value_string = str(self._current_intensity // 2)
                            color = "rgb(" + gray_value_string + ", " + gray_value_string + ", " + gray_value_string + ")"
                        else:
                            #starting position & range on the color wheel using yellow-> green-> blue
                            self._color_range = 180
                            self._color_start = 60

                            #using roygbiv
                            #color_range = 360
                            #color_start = 0


                            #retrieve /255 rgb values
                            color_red = self.get_weight_intensity_255_string(weight, self._current_r_offset+self._current_rotation_offset, self._color_start, self._color_range)
                            color_green = self.get_weight_intensity_255_string(weight,self._current_g_offset+self._current_rotation_offset, self._color_start, self._color_range)
                            color_blue = self.get_weight_intensity_255_string(weight, self._current_b_offset+self._current_rotation_offset, self._color_start, self._color_range)

                            weighted_r = str(color_red)
                            weighted_g = str(color_blue)
                            weighted_b = str(color_green)
                            color = "rgb(" + weighted_r + ", " + weighted_g + ", " + weighted_b + ")"
                    #overriding default dict case here... so it's not really used atm
                    #if weight == self._simulation.get_default_weight() and status == EMPTY:
                    #    color = "rgb(0, " + "255" + ", 255)"
                    #    color = "rgb(0, " + self.get_weight_intensity_255_string(weight) + ", 255)"
                    if color != "White":
                        self.draw_cell(canvas, row, col, color)
                else:
                    if status == (FULL | HAS_HUMAN):
                        raise ValueError, "z-side placed on an obstacle"
                    elif status == (FULL | HAS_ZOMBIE):
                        raise ValueError, "a-side placed on an obstacle"
                    elif status == (FULL | HAS_HUMAN | HAS_ZOMBIE):
                        raise ValueError, "A+Z sides placed on an obstacle"
                    else:
                        raise ValueError, "invalid grid status: " + str(status)
                        
    def get_weight_intensity_255_string(self, weight, offset_degrees, color_start, color_range):

        #get the relative percentage of max weight in the simulation for this weight value
        relative_weight = self._simulation.get_relative_traversable_weight(weight)

        #adjust the relative weight based on the starting color and range settings
        relative_weight *= (color_range/360.0)
        relative_weight += (color_start/360.0)
        relative_weight %= 1.0

        if DEBUG_GWI2S:
            print "weight", weight
            print "relative_weight %", relative_weight

        #convert the weight to a position around a circle
        relative_weight *= 360
        relative_weight += offset_degrees
        relative_weight %= 360

        if DEBUG_GWI2S:
            print "relative_weight / 360 deg", relative_weight

        #convert the circular weight to a number in radians
        relative_weight *= (math.pi/180)

        if DEBUG_GWI2S:
            print "relative_weight radians", relative_weight

        #perform sin function on relative weight for intensity value
        relative_weight = math.sin(relative_weight)

        #convert the value from radians to a number out of 255
        relative_weight *= self._current_intensity
        relative_weight += self._current_intensity // 2
        
        #make sure only to return a value between 0 and 255
        relative_weight = min(relative_weight, 255)
        relative_weight = max(relative_weight, 0)
        

        if DEBUG_GWI2S:
            print "relative_weight (*128 +127 ouput value)", relative_weight

        #convert the output value to string with 0 decimal places
        output_string = str(int(relative_weight))
        if DEBUG_GWI2S:
            print "relative_weight (*128 +127 ouput value)", output_string
        return output_string
        
    def randomize_color_direction(self):
        self._color_direction = self._color_direction_list[random.randrange(len(self._color_direction_list))]

    def start_demo(self):
        global RUN_DEMO
        global DEMO_LOOPS
        global DEMO_STATUS
        self.randomize_color_direction()
        DEMO_STATUS = "START"
        DEMO_LOOPS = 4
        RUN_DEMO = True

    def end_demo(self):
        self._current_intensity = self._default_intensity
        self._current_rotation_offset = self._default_rotation_offset
        self._simulation.load_stored_weight_map()
        self.reset_forbidden_tiles()
        global RUN_DEMO
        RUN_DEMO = False
        self._processing_input = False

    def draw(self, canvas):
        """
        Handler for drawing layout, a & z side, trace, demo mode
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
        
        #change the direction for color rotation
        if not self.is_processing():
            self._color_direction *= -1
        
        #Add output text label
        canvas.draw_text(self._output_text, (12, self._grid_height_pixels-20), 20, "rgb(" + str(self._current_intensity) + ", 0, 0)")
        
        global RUN_DEMO
        if RUN_DEMO:
            self._processing_input = True
            global DEMO_STATUS
            global DEMO_LOOPS

            if DEBUG_DEMO:
                print DEMO_STATUS
            
            if DEMO_LOOPS > 0:
                if DEBUG_DEMO:
                    print self._current_rotation_offset
                if DEMO_STATUS == "START":
                    self._simulation.set_weight_map(self._simulation.get_random_demo_weight_list())
                    DEMO_STATUS = "DIM"
                if DEMO_STATUS == "DIM" and self._current_intensity > 1:
                    self._current_intensity -= (self._current_adjustment_speed * 2)
                if self._current_intensity <= 0:
                    self.clear_output_text()
                    self._simulation.set_weight_map(self._simulation.get_next_demo_weight_list())
                    DEMO_STATUS = "BRIGHT"
                if DEMO_STATUS == "BRIGHT" and self._current_intensity < 255:
                    self._current_intensity += (self._current_adjustment_speed * 2)
                    if self._current_intensity >= 255:
                        DEMO_STATUS = "DIM"
                        DEMO_LOOPS -= 1
                if DEMO_STATUS == "DIM" and INTENSITY >= 255 and DEMO_LOOPS == 1:
                    DEMO_STATUS = "ROTATE"
                    DEMO_LOOPS = 4
                if DEMO_STATUS == "ROTATE":
                    self._current_rotation_offset -= (self._current_adjustment_speed*self._color_direction)
                    if DEMO_LOOPS > 1:
                        if self._current_rotation_offset+self._default_rotation_offset < 0 or self._current_rotation_offset-self._default_rotation_offset >= (self._rotation_modulo):
                            directional_modulo = self._rotation_modulo                            
                            DEMO_LOOPS -= 1
                            if DEBUG_DEMO:
                                print "DEMO_LOOPS -= 1"
                                print "directional_modulo", directional_modulo
                            self._current_rotation_offset %= directional_modulo
                    if DEMO_LOOPS == 1:
                        DEMO_STATUS = "FINISH_ON_DEFAULT_COLOR"
                        if DEBUG_DEMO:
                            print DEMO_STATUS
                
                if DEMO_STATUS == "FINISH_ON_DEFAULT_COLOR":
                    if self._current_rotation_offset > self._default_rotation_offset:
                        self._current_rotation_offset -= (self._current_adjustment_speed*self._color_direction)
                    else:
                        DEMO_STATUS = "RESTORE_ORIGINAL_WEIGHT_DIM"
                
                if DEMO_STATUS == "RESTORE_ORIGINAL_WEIGHT_DIM":
                    if DEBUG_DEMO:
                            print DEMO_STATUS
                            print "self._current_intensity", self._current_intensity
                            print "self._current_adjustment_speed", self._current_adjustment_speed
                    if self._current_intensity > 0:
                        self._current_intensity -= self._current_adjustment_speed                        
                        if DEBUG_DEMO:
                            print "self._current_intensity", self._current_intensity
                    if self._current_intensity <= 0:
                        self._simulation.load_stored_weight_map()
                        self.reset_forbidden_tiles()
                        DEMO_STATUS = "RESTORE_ORIGINAL_WEIGHT_BRIGHT"
                        if DEBUG_DEMO:
                            print DEMO_STATUS
                if DEMO_STATUS == "RESTORE_ORIGINAL_WEIGHT_BRIGHT":
                    if self._current_intensity < self._default_intensity:
                        self._current_intensity += self._current_adjustment_speed
                    else:
                        self._current_intensity = self._default_intensity
                        self.end_demo()
                        RUN_DEMO = False
        else:
            self._demo_mode_timer += 1

        if self._demo_mode_timer >= self._demo_mode_timeout:
            if self.is_processing():
                self._demo_mode_timer = 0
                return
            else:
                DEMO_STATUS = "RESTARTING"

        if DEMO_STATUS == "RESTARTING":
            self._processing_input = True
            if self._simulation.num_zombies() > 1:
                self._simulation.detrace_z()
            else:
                if self._current_intensity > 0:
                    self._current_intensity -= self._current_adjustment_speed
                else:
                    self._demo_mode_timer = 0
                    self.start_demo()
        
        #reset demo timeout whenever processing is taking place
        if self.is_processing():
            self._demo_mode_timer = 0
                    
        
    def is_processing(self):
        if self._processing_input:
            return True
        else:
            return False

# Start interactive simulation
def run_gui(sim, metric = True, slack_length = 5.0, tile_size = 10, adjustment_speed = 6):
    """
    Encapsulate frame
    """
    gui = ApocalypseGUI(sim, metric, slack_length, tile_size)
    gui.start()
