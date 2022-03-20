# draw_cmls_on_folium_map
Visualize CML locations and raw-data on a map.
The script reads a csv metadata file, and additional raw-data files (optional) and creates and html file.
Generally, the metadata file must include the following column names:
`'Link ID', 'Rx Site Latitude', 'Tx Site Latitude', 'Rx Site Longitude', 'Tx Site Longitude'`

If raw data files are given, the CMLs drawn on the map will be ones for which raw data is available.
If not, the metadata will be drawn on the map. 

# Get the data from Omnisol system
After the filtering of the desired raw-data is done, download both the metadata and the raw-data by clicking on the blue icons on the top right as shown here:

<img width="630" alt="Screen Shot 2022-03-20 at 15 36 21" src="https://user-images.githubusercontent.com/60098219/159165005-8a0cd398-3ec0-4f5e-8806-ba0b6e44d8c3.png">


