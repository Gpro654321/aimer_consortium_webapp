import geopandas as gpd
import matplotlib.pyplot as plt


# Load India shape file
india_map = gpd.read_file("static/maps/indian_states.json")  # Adjust path if needed

# Check if map is loaded correctly
print(india_map.head())

# Plot
fig, ax = plt.subplots(figsize=(10, 10))
india_map.plot(ax=ax, edgecolor="black")

plt.title("India Map Test")
plt.show()
