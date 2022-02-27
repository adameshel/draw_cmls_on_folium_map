import os
import numpy as np
import folium
from pathlib import Path
import sys

class Visualizer:
    def __init__(self):
        self.map_name="TRY_MAP.html"
        self.dates_range="01012013_01022013"
        self.data_path_dme=Path(f"./xxx/{self.dates_range}/xxx")
        self.data_path_ims=Path(f"./xxx/{self.dates_range}/xxx")
        self.out_path = Path(f"./xxx/{self.dates_range}/{self.map_name}")
        if not os.path.exists(self.out_path):
            os.makedirs(self.out_path)

        self.color_of_links = 'red'
        self.color_of_gauges ='blue'
        self.gridlines_on = False
        self.num_of_gridlines=30

        self.handle=self.draw_cml_map()

    def parse_instances(self,instance):
        instance_arr=instance.split("-")
        if len(instance_arr)==6:
            #dme
            return {
                "ID": f"{instance_arr[0]}-{instance[3]}",
                "Tx Site Latitude":float(instance_arr[1]),
                "Tx Site Longitude":float(instance_arr[2]),
                "Rx Site Latitude": float(instance_arr[4]),
                "Rx Site Longitude": float(instance_arr[5].replace(".csv",""))
            }
        elif len(instance_arr)==5:
            #ims
            return {
                "ID": f"{instance_arr[2]}",
                "Tx Site Latitude": float(instance_arr[3]),
                "Tx Site Longitude": float(instance_arr[4].replace(".csv","")),
                "Rx Site Latitude": float(instance_arr[3]),
                "Rx Site Longitude": float(instance_arr[4].replace(".csv",""))
            }

        else:
            raise Exception(f"Something went wrong: neither ims or dme provided:{instance_arr}")

    def draw_cml_map(self):
        num_links_map=len(os.listdir(self.data_path_dme))
        num_gagues_map=len(os.listdir(self.data_path_ims))
        station_type={
            "link":self.data_path_dme,
            "gauge": self.data_path_ims
        }
        num_stations_map =  num_gagues_map + num_links_map

        print(f"Number of links on map:{num_links_map}")
        print(f"Number of gauges on map:{num_gagues_map}")
        print(f"Number of stations on map:{num_stations_map}")

        grid = []

        map_1 = folium.Map(location=[32, 35],
                           zoom_start=8,
                           tiles='Stamen Terrain',
                           control_scale=True)

        lat_min=sys.maxsize
        lon_min=sys.maxsize
        lat_max=-sys.maxsize
        lon_max=-sys.maxsize

        for station_type,data_path in station_type.items():
            for instance in os.listdir(data_path):
                instace_dict=self.parse_instances(instance)
                lat_min=min(lat_min,float(instace_dict["Tx Site Latitude"]), float(instace_dict["Rx Site Latitude"]))
                lon_min=min(lon_min,float(instace_dict["Tx Site Longitude"]), float(instace_dict["Rx Site Longitude"]))
                lat_max=max(lat_max, float(instace_dict["Tx Site Latitude"]), float(instace_dict["Rx Site Latitude"]))
                lon_max=max(lon_max, float(instace_dict["Tx Site Longitude"]),float(instace_dict["Rx Site Longitude"]))


                folium.PolyLine([(instace_dict['Rx Site Latitude'],
                                  instace_dict['Rx Site Longitude']),
                                 (instace_dict['Tx Site Latitude'],
                                  instace_dict['Tx Site Longitude'])],
                                color=self.color_of_links if station_type=="link" else self.color_of_gauges,
                                opacity=1.0,
                                popup=f"ID:{instace_dict['ID']}"
                                ).add_to(map_1)

        # plot gridlines
        lats = np.linspace(lat_min, lat_max, self.num_of_gridlines)
        lons = np.linspace(lon_min, lon_max, self.num_of_gridlines)

        for lat in lats:
            grid.append([[lat, -180], [lat, 180]])

        for lon in lons:
            grid.append([[-90, lon], [90, lon]])

        if self.gridlines_on:
            counter = 0
            for g in grid:
                if counter < len(lats):
                    folium.PolyLine(g, color="black", weight=0.5,
                                    opacity=0.5, popup=str(round(g[0][0], 5))).add_to(map_1)
                    counter += 1
                else:
                    folium.PolyLine(g, color="black", weight=0.5,
                                    opacity=0.5, popup=str(round(g[0][1], 5))).add_to(map_1)

        map_1.save((str(self.out_path.joinpath(self.map_name))))

        print(f"Map under the name {self.map_name} was generated")

        return map_1

if __name__=="__main__":
    v=Visualizer()