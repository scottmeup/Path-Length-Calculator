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