import os
import numpy as np
import pandas as pd
import geopandas as gpd
import jaconv
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import contextily as ctx

def safe_process_japanese_text(value):
    """
    Convert half-width Japanese characters to full-width.
    
    Args:
        value: The text to process
        
    Returns:
        Processed text or original value if not a string
    """
    if isinstance(value, str):
        value = jaconv.h2z(value)  # Convert half-width to full-width
    return value  # Return the processed value or the original value if it's not a string

def replace_small_ke_with_big_ke(text):
    """
    Replace small ヶ with big ケ in Japanese text.
    
    Args:
        text: The text to process
        
    Returns:
        Processed text or original value if not a string
    """
    if isinstance(text, str):
        return text.replace('ヶ', 'ケ')
    return text

def get_project_root():
    """
    Get the absolute path to the project root directory.
    
    Returns:
        str: Absolute path to the project root
    """
    # This assumes the script is in Japan/Scripts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    japan_dir = os.path.dirname(script_dir)
    return os.path.dirname(japan_dir)

def get_japan_dir():
    """
    Get the path to the Japan directory.
    
    Returns:
        str: Path to the Japan directory
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)

def get_data_path(relative_path=''):
    """
    Get the path to a data file.
    
    Args:
        relative_path: Path relative to the Japan/Data directory
        
    Returns:
        str: Path to the data file
    """
    japan_dir = get_japan_dir()
    data_dir = os.path.join(japan_dir, 'Data')
    if relative_path:
        return os.path.join(data_dir, relative_path)
    return data_dir

def get_results_path(relative_path=''):
    """
    Get the path to a results file.
    
    Args:
        relative_path: Path relative to the Japan/Results directory
        
    Returns:
        str: Path to the results file
    """
    japan_dir = get_japan_dir()
    results_dir = os.path.join(japan_dir, 'Results')
    
    # Create the results directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    if relative_path:
        return os.path.join(results_dir, relative_path)
    return results_dir

def save_figure(fig, filename):
    """
    Save a figure to the results directory.
    
    Args:
        fig: The matplotlib figure to save
        filename: The filename to save the figure as
    """
    results_path = get_results_path(filename)
    
    # Save the figure
    fig.savefig(results_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {results_path}") 