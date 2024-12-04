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

def generate_floating_points(start, end, count):
    return [start + i * (end - start) / (count - 1) for i in range(count)]

def generate_xyz_points(x_start, x_end, x_points_count, z_start, z_end, z_points_count, y_points_file):
    y_points = np.loadtxt(y_points_file)
    x_points = generate_floating_points(x_start, x_end, x_points_count)
    z_points = generate_floating_points(z_start, z_end, z_points_count)
    xyz_points = []
    for z in z_points:
        for y in y_points:
            for x in x_points:
                xyz_points.append([x, y, z])
    xyz_points = np.array(xyz_points)
    return xyz_points, x_points, y_points, z_points

def save_to_h5_file(x_points, y_points, z_points, velocity_matrices, file_name,startval):
    with h5py.File(file_name, 'w') as f:
        f.create_dataset('xcoor', data=x_points)
        f.create_dataset('ycoor', data=y_points)
        f.create_dataset('zcoor', data=z_points)
        for t, velocity_matrix in enumerate(velocity_matrices, start=startval):
            f.create_dataset(f'Velocity_{t:04d}', data=velocity_matrix.reshape((len(z_points), len(y_points), len(x_points), 3)))

def save_to_xmf_file(h5_file_name, xmf_file_name, dimensions, t_start, t_end):
    xmf_content = f"""
<?xml version="1.0" ?>
<Xdmf Version="2.0">
  <Domain>
    <Grid Name="Velocity" GridType="Collection" CollectionType="Temporal">
"""
    for t in range(t_start, t_end + 1):
        xmf_content += f"""
      <Grid Name="Structured Grid" GridType="Uniform">
        <Time Value="{t}" />
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
            {h5_file_name}:/Velocity_{t:04d}
          </DataItem>
        </Attribute>
      </Grid>
"""
    xmf_content += """
    </Grid>
  </Domain>
</Xdmf>
"""
    with open(xmf_file_name, 'w') as f:
        f.write(xmf_content)

# Example usage
# Step 1: Define parameters
file_template = 'Data_{:d}_time.mat'
t_start = 4300
t_end = 4500

# Generate xyz points
x_start = 176.26
x_end = 322.32
x_points_count = 501  # Set the desired number of points
z_start = 99.89
z_end = 139.9
z_points_count = 342  # Set the desired number of points
y_points_file = 'y_points.txt'

xyz_points, x_points, y_points, z_points = generate_xyz_points(x_start, x_end, x_points_count, z_start, z_end, z_points_count, y_points_file)

# Load and reshape velocity data for each time step
velocity_matrices = []
for t in range(t_start, t_end + 1):
    print("\n time: ",t,"\n")
    file_path = file_template.format(t)
    velocity_matrix = load_and_reshape_mat(file_path)
    velocity_matrices.append(velocity_matrix)

# Check if the number of points match
if xyz_points.shape[0] != velocity_matrices[0].shape[0]:
    raise ValueError("The number of points in xyz does not match the number of velocity vectors")

# Save the data to an HDF5 file
h5_file_name = 'CombinedData.h5'
save_to_h5_file(x_points, y_points, z_points, velocity_matrices, h5_file_name,t_start)
print("\nCombined data saved to CombinedData.h5")

# Save the XMF file
xmf_file_name = 'CombinedData.xmf'
dimensions = (x_points_count, len(y_points), z_points_count)
save_to_xmf_file(h5_file_name, xmf_file_name, dimensions, t_start, t_end)
print("\nXMF file saved to CombinedData.xmf")
