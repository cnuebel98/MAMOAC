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
    
    def calculate_hypervolume(pareto_front, ref_point):
        # Sort the Pareto front in descending order based on the first dimension
        pareto_front = sorted(pareto_front, key=lambda x: x[0], reverse=True)
        
        # Initialize the hypervolume
        hypervolume = 0.0
        
        # Initialize the previous point's coordinates for volume calculations
        prev_point = ref_point  # Make sure to copy the reference point

        for point in pareto_front:
            # Calculate the volume contributed by the current point
            volume = 1.0
            #print(f"Point: {point}")
            for i in range(len(ref_point)):
                # Calculate the contribution along each dimension
                if point[i] < prev_point[i]:
                    volume *= (prev_point[i] - point[i])
                else:
                    volume *= (prev_point[i] - ref_point[i])
                    break

            # Add the volume contribution to the total hypervolume
            hypervolume += volume

            # Update the previous point to the current one for the next iteration
            prev_point = point

        return hypervolume

    def getParetoDominance(valueList1: list, valueList2: list):
        """Returns pareto dominance in the form of boolean (True -> point1 dominates point2)."""

        #Check if points have same dimensions
        if len(valueList1) != len(valueList2):
            ValueError(f"The points do not have the same dimensions. Point 1: {len(valueList1)}, Point 2: {len(valueList2)}")
        
        betterInOne = False
        #Berry nice check for pareto dominance 
        for a, b in zip(valueList1, valueList2):
            if a > b:
                #print(f"{valueList1} does not dominate {valueList2}")
                return False
            elif a < b:
                betterInOne = True

        return betterInOne