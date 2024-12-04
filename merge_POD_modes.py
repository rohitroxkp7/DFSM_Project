import h5py
import numpy as np

# File path for the HDF5 file
h5_file_path = 'CombinedData.h5'
new_h5_file_path = 'POD_modes_combined_t_0.h5'
xmf_file_path = 'POD_modes_combined_t_0.xmf'

# Number of modes to extract and sum up
N = 5  # You can set this value as needed

# Load the HDF5 file and process the velocity data
velocity_data_list = []

with h5py.File(h5_file_path, 'r') as h5_file:
    # Extract spatial coordinates
    x = h5_file['xcoor'][:]
    y = h5_file['ycoor'][:]
    z = h5_file['zcoor'][:]
    
    # Calculate the total number of spatial points
    total_points = len(x) * len(y) * len(z)
    
    # Extract velocity data from Velocity_0001 to Velocity_N
    for key in h5_file.keys():
        if key.startswith('Velocity_'):
            velocity_data = h5_file[key][:]
            # Reshape the velocity data to (617*84*342) rows by 3 columns
            reshaped_data = velocity_data.reshape(-1, 3)
            # Flatten the reshaped data into a single column vector
            column_vector = reshaped_data.flatten()
            velocity_data_list.append(column_vector)

# Convert the list to a matrix X where each column is a time step
X = np.array(velocity_data_list).T
X = X.astype(np.float64)

# Covariance matrix
C = np.dot(X.T, X).astype(np.float64)

# Eigenvalue decomposition of the covariance matrix
eigenvalues, V = np.linalg.eigh(C)

# Flip eigenvalues and eigenvectors to descending order
eigenvalues = np.flip(eigenvalues)
V = np.fliplr(V)


phi_k = ( X @ V[:,1] ) * (1/np.sqrt(eigenvalues[1])) 
a1 = V[:,1]*np.sqrt(eigenvalues[1])

# Initialize the reconstructed dataset for the first time step
reconstructed_data = np.zeros_like(phi_k)

# Sum the first N modes to reconstruct the dataset for the first time step
for k in range(N):
    phi_k = (X @ V[:, k]) * (1/np.sqrt(eigenvalues[k]))
    a_k = V[:, k] * np.sqrt(eigenvalues[k])
    
    # Add the contribution of the k-th mode to the reconstruction
    reconstructed_data += a_k[0] * phi_k

# At this point, 'reconstructed_data' contains the reconstructed dataset 
# for the first time step using the first N modes.

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

h5_file_name = 'POD_modes_combined_t_0.h5'
save_to_h5_file(x, y, z, reconstructed_data, h5_file_name)
print("\nCombined data saved to POD_modes_combined_t_0.h5")

# Step 5: Save the XMF file
xmf_file_name = 'POD_modes_combined_t_0.xmf'
dimensions = (len(x), len(y), len(z))
save_to_xmf_file(h5_file_name, xmf_file_name, dimensions)
print("\nXMF file saved to POD_modes_combined_t_0.xmf")