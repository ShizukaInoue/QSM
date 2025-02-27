#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run the entire QSM Japan pipeline with proper error handling
"""

import os
import sys
import time
import traceback
from utils import get_results_path

def run_pipeline():
    """Run the entire QSM Japan pipeline with proper error handling."""
    try:
        start_time = time.time()
        
        # Step 1: Data preparation
        print("\n=== Step 1: Data Preparation ===")
        from data_preparation import load_and_merge_data
        merged_df = load_and_merge_data()
        merged_df.to_csv(get_results_path('merged_data.csv'), index=False, encoding='utf-8')
        
        # Step 2: Spatial processing
        print("\n=== Step 2: Spatial Processing ===")
        from spatial_processing import process_spatial_data, calculate_distance_matrix, calculate_trade_costs
        final_gdf = process_spatial_data(merged_df)
        distance_matrix = calculate_distance_matrix(final_gdf)
        T = calculate_trade_costs(distance_matrix)
        
        # Save intermediate results
        final_gdf.to_csv(get_results_path('final_gdf.csv'), index=False, encoding='utf-8')
        distance_matrix.to_csv(get_results_path('distance_matrix.csv'), encoding='utf-8')
        
        # Step 3: Model inversion
        print("\n=== Step 3: Model Inversion ===")
        from model_inversion import invert_model
        final_gdf = invert_model(final_gdf, T)
        
        # Step 4: Visualization
        print("\n=== Step 4: Visualization ===")
        from visualization import create_quantile_maps, create_population_amenities_scatter
        
        # Create quantile maps for selected years
        years = [1975, 1990, 2010]
        for year in years:
            create_quantile_maps(final_gdf, year)
        
        # Create population vs amenities scatter plots
        create_population_amenities_scatter(final_gdf, years)
        
        # Step 5: Categorical maps
        print("\n=== Step 5: Categorical Maps ===")
        from categorical_maps import create_categorical_maps
        for year in years:
            create_categorical_maps(final_gdf, year)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\n=== Pipeline completed in {elapsed_time:.2f} seconds ===")
        print(f"Results saved to: {get_results_path()}")
        
        return True
    
    except Exception as e:
        print(f"\n=== ERROR: Pipeline failed ===")
        print(f"Error: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_pipeline() 