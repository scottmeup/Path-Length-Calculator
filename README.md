RUN by loading FullpathCalculator.py

TODO:
-editor mode for cell weight, cabinet ID, etc.

DONE:
-Move "forbidden" setting from GUI to program layer
-figure out why best_move sometimes returns only one element of a tuple (int)
-add gui text inputs for setting a + z sides
-figure out what's going on with GUI toggle mouse type: it seems to be using / listing one mode in the cycle ahead of what the variable says it's set to
-Fixed bug in best move generator (would sometimes start list with int instead of tuple)
-Improved valid move generator: no longer returns coordinates already occupied by trace

changed lists to tuples.

simulation._cabinet_list = {'001-A': [13, 70], '001-B': [12, 70], '002-B': [5, 70], '002-A': [4, 70]}
simulation._forbidden_list = {'001-A': [[1, 66], [1, 67], [28, 66], [28, 67]],
                                '001-B': [[1, 66], [1, 67], [28, 66], [28, 67]],
                                '002-A': [[15, 66], [15, 67]],
                                '002-B': [[15, 66], [15, 67]]}

#using coordinate for cabinet 801                                
offset = [27, 46]
row_800 = {'801': [offset[0]-0, offset[1]], 
           '802': [offset[0]-1, offset[1]], 
           '803': [offset[0]-2, offset[1]], 
           '804': [offset[0]-3, offset[1]], 
           '805': [offset[0]-4, offset[1]], 
           '806': [offset[0]-5, offset[1]], 
           '807': [offset[0]-6, offset[1]], 
           '808': [offset[0]-7, offset[1]], 
           '809': [offset[0]-8, offset[1]],
           '810': [offset[0]-9, offset[1]], 
           '811': [offset[0]-10, offset[1]], 
           '812': [offset[0]-11, offset[1]], 
           '813': [offset[0]-12, offset[1]], 
           '814': [offset[0]-13, offset[1]], 
           '815': [offset[0]-14, offset[1]], 
           '816': [offset[0]-15, offset[1]], 
           '817': [offset[0]-16, offset[1]], 
           '818': [offset[0]-17, offset[1]], 
           '819': [offset[0]-18, offset[1]], 
           '820': [offset[0]-19, offset[1]], 
           '821': [offset[0]-20, offset[1]], 
           '822': [offset[0]-21, offset[1]], 
           '823': [offset[0]-22, offset[1]], 
           '824': [offset[0]-23, offset[1]], 
           '825': [offset[0]-24, offset[1]], 
           '826': [offset[0]-25, offset[1]]}

#using coordinate for cabinet 701   
offset = [27, 49]          
row_700 = {'701': [offset[0]-0, offset[1]], 
           '702': [offset[0]-1, offset[1]], 
           '703': [offset[0]-2, offset[1]], 
           '704': [offset[0]-3, offset[1]], 
           '705': [offset[0]-4, offset[1]], 
           '706': [offset[0]-5, offset[1]], 
           '707': [offset[0]-6, offset[1]], 
           '708': [offset[0]-7, offset[1]], 
           '709': [offset[0]-8, offset[1]],
           '710': [offset[0]-9, offset[1]], 
           '711': [offset[0]-10, offset[1]], 
           '712': [offset[0]-11, offset[1]], 
           '713': [offset[0]-12, offset[1]], 
           '714': [offset[0]-13, offset[1]], 
           '715': [offset[0]-14, offset[1]], 
           '716': [offset[0]-15, offset[1]], 
           '717': [offset[0]-16, offset[1]], 
           '718': [offset[0]-17, offset[1]], 
           '719': [offset[0]-18, offset[1]], 
           '720': [offset[0]-19, offset[1]], 
           '721': [offset[0]-20, offset[1]], 
           '722': [offset[0]-21, offset[1]], 
           '723': [offset[0]-22, offset[1]], 
           '724': [offset[0]-23, offset[1]], 
           '725': [offset[0]-24, offset[1]], 
           '726': [offset[0]-25, offset[1]]}
           
