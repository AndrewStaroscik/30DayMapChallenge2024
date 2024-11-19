# #30DayMapChallenge Day 19 - Typography

## Process

###  Data
Last name frequency is from the [2010 Census](https://www.census.gov/topics/population/genealogy/data/2010_surnames.html)

### Map shape

The contiguous US polygon was extracted from the natural earth 110m cultural shp file and the python package [Rasterio](https://rasterio.readthedocs.io/en/latest/index.html) was used to create the mask for the word cloud

### Word Cloud

The word cloud was generated with [WordCloud](https://amueller.github.io/word_cloud/index.html) using the the Rasterio mask. 

