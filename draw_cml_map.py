import pandas as pd
import folium
import numpy as np
import math
from pathlib import Path
import os
import vincent
import json

class Draw_cml_map():
    def __init__(self):
        self.map_1 = folium.Map(location=[32, 35],
                           zoom_start=8,
                           tiles='Stamen Terrain',
                           control_scale=True)
    def __call__(self,
                 out_path,
                 data_path,
                 metadata_file_name,
                 rawdata_dir=None,
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
        self.out_path: str, path to output.
        self.data_path: str, path to metadata file.
        self.metadata_file_nameh: str, .csv file name.
        self.rawdata_dir: (optional) directory of raw data files (for now only SINK-SOURCE).
        handle: folium.vector_layers.PolyLine, a handle of an existing map you wish to
        edit.
        self.name_of_map_file: str, name of the output file.
        self.interval: (int). 15 (default) for 15 minute measurement self.interval or 24 for 24 h
        self.num_of_gridlines: int, number of gridlines for lat and for lon.
        self.area_min_lon, self.area_max_lon, self.area_min_lat, self.area_max_lat: float, filter area
        of interest by setting coordinates boundaries.
        self.list_of_link_id_to_drop: list of strings, links you wish to discard .
        self.list_of_link_id_to_color: color specific links in different colors.
        self.color_of_links: str, color of links from a given csv file
        self.distort_lat_lon: Distort the coordinates to see links on the same hop when zoomed in.
    
        The function returns a handle for further editing of the .html file.
        By using the handle multiple companies can be plotted by calling the function
        for each of them while drawing them in different colors.
        '''

        self.out_path = out_path
        self.data_path = data_path
        self.metadata_file_name = metadata_file_name
        self.rawdata_dir = rawdata_dir
        self.name_of_map_file = name_of_map_file
        self.interval = interval
        self.num_of_gridlines = num_of_gridlines
        self.area_min_lon = area_min_lon
        self.area_max_lon = area_max_lon
        self.area_min_lat = area_min_lat
        self.area_max_lat = area_max_lat
        self.list_of_link_id_to_drop = list_of_link_id_to_drop
        self.list_of_link_id_to_color = list_of_link_id_to_color
        self.color_of_specific_links = color_of_specific_links
        self.color_of_links = color_of_links
        self.distort_lat_lon = distort_lat_lon
    
        if not os.path.exists(self.out_path):
            os.makedirs(self.out_path)
        self.name_of_map_file = self.name_of_map_file + '.html'
        self.out_path = Path(self.out_path)
        self.data_path = Path(self.data_path)
        meta_path = self.data_path.joinpath(self.metadata_file_name)
        if self.rawdata_dir:
            self.rawdata_path = self.data_path.joinpath(self.rawdata_dir)
        
        df_md = pd.read_csv(meta_path)
        if 'Hop ID' not in df_md.columns.values:
            hop_id = 'Not provided'
            df_md['Hop ID'] = hop_id
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
            if self.color_of_links:
                d_colors = {
                    'Cellcom': self.color_of_links,
                    'Pelephone': self.color_of_links,
                    'PHI': self.color_of_links,
                    'SMBIT': self.color_of_links,
                    'Unknown carrier': self.color_of_links
                }
    
        df_md.drop_duplicates(subset='Link ID', inplace=True)
        df_bool = df_md['Rx Site Longitude'].astype(bool)
        df_md = df_md[df_bool]
        df_md.reset_index(inplace=True, drop=True)
    
        if math.isnan(self.area_min_lon):
            self.area_min_lon = np.nanmin((np.nanmin(df_md['Tx Site Longitude'].values),
                            np.nanmin(df_md['Rx Site Longitude'].values)))
        if math.isnan(self.area_max_lon):
            self.area_max_lon = np.nanmax((np.nanmax(df_md['Tx Site Longitude'].values),
                            np.nanmax(df_md['Rx Site Longitude'].values)))
        if math.isnan(self.area_min_lat):
            self.area_min_lat = np.nanmin((np.nanmin(df_md['Tx Site Latitude'].values),
                            np.nanmin(df_md['Rx Site Latitude'].values)))
        if math.isnan(self.area_max_lat):
            self.area_max_lat = np.nanmax((np.nanmax(df_md['Tx Site Latitude'].values),
                            np.nanmax(df_md['Rx Site Latitude'].values)))
    
        try:
            df_md = df_md[df_md['Rx Site Longitude'] < self.area_max_lon]
            df_md = df_md[df_md['Tx Site Longitude'] < self.area_max_lon]
        except:
            pass
        try:
            df_md = df_md[df_md['Rx Site Longitude'] > self.area_min_lon]
            df_md = df_md[df_md['Tx Site Longitude'] > self.area_min_lon]
        except:
            pass
        try:
            df_md = df_md[df_md['Rx Site Latitude'] < self.area_max_lat]
            df_md = df_md[df_md['Tx Site Latitude'] < self.area_max_lat]
        except:
            pass
        try:
            df_md = df_md[df_md['Rx Site Latitude'] > self.area_min_lat]
            df_md = df_md[df_md['Tx Site Latitude'] > self.area_min_lat]
        except:
            pass
    
        if self.distort_lat_lon:
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
    
        for i,link in df_md.iterrows():
            link_id = link['Link ID']
            # color = self.color_of_links
            self.color = d_colors[link['Link Carrier']]
            if link_id in self.list_of_link_id_to_color:
                self.color = self.color_of_specific_links
            if link_id in self.list_of_link_id_to_drop:
                print('Link ID' + str(link_id) + ' has been dropped')
                num_cmls_map = num_cmls_map - 1
                continue
            if math.isnan(link['Rx Site Latitude']):
                print('No metadata for link ' + str(link['Link ID']))
                num_cmls_map = num_cmls_map - 1
                continue
            else:
                if self.rawdata_dir:
                    self._process_rd(link, link_id, 'SINK_', 'PowerRLTMmin')
                    self._process_rd(link, link_id, 'PHI_TN_RFInputPower_', 'RFInputPower')
                    self._process_rd(link, link_id, 'Pelephone_TN_RFInputPower_', 'RFInputPower')
                else:
                    self.color = d_colors[link['Link Carrier']]
                    folium.PolyLine([(link['Rx Site Latitude'],
                                      link['Rx Site Longitude']),
                                     (link['Tx Site Latitude'],
                                      link['Tx Site Longitude'])],
                                    color=self.color,
                                    opacity=0.6,
                                    popup=str(link['Link Carrier']) +\
                                          '\nLink ID: ' + str(link['Link ID']) +\
                                           '\nHop ID: ' + str(link['Hop ID'])
                                ).add_to(self.map_1)
    
        print('Number of links in map: ')
        print(num_cmls_map)
        print(str(self.out_path.joinpath(self.name_of_map_file)))
        self.map_1.save(str(self.out_path.joinpath(self.name_of_map_file)))
    
        # plot gridlines
        if self.num_of_gridlines:
            lat_min = np.nanmin((np.nanmin(df_md['Tx Site Latitude'].values),
                                np.nanmin(df_md['Rx Site Latitude'].values)))
            lon_min = np.nanmin((np.nanmin(df_md['Tx Site Longitude'].values),
                                np.nanmin(df_md['Rx Site Longitude'].values)))
            lat_max = np.nanmax((np.nanmax(df_md['Tx Site Latitude'].values),
                                np.nanmax(df_md['Rx Site Latitude'].values)))
            lon_max = np.nanmax((np.nanmax(df_md['Tx Site Longitude'].values),
                                np.nanmax(df_md['Rx Site Longitude'].values)))
    
            lats = np.linspace(lat_min,lat_max,self.num_of_gridlines)
            lons = np.linspace(lon_min,lon_max,self.num_of_gridlines)
    
            for lat in lats:
                grid.append([[lat, -180],[lat, 180]])
    
            for lon in lons:
                grid.append([[-90, lon],[90, lon]])
    
            counter = 0
            for g in grid:
                if counter < len (lats):
                    folium.PolyLine(g, color="black", weight=0.5,
                                    opacity=0.5,popup=str(round(g[0][0],5))).add_to(self.map_1)
                    counter += 1
                else:
                    folium.PolyLine(g, color="black", weight=0.5,
                                    opacity=0.5,popup=str(round(g[0][1],5))).add_to(self.map_1)
    
        self.map_1.save(str(self.out_path.joinpath(self.name_of_map_file)))
    
        print('Map under the name ' + self.name_of_map_file + ' was generated.')

    def _process_rd(self, link, link_id, str_in_filename, str_rsl_col):
        appended_data = []
        # loop over raw data rsl 15 min or 24 h
        for filename in sorted(os.listdir(self.rawdata_path)):
            if str_in_filename + link_id in filename:
                # if link_id in filename:
                df_temp = pd.read_csv(self.rawdata_path.joinpath(filename))
                appended_data.append(df_temp)
        if not appended_data:
            pass
        else:
            df_ts = pd.concat(appended_data, sort=False)
            df_ts = df_ts[df_ts['Interval'] == self.interval]
            df_ts.reset_index(inplace=True, drop=True)
            df_ts['Date'] = pd.to_datetime(df_ts['Time'])

            ## create json of each cml timeseries for plotting
            df = df_ts[['Date', str_rsl_col]]
            df.set_index('Date', inplace=True, drop=True)
            timeseries = vincent.Line(
                df[[str_rsl_col]],
                height=350,
                width=750).axis_titles(
                x=link['Link Carrier'] + ':  (Date)',
                y='RSL (dB)'
            )
            timeseries.legend(title='Link ID: ' + str(link['Link ID']) + \
                                    '\nHop ID: ' + str(link['Hop ID']))
            data_json = json.loads(timeseries.to_json())

            v = folium.features.Vega(data_json, width=1000, height=400)
            p = folium.Popup(max_width=1150)

            pl = folium.PolyLine([(link['Rx Site Latitude'],
                                   link['Rx Site Longitude']),
                                  (link['Tx Site Latitude'],
                                   link['Tx Site Longitude'])],
                                 color=self.color,
                                 opacity=0.6
                                 ).add_to(self.map_1)
            pl.add_child(p)
            p.add_child(v)

        


