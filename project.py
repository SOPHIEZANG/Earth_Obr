import rasterio 
from rasterio.merge import merge
from rasterio.warp import transform_geom
from rasterio.mask import mask

import json
from shapely.geometry import shape
import shutil
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import requests
from shapely.geometry import shape
import pandas as pd
import os, shutil, re
import glob
import json
import matplotlib.pyplot as plt
import folium

def plot_Area_of_interest(City,path):
    city_shape = None
    with open(os.path.join(path,'cities.geojson'), encoding='utf-8') as f:
        data = json.load(f)
    for feature in data['features']:
        if 'name' in feature['properties']:
            city1 = str(feature['properties']['name']).lower()
            city2 = City.lower()
            if city1 == city2:
                city_shape = shape(feature['geometry']) 
                break
    if city_shape == None:
        return city_shape
    bounds = gpd.GeoDataFrame.from_dict({'geometry': [city_shape]})
    bounds1 = gpd.GeoDataFrame(geometry=bounds.envelope)
    # unzip the wrs2.zip file
    file_zip = os.path.join(path, 'wrs2_descending.zip')
    path_unzip = os.path.join(path, 'wrs2')
    shutil.unpack_archive(file_zip, path_unzip)
    # reand the .shp file, and get the wrs system
    file_shp = os.path.join(path_unzip, 'wrs2_descending.shp')
    wrs = gpd.GeoDataFrame.from_file(file_shp)
    wrs_intersection = wrs[wrs.intersects(bounds.geometry[0])]
    # Get the center of the map
    xy = np.asarray(bounds.centroid[0].xy).squeeze()
    center = list(xy[::-1])
    # Select a zoom
    zoom = 6
    # Create the most basic OSM folium map
    m = folium.Map(location=center, zoom_start=zoom, control_scale=True)

    # Add the bounds GeoDataFrame in red
    m.add_child(folium.GeoJson(bounds.__geo_interface__, name='Area of Study', 
                            style_function=lambda x: {'color': 'red', 'alpha': 0}))

    m.add_child(folium.GeoJson(bounds1.__geo_interface__, name='MY Area of Study', 
                            style_function=lambda x: {'color': 'green', 'alpha': 0}))

    # Iterate through each Polygon of paths and rows intersecting the area
    for i, row in wrs_intersection.iterrows():
        # Create a string for the name containing the path and row of this Polygon
        name = 'path: %03d, row: %03d' % (row.PATH, row.ROW)
        # Create the folium geometry of this Polygon 
        g = folium.GeoJson(row.geometry.__geo_interface__, name=name)
        # Add a folium Popup object with the name string
        g.add_child(folium.Popup(name))
        # Add the object to the map
        g.add_to(m)

    folium.LayerControl().add_to(m)
    fname = os.path.join(path,'image','wrs_',City,'.html')
    m.save(fname)
    return True

def get_boundary(City,path):
    with open(os.path.join(path,'cities.geojson'), encoding='utf-8') as f:
            data = json.load(f)
    for feature in data['features']:
        if 'name' in feature['properties']:
            city1 = str(feature['properties']['name']).lower()
            city2 = City.lower()
            if city1 == city2:
                city_shape = shape(feature['geometry']) 
                return city_shape

def get_bands_plot(ndvi,city_name,path):
    plt.imshow(ndvi, cmap='RdYlGn')
    plt.colorbar()    
    bounds=get_boundary(city_name,path)
    boundary = gpd.GeoDataFrame.from_dict({'geometry': [bounds]})
    x = boundary.representative_point()[0].x
    y = boundary.representative_point()[0].y
    plt.title(f'NDVI of {city_name}  （{x:.2f},{y:.2f}）')
    plt.show()
    plt.savefig(f'ndvi_{city_name}.png')
    
def get_NDVI(path,city):  
    city=city.lower()             
    band_red=rasterio.open(os.path.join(path, city+"_merge_output_B4.tif"))
    
    red = band_red.read(1).astype('float64')

    band_nir = rasterio.open(os.path.join(path, city+"_merge_output_B5.tif"))
    nir = band_nir.read(1).astype('float64')
    
    ndvi=np.where( (nir==0.) | (red ==0.), 0.1, 
            np.where((nir+red)==0., 0, (nir-red)/(nir+red)))
    
    return ndvi

