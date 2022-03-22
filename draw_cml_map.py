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
        df_md.columns = df_md.columns.str.lower()
        if 'hop id' not in df_md.columns.values:
            hop_id = 'not provided'
            df_md['hop id'] = hop_id
        if 'link carrier' not in df_md.columns.values:
            carrier = 'unknown carrier'
            df_md['link carrier'] = carrier
        else:
            df_md['link carrier'] = df_md['link carrier'].str.lower()
            carriers = df_md['link carrier'].unique()
            print('carriers:')
            print(carriers)
            d_colors = {
                'cellcom': 'purple',
                'pelephone': 'blue',
                'phi': 'orange',
                'smbit': 'green',
                'unknown carrier': 'black'
            }
            if self.color_of_links:
                d_colors = {
                    'cellcom': self.color_of_links,
                    'pelephone': self.color_of_links,
                    'phi': self.color_of_links,
                    'smbit': self.color_of_links,
                    'unknown carrier': self.color_of_links
                }
    
        df_md.drop_duplicates(subset='link id', inplace=True)
        df_bool = df_md['rx site longitude'].astype(bool)
        df_md = df_md[df_bool]
        df_md.reset_index(inplace=True, drop=True)
    
        if math.isnan(self.area_min_lon):
            self.area_min_lon = np.nanmin((np.nanmin(df_md['tx site longitude'].values),
                            np.nanmin(df_md['rx site longitude'].values)))
        if math.isnan(self.area_max_lon):
            self.area_max_lon = np.nanmax((np.nanmax(df_md['tx site longitude'].values),
                            np.nanmax(df_md['rx site longitude'].values)))
        if math.isnan(self.area_min_lat):
            self.area_min_lat = np.nanmin((np.nanmin(df_md['tx site latitude'].values),
                            np.nanmin(df_md['rx site latitude'].values)))
        if math.isnan(self.area_max_lat):
            self.area_max_lat = np.nanmax((np.nanmax(df_md['tx site latitude'].values),
                            np.nanmax(df_md['rx site latitude'].values)))
    
        try:
            df_md = df_md[df_md['rx site longitude'] < self.area_max_lon]
            df_md = df_md[df_md['tx site longitude'] < self.area_max_lon]
        except:
            pass
        try:
            df_md = df_md[df_md['rx site longitude'] > self.area_min_lon]
            df_md = df_md[df_md['tx site longitude'] > self.area_min_lon]
        except:
            pass
        try:
            df_md = df_md[df_md['rx site latitude'] < self.area_max_lat]
            df_md = df_md[df_md['tx site latitude'] < self.area_max_lat]
        except:
            pass
        try:
            df_md = df_md[df_md['rx site latitude'] > self.area_min_lat]
            df_md = df_md[df_md['tx site latitude'] > self.area_min_lat]
        except:
            pass
    
        if self.distort_lat_lon:
            df_md['distort rx site longitude'] = np.random.randint(-5, 5, df_md.shape[0]) / 10000
            df_md['distort tx site longitude'] = np.random.randint(-5, 5, df_md.shape[0]) / 10000
            df_md['distort rx site latitude'] = np.random.randint(-5, 5, df_md.shape[0]) / 10000
            df_md['distort tx site latitude'] = np.random.randint(-5, 5, df_md.shape[0]) / 10000
    
            df_md['rx site longitude'] = df_md['rx site longitude'] + df_md['distort rx site longitude']
            df_md['tx site longitude'] = df_md['tx site longitude'] + df_md['distort tx site longitude']
            df_md['rx site latitude'] = df_md['rx site latitude'] + df_md['distort rx site latitude']
            df_md['tx site latitude'] = df_md['tx site latitude'] + df_md['distort tx site latitude']
    
        df_md.reset_index(inplace=True,drop=True)
        num_cmls_map = len(df_md['link id'])
    
        grid = []
    
        for i,link in df_md.iterrows():
            link_id = link['link id']
            hop_id = link['hop id']
            # color = self.color_of_links
            self.color = d_colors[link['link carrier']]
            if link_id in self.list_of_link_id_to_drop:
                print('link id' + str(link_id) + ' has been dropped')
                num_cmls_map = num_cmls_map - 1
                continue
            if math.isnan(link['rx site latitude']):
                print('No metadata for link ' + str(link['link id']))
                num_cmls_map = num_cmls_map - 1
                continue
            else:
                if link_id in self.list_of_link_id_to_color or hop_id in self.list_of_link_id_to_color:
                    self.color = self.color_of_specific_links
                else:
                    self.color = d_colors[link['link carrier']]
                if self.rawdata_dir:
                    self._process_rd(link, link_id, 'Cellcom_HC_RADIO_SINK_', 'PowerRLTMmin')
                    self._process_rd(link, link_id, 'PHI_TN_RFInputPower_', 'RFInputPower')
                    self._process_rd(link, link_id, 'Pelephone_TN_RFInputPower_', 'RFInputPower')
                else:
                    folium.PolyLine([(link['rx site latitude'],
                                      link['rx site longitude']),
                                     (link['tx site latitude'],
                                      link['tx site longitude'])],
                                    color=self.color,
                                    opacity=0.6,
                                    popup=str(link['link carrier']) +\
                                          '\nLink ID: ' + str(link['link id']) +\
                                           '\nHop ID: ' + str(link['hop id'])
                                ).add_to(self.map_1)
    
        print('Number of links in map: ')
        print(num_cmls_map)
        print(str(self.out_path.joinpath(self.name_of_map_file)))
        self.map_1.save(str(self.out_path.joinpath(self.name_of_map_file)))
    
        # plot gridlines
        if self.num_of_gridlines:
            lat_min = np.nanmin((np.nanmin(df_md['tx site latitude'].values),
                                np.nanmin(df_md['rx site latitude'].values)))
            lon_min = np.nanmin((np.nanmin(df_md['tx site longitude'].values),
                                np.nanmin(df_md['rx site longitude'].values)))
            lat_max = np.nanmax((np.nanmax(df_md['tx site latitude'].values),
                                np.nanmax(df_md['rx site latitude'].values)))
            lon_max = np.nanmax((np.nanmax(df_md['tx site longitude'].values),
                                np.nanmax(df_md['rx site longitude'].values)))
    
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
        str_rsl_col = str_rsl_col.lower()
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
            df_ts.columns = df_ts.columns.str.lower()
            df_ts = df_ts[df_ts['interval'] == self.interval]
            df_ts.reset_index(inplace=True, drop=True)
            df_ts['date'] = pd.to_datetime(df_ts['time'])

            ## create json of each cml timeseries for plotting
            df = df_ts[['date', str_rsl_col]]
            df.set_index('date', inplace=True, drop=True)
            timeseries = vincent.Line(
                df[[str_rsl_col]],
                height=350,
                width=750).axis_titles(
                x=link['link carrier'] + ':  (Date)',
                y='RSL (dB)'
            )
            timeseries.legend(title='Link ID: ' + str(link['link id']) + \
                                    '\nHop ID: ' + str(link['hop id']))
            data_json = json.loads(timeseries.to_json())

            v = folium.features.Vega(data_json, width=1000, height=400)
            p = folium.Popup(max_width=1150)

            pl = folium.PolyLine([(link['rx site latitude'],
                                   link['rx site longitude']),
                                  (link['tx site latitude'],
                                   link['tx site longitude'])],
                                 color=self.color,
                                 opacity=0.6
                                 ).add_to(self.map_1)
            pl.add_child(p)
            p.add_child(v)

    def _load_json_file(self, file):
        # Load and fix the file to json
        data_str = file.read()
        data_str = data_str.replace("'", '"')
        data_str = data_str.replace("datetime", '"datetime')
        data_str = data_str.replace(")", ')"')
        return json.loads(data_str)

    def get_hop_id_from_file(file, names):
        # Returns hop ID and hop's direction
        name = file[0]['name'].lower()
        name1, name2 = parse_hop_name(name)
        if name1 in names:
            direction = 'up'
            hop_id = names.index(name1) + 1
            # hop_name = name1
        elif name2 in names:
            direction = 'down'
            hop_id = names.index(name2) + 1
            # hop_name = name2
        else:
            print('Hop name not available')
            hop_id = -1
            direction = 'up'
        return hop_id, direction


