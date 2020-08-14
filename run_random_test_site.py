import FullpathCalculator
import poc_zombie_gui
import random

height = 30
width = 75
border = 1

test_site = FullpathCalculator.path_calculator(height, width)

test_site.set_weight_map(test_site.get_random_demo_weight_list())
test_site.store_current_weight_map()

for row in range(height):
    for col in range(width):
        test_site.set_full(row, col)

for row in range(height):
    for col in range(width):
        #test_site.set_weight(row, col, dummy_idx)
        #ratio of coordinates to start setting as blocked
        direction = 0
        start = 0
        end = 0
        if not test_site.is_empty(row, col):
            #35/1000 is about the max you want with lengths of between 1/10 and 1/2 the largest grid dimension
            if random.randrange(1000) < 30:
                length = random.randrange(max(width, height)/10, max(width, height)/2, 1)

                #pick a direction, forward or backward
                if random.randrange(2) < 1:
                    direction = -1
                else:
                    direction = 1

                #pick a direction, vertical or horizontal
                #vertical
                if random.randrange(2) < 1:
                    if direction == 1:
                        start = row
                        end = min((row+length)*direction, height)
                    elif direction == -1:
                        start = max((row+length)*direction, 0)
                        end = row
                    for dummy_idx in range(start, end, direction):
                        if dummy_idx < 0 or dummy_idx > height:
                            raise ValueError, "height out of bounds: " + str(dummy_idx)
                        test_site.set_empty(dummy_idx, col)

                #horizontal
                else:
                    if direction == 1:
                        start = col
                        end = min((col+length)*direction, width)
                    elif direction == -1:
                        start = max((col+length)*direction, 0)
                        end = col
                    for dummy_idx in range(start, end, direction):
                        if dummy_idx < 0 or dummy_idx > width:
                            raise ValueError, "width out of bounds: " + str(dummy_idx)
                        test_site.set_empty(row, dummy_idx)
                if col+1 < width:
                    col += 1
                if row+1 < height:
                    row += 1

            #random tiles
            if random.randrange(1000) < 200:
                test_site.set_empty(row, col)



hall_dict = {1: ((border, border), (height-(2*border), width-(2*border))),
             2: ((height+border, border), (height-2*border, width-2*border))}

def print_halls():
    for item in hall_dict:
        print item, ":"
        print hall_dict[item][0]
        print hall_dict[item][1]

poc_zombie_gui.run_gui(test_site)