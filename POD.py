'''
Individual snippets of this code with deletion and recreation of variables
might be needed if memory outage occurs during code execution. 
'''

import h5py
import numpy as np

# File path for the HDF5 file
h5_file_path = 'CombinedData.h5'
new_h5_file_path = 'ProcessedData.h5'
xmf_file_path = 'ProcessedData.xmf'

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
C = np.dot(X.T, X).astype(np.float64)

# Eigenvalue decomposition of the covariance matrix
eigenvalues, V = np.linalg.eigh(C)

# Compute the singular values from the eigenvalues
#Sigma_snapshot = np.sqrt(np.flip(eigenvalues))  # Flip to get descending order

# The right singular vectors are the eigenvectors of C, flipped to match order
#V_snapshot = np.fliplr(V)

# Compute the left singular vectors using the relationship U = AV / Sigma
#U_snapshot = np.dot(X, V_snapshot) / Sigma_snapshot


eigenvalues = np.flip(eigenvalues)
V = np.fliplr(V)

phi1 = ( X @ V[:,1] ) * (1/np.sqrt(eigenvalues[1]))
a1 = V[:,1]*np.sqrt(eigenvalues[1])
#vel_mode_1_vector = a1[0]*phi1

######################################################################################
for i in range(X.shape[1]):  # X.shape[1] gives the number of time steps
    vel_mode_i_vector = a1[i] * phi1



with h5py.File(new_h5_file_path, 'w') as new_h5_file:
    # Write spatial coordinates
    new_h5_file.create_dataset('xcoor', data=x)
    new_h5_file.create_dataset('ycoor', data=y)
    new_h5_file.create_dataset('zcoor', data=z)
    start=4300
    # Compute and store velocity modes for each time step
    for i in range(X.shape[1]):  # X.shape[1] gives the number of time steps
        vel_mode_i_vector = a1[i] * phi1
        
        # Reshape vel_mode_i_vector back to (617, 84, 342, 3)
        reshaped_vel_mode = vel_mode_i_vector.reshape(len(z), len(y), len(x), 3)
        
        # Store u, v, w components in the new HDF5 file
        new_h5_file.create_dataset(f'Velocity_{start:04d}', data=reshaped_vel_mode)
        start = start+1

# XMF Header
xmf_content = """<?xml version="1.0" ?>
<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>
<Xdmf Version="2.0">
  <Domain>
    <Grid Name="Velocity" GridType="Collection" CollectionType="Temporal">
"""

# Add Grids for each time step
num_time_steps = X.shape[1]  # Number of time steps
for i in range(4300,4501):
    xmf_content += f"""
      <Grid Name="Structured Grid" GridType="Uniform">
        <Time Value="{i}" />
        <Topology TopologyType="3DRectMesh" NumberOfElements="342 84 501" />
        <Geometry GeometryType="VXVYVZ">
          <DataItem Name="Xcoor" Dimensions="501" NumberType="Float" Precision="4" Format="HDF">
            {new_h5_file_path}:/xcoor
          </DataItem>
          <DataItem Name="Ycoor" Dimensions="84" NumberType="Float" Precision="4" Format="HDF">
            {new_h5_file_path}:/ycoor
          </DataItem>
          <DataItem Name="Zcoor" Dimensions="342" NumberType="Float" Precision="4" Format="HDF">
            {new_h5_file_path}:/zcoor
          </DataItem>
        </Geometry>
        <Attribute Name="Velocity" AttributeType="Vector" Center="Node">
          <DataItem Dimensions="342 84 501 3" NumberType="Float" Precision="4" Format="HDF">
            {new_h5_file_path}:/Velocity_{i:04d}
          </DataItem>
        </Attribute>
      </Grid>
    """

# XMF Footer
xmf_content += """
    </Grid>
  </Domain>
</Xdmf>
"""

# Write the XMF content to the file
with open(xmf_file_path, 'w') as xmf_file:
    xmf_file.write(xmf_content)

print(f"Processed data saved to {new_h5_file_path} and {xmf_file_path}")
