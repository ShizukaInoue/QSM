#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualization Script for QSM Japan

This script creates visualizations of the model results, including:
- Maps of amenities and utilities
- Categorical/quantile maps
- Scatter plots of population vs. productivity and amenities
- Time series of key metrics
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm, Normalize
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import geopandas as gpd
import contextily as ctx
from utils import get_data_path, get_results_path, save_figure

def create_maps(final_gdf, years=None, output_dir=None):
    """
    Create maps of amenities and utilities for each year.
    
    Args:
        final_gdf: GeoDataFrame with model results
        years: List of years to visualize (default: [1975, 1990, 2010])
        output_dir: Directory to save the figures (optional)
    """
    if years is None:
        years = [1975, 1990, 2010]  # Selected years for visualization
    
    print("Creating maps...")
    
    # Create a copy of the GeoDataFrame
    map_gdf = final_gdf.copy()
    
    # Create maps for productivity (A)
    fig, axes = plt.subplots(1, len(years), figsize=(15, 5))
    if len(years) == 1:
        axes = [axes]  # Make sure axes is always a list
    
    # Set the figure title
    fig.suptitle('Productivity (A) Across Japan', fontsize=16)
    
    # Use the same colormap for both productivity and amenities
    cmap = 'viridis'
    
    # Create a map for each year
    for i, year in enumerate(years):
        # Check if the column exists
        if f'A_{year}' not in map_gdf.columns:
            print(f"Warning: A_{year} not found in the data. Skipping.")
            continue
        
        # Plot the map
        map_gdf.plot(column=f'A_{year}', ax=axes[i], cmap=cmap, 
                     legend=True, norm=LogNorm())
        
        # Set the title and remove axis labels
        axes[i].set_title(f'Year {year}')
        axes[i].set_axis_off()
    
    # Adjust the layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the suptitle
    
    # Save the figure
    if output_dir is None:
        save_figure(fig, 'productivity_maps.png')
    else:
        fig.savefig(os.path.join(output_dir, 'productivity_maps.png'), dpi=300, bbox_inches='tight')
    
    plt.close(fig)
    
    # Create maps for amenities (u)
    fig, axes = plt.subplots(1, len(years), figsize=(15, 5))
    if len(years) == 1:
        axes = [axes]  # Make sure axes is always a list
    
    # Set the figure title
    fig.suptitle('Amenities (u) Across Japan', fontsize=16)
    
    # Create a map for each year
    for i, year in enumerate(years):
        # Check if the column exists
        if f'u_{year}' not in map_gdf.columns:
            print(f"Warning: u_{year} not found in the data. Skipping.")
            continue
        
        # Plot the map - using the same colormap as productivity
        map_gdf.plot(column=f'u_{year}', ax=axes[i], cmap=cmap, 
                     legend=True, norm=LogNorm())
        
        # Set the title and remove axis labels
        axes[i].set_title(f'Year {year}')
        axes[i].set_axis_off()
    
    # Adjust the layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the suptitle
    
    # Save the figure
    if output_dir is None:
        save_figure(fig, 'amenities_maps.png')
    else:
        fig.savefig(os.path.join(output_dir, 'amenities_maps.png'), dpi=300, bbox_inches='tight')
    
    plt.close(fig)
    
    print("Maps created successfully.")

