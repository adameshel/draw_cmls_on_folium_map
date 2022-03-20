from draw_cml_map import *

name_map = 'my_map'
dir_out = '/directory/of/out/'
dir_data = '/directory/of/metadata/'
md_filename_1 = 'metadata_file_name_1.csv'
md_filename_2 = 'metadata_file_name_2.csv'
raw_data_folder_name = 'rawdata'

map = Draw_cml_map()
# visualize locations on the map.
map(out_path=dir_out,
    data_path=dir_data,
    metadata_file_name=md_filename_1,
    distort_lat_lon=False,
    name_of_map_file=name_map)

# to the same map, add raw-data visualization, drop certain links, color
# specific ones in pink, and add gridlines.
map(out_path=dir_out,
    data_path=dir_data,
    rawdata_dir=raw_data_folder_name,
    metadata_file_name=md_filename_2,
    list_of_link_id_to_drop=['4673-7HZ4','7HZ4-4673'],
    list_of_link_id_to_color=['TS01-7330','j220-s220', '462D-6872'],
    color_of_specific_links='pink',
    num_of_gridlines=30,
    name_of_map_file=name_map)