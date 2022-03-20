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

# Directory
Place both the metadata file and the raw-data folder in the same directory.

# Run
Play around by running the file `run_example.py`, after changing the following lines to your own needs:

`name_map = 'my_map'`

`dir_out = '/directory/of/out/'`

`dir_data = '/directory/of/metadata/'`

`md_filename_1 = 'metadata_file_name_1.csv'`

`md_filename_2 = 'metadata_file_name_2.csv'`

`raw_data_folder_name = 'rawdata'`

# Outcome
A .html file will be generated and when opening it youshould be able to see something like this:

![Screen Shot 2022-03-20 at 15 57 16](https://user-images.githubusercontent.com/60098219/159165977-d15007ac-afc5-49e8-9e52-7f209f9f6e9a.png)

When only metadata is loaded, clicking on a link should start a pop-up containing the link id, hop id and carrier. Clicking on a gridline should show its value.
When raw-data is also incorporated, clicking on a link should show you the timeseries of the raw-data you have downloaded, e.g.:

![Screen Shot 2022-03-20 at 16 03 57](https://user-images.githubusercontent.com/60098219/159166254-02e78e0b-1c88-4a5d-b4c8-7229b9da9a80.png)