def create_quantile_maps(final_gdf, year=2000, n_quantiles=5, output_dir=None):
    """
    Create maps with quantile-based coloring.
    
    Args:
        final_gdf: GeoDataFrame with model results
        year: Year to visualize (default: 2000)
        n_quantiles: Number of quantiles to use (default: 5)
        output_dir: Directory to save the figure (optional)
    """
    print(f"Creating quantile maps for year {year}...")
    
    try:
        # Create a copy of the GeoDataFrame
        map_gdf = final_gdf.copy()
        
        # Check if the required columns exist
        if f'A_{year}' not in map_gdf.columns or f'u_{year}' not in map_gdf.columns:
            print(f"Warning: A_{year} or u_{year} not found in the data. Skipping.")
            return
        
        # Create a figure with two subplots
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Set the figure title
        fig.suptitle(f'Productivity and Amenities Quantiles ({year})', fontsize=16)
        
        # Use the same colormap for both maps
        cmap = plt.cm.viridis
        
        # Create quantile-based categories for productivity (A)
        try:
            # Ensure no negative values (floor at zero)
            map_gdf[f'A_{year}'] = map_gdf[f'A_{year}'].clip(lower=0)
            
            # Create quantile categories and get the bin edges
            _, bins = pd.qcut(map_gdf[f'A_{year}'], q=n_quantiles, duplicates='drop', retbins=True)
            
            # Create a new column with the bin indices
            map_gdf[f'A_{year}_binned'] = pd.cut(
                map_gdf[f'A_{year}'], 
                bins=bins, 
                labels=False, 
                include_lowest=True
            )
            
            # Plot with the binned column - no default legend
            map_gdf.plot(
                column=f'A_{year}_binned',
                cmap=cmap,
                legend=False,
                ax=axes[0]
            )
            
            # Create a compact custom legend
            norm = mcolors.Normalize(vmin=0, vmax=n_quantiles-1)
            
            # Create legend patches with compact labels
            legend_patches = []
            for i in range(len(bins)-1):
                color = cmap(norm(i))
                label = f"{bins[i]:.2f}-{bins[i+1]:.2f}"
                patch = mpatches.Patch(color=color, label=label)
                legend_patches.append(patch)
            
            # Add the custom legend with smaller font and compact layout
            legend = axes[0].legend(
                handles=legend_patches,
                title="Productivity",
                loc='lower left',
                fontsize='x-small',
                title_fontsize='small',
                framealpha=0.7,
                handlelength=1.0,
                handletextpad=0.5,
                borderpad=0.3,
                labelspacing=0.2
            )
            
        except Exception as e:
            print(f"Warning: Could not create quantile map for productivity. Error: {str(e)}")
            # Fallback to simple plotting without legend
            map_gdf.plot(
                column=f'A_{year}',
                cmap=cmap,
                legend=False,
                ax=axes[0]
            )
        
        # Set the title and remove axis labels
        axes[0].set_title(f'Spatial Distribution of Productivity in {year}', fontsize=14)
        axes[0].set_axis_off()
        
        # Create quantile-based categories for amenities (u)
        try:
            # Ensure no negative values (floor at zero)
            map_gdf[f'u_{year}'] = map_gdf[f'u_{year}'].clip(lower=0)
            
            # Create quantile categories and get the bin edges
            _, bins = pd.qcut(map_gdf[f'u_{year}'], q=n_quantiles, duplicates='drop', retbins=True)
            
            # Create a new column with the bin indices
            map_gdf[f'u_{year}_binned'] = pd.cut(
                map_gdf[f'u_{year}'], 
                bins=bins, 
                labels=False, 
                include_lowest=True
            )
            
            # Plot with the binned column - no default legend
            map_gdf.plot(
                column=f'u_{year}_binned',
                cmap=cmap,  # Same colormap as productivity
                legend=False,
                ax=axes[1]
            )
            
            # Create a compact custom legend
            norm = mcolors.Normalize(vmin=0, vmax=n_quantiles-1)
            
            # Create legend patches with compact labels
            legend_patches = []
            for i in range(len(bins)-1):
                color = cmap(norm(i))
                label = f"{bins[i]:.2f}-{bins[i+1]:.2f}"
                patch = mpatches.Patch(color=color, label=label)
                legend_patches.append(patch)
            
            # Add the custom legend with smaller font and compact layout
            legend = axes[1].legend(
                handles=legend_patches,
                title="Amenities",
                loc='lower left',
                fontsize='x-small',
                title_fontsize='small',
                framealpha=0.7,
                handlelength=1.0,
                handletextpad=0.5,
                borderpad=0.3,
                labelspacing=0.2
            )
            
        except Exception as e:
            print(f"Warning: Could not create quantile map for amenities. Error: {str(e)}")
            # Fallback to simple plotting without legend
            map_gdf.plot(
                column=f'u_{year}',
                cmap=cmap,
                legend=False,
                ax=axes[1]
            )
        
        # Set the title and remove axis labels
        axes[1].set_title(f'Spatial Distribution of Amenities in {year}', fontsize=14)
        axes[1].set_axis_off()
        
        # Add a source note at the bottom of the figure
        fig.text(0.5, 0.01, f'QSM Japan Analysis - {year}', ha='center', fontsize=10)
        
        # Adjust the layout
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the suptitle
        
        # Save the figure
        if output_dir is None:
            save_figure(fig, f'quantile_maps_{year}.png')
        else:
            fig.savefig(os.path.join(output_dir, f'quantile_maps_{year}.png'), dpi=300, bbox_inches='tight')
        
        plt.close(fig)
        
        print(f"Quantile maps for year {year} created successfully.")
    
    except Exception as e:
        print(f"Error creating quantile maps: {str(e)}")

