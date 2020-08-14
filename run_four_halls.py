# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 16:19:56 2016

@author: andrewscott
"""

import FullpathCalculator
import poc_zombie_gui

#each hall is 30*75
#total board dimensions are set to (2*hall_size)+1, for 4 halls 1 is used for interconnectivity tiles
hall_dimension = (30, 75)
n_halls = (2, 2)
height = n_halls[0]*hall_dimension[0]+n_halls[0]-1
width = n_halls[1]*hall_dimension[1]+n_halls[1]-1
width = 151
border = 1
tile_size = 5

four_halls_site_01 = FullpathCalculator.path_calculator(height, width)
hall_1_offset = (31, 0)
hall_2_offset = (0, 0)
hall_3_offset = (0, 76)
hall_4_offset = (31, 76)
offset = hall_1_offset

clear_lines = []
excluded_tiles = []
                
                #setup hall 1
              #full hall horizontal paths
clear_lines = clear_lines + [((offset[0]+2, offset[1]+2), (offset[0]+2, offset[1]+74)),
              ((offset[0]+16, offset[1]+2), (offset[0]+16, offset[1]+74)),
              ((offset[0]+29, offset[1]+2), (offset[0]+29, offset[1]+74)),
              #full-hall vertical paths
              ((offset[0]+2, offset[1]+2), (offset[0]+29, offset[1]+2)),
              ((offset[0]+2, offset[1]+5), (offset[0]+29, offset[1]+5)),
              ((offset[0]+2, offset[1]+8), (offset[0]+29, offset[1]+8)),
              ((offset[0]+2, offset[1]+13), (offset[0]+29, offset[1]+13)),
              ((offset[0]+2, offset[1]+16), (offset[0]+29, offset[1]+16)),
              ((offset[0]+2, offset[1]+21), (offset[0]+29, offset[1]+21)),
              ((offset[0]+2, offset[1]+24), (offset[0]+29, offset[1]+24)),
              ((offset[0]+2, offset[1]+29), (offset[0]+29, offset[1]+29)),
              ((offset[0]+2, offset[1]+32), (offset[0]+29, offset[1]+32)),
              ((offset[0]+2, offset[1]+37), (offset[0]+29, offset[1]+37)),
              ((offset[0]+2, offset[1]+40), (offset[0]+29, offset[1]+40)),
              ((offset[0]+2, offset[1]+47), (offset[0]+29, offset[1]+47)),
              ((offset[0]+2, offset[1]+50), (offset[0]+29, offset[1]+50)),
              ((offset[0]+2, offset[1]+55), (offset[0]+29, offset[1]+55)),
              ((offset[0]+2, offset[1]+58), (offset[0]+29, offset[1]+58)),
              ((offset[0]+2, offset[1]+63), (offset[0]+29, offset[1]+63)),
              ((offset[0]+2, offset[1]+66), (offset[0]+29, offset[1]+66)),
              ((offset[0]+2, offset[1]+71), (offset[0]+29, offset[1]+71)),
              ((offset[0]+2, offset[1]+74), (offset[0]+29, offset[1]+74)),
              #additional paths
              ((offset[0]+2, offset[1]+69), (offset[0]+16, offset[1]+69)),
              ((offset[0]+2, offset[1]+70), (offset[0]+16, offset[1]+70)),
              ((offset[0]+2, offset[1]+73), (offset[0]+16, offset[1]+73)),
              ((offset[0]+2, offset[1]+74), (offset[0]+16, offset[1]+74)),
              ((offset[0]+6, offset[1]+69), (offset[0]+6, offset[1]+74)),
              ((offset[0]+9, offset[1]+69), (offset[0]+9, offset[1]+74)),
              ((offset[0]+14, offset[1]+69), (offset[0]+14, offset[1]+74)),
              ((offset[0]+15, offset[1]+69), (offset[0]+15, offset[1]+74)),
              ((offset[0]+16, offset[1]+69), (offset[0]+16, offset[1]+74))]

excluded_tiles = excluded_tiles + [four_halls_site_01.panel_to_index(offset[0] + 2, offset[1] + 75),
                                   four_halls_site_01.panel_to_index(offset[0] + 16, offset[1] + 75),
                                   four_halls_site_01.panel_to_index(offset[0] + 29, offset[1] + 75)]
                  
#setup hall 2
offset = hall_2_offset                 
clear_lines = clear_lines + [((offset[0]+2, offset[1]+2), (offset[0]+2, offset[1]+74)),
              ((offset[0]+16, offset[1]+2), (offset[0]+16, offset[1]+74)),
              ((offset[0]+29, offset[1]+2), (offset[0]+29, offset[1]+74)),
              #full-hall vertical paths
              ((offset[0]+2, offset[1]+2), (offset[0]+29, offset[1]+2)),
              ((offset[0]+2, offset[1]+5), (offset[0]+29, offset[1]+5)),
              ((offset[0]+2, offset[1]+8), (offset[0]+29, offset[1]+8)),
              ((offset[0]+2, offset[1]+13), (offset[0]+29, offset[1]+13)),
              ((offset[0]+2, offset[1]+16), (offset[0]+29, offset[1]+16)),
              ((offset[0]+2, offset[1]+21), (offset[0]+29, offset[1]+21)),
              ((offset[0]+2, offset[1]+24), (offset[0]+29, offset[1]+24)),
              ((offset[0]+2, offset[1]+29), (offset[0]+29, offset[1]+29)),
              ((offset[0]+2, offset[1]+32), (offset[0]+29, offset[1]+32)),
              ((offset[0]+2, offset[1]+37), (offset[0]+29, offset[1]+37)),
              ((offset[0]+2, offset[1]+40), (offset[0]+29, offset[1]+40)),
              ((offset[0]+2, offset[1]+47), (offset[0]+29, offset[1]+47)),
              ((offset[0]+2, offset[1]+50), (offset[0]+29, offset[1]+50)),
              ((offset[0]+2, offset[1]+55), (offset[0]+29, offset[1]+55)),
              ((offset[0]+2, offset[1]+58), (offset[0]+29, offset[1]+58)),
              ((offset[0]+2, offset[1]+63), (offset[0]+29, offset[1]+63)),
              ((offset[0]+2, offset[1]+66), (offset[0]+29, offset[1]+66)),
              ((offset[0]+2, offset[1]+71), (offset[0]+29, offset[1]+71)),
              ((offset[0]+2, offset[1]+74), (offset[0]+29, offset[1]+74))]
              
#setup hall 3
offset = hall_3_offset                 
clear_lines = clear_lines + [((offset[0]+2, offset[1]+2), (offset[0]+2, offset[1]+74)),
              ((offset[0]+16, offset[1]+2), (offset[0]+16, offset[1]+74)),
              ((offset[0]+29, offset[1]+2), (offset[0]+29, offset[1]+74)),
              #full-hall vertical paths
              ((offset[0]+2, offset[1]+2), (offset[0]+29, offset[1]+2)),
              ((offset[0]+2, offset[1]+5), (offset[0]+29, offset[1]+5)),
              ((offset[0]+2, offset[1]+8), (offset[0]+29, offset[1]+8)),
              ((offset[0]+2, offset[1]+13), (offset[0]+29, offset[1]+13)),
              ((offset[0]+2, offset[1]+16), (offset[0]+29, offset[1]+16)),
              ((offset[0]+2, offset[1]+21), (offset[0]+29, offset[1]+21)),
              ((offset[0]+2, offset[1]+24), (offset[0]+29, offset[1]+24)),
              ((offset[0]+2, offset[1]+29), (offset[0]+29, offset[1]+29)),
              ((offset[0]+2, offset[1]+32), (offset[0]+29, offset[1]+32)),
              ((offset[0]+2, offset[1]+37), (offset[0]+29, offset[1]+37)),
              ((offset[0]+2, offset[1]+40), (offset[0]+29, offset[1]+40)),
              ((offset[0]+2, offset[1]+47), (offset[0]+29, offset[1]+47)),
              ((offset[0]+2, offset[1]+50), (offset[0]+29, offset[1]+50)),
              ((offset[0]+2, offset[1]+55), (offset[0]+29, offset[1]+55)),
              ((offset[0]+2, offset[1]+58), (offset[0]+29, offset[1]+58)),
              ((offset[0]+2, offset[1]+63), (offset[0]+29, offset[1]+63)),
              ((offset[0]+2, offset[1]+66), (offset[0]+29, offset[1]+66)),
              ((offset[0]+2, offset[1]+71), (offset[0]+29, offset[1]+71)),
              ((offset[0]+2, offset[1]+74), (offset[0]+29, offset[1]+74))]              

#setup hall 4
offset = hall_4_offset                 
clear_lines = clear_lines + [((offset[0]+2, offset[1]+2), (offset[0]+2, offset[1]+74)),
              ((offset[0]+16, offset[1]+2), (offset[0]+16, offset[1]+74)),
              ((offset[0]+29, offset[1]+2), (offset[0]+29, offset[1]+74)),
              #full-hall vertical paths
              ((offset[0]+2, offset[1]+2), (offset[0]+29, offset[1]+2)),
              ((offset[0]+2, offset[1]+5), (offset[0]+29, offset[1]+5)),
              ((offset[0]+2, offset[1]+8), (offset[0]+29, offset[1]+8)),
              ((offset[0]+2, offset[1]+13), (offset[0]+29, offset[1]+13)),
              ((offset[0]+2, offset[1]+16), (offset[0]+29, offset[1]+16)),
              ((offset[0]+2, offset[1]+21), (offset[0]+29, offset[1]+21)),
              ((offset[0]+2, offset[1]+24), (offset[0]+29, offset[1]+24)),
              ((offset[0]+2, offset[1]+29), (offset[0]+29, offset[1]+29)),
              ((offset[0]+2, offset[1]+32), (offset[0]+29, offset[1]+32)),
              ((offset[0]+2, offset[1]+37), (offset[0]+29, offset[1]+37)),
              ((offset[0]+2, offset[1]+40), (offset[0]+29, offset[1]+40)),
              ((offset[0]+2, offset[1]+47), (offset[0]+29, offset[1]+47)),
              ((offset[0]+2, offset[1]+50), (offset[0]+29, offset[1]+50)),
              ((offset[0]+2, offset[1]+55), (offset[0]+29, offset[1]+55)),
              ((offset[0]+2, offset[1]+58), (offset[0]+29, offset[1]+58)),
              ((offset[0]+2, offset[1]+63), (offset[0]+29, offset[1]+63)),
              ((offset[0]+2, offset[1]+66), (offset[0]+29, offset[1]+66)),
              ((offset[0]+2, offset[1]+71), (offset[0]+29, offset[1]+71)),
              ((offset[0]+2, offset[1]+74), (offset[0]+29, offset[1]+74))]

offset = hall_1_offset                  
#define coord dictionaries
four_halls_site_01._z_side_list = ("212-A", "212-B", "216-A", "216-B")
#four_halls_site_01._z_side_coord_list = {'212-A': (1, 1), '212-B': (1, 1), '216-A': (1, 1), '216-B': (1, 1)}
four_halls_site_01._z_side_hall_list = {'212-A': 0, '212-B': 0, '216-A': 0, '216-B': 0}
hall_1_cabinet_list = {'212-A': (offset[0]+13, offset[1]+70),
                       '212-B': (offset[0]+12, offset[1]+70), 
                       '216-B': (offset[0]+5, offset[1]+70), 
                       '216-A': (offset[0]+4, offset[1]+70)}

#this forbidden list only blocks the entrance areas
four_halls_site_01._forbidden_list = {'212-A': ((offset[0] + 1, offset[1] + 66), (offset[0] + 1, offset[1] + 67), (offset[0] + 28, offset[1] + 66), (offset[0] + 28, offset[1] + 67)),
                                '212-B': ((offset[0]+1, offset[1]+66), (offset[0]+1, offset[1]+67), (offset[0]+28, offset[1]+66), (offset[0]+28, offset[1]+67)),
                                '216-A': ((offset[0]+15, offset[1]+66), (offset[0]+15, offset[1]+67)),
                                '216-B': ((offset[0]+15, offset[1]+66), (offset[0]+15, offset[1]+67))}
                  
racetrack =  four_halls_site_01.all_paths(clear_lines, excluded_tiles)
no_path = []
for grid_y in range(0, height):
    for grid_x in range(0, width):
        no_path.append((grid_y, grid_x))
#print no_path

floorplan = four_halls_site_01.difference_of_lists(no_path, racetrack)
four_halls_site_01.set_floorplan(floorplan)

#create and add the midpoint to the forbidden list of cabinets that don't use
#the midpoint as an access path: traces should run around the outside of the track
midpoint = tuple(four_halls_site_01.line((offset[0] + 16, offset[1] + 2), (offset[0] + 16, offset[1] + 68)))
two_one_six_a = four_halls_site_01._forbidden_list['216-A']
two_one_six_b = four_halls_site_01._forbidden_list['216-B']
four_halls_site_01._forbidden_list['216-A'] = midpoint + two_one_six_a
four_halls_site_01._forbidden_list['216-B'] = midpoint + two_one_six_b

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
hall1_reverse_cabinet_list = four_halls_site_01.invert_dictionary(hall_1_cabinet_list)

#add the hall dictionaries to the 'all' lists
four_halls_site_01._all_hall_cabinet_list.append(hall_1_cabinet_list)
four_halls_site_01._all_hall_reverse_cabinet_list.append(hall1_reverse_cabinet_list)

#Starting points for a + z sides
starting_a = [27, 54]
starting_z = four_halls_site_01._all_hall_cabinet_list[0][four_halls_site_01._z_side_list[-1]]
four_halls_site_01.set_aside(starting_a[0], starting_a[1])
four_halls_site_01.set_zside(starting_z[0], starting_z[1])

poc_zombie_gui.run_gui(four_halls_site_01, tile_size=5, adjustment_speed = 1)