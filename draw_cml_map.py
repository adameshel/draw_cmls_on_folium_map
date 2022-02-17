import pandas as pd
import folium
import numpy as np
import math
from pathlib import Path

def draw_cml_map(out_path,
                 data_path,
                 metadata_file_name,
                 handle=None,
                 name_of_map_file='link_map1.html',
                 num_of_gridlines=30,
                 area_min_lon=np.nan,
                 area_max_lon=np.nan,
                 area_min_lat=np.nan,
                 area_max_lat=np.nan,
                 list_of_link_id_to_drop=[],
                 list_of_link_id_to_color=[],
                 color_of_specific_links='red',
                 color_of_links='purple',
                 gridlines_on=True
            ):
    '''Create a Folium interactive map of cmls:
    out_path: str, path to output
    data_path: str, path to metadata file
    metadata_file_nameh: str, .csv file name
    handle: folium.vector_layers.PolyLine, a handle of an exsisting map you wish to
    edit
    name_of_map_file: str, name of the output file
    num_of_gridlines: int, number of gridlines for lat and for lon
    area_min_lon, area_max_lon, area_min_lat, area_max_lat: float, filter area
    of interest by setting coordinates boundaries
    list_of_link_id_to_drop: list of strings, links you wish to discard 
    color_of_links: str, color of links from a given csv file
    
    The function returns a handle for further edditing of the .html file.
    By using the handle multiple companies can be plotted by calling the finction
    for each of them while drawing them in different colors.
    '''
    out_path = Path(out_path)
    data_path = Path(data_path)
    meta_path = data_path.joinpath(metadata_file_name)
    
    df_md = pd.read_csv(meta_path)
    if 'Link Carrier' not in df_md.columns.values:
        carrier = 'Unknown carrier'
        df_md['Link Carrier'] = carrier

    df_md.drop_duplicates(subset='Link ID', inplace=True)

    df_bool = df_md['Rx Site Longitude'].astype(bool)
    df_md = df_md[df_bool]
    df_md.reset_index(inplace=True, drop=True)

    if math.isnan(area_min_lon):
        area_min_lon = np.nanmin((np.nanmin(df_md['Tx Site Longitude'].values),
                        np.nanmin(df_md['Rx Site Longitude'].values)))
    if math.isnan(area_max_lon):
        area_max_lon = np.nanmax((np.nanmax(df_md['Tx Site Longitude'].values),
                        np.nanmax(df_md['Rx Site Longitude'].values)))
    if math.isnan(area_min_lat):
        area_min_lat = np.nanmin((np.nanmin(df_md['Tx Site Latitude'].values),
                        np.nanmin(df_md['Rx Site Latitude'].values)))
    if math.isnan(area_max_lat):
        area_max_lat = np.nanmax((np.nanmax(df_md['Tx Site Latitude'].values),
                        np.nanmax(df_md['Rx Site Latitude'].values)))

    try:
        df_md = df_md[df_md['Rx Site Longitude'] < area_max_lon]
        df_md = df_md[df_md['Tx Site Longitude'] < area_max_lon]
    except:
        pass
    try:
        df_md = df_md[df_md['Rx Site Longitude'] > area_min_lon]
        df_md = df_md[df_md['Tx Site Longitude'] > area_min_lon]
    except:
        pass
    try:
        df_md = df_md[df_md['Rx Site Latitude'] < area_max_lat]
        df_md = df_md[df_md['Tx Site Latitude'] < area_max_lat]
    except:
        pass
    try:
        df_md = df_md[df_md['Rx Site Latitude'] > area_min_lat]
        df_md = df_md[df_md['Tx Site Latitude'] > area_min_lat]
    except:
        pass

    df_md.reset_index(inplace=True,drop=True)
    num_cmls_map = len(df_md['Link ID'])

    grid = []
    if not handle:
        map_1 = folium.Map(location=[32, 35],
                               zoom_start=8,
                               tiles='Stamen Terrain',
                          control_scale=True)
    else:
        map_1 = handle

    for i,link in df_md.iterrows():
        if link['Link ID'] in list_of_link_id_to_drop:
            print('Link ID' + str(link['Link ID']) + ' has been dropped')
            num_cmls_map = num_cmls_map - 1
            continue
        if math.isnan(link['Rx Site Latitude']):
            print('No metadata for link ' + str(link['Link ID']))
            num_cmls_map = num_cmls_map - 1
            continue
        else:
            folium.PolyLine([(link['Rx Site Latitude'], 
                              link['Rx Site Longitude']),
                             (link['Tx Site Latitude'], 
                              link['Tx Site Longitude'])], 
                            color=color_of_links, 
                            opacity=0.6,
                            popup=str(link['Link Carrier']) + '\nID: ' + str(link['Link ID'])
                        ).add_to(map_1)

    print('Number of links in map: ')
    print(num_cmls_map)

    for l_color in list_of_link_id_to_color:
        link = df_md.loc[df_md['Link ID'] == l_color]
        folium.PolyLine([(float(link['Rx Site Latitude'].values),
                          float(link['Rx Site Longitude'].values)),
                         (float(link['Tx Site Latitude'].values),
                          float(link['Tx Site Longitude'].values))],
                        color=color_of_specific_links,
                        opacity=0.8,
                        popup=str(link['Link Carrier'].values) + '\nID: ' + str(link['Link ID'].values)
                        ).add_to(map_1)


    # plot gridlines
    lat_min = np.nanmin((np.nanmin(df_md['Tx Site Latitude'].values),
                        np.nanmin(df_md['Rx Site Latitude'].values)))
    lon_min = np.nanmin((np.nanmin(df_md['Tx Site Longitude'].values),
                        np.nanmin(df_md['Rx Site Longitude'].values)))
    lat_max = np.nanmax((np.nanmax(df_md['Tx Site Latitude'].values),
                        np.nanmax(df_md['Rx Site Latitude'].values)))
    lon_max = np.nanmax((np.nanmax(df_md['Tx Site Longitude'].values),
                        np.nanmax(df_md['Rx Site Longitude'].values)))

    lats = np.linspace(lat_min,lat_max,num_of_gridlines)
    lons = np.linspace(lon_min,lon_max,num_of_gridlines)

    for lat in lats:
        grid.append([[lat, -180],[lat, 180]])

    for lon in lons:
        grid.append([[-90, lon],[90, lon]])
    
    if gridlines_on:
        counter = 0
        for g in grid:
            if counter < len (lats):
                folium.PolyLine(g, color="black", weight=0.5, 
                                opacity=0.5,popup=str(round(g[0][0],5))).add_to(map_1)
                counter += 1
            else: 
                folium.PolyLine(g, color="black", weight=0.5, 
                                opacity=0.5,popup=str(round(g[0][1],5))).add_to(map_1)

    map_1.save(str(out_path.joinpath(name_of_map_file)))

    print('Map under the name ' + name_of_map_file + ' was generated.')
    
    return map_1