# Alias for backward compatibility
create_categorical_maps = create_quantile_maps

def create_population_productivity_scatter(final_gdf, years=None, output_dir=None):
    """
    Create scatter plots of population vs. productivity.
    
    Args:
        final_gdf: GeoDataFrame with model results
        years: List of years to visualize (default: [1975, 1990, 2010])
        output_dir: Directory to save the figure (optional)
    """
    if years is None:
        years = [1975, 1990, 2010]  # Selected years for visualization
    
    print("Creating population vs. productivity scatter plots...")
    
    try:
        # Set a modern style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Create a figure with a clean white background
        fig = plt.figure(figsize=(15, 6), facecolor='white')
        
        # Modern color palette
        colors = ['#3498db', '#2ecc71', '#e74c3c']  # Blue, Green, Red
        
        for idx, year in enumerate(years, 1):
            ax = plt.subplot(1, len(years), idx)
            
            # Check if the required columns exist
            if f'Population_{year}' not in final_gdf.columns or f'A_{year}' not in final_gdf.columns:
                print(f"Warning: Population_{year} or A_{year} not found in the data. Skipping.")
                ax.text(0.5, 0.5, f"No data for {year}", 
                       ha='center', va='center', fontsize=12, color='#555555')
                continue
            
            # Filter out any NaN or zero values for cleaner plots
            valid_data = final_gdf[
                (final_gdf[f'Population_{year}'] > 0) & 
                (final_gdf[f'A_{year}'] > 0) &
                (~np.isnan(final_gdf[f'Population_{year}'])) &
                (~np.isnan(final_gdf[f'A_{year}']))
            ].copy()
            
            if len(valid_data) == 0:
                ax.text(0.5, 0.5, f"No valid data for {year}", 
                       ha='center', va='center', fontsize=12, color='#555555')
                continue
            
            # Create scatter plot with modern styling
            scatter = ax.scatter(
                np.log(valid_data[f'Population_{year}']), 
                np.log(valid_data[f'A_{year}']),
                alpha=0.7,
                s=40,
                c=colors[idx-1 % len(colors)],  # Use modulo to avoid index errors
                edgecolor='white',
                linewidth=0.5
            )
            
            # Add trend line with modern styling
            try:
                z = np.polyfit(
                    np.log(valid_data[f'Population_{year}']), 
                    np.log(valid_data[f'A_{year}']), 
                    1
                )
                p = np.poly1d(z)
                
                # Get x range for smoother line
                x_range = np.linspace(
                    np.log(valid_data[f'Population_{year}']).min(),
                    np.log(valid_data[f'Population_{year}']).max(),
                    100
                )
                
                ax.plot(
                    x_range,
                    p(x_range),
                    linestyle='--',
                    color='#2c3e50',  # Dark blue-gray
                    linewidth=2,
                    alpha=0.8
                )
                
                # Calculate correlation
                corr = np.corrcoef(
                    np.log(valid_data[f'Population_{year}']),
                    np.log(valid_data[f'A_{year}'])
                )[0,1]
                
                # Add equation to the plot
                equation = f"y = {z[0]:.2f}x + {z[1]:.2f}"
                ax.text(
                    0.05, 0.15, 
                    equation, 
                    transform=ax.transAxes,
                    fontsize=10,
                    verticalalignment='top',
                    color='#2c3e50'
                )
                
                # Add correlation to the plot
                ax.text(
                    0.05, 0.08, 
                    f"Correlation: {corr:.2f}", 
                    transform=ax.transAxes,
                    fontsize=11,
                    verticalalignment='top',
                    color='#2c3e50'
                )
            except Exception as e:
                print(f"Warning: Could not add trend line for year {year}: {str(e)}")
            
            # Modern, clean title and labels
            ax.set_title(f'{year}', fontsize=14, fontweight='bold', pad=15)
            ax.set_xlabel('Log Population', fontsize=12)
            ax.set_ylabel('Log Productivity', fontsize=12)
            
            # Clean up the plot
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, alpha=0.3)
        
        # Add a main title
        plt.suptitle('Population vs. Productivity Relationship', fontsize=16, y=0.98)
        
        # Add a source note at the bottom of the figure
        fig.text(0.5, 0.01, 'QSM Japan Analysis', ha='center', fontsize=10)
        
        # Adjust the layout
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the suptitle
        
        # Save the figure
        if output_dir is None:
            save_figure(fig, 'population_productivity_scatter.png')
        else:
            fig.savefig(os.path.join(output_dir, 'population_productivity_scatter.png'), dpi=300, bbox_inches='tight')
        
        plt.close(fig)
        
        print("Population vs. productivity scatter plots created successfully.")
    
    except Exception as e:
        print(f"Error creating population vs. productivity scatter plots: {str(e)}")

