# PaleographyTools
Tools for creating paleographies for Ancient Texts
## Purpose
The purpose of these scripts is to aid in the creation of Paleographies similar to Georg Moeller's Hieratic Paleography, "Hieratische Palaeographie", wherein a series of images are attached to a single key and can be displayed in comparison with other images of that same key as needed. The purpose of the project is to help in creating paleographies that are readable by people for the purpose of study, not to train machines to read glyphs.
## Scripts
### snip_characters.py
####  Purpose 
Given a JSON file in coco format, this script uses coordinates supplied by the json to "cut" delineated areas from a large image. The result is a series of thumbnails, each containing an area of interest, which are mapped to labels supplied by the original JSON file in a new JSON file, which can be used to insert references to the images in database.
#### Requirements
1. Python 3.x
2. Shapely
3. Pillow
(And their depencdencies as noted in the requirements.txt.)
#### Usage
Generate the COCO JSON file using a labeling tool for training machine learning algorithms. The file json/sample.json was generated for the image reference_imates/sample.jpg using the program [Make-Sense](https://makesense.ai). The github for this project can be found here: [SkalskiP's Make-Sense on Github](https://github.com/SkalskiP/make-sense). Label the segments with the value that you want to key them with. Here, I've given the segments Manuel de Codage names, but Gardiner codes might also be useful. Export to a JSON file, and chose the COCO format. 
To see the options for the script, run it with the --help option.
```
usage: snip_characters.py [-h] [--t T T] input output name

positional arguments:
  input                 Path of Input JSON file.
  output                Path where the output images ought to go.
  name                  What artifact is this associated with?

optional arguments:
  -h, --help            show this help message and exit
  --t T T, --thumbnail T T
                        Override default thumbnail size of 200x200
```
Here's an example which generated thumbnails of size 50 pixels by 50 pixels:
```
python snip_characters.py json/sample.json thumbnails/ canopic_box --t 50 50
```
Note that for now, the original images need to be in the reference_images folder. This will probably be fixed later.

