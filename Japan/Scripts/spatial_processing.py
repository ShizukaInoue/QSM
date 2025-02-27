#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spatial Processing Script for QSM Japan

This script processes spatial data for Japanese municipalities, including:
- Loading and processing shapefiles
- Merging spatial data with demographic data
- Calculating distances between municipalities
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
from utils import replace_small_ke_with_big_ke, get_data_path, get_results_path

def process_spatial_data(merged_df):
    """
    Process spatial data for Japanese municipalities.
    
    Args:
        merged_df: DataFrame with merged population and wage data
        
    Returns:
        geopandas.GeoDataFrame: Final GeoDataFrame with spatial and demographic data
    """
    print("Processing spatial data...")
    
    # List of specified municipalities (政令指定都市)
    specified_municipalities = [
        "札幌市", "仙台市", "さいたま市", "千葉市", "横浜市", "川崎市", "相模原市", "新潟市",
        "静岡市", "浜松市", "名古屋市", "京都市", "大阪市", "堺市", "神戸市", "岡山市",
        "広島市", "北九州市", "福岡市", "熊本市"
    ]
    
    # Corresponding codes for 政令指定都市
    # These are used because 区 (ku) has its own city code, but we want to aggregate ku to city level
    specified_codes = [
        "01100", "04201", "11100", "12201", "14100", "14130", "14209", "15201",
        "22201", "22202", "23100", "26100", "27100", "27201", "28100", "33201",
        "34100", "40100", "40130", "43201"
    ]
    
    try:
        # Set up the base directory and file path
        base_path = get_data_path('jpn2014/jpn2014geo.shp')
        
        # Read the shapefile
        base_gdf = gpd.read_file(base_path, encoding='shift_jis')
        
        # Replace 'CITY' with 'GUN' for specified municipalities
        base_gdf.loc[base_gdf['GUN'].isin(specified_municipalities), 'CITY'] = base_gdf['GUN']
        
        # Replace 'CITY' with 'GUN' for areas containing '区' (ku)
        base_gdf.loc[base_gdf['GUN'].fillna('').str.contains('区'), 'CITY'] = base_gdf['GUN']
        
        # Create a mapping of municipalities to their codes
        municipality_to_code = dict(zip(specified_municipalities, specified_codes))
        
        # Apply new codes to specified municipalities, leaving others unchanged
        base_gdf['N03_007'] = base_gdf['CITY'].map(municipality_to_code).fillna(base_gdf['N03_007'])    
        
        # Create a unique key for each area
        base_gdf['dissolve_key'] = base_gdf['PREF'].astype(str) + "_" + base_gdf['GUN'].astype(str) + "_" + base_gdf['CITY'].astype(str) 
        
        # Dissolve (merge) areas with the same dissolve_key
        base_gdf = base_gdf.dissolve(by="dissolve_key")
        
        # Reset the index after dissolving
        base_gdf.reset_index(inplace=True)
        
        # Project the data to a suitable Coordinate Reference System (CRS) for Japan
        base_gdf = base_gdf.to_crs(epsg=2451)  # EPSG:2451 is JGD2000 / Japan Plane Rectangular CS IX
        
        # Fix any invalid geometries
        base_gdf['geometry'] = base_gdf['geometry'].buffer(0)
        
        # Calculate the centroid of each area
        base_gdf['centroid'] = base_gdf.geometry.centroid
        
        # Sort the GeoDataFrame by the area code
        base_gdf = base_gdf.sort_values(by='N03_007', ascending=True)
        
        # Remove any rows with missing area codes
        base_gdf = base_gdf.dropna(subset=['N03_007'])
        
        # Ensure the area code is a string type
        base_gdf['N03_007'] = base_gdf['N03_007'].astype(str)
        
        # Remove leading zeros from the area code
        base_gdf['N03_007'] = base_gdf['N03_007'].str.lstrip('0')
        
        # Convert the area code to integer type
        base_gdf['N03_007'] = base_gdf['N03_007'].astype(int)
        
        # Replace small ヶ with big ケ in city names
        base_gdf['CITY'] = base_gdf['CITY'].apply(replace_small_ke_with_big_ke)
        
        # Keep necessary columns from base_gdf, including centroid
        base_gdf = base_gdf[['PREF', 'CITY', 'geometry', 'centroid']]
        
        # Merge the processed GeoDataFrame with the previously created merged_df
        # Note: In your notebook, you're using merged_df.merge(base_gdf), not the other way around
        final_gdf = merged_df.merge(base_gdf, on=['PREF', 'CITY'], how='left', indicator=True)
        
        # Ensure the result is a GeoDataFrame
        final_gdf = gpd.GeoDataFrame(final_gdf, geometry='geometry', crs=base_gdf.crs)
        
        print(f"Spatial data processed successfully. Shape: {final_gdf.shape}")
        
        return final_gdf
    
    except Exception as e:
        print(f"Error processing spatial data: {str(e)}")
        raise