def create_population_amenities_scatter(final_gdf, years=None, output_dir=None):
    """
    Create scatter plots of population vs. amenities.
    
    Args:
        final_gdf: GeoDataFrame with model results
        years: List of years to visualize (default: [1975, 1990, 2010])
        output_dir: Directory to save the figure (optional)
    """
    if years is None:
        years = [1975, 1990, 2010]  # Selected years for visualization
    
    print("Creating population vs. amenities scatter plots...")
    
    try:
        # Set a modern style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Create a figure with a clean white background
        fig = plt.figure(figsize=(15, 6), facecolor='white')
        
        # Modern color palette
        colors = ['#3498db', '#2ecc71', '#e74c3c']  # Blue, Green, Red
        
        for idx, year in enumerate(years, 1):
            ax = plt.subplot(1, len(years), idx)
            
            # Check if the required columns exist
            if f'Population_{year}' not in final_gdf.columns or f'u_{year}' not in final_gdf.columns:
                print(f"Warning: Population_{year} or u_{year} not found in the data. Skipping.")
                ax.text(0.5, 0.5, f"No data for {year}", 
                       ha='center', va='center', fontsize=12, color='#555555')
                continue
            
            # Filter out any NaN or zero values for cleaner plots
            valid_data = final_gdf[
                (final_gdf[f'Population_{year}'] > 0) & 
                (final_gdf[f'u_{year}'] > 0) &
                (~np.isnan(final_gdf[f'Population_{year}'])) &
                (~np.isnan(final_gdf[f'u_{year}']))
            ].copy()
            
            if len(valid_data) == 0:
                ax.text(0.5, 0.5, f"No valid data for {year}", 
                       ha='center', va='center', fontsize=12, color='#555555')
                continue
            
            # Create scatter plot with modern styling
            scatter = ax.scatter(
                np.log(valid_data[f'Population_{year}']), 
                np.log(valid_data[f'u_{year}']),
                alpha=0.7,
                s=40,
                c=colors[idx-1 % len(colors)],  # Use modulo to avoid index errors
                edgecolor='white',
                linewidth=0.5
            )
            
            # Add trend line with modern styling
            try:
                z = np.polyfit(
                    np.log(valid_data[f'Population_{year}']), 
                    np.log(valid_data[f'u_{year}']), 
                    1
                )
                p = np.poly1d(z)
                
                # Get x range for smoother line
                x_range = np.linspace(
                    np.log(valid_data[f'Population_{year}']).min(),
                    np.log(valid_data[f'Population_{year}']).max(),
                    100
                )
                
                ax.plot(
                    x_range,
                    p(x_range),
                    linestyle='--',
                    color='#2c3e50',  # Dark blue-gray
                    linewidth=2,
                    alpha=0.8
                )
                
                # Calculate correlation
                corr = np.corrcoef(
                    np.log(valid_data[f'Population_{year}']),
                    np.log(valid_data[f'u_{year}'])
                )[0,1]
                
                # Add equation to the plot
                equation = f"y = {z[0]:.2f}x + {z[1]:.2f}"
                ax.text(
                    0.05, 0.15, 
                    equation, 
                    transform=ax.transAxes,
                    fontsize=10,
                    verticalalignment='top',
                    color='#2c3e50'
                )
                
                # Add correlation to the plot
                ax.text(
                    0.05, 0.08, 
                    f"Correlation: {corr:.2f}", 
                    transform=ax.transAxes,
                    fontsize=11,
                    verticalalignment='top',
                    color='#2c3e50'
                )
            except Exception as e:
                print(f"Warning: Could not add trend line for year {year}: {str(e)}")
            
            # Modern, clean title and labels
            ax.set_title(f'{year}', fontsize=14, fontweight='bold', pad=15)
            ax.set_xlabel('Log Population', fontsize=12)
            ax.set_ylabel('Log Amenities', fontsize=12)
            
            # Clean up the plot
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, alpha=0.3)
        
        # Add a main title
        plt.suptitle('Population vs. Amenities Relationship', fontsize=16, y=0.98)
        
        # Add a source note at the bottom of the figure
        fig.text(0.5, 0.01, 'QSM Japan Analysis', ha='center', fontsize=10)
        
        # Adjust the layout
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the suptitle
        
        # Save the figure
        if output_dir is None:
            save_figure(fig, 'population_amenities_scatter.png')
        else:
            fig.savefig(os.path.join(output_dir, 'population_amenities_scatter.png'), dpi=300, bbox_inches='tight')
        
        plt.close(fig)
        
        print("Population vs. amenities scatter plots created successfully.")
    
    except Exception as e:
        print(f"Error creating population vs. amenities scatter plots: {str(e)}")

