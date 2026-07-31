
class BitmapTrace:
    """
    BitmapTrace is a particular kind of shading/filling that takes a bitmap (array of booleans)
    and converts it to a series of paths.
    """

    def simple_horizontal_scan(bitmap):
        paths = []
        rows = len(bitmap)
        cols = len(bitmap[0])
        visited = [[0 for col in row] for row in bitmap]

        for row in range(len(bitmap)):
            for col in range(len(bitmap[row])):
                # Find a starting cell
                if (bitmap[row][col] and visited[row][col] == 0):
                    # Begin a path
                    path = []
                    current_col = col
                    current_row = row
                    while (current_col < cols and bitmap[current_row][current_col]):
                        x = current_col
                        y = current_row
                        path.append((x, y))
                        visited[current_row][current_col] += 1
                        current_col += 1
                    paths.append(path)

        return paths

    def horizontal_scan(bitmap):
        """
        Creates lines in a generally horizontal way
        0. Starts scan at 0,0
        1. Find a starting cell
            Start a path
        2. From that starting cell:
            2a. Set current cell, add to path, increment visited 
            2b. Check direction for valid target
                Yes: go to 2a
                No:

        ## Direction Priority Listing

        I should have like a priority list of which directions to go
        Maybe a locked in, default list, and also a "stack" list to handle temporary adjustments
            Why a stack?
            I want it to be able to go "around" a small obstacle
        Or, maybe it's sort of a heuristic pathfinding approach, where cells get a value for how valid they are, and I choose the best one?
        Have a default grid, and then also a temporary grid?
        Subtract the visited value to de-prioritize visited cells
        0 0 3
        0 0 4 ->
        1 2 3

        If it goes down to the right, update the modifier:
        0 0 2
        0 0 0
        0 0 0

        If a modifier-influenced cell is chosen, decrement that cell

        Okay, what if I didn't get ahead of myself, and I made a "simple" scan, that only goes in one direction, only perfect horizontal lines?




        """
        paths = []
        rows = len(bitmap)
        cols = len(bitmap[0])

        visited = [[0 for col in row] for row in bitmap]

        for row in bitmap:
            for col in row:
                # Find a starting cell
                if (bitmap[row][col] and visited[row][col] == 0):
                    # Begin a path
                    path = []
                    # Do I create the path as (row, col) or (col, row)? 
                    # Is it "gridwise" or x,y coordinate? Going with x,y I think
                    x = col
                    y = row
                    path.append(x, y)
                    visited[row][col] += 1
                    direction = 1 # TODO; maybe this should be a 2d vector?
                    
