import pandas as pd
import folium
import numpy as np
import math
from pathlib import Path
import os
import vincent
import json

def draw_cml_map(out_path,
                 data_path,
                 metadata_file_name,
                 rawdata_dir=None,
                 handle=None,
                 name_of_map_file='link_map1',
                 interval=15,
                 num_of_gridlines=None,
                 area_min_lon=np.nan,
                 area_max_lon=np.nan,
                 area_min_lat=np.nan,
                 area_max_lat=np.nan,
                 list_of_link_id_to_drop=[],
                 list_of_link_id_to_color=[],
                 color_of_specific_links='red',
                 color_of_links=None,
                 distort_lat_lon=True
            ):
    '''Create a Folium interactive map of cmls:
    out_path: str, path to output.
    data_path: str, path to metadata file.
    metadata_file_nameh: str, .csv file name.
    rawdata_dir: (optional) directory of raw data files (for now only SINK-SOURCE).
    handle: folium.vector_layers.PolyLine, a handle of an existing map you wish to
    edit.
    name_of_map_file: str, name of the output file.
    interval: (int). 15 (default) for 15 minute measurement interval or 24 for 24 h
    num_of_gridlines: int, number of gridlines for lat and for lon.
    area_min_lon, area_max_lon, area_min_lat, area_max_lat: float, filter area
    of interest by setting coordinates boundaries.
    list_of_link_id_to_drop: list of strings, links you wish to discard .
    list_of_link_id_to_color: color specific links in different colors.
    color_of_links: str, color of links from a given csv file
    Distort_lat_lon: Distort the coordinates to see links on the same hop when zoomed in.

    The function returns a handle for further editing of the .html file.
    By using the handle multiple companies can be plotted by calling the function
    for each of them while drawing them in different colors.
    '''

    name_of_map_file = name_of_map_file + '.html'
    out_path = Path(out_path)
    data_path = Path(data_path)
    meta_path = data_path.joinpath(metadata_file_name)
    if rawdata_dir:
        rawdata_path = data_path.joinpath(rawdata_dir)
    
    df_md = pd.read_csv(meta_path)
    if 'Link Carrier' not in df_md.columns.values:
        carrier = 'Unknown carrier'
        df_md['Link Carrier'] = carrier
    else:
        carriers = df_md['Link Carrier'].unique()
        print('Carriers:')
        print(carriers)
        d_colors = {
            'Cellcom': 'purple',
            'Pelephone': 'blue',
            'PHI': 'orange',
            'SMBIT': 'white',
            'Unknown carrier': 'green'
        }
        if color_of_links:
            d_colors = {
                'Cellcom': color_of_links,
                'Pelephone': color_of_links,
                'PHI': color_of_links,
                'SMBIT': color_of_links,
                'Unknown carrier': color_of_links
            }

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

    if distort_lat_lon:
        df_md['Distort Rx Site Longitude'] = np.random.randint(-5, 5, df_md.shape[0]) / 10000
        df_md['Distort Tx Site Longitude'] = np.random.randint(-5, 5, df_md.shape[0]) / 10000
        df_md['Distort Rx Site Latitude'] = np.random.randint(-5, 5, df_md.shape[0]) / 10000
        df_md['Distort Tx Site Latitude'] = np.random.randint(-5, 5, df_md.shape[0]) / 10000

        df_md['Rx Site Longitude'] = df_md['Rx Site Longitude'] + df_md['Distort Rx Site Longitude']
        df_md['Tx Site Longitude'] = df_md['Tx Site Longitude'] + df_md['Distort Tx Site Longitude']
        df_md['Rx Site Latitude'] = df_md['Rx Site Latitude'] + df_md['Distort Rx Site Latitude']
        df_md['Tx Site Latitude'] = df_md['Tx Site Latitude'] + df_md['Distort Tx Site Latitude']

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
        link_id = link['Link ID']
        # color = color_of_links
        color = d_colors[link['Link Carrier']]
        if link_id in list_of_link_id_to_color:
            color = color_of_specific_links
        if link_id in list_of_link_id_to_drop:
            print('Link ID' + str(link_id) + ' has been dropped')
            num_cmls_map = num_cmls_map - 1
            continue
        if math.isnan(link['Rx Site Latitude']):
            print('No metadata for link ' + str(link['Link ID']))
            num_cmls_map = num_cmls_map - 1
            continue
        else:
            if rawdata_dir:
                try:
                    appended_data = []
                    # loop over raw data rsl 15 min or 24 h
                    for filename in sorted(os.listdir(rawdata_path)):
                        if 'SINK_' + link_id in filename:
                        # if link_id in filename:
                            df_temp = pd.read_csv(rawdata_path.joinpath(filename))
                            appended_data.append(df_temp)
                    df_ts = pd.concat(appended_data, sort=False)
                    df_ts = df_ts[df_ts['Interval'] == interval]
                    df_ts.reset_index(inplace=True, drop=True)
                    df_ts['Date'] = pd.to_datetime(df_ts['Time'])

                    ## create json of each cml timeseries for plotting
                    df = df_ts[['Date', 'PowerRLTMmin']]
                    df.set_index('Date', inplace=True, drop=True)
                    timeseries = vincent.Line(df[['PowerRLTMmin']], height=350, width=750)
                    timeseries.legend(title=str(link['Link Carrier']) + '\nID: ' + str(link['Link ID']))
                    data_json = json.loads(timeseries.to_json())

                    v = folium.features.Vega(data_json, width=950, height=400)
                    p = folium.Popup(max_width=950)

                    pl = folium.PolyLine([(link['Rx Site Latitude'],
                                           link['Rx Site Longitude']),
                                          (link['Tx Site Latitude'],
                                           link['Tx Site Longitude'])],
                                         color=color,
                                         opacity=0.6
                                         ).add_to(map_1)
                    pl.add_child(p)
                    p.add_child(v)
                except:
                    pass
                try:
                    appended_data = []
                    # loop over raw data minimum rsl 15 min
                    for filename in sorted(os.listdir(rawdata_path)):
                        if 'RFInputPower_' + link_id in filename:
                        # if link_id in filename:
                            df_temp = pd.read_csv(rawdata_path.joinpath(filename))
                            appended_data.append(df_temp)
                    df_ts = pd.concat(appended_data, sort=False)
                    df_ts = df_ts[df_ts['Interval'] == 15]
                    df_ts.reset_index(inplace=True, drop=True)
                    df_ts['Date'] = pd.to_datetime(df_ts['Time'])

                    ## create json of each cml timeseries for plotting
                    df = df_ts[['Date', 'RFInputPower']]
                    df.set_index('Date', inplace=True, drop=True)
                    timeseries = vincent.Line(df[['RFInputPower']], height=350, width=750)
                    timeseries.legend(title=str(link['Link Carrier']) + '\nID: ' + str(link['Link ID']))
                    data_json = json.loads(timeseries.to_json())

                    v = folium.features.Vega(data_json, width=950, height=400)
                    p = folium.Popup(max_width=950)

                    pl = folium.PolyLine([(link['Rx Site Latitude'],
                                           link['Rx Site Longitude']),
                                          (link['Tx Site Latitude'],
                                           link['Tx Site Longitude'])],
                                         color=color,
                                         opacity=0.6
                                         ).add_to(map_1)
                    pl.add_child(p)
                    p.add_child(v)
                except:
                    pass
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
    print(str(out_path.joinpath(name_of_map_file)))
    map_1.save(str(out_path.joinpath(name_of_map_file)))

    # plot gridlines
    if num_of_gridlines:
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



