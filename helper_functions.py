class HelperFunctions:

    def get_possible_directions(current_cell, temp_grid):
        '''This function returns a list of possible direction 
        for moving to or shifting to'''
        directions = []
        # even, even or odd, even: A2
        if ((current_cell[0] % 2 == 1 and current_cell[1] % 2 == 0)
            or (current_cell[0] % 2 == 0 and current_cell[1] % 2 == 0)):
            # check all 6 possible cells for validity
            if temp_grid.is_valid_position(current_cell[0], current_cell[1] + 1):
                directions.append("bottom_right")
            if temp_grid.is_valid_position(current_cell[0] - 1, current_cell[1]):
                directions.append("up")
            if temp_grid.is_valid_position(current_cell[0] + 1, current_cell[1]):
                directions.append("down")
            if temp_grid.is_valid_position(current_cell[0], current_cell[1] - 1):
                directions.append("bottom_left")
            if temp_grid.is_valid_position(current_cell[0] - 1, current_cell[1] + 1):
                directions.append("top_right")
            if temp_grid.is_valid_position(current_cell[0] - 1, current_cell[1] - 1):
                directions.append("top_left")

        # row even col odd or odd and odd: A1
        elif((current_cell[0] % 2 == 0 and current_cell[1] % 2 == 1)
            or (current_cell[0] % 2 == 1 and current_cell[1] % 2 == 1)):
            # check all 6 possible cells for validity
            if temp_grid.is_valid_position(current_cell[0] + 1, current_cell[1]):
                directions.append("down")
            if temp_grid.is_valid_position(current_cell[0] + 1, current_cell[1] + 1):
                directions.append("bottom_right")
            if temp_grid.is_valid_position(current_cell[0] + 1, current_cell[1] - 1):
                directions.append("bottom_left")
            if temp_grid.is_valid_position(current_cell[0], current_cell[1] - 1):
                directions.append("top_left")
            if temp_grid.is_valid_position(current_cell[0], current_cell[1] + 1):
                directions.append("top_right")
            if temp_grid.is_valid_position(current_cell[0] - 1, current_cell[1]):
                directions.append("up")
        return directions