def create_time_series(final_gdf, output_dir=None):
    """
    Create time series plots of key metrics.
    
    Args:
        final_gdf: GeoDataFrame with model results
        output_dir: Directory to save the figure (optional)
    """
    print("Creating time series plots...")
    
    # Define the years to include
    years = [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010]
    
    # Create a figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Set the figure title
    fig.suptitle('Time Series of Key Metrics', fontsize=16)
    
    # Flatten the axes array for easier indexing
    axes = axes.flatten()
    
    # Plot 1: Mean Population
    mean_population = [final_gdf[f'Population_{year}'].mean() for year in years]
    axes[0].plot(years, mean_population, marker='o')
    axes[0].set_title('Mean Population')
    axes[0].set_xlabel('Year')
    axes[0].set_ylabel('Population')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Mean Wage
    mean_wage = [final_gdf[f'Wage_{year}'].mean() for year in years]
    axes[1].plot(years, mean_wage, marker='o', color='orange')
    axes[1].set_title('Mean Wage')
    axes[1].set_xlabel('Year')
    axes[1].set_ylabel('Wage')
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Mean Productivity
    mean_productivity = [final_gdf[f'A_{year}'].mean() for year in years]
    axes[2].plot(years, mean_productivity, marker='o', color='green')
    axes[2].set_title('Mean Productivity (A)')
    axes[2].set_xlabel('Year')
    axes[2].set_ylabel('Productivity')
    axes[2].grid(True, alpha=0.3)
    
    # Plot 4: Mean Amenities
    mean_amenities = [final_gdf[f'u_{year}'].mean() for year in years]
    axes[3].plot(years, mean_amenities, marker='o', color='purple')
    axes[3].set_title('Mean Amenities (u)')
    axes[3].set_xlabel('Year')
    axes[3].set_ylabel('Amenities')
    axes[3].grid(True, alpha=0.3)
    
    # Adjust the layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the suptitle
    
    # Save the figure
    if output_dir is None:
        save_figure(fig, 'time_series.png')
    else:
        fig.savefig(os.path.join(output_dir, 'time_series.png'), dpi=300, bbox_inches='tight')
    
    plt.close(fig)
    
    print("Time series plots created successfully.")

def generate_all_visualizations(final_gdf=None, years=None):
    """
    Generate all visualizations.
    
    Args:
        final_gdf: GeoDataFrame with model results (optional)
        years: List of years to visualize (optional)
    """
    print("Generating all visualizations...")
    
    try:
        # Load the model results if not provided
        if final_gdf is None:
            try:
                final_gdf = pd.read_csv(get_results_path('model_results.csv'))
                
                # Convert to GeoDataFrame
                try:
                    geometry = gpd.GeoSeries.from_wkt(final_gdf['geometry'])
                    final_gdf = gpd.GeoDataFrame(final_gdf, geometry=geometry, crs='epsg:2451')
                except Exception as e:
                    print(f"Warning: Could not convert to GeoDataFrame. Error: {str(e)}")
                    print("Some functionality may be limited.")
            except Exception as e:
                print(f"Error loading model results: {str(e)}")
                return
        
        # Define the years to visualize if not provided
        if years is None:
            years = [1975, 1990, 2010]
        
        # Create maps
        create_maps(final_gdf, years)
        
        # Create quantile maps for each year
        for year in years:
            create_quantile_maps(final_gdf, year)
        
        # Create population vs productivity scatter plots
        create_population_productivity_scatter(final_gdf, years)
        
        # Create population vs amenities scatter plots
        create_population_amenities_scatter(final_gdf, years)
        
        # Create time series plots
        create_time_series(final_gdf)
        
        print("All visualizations generated successfully.")
    
    except Exception as e:
        print(f"Error generating visualizations: {str(e)}")

if __name__ == "__main__":
    # Generate all visualizations
    generate_all_visualizations()
    
    print("Visualization completed successfully.") 