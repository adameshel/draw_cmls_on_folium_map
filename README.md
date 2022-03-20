# draw_cmls_on_folium_map
Visualize CML locations on a map.
The script reads a csv metadata file and creates and html file.
The metadata file must include the following column names:
`'Link ID', 'Rx Site Latitude', 'Tx Site Latitude', 'Rx Site Longitude', 'Tx Site Longitude'`
If raw data files are given, the CMLs drawn on the map will be ones for which raw data is available.
If not, the metadata will be drawn on the map. 


