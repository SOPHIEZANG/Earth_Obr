import pytest
from project import *
import os

def main():
    test_DownloadData()
    test_data_processing()
    test_get_NDVI()
    test_get_band()
    test_get_boundary()
    
def test_DownloadData():
    path = os.path.dirname(__file__) 
    bands=[4,5]
    assert DownloadData('Shanghai','2020-01-01','2020-12-31',5,path,bands)==True

def test_data_processing():
    path = os.path.dirname(__file__) 
    assert data_processing('Beijing',path)==True
    assert data_processing('Shanghai',path)==True

def test_get_NDVI():
    path = os.path.dirname(__file__) 
    ndvi=get_NDVI(path,"shanghai")
    assert len(ndvi) > 0
    

def test_get_band():
    path = os.path.dirname(__file__) 
    assert get_band(path,'Beijing',4)==True
    assert get_band(path,'Beijing',5)==True

def test_get_boundary():
    path = os.path.dirname(__file__) 
    city_shape = get_boundary('beijing',path)
    assert city_shape.length > 0

if __name__ == "__main__":
    main()