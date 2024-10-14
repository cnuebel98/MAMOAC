class HelperFunctions:

    def get_possible_directions(current_cell, temp_grid):
        '''This function returns a list of possible direction 
        for moving to or shifting to'''
        directions = []
        row, col = current_cell
        row_mod, col_mod = row % 2, col % 2
        # even, even or odd, even: A2
        if ((row_mod == 1 and col_mod == 0) or (row_mod == 0 and col_mod == 0)):
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
        elif((row_mod == 0 and col_mod == 1) or (row_mod == 1 and col_mod == 1)):
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
    
    def calculate_hypervolume(pareto_front, ref_point):
        # Sort the Pareto front in descending order based on the first dimension
        pareto_front = sorted(pareto_front, key=lambda x: x[0], reverse=True)

        # Initialize the hypervolume
        hypervolume = 0.0

        # Initialize the previous point as the reference point
        prev_point = ref_point

        # Loop through each point in the Pareto front
        for point in pareto_front:
            # Calculate the volume of the cuboid formed by this point and the previous one
            volume = 1.0  # Initialize volume for this point

            for i in range(len(ref_point)):
                # Contribution along each dimension is the difference between the previous point and the current one
                volume *= (prev_point[i] - point[i])

            # Add the volume of the current cuboid to the total hypervolume
            hypervolume += volume

            # Update the previous point to be the current point for the next iteration
            prev_point = point

        return hypervolume

