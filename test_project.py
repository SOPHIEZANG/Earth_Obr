import pytest
from project import *

# from project import get_bands_plot ,get_date,get_NDVI,get_bands_plot,data_processing,DownloadData,get_boundary,get_band,get_city_name
def main():
    test_DownloadData()
    test_data_processing()
    test_get_NDVI()

    test_get_band()

    test_get_boundary()
    
#city_name,Beg_date,End_date,Cloud_cover,path,bands
def test_DownloadData():
    # assert DownloadData(city_name,Beg_date,End_date,Cloud_cover,path)==True
    path = r'C:\Users\Sophiezang\KaggleDataset'
    bands=[4,5]
    assert DownloadData('Shanghai','2020-01-01','2020-12-31',5,path,bands)==True
#     assert DownloadData('Berlin','2020-01-01','2020-12-31',5,path)==True

def test_data_processing():
    path = r'C:\Users\Sophiezang\KaggleDataset'
    assert data_processing('Beijing',path)==True
    assert data_processing('Shanghai',path)==True
#     ...

def test_get_NDVI():
    path = r'C:\Users\Sophiezang\KaggleDataset'
    ndvi=get_NDVI(path,"shanghai")
    assert len(ndvi) > 0
    

def test_get_band():
    path= r'C:\Users\Sophiezang\KaggleDataset'
    assert get_band(path,'Beijing',4)==True
    assert get_band(path,'Beijing',5)==True


def test_get_boundary():
    path=r'C:\Users\Sophiezang\KaggleDataset'
    city_shape = get_boundary('beijing',path)
    assert city_shape.length > 0
#     ...

# def test_get_data():
#     ...

# def get_city_name():
#     ...

# def get_bands_plot():
#     ...

if __name__ == "__main__":
    main()