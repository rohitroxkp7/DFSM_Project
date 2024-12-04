def process_y_points(input_file, output_removed_file):
    # Read the y points from the original file
    with open(input_file, 'r') as file:
        y_points = file.readlines()

    # Remove every second point
    removed_points = y_points[1::2]
    remaining_points = y_points[::2]

    # Write removed points to a new file
    with open(output_removed_file, 'w') as file:
        file.writelines(removed_points)

    # Overwrite the original file with remaining points
    with open(input_file, 'w') as file:
        file.writelines(remaining_points)

# Example usage
input_file = 'y_points.txt'
output_removed_file = 'removed_points.txt'

process_y_points(input_file, output_removed_file)