def calculate_distance_matrix(final_gdf):
    """
    Calculate the distance matrix between all pairs of municipalities.
    
    Args:
        final_gdf: GeoDataFrame with spatial and demographic data
        
    Returns:
        pandas.DataFrame: Distance matrix between municipalities
    """
    print("Calculating distance matrix...")
    
    try:
        # Check if 'centroid' column exists, if not, calculate it
        if 'centroid' not in final_gdf.columns:
            print("Calculating centroids...")
            final_gdf['centroid'] = final_gdf.geometry.centroid
        
        # Extract the centroids and their coordinates from the final_gdf
        centroids = final_gdf['centroid']
        city_names = final_gdf['CITY'] if 'dissolve_key' not in final_gdf.columns else final_gdf['dissolve_key']
        
        # Initialize a dataframe to store the distances between cities
        # The rows and columns are labeled with city names
        distance_matrix = pd.DataFrame(index=city_names, columns=city_names)
        
        # Calculate distances between all pairs of cities
        for i, city1 in enumerate(centroids):
            if i % 50 == 0:
                print(f"Processing city {i+1}/{len(centroids)}...")
            for j, city2 in enumerate(centroids):
                if i != j:
                    # Calculate the Euclidean distance between city1 and city2
                    # The formula is sqrt((x1-x2)^2 + (y1-y2)^2)
                    # Divide by 1000 to convert from meters to kilometers
                    distance = ((city1.x - city2.x)**2 + (city1.y - city2.y)**2)**0.5 / 1000
                    distance_matrix.iloc[i, j] = distance
                else:
                    # Distance from a city to itself is zero
                    distance_matrix.iloc[i, j] = 0
        
        print("Distance matrix calculated successfully.")
        
        return distance_matrix
    
    except Exception as e:
        print(f"Error calculating distance matrix: {str(e)}")
        raise

def calculate_trade_costs(distance_matrix, phi=0.01):
    """
    Calculate trade costs based on distances.
    
    Args:
        distance_matrix: DataFrame with distances between municipalities
        phi: Trade cost parameter (default: 0.01)
        
    Returns:
        numpy.ndarray: Trade cost matrix
    """
    print("Calculating trade costs...")
    
    # Convert the DataFrame to a NumPy array and ensure all values are numeric
    distance_matrix_array = distance_matrix.to_numpy().astype(float)
    
    # Multiply all values in the distance matrix by phi
    # This scales the distances by the trade cost parameter
    distance_matrix_array *= phi
    
    # Calculate the trade costs (T) using a numerically stable approach
    # np.clip is used to avoid overflow in exp calculation
    # The resulting T represents the trade costs between locations
    T = np.exp(np.clip(distance_matrix_array, -700, 700))
    
    print("Trade costs calculated successfully.")
    
    return T

def save_spatial_data(final_gdf, distance_matrix, T=None):
    """
    Save the processed spatial data to files.
    
    Args:
        final_gdf: GeoDataFrame with spatial and demographic data
        distance_matrix: DataFrame with distances between municipalities
        T: Trade cost matrix (optional)
    """
    # Save the final GeoDataFrame
    final_gdf.to_csv(get_results_path('final_gdf.csv'), index=False, encoding='utf-8')
    
    # Save the distance matrix
    distance_matrix.to_csv(get_results_path('distance_matrix.csv'), encoding='utf-8')
    
    # Save the trade costs if provided
    if T is not None:
        np.save(get_results_path('trade_costs.npy'), T)
    
    print(f"Spatial data saved to {get_results_path()}")

if __name__ == "__main__":
    # Import the data preparation module
    from data_preparation import load_and_merge_data
    
    # Load and merge data
    merged_df = load_and_merge_data()
    
    # Process spatial data
    final_gdf = process_spatial_data(merged_df)
    
    # Calculate distance matrix
    distance_matrix = calculate_distance_matrix(final_gdf)
    
    # Calculate trade costs
    T = calculate_trade_costs(distance_matrix)
    
    # Save the processed data
    save_spatial_data(final_gdf, distance_matrix, T)
    
    print("Spatial processing completed successfully.") 