def get_band(path,City,count):
    list_geom=[]
    with open(os.path.join(path,'cities.geojson'), encoding='utf-8') as f:
        data = json.load(f)
    for feature in data['features']:
        if 'name' in feature['properties']:
            city1 = str(feature['properties']['name']).lower()
            city2 = City.lower()
            if city1 == city2:
                list_geom.append(feature['geometry'])
                break
    
    fn = os.path.join(path, City,"*\\*_B"+str(count)+".TIF")
    files = glob.glob(fn)            
    sources = [rasterio.open(file) for file in files]        
    merge(sources, dst_path="merge_output"+str(count)+".tif")

    with rasterio.open("merge_output"+str(count)+".tif") as src:                       
        city_shape_list = []
        geom = transform_geom('EPSG:4326', src.crs, list_geom[0],precision=6)
        city_shape_list.append(geom)

        out_image, out_transform = mask(src, city_shape_list, crop=True)        
        out_meta = src.meta
        out_meta.update({"driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform})
        new_filename = os.path.join(path,city2+"_merge_output_B"+str(count)+".tif")
        with rasterio.open(new_filename, "w", **out_meta) as dest:
            dest.write(out_image)

    return True


def data_processing(City,path):        
    count = 4
    get_band(path,City,count)
    count = 5
    get_band(path,City,count)
    return True


def DownloadData(city_name,Beg_date,End_date,Cloud_cover,path,bands):   
    try:      
        list_geom=[]
        with open(os.path.join(path,'cities.geojson'), encoding='utf-8') as f:
            data = json.load(f)
        for feature in data['features']:
            if 'name' in feature['properties']:
                city1 = str(feature['properties']['name']).lower()
                city2 = city_name.lower()
                if city1 == city2:
                    city_shape = shape(feature['geometry'])
                    list_geom.append(feature['geometry'])
                    break
        if not city_shape:
            print(f'NOT FOUND This city\'s name: {city_name}!')
            return False
        bounds = gpd.GeoDataFrame.from_dict({'geometry': [city_shape]}) 

        shutil.unpack_archive(os.path.join(path,'wrs2_descending.zip'),
                            os.path.join(path, 'wrs2'))
        wrs = gpd.GeoDataFrame.from_file(os.path.join(path, 'wrs2',
                                        'wrs2_descending.shp'))
        wrs_intersection = wrs[wrs.intersects(bounds.geometry[0])]
        paths, rows = wrs_intersection['PATH'].values, wrs_intersection['ROW'].values

        google_scenes = pd.read_csv(os.path.join(path,'index.csv.gz'), compression='gzip')
        google_scenes['SENSING_TIME'] = google_scenes['SENSING_TIME'].str[0:10]
        
        bulk_list = []
        for path, row in zip(paths, rows):
            print('Path:',path, 'Row:', row)
            scenes = google_scenes[(google_scenes.WRS_PATH == path) & (google_scenes.WRS_ROW == row) & 
                            (google_scenes.CLOUD_COVER <= Cloud_cover) & 
                            (google_scenes.PRODUCT_ID.str.contains('_T1')) &
                            (google_scenes.PRODUCT_ID.str.contains('08_L')) &
                            (google_scenes['SENSING_TIME'] > Beg_date) &
                            (google_scenes['SENSING_TIME'] < End_date)]
            print(' Found {} images\n'.format(len(scenes)))
            if len(scenes):
                scene = scenes.sort_values('CLOUD_COVER').iloc[0]
                bulk_list.append(scene)                
    except Exception as ex:
        if(len(bulk_list)==0):
            print('DIDN\'T FIND ANY PICTURES YOU REQUIRED!')
        return False
            
    bulk_frame = pd.concat(bulk_list, 1).T
    for _, row in bulk_frame.iterrows():
        base_url = row.BASE_URL.replace('gs://','https://storage.googleapis.com/')
        entity_dir = os.path.join(city_name, row.PRODUCT_ID)
        os.makedirs(entity_dir, exist_ok=True)
        for band in bands:
            file = row.PRODUCT_ID + '_B' + str(band) + '.TIF'
            download_url = base_url + '/' + file            
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                print('  Downloading: {}'.format(file))
                print('from \n' + download_url)
                with open(os.path.join(entity_dir, file), 'wb') as output:
                    shutil.copyfileobj(response.raw, output)
            del response

    print(f'Your required images have been downloaded in {entity_dir}')    
    return True

def get_date(Beg_date):
    if re.search(r'\d{4}-((1[0-2])|(0[1-9]))-(0[1-9]|(1[0-9]|2[0-9])|3[0-1])',Beg_date):
        year,month,day=Beg_date.split('-')

        if int(year)>=2000 and int(year)<2023:
            return True
        else:
            return False

def get_city_name(path,City):
    with open(os.path.join(path,'cities.geojson'), encoding='utf-8') as f:
        data = json.load(f)
    for feature in data['features']:
        if 'name' in feature['properties']:
            city1 = str(feature['properties']['name']).lower()
            city2 = City.lower()
            if city1 == city2:                
                return True
    return False    


def main():
    path = os.path.dirname(__file__) 
    
    while True:   
        City=input("What is your City name? ")
        print(f"Your input City is :{City}")            
        if get_city_name(path,City)==True:           
            break
        else:
            print('【Cannot find this city in our dataset.】')
    
    while True:
        Beg_date=input("Begining of Year-Month-Days:")
        begin_date = get_date(Beg_date)
        if begin_date ==True:
            break
        else:
            print("WRONG time format, plese input again.")
            print("Your input data format is not correct, you should input like ****-**-**:")
    
    while True:  
        End_date=input("what is the end Year-Month-day: ")
        End_Date=get_date(End_date)
        if End_Date==True:
            break        
        else:
            print("WRONG time format, plese input again.")
            print("Your input data format is not correct, you should input like ****-**-**:")

    Cloud_cover=int(input("what is your favorate Cloud cover[1-100]:?"))
    bands=[]
    band=input("Which band will you download? (e.g 1 2 4 5): ")
    bands=band.split()
    
    DownloadData(City,Beg_date,End_date,Cloud_cover,path,bands)
    data_processing(City,path)  
    ndvi=get_NDVI(path,City)
    get_bands_plot(ndvi,City,path)
    plot_Area_of_interest(City,path)   


if __name__ == "__main__":
    main()