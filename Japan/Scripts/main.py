#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Script for QSM Japan

This script runs the entire QSM Japan pipeline:
1. Data preparation
2. Spatial processing
3. Model inversion
4. Visualization

Usage:
    python main.py [--skip-steps STEPS] [--years YEARS]

Options:
    --skip-steps STEPS    Comma-separated list of steps to skip (e.g., "data,spatial,model,viz")
    --years YEARS         Comma-separated list of years to process (e.g., "1975,1990,2010")
"""

import os
import sys
import argparse
import time
import numpy as np
import pandas as pd
import geopandas as gpd
from utils import get_results_path

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the QSM Japan pipeline.')
    parser.add_argument('--skip-steps', type=str, default='',
                        help='Comma-separated list of steps to skip (e.g., "data,spatial,model,viz")')
    parser.add_argument('--years', type=str, default='',
                        help='Comma-separated list of years to process (e.g., "1975,1990,2010")')
    return parser.parse_args()

def main():
    """Run the QSM Japan pipeline."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        skip_steps = args.skip_steps.split(',') if args.skip_steps else []
        years = [int(year) for year in args.years.split(',')] if args.years else None
        
        # Create a Results directory if it doesn't exist
        results_dir = get_results_path()
        
        # Start timing
        start_time = time.time()
        
        # Step 1: Data preparation
        if 'data' not in skip_steps:
            print("\n=== Step 1: Data Preparation ===")
            from data_preparation import load_and_merge_data
            merged_df = load_and_merge_data()
            merged_df.to_csv(get_results_path('merged_data.csv'), index=False, encoding='utf-8')
        else:
            print("\n=== Skipping Step 1: Data Preparation ===")
            merged_df = pd.read_csv(get_results_path('merged_data.csv'))
        
        # Step 2: Spatial processing
        if 'spatial' not in skip_steps:
            print("\n=== Step 2: Spatial Processing ===")
            from spatial_processing import process_spatial_data, calculate_distance_matrix, calculate_trade_costs
            final_gdf = process_spatial_data(merged_df)
            distance_matrix = calculate_distance_matrix(final_gdf)
            T = calculate_trade_costs(distance_matrix)
            
            # Save intermediate results
            final_gdf.to_csv(get_results_path('final_gdf.csv'), index=False, encoding='utf-8')
            distance_matrix.to_csv(get_results_path('distance_matrix.csv'), encoding='utf-8')
            np.save(get_results_path('trade_costs.npy'), T)
        else:
            print("\n=== Skipping Step 2: Spatial Processing ===")
            final_gdf = pd.read_csv(get_results_path('final_gdf.csv'))
            
            # Convert to GeoDataFrame
            try:
                geometry = gpd.GeoSeries.from_wkt(final_gdf['geometry'])
                final_gdf = gpd.GeoDataFrame(final_gdf, geometry=geometry, crs='epsg:2451')
            except Exception as e:
                print(f"Warning: Could not convert to GeoDataFrame. Error: {str(e)}")
                print("Some functionality may be limited.")
            
            distance_matrix = pd.read_csv(get_results_path('distance_matrix.csv'), index_col=0)
            T = np.load(get_results_path('trade_costs.npy'))
        
        # Step 3: Model inversion
        if 'model' not in skip_steps:
            print("\n=== Step 3: Model Inversion ===")
            from model_inversion import invert_model
            final_gdf = invert_model(final_gdf, T, years=years)
        else:
            print("\n=== Skipping Step 3: Model Inversion ===")
            final_gdf = pd.read_csv(get_results_path('model_results.csv'))
            
            # Convert to GeoDataFrame
            try:
                geometry = gpd.GeoSeries.from_wkt(final_gdf['geometry'])
                final_gdf = gpd.GeoDataFrame(final_gdf, geometry=geometry, crs='epsg:2451')
            except Exception as e:
                print(f"Warning: Could not convert to GeoDataFrame. Error: {str(e)}")
                print("Some functionality may be limited.")
        
        # Step 4: Visualization
        if 'viz' not in skip_steps:
            print("\n=== Step 4: Visualization ===")
            from visualization import generate_all_visualizations
            generate_all_visualizations(final_gdf)
        else:
            print("\n=== Skipping Step 4: Visualization ===")
        
        # End timing
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\n=== Pipeline completed in {elapsed_time:.2f} seconds ===")
        print(f"Results saved to: {results_dir}")
    except Exception as e:
        print(f"Error running the pipeline: {str(e)}")

if __name__ == "__main__":
    main() 