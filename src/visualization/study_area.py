import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box

# Load world boundaries
world = gpd.read_file("data/ne_10m_admin_0_countries.shx")

# Uttarakhand bounding box
bbox = box(77, 28, 81, 31.5)
study_area = gpd.GeoDataFrame(geometry=[bbox], crs="EPSG:4326")

fig, ax = plt.subplots(figsize=(6, 6))

world.plot(ax=ax, color="lightgray", edgecolor="black", linewidth=0.4)
study_area.plot(ax=ax, facecolor="none", edgecolor="red", linewidth=2)

ax.set_title("Study Area: Uttarakhand, India", fontsize=12)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_xlim(75, 90)
ax.set_ylim(25, 35)

plt.tight_layout()
plt.savefig("figures/output/fig1_study_area.png", dpi=300)
plt.close()
