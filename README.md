# draw_cmls_on_folium_map
Visualize CML locations and raw-data on a map.
The script reads a csv metadata file, and additional raw-data files (optional) and creates and html file.
The metadata file must include the following column names:
`'Link ID', 'Rx Site Latitude', 'Tx Site Latitude', 'Rx Site Longitude', 'Tx Site Longitude'`
If raw data files are given, the CMLs drawn on the map will be ones for which raw data is available.
If not, the metadata will be drawn on the map. 

![Screen Shot 2022-03-20 at 15 29 36](https://user-images.githubusercontent.com/60098219/159164695-42601a5c-3e18-47fd-9860-f2f7827f14c3.png)
