# Quantitative Spatial Model (QSM) for Japan

This repository contains a Quantitative Spatial Model analysis for Japan, examining spatial economic patterns across Japanese prefectures from 1975 to 2010.

## Project Overview

This project implements a Quantitative Spatial Model based on the framework developed by Allen and Arkolakis (2014). The model analyzes:

- Population and wage data across Japanese prefectures
- Spatial economic patterns and their evolution over time
- Productivity and amenity calculations

## Data

The data directory contains:
- Population data from 1970-2010
- Wage data from 1975-2014
- Shapefiles for Japanese prefectures
- Generated amenities and productivity data

## Code

The main analysis is contained in the Jupyter notebook:
- `Japan/Code/QSM_Japan.ipynb`

## Requirements

- Python 3.x
- Required packages:
  - numpy
  - pandas
  - geopandas
  - matplotlib
  - jaconv
  - contextily

## Results

The model calculates productivity and amenity values for Japanese prefectures, providing insights into spatial economic patterns and their changes over time.

## References

- Allen, T., & Arkolakis, C. (2014). Trade and the Topography of the Spatial Economy. The Quarterly Journal of Economics, 129(3), 1085-1140. 

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/ShizukaInoue/QSM.git
   cd QSM
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. Launch Jupyter Notebook:
   ```
   jupyter notebook
   ```

4. Open `Japan/Code/QSM_Japan.ipynb` to run the analysis.

## Data Files

Note: Large data files are not included in this repository due to size constraints. The required data files include:
- Population data (1970-2010)
- Wage data (1975-2014)
- Shapefiles for Japanese cities

If you need access to these data files, please contact the repository owner.

## Model Details

The Quantitative Spatial Model (QSM) used in this analysis is based on the equilibrium conditions from Allen and Arkolakis (2014). The model:

1. Processes data for years 1975-2010 in 5-year intervals
2. Calculates productivity and amenity values for each prefecture
3. Analyzes spatial patterns and their evolution over time
4. Visualizes results using maps and charts

