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

### Note on File Paths

The notebook uses relative paths to access data files. All data files should be placed in the `Japan/Data` directory as described in the "How to Obtain the Data" section. The notebook will automatically look for data files in the correct location relative to the notebook's location.

## Data Files

Note: Large data files are not included in this repository due to size constraints. The required data files include:
- Population data (1970-2010)
- Wage data (1975-2014)
- Shapefiles for Japanese prefectures

### How to Obtain the Data

To run this analysis, you'll need to download the following data:

1. **Population Data (1970-2010) and Wage Data (1975-2014)**
   - Source: [Cabinet Office of Japan](https://www5.cao.go.jp/keizai-shimon/kaigi/special/future/keizai-jinkou_data.html)
   - This official government website provides comprehensive municipal-level data for Japan, including:
     - Population data from the Census (人口総数：総務省『国勢調査』)
     - Economic indicators including wage data
   - Download the Excel files for population and wage data
   - Save as `population 1970 2010.xls` and `average wage 1975_2014.xls` in the `Japan/Data` directory

2. **Shapefiles for Japanese Prefectures**
   - Source: [National Land Numerical Information](https://nlftp.mlit.go.jp/ksj/index.html) (MLIT)
   - Download the administrative boundary data for Japan
   - Create directories `Japan/Data/jpn1975` and `Japan/Data/jpn2014`
   - Extract the shapefiles into these directories

If you need assistance accessing these data sources, please contact the repository owner.

## Model Details

The Quantitative Spatial Model (QSM) used in this analysis is based on the equilibrium conditions from Allen and Arkolakis (2014). The model:

1. Processes data for years 1975-2010 in 5-year intervals
2. Calculates productivity and amenity values for each prefecture
3. Analyzes spatial patterns and their evolution over time
4. Visualizes results using maps and charts


