import scipy.io
import numpy as np
import h5py

def load_and_reshape_mat(file_path):
    # Load the .mat file
    mat_data = scipy.io.loadmat(file_path)
    
    # Access the flattened velocity data stored in the variable 'result'
    velocity_data = mat_data['result'].flatten()
    
    # Reshape the data into an Nx3 matrix
    n = len(velocity_data) // 3
    velocity_matrix = velocity_data.reshape((n, 3))
    
    return velocity_matrix

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
    
    return xyz_points, x_points, y_points, z_points

def save_to_h5_file(x_points, y_points, z_points, velocity_matrix, file_name):
    with h5py.File(file_name, 'w') as f:
        f.create_dataset('xcoor', data=x_points)
        f.create_dataset('ycoor', data=y_points)
        f.create_dataset('zcoor', data=z_points)
        f.create_dataset('Velocity_0001', data=velocity_matrix.reshape((len(z_points), len(y_points), len(x_points), 3)))

def save_to_xmf_file(h5_file_name, xmf_file_name, dimensions):
    xmf_content = f"""
<?xml version="1.0" ?>
<Xdmf Version="2.0">
  <Domain>
    <Grid Name="Velocity" GridType="Collection" CollectionType="Temporal">
      <Grid Name="Structured Grid" GridType="Uniform">
        <Time Value="1" />
        <Topology TopologyType="3DRectMesh" NumberOfElements="{dimensions[2]} {dimensions[1]} {dimensions[0]}" />
        <Geometry GeometryType="VXVYVZ">
          <DataItem Name="Xcoor" Dimensions="{dimensions[0]}" NumberType="Float" Precision="4" Format="HDF">
            {h5_file_name}:/xcoor
          </DataItem>
          <DataItem Name="Ycoor" Dimensions="{dimensions[1]}" NumberType="Float" Precision="4" Format="HDF">
            {h5_file_name}:/ycoor
          </DataItem>
          <DataItem Name="Zcoor" Dimensions="{dimensions[2]}" NumberType="Float" Precision="4" Format="HDF">
            {h5_file_name}:/zcoor
          </DataItem>
        </Geometry>
        <Attribute Name="Velocity" AttributeType="Vector" Center="Node">
          <DataItem Dimensions="{dimensions[2]} {dimensions[1]} {dimensions[0]} 3" NumberType="Float" Precision="4" Format="HDF">
            {h5_file_name}:/Velocity_0001
          </DataItem>
        </Attribute>
      </Grid>
    </Grid>
  </Domain>
</Xdmf>
"""
    with open(xmf_file_name, 'w') as f:
        f.write(xmf_content)

# Example usage
# Step 1: Load and reshape .mat data
file_path = 'Data_1_time.mat'
velocity_matrix = load_and_reshape_mat(file_path)

# Step 2: Generate xyz points
x_start = 1608
x_end = 2224
x_points_count = (x_end-x_start)+1
z_start = 853
z_end = 1194
z_points_count = (z_end-z_start)+1
y_points_file = 'y_points.txt'

xyz_points, x_points, y_points, z_points = generate_xyz_points(x_start, x_end, x_points_count, z_start, z_end, z_points_count, y_points_file)

# Step 3: Check if the number of points match
if xyz_points.shape[0] != velocity_matrix.shape[0]:
    raise ValueError("The number of points in xyz does not match the number of velocity vectors")

# Step 4: Save the data to an HDF5 file
h5_file_name = 'CombinedData.h5'
save_to_h5_file(x_points, y_points, z_points, velocity_matrix, h5_file_name)
print("\nCombined data saved to CombinedData.h5")

# Step 5: Save the XMF file
xmf_file_name = 'CombinedData.xmf'
dimensions = (x_points_count, len(y_points), z_points_count)
save_to_xmf_file(h5_file_name, xmf_file_name, dimensions)
print("\nXMF file saved to CombinedData.xmf")
