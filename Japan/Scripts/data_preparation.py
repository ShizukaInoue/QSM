#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Preparation Script for QSM Japan

This script loads and merges population and wage data for Japanese municipalities.
"""

import os
import pandas as pd
from utils import replace_small_ke_with_big_ke, get_data_path, get_results_path

def load_and_merge_data():
    """
    Load population and wage data from Excel files and merge them.
    
    Returns:
        pandas.DataFrame: Merged dataframe with population and wage data
    """
    print("Loading population and wage data...")
    
    # Load population and wage data from Excel files
    population_df = pd.read_excel(get_data_path('population 1970 2010.xls'))
    wage_df = pd.read_excel(get_data_path('average wage 1975_2014.xls'))
    
    # Clean up column names by removing leading/trailing spaces
    population_df.columns = population_df.columns.str.strip()
    wage_df.columns = wage_df.columns.str.strip()
    
    # Rename population columns for clarity
    population_df.columns = ['Municipality_Info', 'Municipality_Code', 'Population_1970', 'Population_1975', 'Population_1980', 
                             'Population_1985', 'Population_1990', 'Population_1995', 'Population_2000', 'Population_2005', 
                             'Population_2010']
    
    # Rename wage columns dynamically
    wage_columns = ['Municipality_Name', 'Municipality_Code'] + [f'Wage_{year}' for year in range(1975, 2014)]
    wage_df.columns = wage_columns
    
    # Ensure municipality codes are of the same type (string) for merging
    population_df['Municipality_Code'] = population_df['Municipality_Code'].astype(str)
    wage_df['Municipality_Code'] = wage_df['Municipality_Code'].astype(str)
    
    # Merge population and wage datasets on the municipality code
    merged_df = pd.merge(population_df, wage_df, left_on='Municipality_Code', right_on='Municipality_Code', how='inner')
    
    # Ensure the 'Municipality_Code' column is of string type for manipulation
    merged_df['Municipality_Code'] = merged_df['Municipality_Code'].astype(str)
    
    # Drop the last digit from the 'Municipality_Code' column (possibly to standardize codes)
    merged_df['Municipality_Code'] = merged_df['Municipality_Code'].str[:-1]
    
    # Convert 'Municipality_Code' back to integer type
    merged_df['Municipality_Code'] = merged_df['Municipality_Code'].astype(int)
    
    # Split 'Municipality_Info' into 'PREF' (prefecture) and 'CITY' columns
    merged_df[['PREF', 'CITY']] = merged_df['Municipality_Info'].str.split(n=1, expand=True)
    
    # Apply text processing to standardize city names
    merged_df['CITY'] = merged_df['CITY'].apply(replace_small_ke_with_big_ke)
    
    print(f"Data loaded and merged successfully. Shape: {merged_df.shape}")
    
    return merged_df

def save_merged_data(merged_df, output_path=None):
    """
    Save the merged dataframe to a CSV file.
    
    Args:
        merged_df: The merged dataframe to save
        output_path: Path to save the CSV file (optional)
    """
    if output_path is None:
        output_path = get_results_path('merged_data.csv')
    
    merged_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Merged data saved to {output_path}")

if __name__ == "__main__":
    # Load and merge data
    merged_df = load_and_merge_data()
    
    # Save the merged data
    save_merged_data(merged_df)
    
    print("Data preparation completed successfully.") 