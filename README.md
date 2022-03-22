# draw_cmls_on_folium_map
Visualize CML locations and raw-data on a map.
The script reads a csv metadata file, and additional raw-data files (optional) and creates and html file.
Generally, the metadata file must include the following column names:
`'link id', 'rx site latitude', 'tx site latitude', 'rx site longitude', 'tx site longitude'`.

The names `carrier` and `hop_id` are optional and will be assigned with `'unknown carrier'` and `not provided` if they do not exist, respectively.

In the Class `Draw_cml_map` you can can also:
* Determine domain boundaries
* Color specific links in different colors
* Drop specific links
* Add grid-lines
* Create distortion to the locations of the base stations to avoid geographic overlaps
All aforementions options are well documented in the description of the Class.

# Raw-data RSL popups
If raw data files are given, the CMLs drawn on the map will be ones for which raw data is available, and the popup of each link will consist of the timeseries available for it.
Note that the variable `interval` is set to 15 (minutes) by default. Change it according to the resolution you possess.

If raw-data is not provided, the metadata will be drawn on the map. 

# Get the data from Omnisol system
If you choose to visualize data downloaded from the Omnisol system follow these steps.
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
An .html file will be generated and when opening it youshould be able to see something like this:

![Screen Shot 2022-03-20 at 15 57 16](https://user-images.githubusercontent.com/60098219/159165977-d15007ac-afc5-49e8-9e52-7f209f9f6e9a.png)

When only metadata is loaded, clicking on a link should start a pop-up containing the link id, hop id and carrier. Clicking on a gridline should show its value.
When raw-data is also incorporated, clicking on a link should show you the timeseries of the raw-data you have downloaded, e.g.:

![Screen Shot 2022-03-20 at 16 07 35](https://user-images.githubusercontent.com/60098219/159166464-74643a39-d2ee-4436-b561-a190c6e2c158.png)
