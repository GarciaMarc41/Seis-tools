#!/usr/bin/env python
# coding: utf-8

# In[133]:


import pygmt
import pandas as pd
import os
import numpy as np
import warnings
warnings.filterwarnings("ignore")

data = pd.read_csv("IEB_export_south_mexico.csv")

# Define A and A' coordinates
A = (-95.7, 15.5)
A_prime = (-94.7, 16.5)

C = (-95.1, 15)
C_prime = (-94.2, 16.2)

# Define B and B' coordinates
B = (-93.7,  14.2)
B_prime = (-93, 15.4)


D = (-94.3, 14.5)
D_prime = (-93.6, 15.8)

F = (-93, 13.9)
F_prime = (-92.4, 15.1)


rectangle1 = [A, A_prime, C_prime, C, A]
rectangle2 = [C, C_prime, D_prime, D, C]
rectangle3 = [D, D_prime, B_prime, B, D]
rectangle4 = [B, B_prime, F_prime, F, B]







region = "-98/-91/13/19"
# Plotting data 
fig = pygmt.Figure()

# Color pallets for topo
pygmt.makecpt(cmap='etopo1', series='-8000/8000/1000', continuous=True)

# etopo data file
topo_data = '@earth_relief_15s'

# Plot high res topography
fig.grdimage(grid=topo_data, region=region, projection='M4i', frame=True, shading=True)

# Adding coasts & base layer
fig.coast(shorelines=True, frame=True, borders=["1/0.8p,black", "2/0.5p,black", "3/0.5p,black"])
fig.basemap(region=region, frame=["af",])

# Color pallet for eqlocations
pygmt.makecpt(cmap="viridis", series=[data.Depth.min(), data.Depth.max()])

# Plotting data points
fig.plot(x=data.Lon, y=data.Lat, style="c0.07c", fill=data.Depth, cmap=True, pen="black")



fig.plot(x=[point[0] for point in rectangle1], y=[point[1] for point in rectangle1], pen="1p,yellow")
fig.plot(x=[point[0] for point in rectangle2], y=[point[1] for point in rectangle2], pen="1p,yellow")
fig.plot(x=[point[0] for point in rectangle3], y=[point[1] for point in rectangle3], pen="1p,yellow")
fig.plot(x=[F[0], F_prime[0]], y=[F[1], F_prime[1]], pen="1p,red")
fig.plot(x=[point[0] for point in rectangle4], y=[point[1] for point in rectangle4], pen="1p,yellow")

#fig.plot(x=[D[0], D_prime[0]], y=[D[1], D_prime[1]], pen="1p,red")
fig.show()


# In[134]:






# In[148]:


import pandas as pd
import matplotlib.pyplot as plt

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# Read the earthquake data CSV file
data = pd.read_csv("IEB_export_south_mexico.csv")

# Define the coordinates of the rectangle
A = (-95.7, 15.5)
A_prime = (-94.7, 16.5)

C = (-95.1, 15)
C_prime = (-94.2, 16.2)

# Filter the earthquakes inside the rectangle
filtered_data = data[
    (data['Lon'] >= min(A[0], A_prime[0])) &
    (data['Lon'] <= max(A[0], A_prime[0])) &
    (data['Lat'] >= min(A[1], C[1])) &
    (data['Lat'] <= max(A_prime[1], C_prime[1]))
]

# Save the filtered data as a CSV file
filtered_data.to_csv("filtered_earthquakes.csv", index=False)

# Print the count of earthquakes in the filtered list
count = filtered_data.shape[0]
print("Number of earthquakes inside the rectangle:", count)

# Read the earthquake data CSV file
data = pd.read_csv("filtered_earthquakes.csv")


# Set up the plot
fig, ax = plt.subplots()

# Plot the rectangle
rectangle = [A, A_prime, C_prime, C, A]
rectangle_x = [point[0] for point in rectangle]
rectangle_y = [point[1] for point in rectangle]
ax.plot(rectangle_x, rectangle_y, color='red', linewidth=1)

# Create a color palette for the earthquakes
cmap = plt.get_cmap("viridis")
normalize = plt.Normalize(data['Depth'].min(), data['Depth'].max())
colors = [cmap(normalize(value)) for value in data['Depth']]

# Plot the earthquakes inside the rectangle
ax.scatter(data['Lon'], data['Lat'], c=colors, marker='o')

# Set labels and title
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Region Selected")

# Show the plot
plt.show()

# Print the count of earthquakes inside the rectangle
count = data.shape[0]
print("Number of earthquakes inside the rectangle:", count)

# Calculate distance along A-A' for each earthquake and add it to the DataFrame
data['distance'] = data.apply(lambda row: haversine(A[1], A[0], row.Lat, row.Lon), axis=1)

# Set up the cross-section plot
fig, ax = plt.subplots()

# Create a color palette for the cross-section plot
cmap = plt.get_cmap("viridis")
normalize = plt.Normalize(data['Depth'].min(), data['Depth'].max())
colors = [cmap(normalize(value)) for value in data['Depth']]

# Plot the cross-section
ax.scatter(data['distance'], data['Depth'], c=colors, marker="o")

# Invert the y-axis
ax.invert_yaxis()

# Set labels and title
ax.set_xlabel("Distance along A-A' (km)")
ax.set_ylabel("Depth")
ax.set_title("Cross-Section Map of Earthquake Depths")

# Show the plot
plt.show()

# Print the count of earthquakes in the cross-section plot
count = data.shape[0]
print("Number of earthquakes in the cross-section plot:", count)


# In[144]:


import pandas as pd
import matplotlib.pyplot as plt


# Read the earthquake data CSV file
data = pd.read_csv("IEB_export_south_mexico.csv")

