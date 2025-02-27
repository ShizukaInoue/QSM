#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Inversion Script for QSM Japan

This script implements the model inversion procedure based on Allen and Arkolakis (2014).
It calculates amenities and utilities for Japanese municipalities.
"""

import os
import numpy as np
import pandas as pd
from utils import get_data_path, get_results_path

def invert_model(final_gdf, T, years=None, output_dir=None):
    """
    Invert the model to calculate amenities and utilities.
    
    Args:
        final_gdf: GeoDataFrame with spatial and demographic data
        T: Trade cost matrix
        years: List of years to process (default: [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010])
        output_dir: Directory to save the results (optional)
        
    Returns:
        pandas.DataFrame: Updated GeoDataFrame with amenities and utilities
    """
    if years is None:
        years = [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010]
    
    print("Inverting the model...")
    
    # Parameters for the model
    sigma = 9  # Elasticity of substitution
    N = len(final_gdf)  # Number of locations
    tol = 1e-6  # Convergence tolerance
    max_iter = 1000  # Maximum number of iterations
    min_alpha = 0.01  # Minimum learning rate
    initial_alpha = 0.1  # Initial learning rate
    
    # Dictionary to store convergence statistics
    convergence_stats = {year: {'iterations': 0, 'final_diff': 0.0} for year in years}
    
    for year in years:
        print(f"\nProcessing year {year}")
        
        # Extract Population (L) and Wage (w) for the current year
        L = final_gdf[f'Population_{year}'].tolist()
        w = final_gdf[f'Wage_{year}'].tolist()
        
        # Check for missing or invalid values
        missing_L = np.sum(np.isnan(L))
        missing_w = np.sum(np.isnan(w))
        if missing_L > 0 or missing_w > 0:
            print(f"Warning: Found missing values in year {year}")
            print(f"Missing population values: {missing_L}")
            print(f"Missing wage values: {missing_w}")
            
            # Fill missing values with mean
            L = np.nan_to_num(L, nan=np.nanmean(L))
            w = np.nan_to_num(w, nan=np.nanmean(w))
        
        # Normalize L and w to have a mean of 1
        L = np.array(L) / np.mean(L)
        w = np.array(w) / np.mean(w)
        
        # Print data statistics
        print(f"Data statistics for {year}:")
        print(f"Population - min: {np.min(L):.2f}, max: {np.max(L):.2f}, mean: {np.mean(L):.2f}")
        print(f"Wage - min: {np.min(w):.2f}, max: {np.max(w):.2f}, mean: {np.mean(w):.2f}")
        
        # Initial guesses for amenities (A) and utility (u)
        A = np.ones(N)
        u = np.ones(N)
        
        # Variables to track best solution
        best_diff = float('inf')
        best_A = None
        best_u = None
        
        # Iterative loop for estimating A and u
        diff = 1
        iter_count = 0
        no_improvement_count = 0
        
        while diff > tol and iter_count < max_iter:
            # Adaptive learning rate
            alpha_update = max(min_alpha, initial_alpha / np.sqrt(1 + iter_count))
            
            if iter_count % 100 == 0:
                print(f"Iteration {iter_count}, diff: {diff:.6f}, learning rate: {alpha_update:.6f}")
            
            try:
                # Update utility (u) with numerical stability improvements
                term1 = np.clip(T ** (1 - sigma), 1e-10, 1e10)
                term2 = np.clip((w * np.ones(N)) ** (sigma - 1), 1e-10, 1e10)
                term3 = np.clip(np.ones(N)[:, None] * ((A / w) ** (sigma - 1)), 1e-10, 1e10)
                
                combined_terms = np.clip(term1 * term2[:, None] * term3, 1e-10, 1e10)
                u_new = np.clip((np.mean(combined_terms, axis=1)) ** (1 / (1 - sigma)), 1e-10, 1e10)
                u_new = u_new / np.mean(u_new)  # Normalize u
                
                # Update amenities (A) with numerical stability improvements
                A_new = np.clip((L * w ** (2 * sigma - 1) * u ** (sigma - 1)) ** (1 / (sigma - 1)), 1e-10, 1e10)
                A_new = A_new / np.mean(A_new)  # Normalize A
                
                # Calculate the difference between old and new values
                diff = np.linalg.norm(A - A_new) + np.linalg.norm(u - u_new)
                
                # Track best solution
                if diff < best_diff:
                    best_diff = diff
                    best_A = A_new.copy()
                    best_u = u_new.copy()
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1
                
                # Update A and u with adaptive learning rate
                A = alpha_update * A_new + (1 - alpha_update) * A
                u = alpha_update * u_new + (1 - alpha_update) * u
                
                # Early stopping if no improvement for many iterations
                if no_improvement_count > 50:
                    print(f"Early stopping: No improvement for {no_improvement_count} iterations")
                    break
                
            except Exception as e:
                print(f"Error in iteration {iter_count}: {str(e)}")
                break
            
            iter_count += 1
        
        # Use the best solution found
        if best_A is not None and best_u is not None:
            A = best_A
            u = best_u
            diff = best_diff
        
        # Store convergence statistics
        convergence_stats[year]['iterations'] = iter_count
        convergence_stats[year]['final_diff'] = diff
        
        if iter_count >= max_iter:
            print(f"Warning: Maximum iterations ({max_iter}) reached for year {year}")
        else:
            print(f"Converged after {iter_count} iterations with final diff: {diff:.6f}")
        
        # Validation checks
        print("\nValidation checks:")
        print(f"Amenities (A) - min: {np.min(A):.2f}, max: {np.max(A):.2f}, mean: {np.mean(A):.2f}")
        print(f"Utility (u) - min: {np.min(u):.2f}, max: {np.max(u):.2f}, mean: {np.mean(u):.2f}")
        
        # Store the estimated A and u in the final_gdf DataFrame
        final_gdf[f'A_{year}'] = A
        final_gdf[f'u_{year}'] = u
    
    # Print summary statistics
    print("\nConvergence Summary:")
    for year in years:
        stats = convergence_stats[year]
        print(f"Year {year}: {stats['iterations']} iterations, final diff: {stats['final_diff']:.6f}")
    
    # Save the results
    if output_dir is None:
        output_dir = get_results_path()
    
    # Save the final_gdf DataFrame to a CSV file
    final_gdf.to_csv(get_results_path('model_results.csv'), index=False, encoding='utf-8')
    
    # Save the convergence statistics to a CSV file
    convergence_df = pd.DataFrame.from_dict(convergence_stats, orient='index')
    convergence_df.index.name = 'Year'
    convergence_df.to_csv(get_results_path('convergence_stats.csv'), encoding='utf-8')
    
    print(f"Model inversion results saved to {output_dir}")
    
    return final_gdf

if __name__ == "__main__":
    # Import the data preparation and spatial processing modules
    from data_preparation import load_and_merge_data
    from spatial_processing import process_spatial_data, calculate_distance_matrix, calculate_trade_costs
    
    # Load and merge data
    merged_df = load_and_merge_data()
    
    # Process spatial data
    final_gdf = process_spatial_data(merged_df)
    
    # Calculate distance matrix
    distance_matrix = calculate_distance_matrix(final_gdf)
    
    # Calculate trade costs
    T = calculate_trade_costs(distance_matrix)
    
    # Invert the model
    final_gdf = invert_model(final_gdf, T)
    
    print("Model inversion completed successfully.") 