import numpy as np

def generate_xyz_points(x_start, x_end, x_points_count, z_start, z_end, z_points_count, y_points_file):
    # Load y points from the text file
    y_points = np.loadtxt(y_points_file)
    
    # Generate x and z points with equal spacing including the end points
    x_points = np.linspace(x_start, x_end, x_points_count)
    z_points = np.linspace(z_start, z_end, z_points_count)
    
    # Initialize the list to store the generated points
    xyz_points = []
    
    # Iterate over z points
    for z in z_points:
        # Iterate over y points
        for y in y_points:
            # Iterate over x points
            for x in x_points:
                xyz_points.append([x, y, z])
    
    # Convert to numpy array for easier handling
    xyz_points = np.array(xyz_points)
    
    return xyz_points

def save_to_text_file(data, file_name):
    # Save the data to a text file
    np.savetxt(file_name, data, delimiter='\t', header='x\ty\tz', comments='')

def count_points_in_file(file_name):
    with open(file_name, 'r') as file:
        # Skip the header line
        next(file)
        # Count the remaining lines
        num_points = sum(1 for line in file)
    return num_points

# Example usage
x_start = 500
x_end = 680
x_points_count = 617
z_start = 100
z_end = 140
z_points_count = 342
y_points_file = 'y_points.txt'

xyz_points = generate_xyz_points(x_start, x_end, x_points_count, z_start, z_end, z_points_count, y_points_file)
print("\nGenerated XYZ points:")
print(xyz_points)

# Save the generated points to a text file
file_name = 'GeneratedPoints.txt'
save_to_text_file(xyz_points, file_name)
print("\nGenerated points saved to GeneratedPoints.txt")

# Count the total number of points
num_points = count_points_in_file(file_name)
print(f"\nTotal number of points: {num_points}")