# Define the coordinates of the rectangle
C = (-95.1, 15)
C_prime = (-94.2, 16.2)

# Define B and B' coordinates
D = (-94.3, 14.5)
D_prime = (-93.6, 15.8)

# Filter the earthquakes inside the rectangle
filtered_data = data[
    (data['Lon'] >= min(C[0], C_prime[0])) &
    (data['Lon'] <= max(C[0], C_prime[0])) &
    (data['Lat'] >= min(C[1], D[1])) &
    (data['Lat'] <= max(C_prime[1], D_prime[1]))
]

# Save the filtered data as a CSV file
filtered_data.to_csv("filtered_earthquakes2.csv", index=False)

# Print the count of earthquakes in the filtered list
count = filtered_data.shape[0]
print("Number of earthquakes inside the rectangle:", count)

# Read the earthquake data CSV file
data = pd.read_csv("filtered_earthquakes2.csv")



# Set up the plot
fig, ax = plt.subplots()

# Plot the rectangle
rectangle = [C, C_prime, D_prime, D, C]
rectangle_x = [point[0] for point in rectangle]
rectangle_y = [point[1] for point in rectangle]
ax.plot(rectangle_x, rectangle_y, color='red', linewidth=1)

# Create a color palette for the earthquakes
cmap = plt.get_cmap("viridis")
normalize = plt.Normalize(data['Depth'].min(), data['Depth'].max())
colors = [cmap(normalize(value)) for value in data['Depth']]

# Plot the earthquakes inside the rectangle
ax.scatter(data['Lon'], data['Lat'], c=colors, marker='o')

# Set labels and title
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Region Selected")

# Show the plot
plt.show()

# Print the count of earthquakes inside the rectangle
count = data.shape[0]
print("Number of earthquakes inside the rectangle:", count)


# In[145]:


import pandas as pd
import matplotlib.pyplot as plt


# Read the earthquake data CSV file
data = pd.read_csv("IEB_export_south_mexico.csv")

# Define the coordinates of the rectangle
B = (-93.7,  14.2)
B_prime = (-93, 15.4)


D = (-94.3, 14.5)
D_prime = (-93.6, 15.8)

# Filter the earthquakes inside the rectangle
filtered_data = data[
    (data['Lon'] >= min(D[0], D_prime[0])) &
    (data['Lon'] <= max(D[0], D_prime[0])) &
    (data['Lat'] >= min(D[1], B[1])) &
    (data['Lat'] <= max(D_prime[1], B_prime[1]))
]

# Save the filtered data as a CSV file
filtered_data.to_csv("filtered_earthquakes.csv", index=False)

# Print the count of earthquakes in the filtered list
count = filtered_data.shape[0]
print("Number of earthquakes inside the rectangle:", count)

# Read the earthquake data CSV file
data = pd.read_csv("filtered_earthquakes.csv")


# Set up the plot
fig, ax = plt.subplots()

# Plot the rectangle
rectangle = [D, D_prime, B_prime, B, D]
rectangle_x = [point[0] for point in rectangle]
rectangle_y = [point[1] for point in rectangle]
ax.plot(rectangle_x, rectangle_y, color='red', linewidth=1)

# Create a color palette for the earthquakes
cmap = plt.get_cmap("viridis")
normalize = plt.Normalize(data['Depth'].min(), data['Depth'].max())
colors = [cmap(normalize(value)) for value in data['Depth']]

# Plot the earthquakes inside the rectangle
ax.scatter(data['Lon'], data['Lat'], c=colors, marker='o')

# Set labels and title
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Region Selected")

# Show the plot
plt.show()

# Print the count of earthquakes inside the rectangle
count = data.shape[0]
print("Number of earthquakes inside the rectangle:", count)


# In[146]:


import pandas as pd
import matplotlib.pyplot as plt


# Read the earthquake data CSV file
data = pd.read_csv("IEB_export_south_mexico.csv")

# Define B and B' coordinates
B = (-93.7,  14.2)
B_prime = (-93, 15.4)


F = (-93, 13.9)
F_prime = (-92.4, 15.1)

# Filter the earthquakes inside the rectangle
filtered_data = data[
    (data['Lon'] >= min(B[0], B_prime[0])) &
    (data['Lon'] <= max(B[0], B_prime[0])) &
    (data['Lat'] >= min(B[1], F[1])) &
    (data['Lat'] <= max(B_prime[1], F_prime[1]))
]

# Save the filtered data as a CSV file
filtered_data.to_csv("filtered_earthquakes2.csv", index=False)

# Print the count of earthquakes in the filtered list
count = filtered_data.shape[0]
print("Number of earthquakes inside the rectangle:", count)

# Read the earthquake data CSV file
data = pd.read_csv("filtered_earthquakes2.csv")



# Set up the plot
fig, ax = plt.subplots()

# Plot the rectangle
rectangle = [B, B_prime, F_prime, F, B]
rectangle_x = [point[0] for point in rectangle]
rectangle_y = [point[1] for point in rectangle]
ax.plot(rectangle_x, rectangle_y, color='red', linewidth=1)

# Create a color palette for the earthquakes
cmap = plt.get_cmap("viridis")
normalize = plt.Normalize(data['Depth'].min(), data['Depth'].max())
colors = [cmap(normalize(value)) for value in data['Depth']]

# Plot the earthquakes inside the rectangle
ax.scatter(data['Lon'], data['Lat'], c=colors, marker='o')

# Set labels and title
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Region Selected")

# Show the plot
plt.show()

# Print the count of earthquakes inside the rectangle
count = data.shape[0]
print("Number of earthquakes inside the rectangle:", count)


# In[ ]:




