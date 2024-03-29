﻿import pandas as pd
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
        '''Create a Folium interactive map of lines (cmls):
        out_path: str, path to output (created automatically if not provided).
        data_path: str, path to metadata file.
        metadata_file_nameh: str, .csv file name.
        rawdata_dir: (optional) directory of raw data files (for now only SINK-SOURCE).
        name_of_map_file: str, name of the output file.
        interval: (int). 15 (default) for 15 minute measurement interval or 24 for 24 h
        num_of_gridlines: int, number of gridlines for lat and for lon.
        area_min_lon, area_max_lon, area_min_lat, area_max_lat: float, filter area
        of interest by setting coordinates boundaries.
        list_of_link_id_to_drop: list of strings, links you wish to discard .
        list_of_link_id_to_color: color specific links in different colors.
        color_of_links: str, color of links from a given csv file
        distort_lat_lon: Distort the coordinates to see links on the same hop when zoomed in.

        The object can be called multiple times so that more information can be added onto it.
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
        if 'link id' not in df_md.columns:
            if 'link_id' in df_md.columns:
                try:
                    df_md.rename(columns={'hop_id': 'hop id'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'link_id':'link id'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'txsite_longitude':'tx site longitude'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'txsite_latitude': 'tx site latitude'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'rxsite_longitude': 'rx site longitude'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'rxsite_latitude': 'rx site latitude'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'carrier': 'link carrier'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'tx_site_longitude':'tx site longitude'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'tx_site_latitude': 'tx site latitude'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'rx_site_longitude': 'rx site longitude'}, inplace=True)
                except:
                    pass
                try:
                    df_md.rename(columns={'rx_site_latitude': 'rx site latitude'}, inplace=True)
                except:
                    pass
                #     df_md.rename(columns={'hop_id':'hop id',
                #                           'link_id':'link id',
                #                           'txsite_longitude':'tx site longitude',
                #                           'txsite_latitude': 'tx site latitude',
                #                           'rxsite_longitude': 'rx site longitude',
                #                           'rxsite_latitude': 'rx site latitude',
                #                           'carrier': 'link carrier'},
                #                  inplace=True)
                # except:
                #     pass
            else:
                df_md = self._process_smbit_md(df_md)
        if 'hop id' not in df_md.columns.values:
            hop_id = 'not provided'
            df_md['hop id'] = hop_id
        if 'link carrier' not in df_md.columns.values:
            carrier = 'unknown carrier'
            df_md['link carrier'] = carrier
        df_md['link carrier'] = df_md['link carrier'].str.lower()
        carriers = df_md['link carrier'].unique()
        print('carriers:')
        print(carriers)
        d_colors = {
            'cellcom': 'purple',
            'pelephone': 'blue',
            'phi': 'orange',
            'smbit': 'green',
            'ericsson': 'blue',
            'unknown carrier': 'black'
        }
        if self.color_of_links:
            d_colors = {
                'cellcom': self.color_of_links,
                'pelephone': self.color_of_links,
                'phi': self.color_of_links,
                'smbit': self.color_of_links,
                'ericsson': self.color_of_links,
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
                    try:
                        self._process_rd(link, link_id, 'Cellcom_HC_RADIO_SINK_', 'PowerRLTMmin')
                    except:
                        pass
                    try:
                        self._process_rd(link, link_id, 'PHI_TN_RFInputPower_', 'RFInputPower')
                    except:
                        pass
                    try:
                        self._process_rd(link, link_id, 'Pelephone_TN_RFInputPower_', 'RFInputPower')
                    except:
                        pass
                    try:
                        self._process_rd(link, link_id, 'SMBIT', 'lastvalue')
                    except:
                        pass
                    try:
                        self._process_rd(link, link_id, 'Ericsson_MW_', 'rsl')
                    except:
                        pass
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
        # loop over rsl raw data
        for filename in sorted(os.listdir(self.rawdata_path)):
            if 'SMBIT' in filename and link_id in filename.lower():
                f = open(self.rawdata_path.joinpath(filename))
                f_content = self._load_json_file(f)
                dic = self._load_raw_data(f_content, str_rsl_col)
                df_temp = pd.DataFrame(dic, dtype=np.int32)
                df_temp['time'] = pd.to_datetime(df_temp['clk'], unit='s')
                appended_data.append(df_temp)
            elif str_in_filename + link_id in filename:
                # if link_id in filename:
                if str_in_filename=='Ericsson_MW_':
                    cols_names = ['time','link id','tsl', str_rsl_col]
                    df_temp = pd.read_csv(self.rawdata_path.joinpath(filename),
                                          names=cols_names,
                                          header=None)
                else:
                    df_temp = pd.read_csv(self.rawdata_path.joinpath(filename))
                appended_data.append(df_temp)
        if not appended_data:
            pass
        else:
            df_ts = pd.concat(appended_data, sort=False)
            df_ts.columns = df_ts.columns.str.lower()
            try:
                df_ts = df_ts[df_ts['interval'] == self.interval]
            except:
                pass
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
        # Load and fix the file to json- SMBIT
        data_str = file.read()
        data_str = data_str.replace("'", '"')
        data_str = data_str.replace("datetime", '"datetime')
        data_str = data_str.replace(")", ')"')
        return json.loads(data_str)

    def _load_raw_data(self, file, str_rsl_col):
        # returns a dictionary containing clock and rsl values- SMBIT
        rsl = [float(d['siklu.rssavg']['lastvalue']) for d in file if
               d['siklu.rssavg']['lastclock'] != '0']  # Add rsl if it is not empty
        clk = [int(d['siklu.rssavg']['lastclock']) + 7200 for d in file if
               d['siklu.rssavg']['lastclock'] != '0']  # Add 2 hours to clock value
        dic = {}
        dic[str_rsl_col] = rsl
        dic['clk'] = clk
        return dic

    def _process_smbit_md(self, df):
        # usen in case the metadata file is not from Omnisol- SMBIT
        if 'link carrier' not in df.columns.values:
            carrier = 'smbit'
            df['link carrier'] = carrier
        df_1 = df[['link carrier', 'hop_name', 'site1_longitude', 'site1_latitude',
                   'site2_longitude', 'site2_latitude', 'up_valid_names']]
        df_1.rename(columns={'hop_name':'hop id',
                             'site1_longitude':'rx site longitude',
                             'site1_latitude':'rx site latitude',
                             'site2_longitude':'tx site longitude',
                             'site2_latitude':'tx site latitude',
                             'up_valid_names':'link id'}, inplace=True)
        for i,row in df_1.iterrows():
            try:
                if ',' in row['link id']:
                    str0 = row['link id'].split(',')[0]
                    str1 = row['link id'].split(',')[1]
                    df_1.iat[i, df_1.columns.get_loc('link id')] = str0
                    df_1 = df_1.append(df_1.iloc[i], ignore_index=True)
                    df_1.iat[-1, df_1.columns.get_loc('link id')] = str1
            except:
                pass

        df_2 = df[['link carrier', 'hop_name', 'site1_longitude', 'site1_latitude',
                   'site2_longitude', 'site2_latitude', 'down_valid_names']]
        df_2.rename(columns={'hop_name': 'hop id',
                             'site1_longitude': 'rx site longitude',
                             'site1_latitude': 'rx site latitude',
                             'site2_longitude': 'tx site longitude',
                             'site2_latitude': 'tx site latitude',
                             'down_valid_names': 'link id'}, inplace=True)
        for i,row in df_2.iterrows():
            try:
                if ',' in row['link id']:
                    str0 = row['link id'].split(',')[0]
                    str1 = row['link id'].split(',')[1]
                    df_2.iat[i, df_2.columns.get_loc('link id')] = str0
                    df_2 = df_2.append(df_2.iloc[i], ignore_index=True)
                    df_2.iat[-1, df_2.columns.get_loc('link id')] = str1
            except:
                pass
        df_new = pd.concat([df_1, df_2], ignore_index=True)
        df_new['link id'] = df_new['link id'].str.lower()
        for i, row in df_new.iterrows():
            try:
                if 'siklu_' in row['link id']:
                    str1 = row['link id'].split('siklu_')[1]
                    df_new.iat[i, df_new.columns.get_loc('link id')] = str1
            except:
                pass
        return df_new


