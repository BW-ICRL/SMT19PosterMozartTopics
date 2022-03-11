# Musical Topics in Mozart’s Piano Sonatas: A Data Science Approach
## An Interactive Poster Presented at [SMT19](https://societymusictheory.org/archives/events/meeting2019)

This is a dash-based poster that we used to present our work to the Society of Music Theory 2019 meeting in Columbus, Ohio

## Getting Started
Clone the git repository, then install the requirements with pip

```
git clone https://github.com/BW-ICRL/SMT19PosterMozartTopics.git
cd SMT19PosterMozartTopics
pip install -r requirements.txt
```
Run the app
```
python app.py
```
Open a web browser to http://127.0.0.1:8050/

## About this app
This dash app displays a variety of information related to the use of Topics in the first movements of Mozart's Piano Sonatas. Choosing one or more movement to explore will alter the various visualizations.

## Data File Description
The primary data analysis of the first movements of these selected Mozart piano sonatas can be found in the file assets/Movement1ExtractedDataWithSecondaryTopics.xlsx Here is a partial description of the columns of this data:

- Sonata--K number for the sonata (e.g., K279-1 indicates movement of of sonata K279)<br>
- Indetifier--A label for the measures being analyzed (e.g., K279-1[1-4] refers to measures 1-4 of movement 1 of K279)<br>
- Part--Indicates the part (section) of the movement: expostion (e), development, and recapitulation (r) along with primary, transition, secondary, and closing where applicable<br>
- starting measure--The beginning measure number of this chunk being analyzed<br>
- ending measure--The ending measure number of the chunk being analyzed<br>
- Topic--The primary topic illustrated in this particular chunk<br>
- Secondary Topic--If a secondary topic is present, this column lists that secondary topic<br>
- weighting--How dominant is each topic (primary and secondary): 
  - 'a' 100% Primary
  - 'b' 70% Primary 30% Secondary 
  - 'c' 50% Primary 50% Secondary
- length--how long, in measures, is this chunk<br>
- The remaining columns are a variety of features extracted from each chunk using the [Music21](https://web.mit.edu/music21/) feature extractors [native](https://web.mit.edu/music21/doc/moduleReference/moduleFeaturesNative.html) and [jSymbolic](https://web.mit.edu/music21/doc/moduleReference/moduleFeaturesJSymbolic.html)