#using coordinate for cabinet 601   
offset = [27, 54]          
row_600 = {'601': [offset[0]-0, offset[1]], 
           '602': [offset[0]-1, offset[1]], 
           '603': [offset[0]-2, offset[1]], 
           '604': [offset[0]-3, offset[1]], 
           '605': [offset[0]-4, offset[1]], 
           '606': [offset[0]-5, offset[1]], 
           '607': [offset[0]-6, offset[1]], 
           '608': [offset[0]-7, offset[1]], 
           '609': [offset[0]-8, offset[1]],
           '610': [offset[0]-9, offset[1]], 
           '611': [offset[0]-10, offset[1]], 
           '612': [offset[0]-11, offset[1]], 
           '613': [offset[0]-12, offset[1]], 
           '614': [offset[0]-13, offset[1]], 
           '615': [offset[0]-14, offset[1]], 
           '616': [offset[0]-15, offset[1]], 
           '617': [offset[0]-16, offset[1]], 
           '618': [offset[0]-17, offset[1]], 
           '619': [offset[0]-18, offset[1]], 
           '620': [offset[0]-19, offset[1]], 
           '621': [offset[0]-20, offset[1]], 
           '622': [offset[0]-21, offset[1]], 
           '623': [offset[0]-22, offset[1]], 
           '624': [offset[0]-23, offset[1]], 
           '625': [offset[0]-24, offset[1]], 
           '626': [offset[0]-25, offset[1]]}
           
#using coordinate for cabinet 501   
offset = [27, 57]          
row_500 = {'501': [offset[0]-0, offset[1]], 
           '502': [offset[0]-1, offset[1]], 
           '503': [offset[0]-2, offset[1]], 
           '504': [offset[0]-3, offset[1]], 
           '505': [offset[0]-4, offset[1]], 
           '506': [offset[0]-5, offset[1]], 
           '507': [offset[0]-6, offset[1]], 
           '508': [offset[0]-7, offset[1]], 
           '509': [offset[0]-8, offset[1]],
           '510': [offset[0]-9, offset[1]], 
           '511': [offset[0]-10, offset[1]], 
           '512': [offset[0]-11, offset[1]], 
           '513': [offset[0]-12, offset[1]], 
           '514': [offset[0]-13, offset[1]], 
           '515': [offset[0]-14, offset[1]], 
           '516': [offset[0]-15, offset[1]], 
           '517': [offset[0]-16, offset[1]], 
           '518': [offset[0]-17, offset[1]], 
           '519': [offset[0]-18, offset[1]], 
           '520': [offset[0]-19, offset[1]], 
           '521': [offset[0]-20, offset[1]], 
           '522': [offset[0]-21, offset[1]], 
           '523': [offset[0]-22, offset[1]], 
           '524': [offset[0]-23, offset[1]], 
           '525': [offset[0]-24, offset[1]], 
           '526': [offset[0]-25, offset[1]]}
           
#using coordinate for cabinet 401   
offset = [27, 62]          
row_400 = {'407': [offset[0]-6, offset[1]], 
           '408': [offset[0]-7, offset[1]], 
           '409': [offset[0]-8, offset[1]],
           '410': [offset[0]-9, offset[1]], 
           '411': [offset[0]-10, offset[1]], 
           '412': [offset[0]-11, offset[1]], 
           '413': [offset[0]-12, offset[1]], 
           '414': [offset[0]-13, offset[1]], 
           '415': [offset[0]-14, offset[1]], 
           '416': [offset[0]-15, offset[1]], 
           '417': [offset[0]-16, offset[1]], 
           '418': [offset[0]-17, offset[1]], 
           '419': [offset[0]-18, offset[1]], 
           '420': [offset[0]-19, offset[1]], 
           '421': [offset[0]-20, offset[1]], 
           '422': [offset[0]-21, offset[1]], 
           '423': [offset[0]-22, offset[1]], 
           '424': [offset[0]-23, offset[1]], 
           '425': [offset[0]-24, offset[1]], 
           '426': [offset[0]-25, offset[1]]}
          
#using coordinate for cabinet 301   
offset = [27, 65]          
row_300 = {'307': [offset[0]-6, offset[1]], 
           '308': [offset[0]-7, offset[1]], 
           '309': [offset[0]-8, offset[1]],
           '310': [offset[0]-9, offset[1]], 
           '311': [offset[0]-10, offset[1]], 
           '312': [offset[0]-11, offset[1]], 
           '313': [offset[0]-12, offset[1]], 
           '314': [offset[0]-13, offset[1]], 
           '315': [offset[0]-14, offset[1]], 
           '316': [offset[0]-15, offset[1]], 
           '317': [offset[0]-16, offset[1]], 
           '318': [offset[0]-17, offset[1]], 
           '319': [offset[0]-18, offset[1]], 
           '320': [offset[0]-19, offset[1]], 
           '321': [offset[0]-20, offset[1]], 
           '322': [offset[0]-21, offset[1]], 
           '323': [offset[0]-22, offset[1]], 
           '324': [offset[0]-23, offset[1]], 
           '325': [offset[0]-24, offset[1]], 
           '326': [offset[0]-25, offset[1]]}