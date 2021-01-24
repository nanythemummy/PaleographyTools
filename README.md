# PaleographyTools
Tools for creating paleographies for ancient texts, and comparative image libraries.
## Purpose
The purpose of these scripts is to aid in the creation of Paleographies similar to Georg Moeller's Hieratic Paleography, "Hieratische Palaeographie", wherein a series of images are attached to a single key and can be displayed in comparison with other images of that same key as needed. The purpose of the project is to help in creating paleographies that are readable by people for the purpose of study, not to train machines to read glyphs.
## Scripts
### snip_characters.py
####  Purpose 
Given a folder of JSON file in coco format, this script uses coordinates supplied by the json to "cut" delineated areas from a large image. The result is a series of thumbnails, each containing an area of interest, which are mapped to labels supplied by the original JSON files in a new JSON file, which can be used to insert references to the images in database.

#### Requirements
1. Python 3.x
2. Shapely
3. Pillow
4. cltk (Classical Languages Toolkit)
5. Fonts supporting Unicode Egyptian Hieroglyphs and Unicode Transliteration symbols. Possibilities are the New Gardiner Truetype font by Mark-jan Nederhof, and the Jsesh font. Google Noto also has good fonts for glyphs.
Various transliteration fonts can also be found on the JSESH page: https://jsesh.qenherkhopeshef.org/varia/transliteration

(And their depencdencies as noted in the requirements.txt.)

#### Usage
After working with this script, I've come to the conclusion that it is more useful and efficient
that it work on a batch of files and have fewer parameters passed in from the command line. In order to use it,
use Makesense.ai to generate a coco json file: Import the picture you want to build a comparative library of images from,
use the polygon tool to select those areas you want to compare, and give them a label. This script supports three types of comparative image libraries: Egyptological Paleography, Egyptological Orthography, and Iconography. The difference is in the labels given to the areas.
If you are building an Egyptological paleography, the label should be the gardiner sign code for the character you are highlighting: A2 for 𓀁 (seated man with hand to mouth), etc.
If you are building an egyptological orthography, the label should be in Manuel de Codage. If you are building an Iconography database,
the label is simply a descriptive string.


In Makesense.ai, export your data to a COCO JSON file.
You need to build the following directory structure and save your json file in the folder according to the type of
paleography you are building with it. For example, sample json describes a picture that I annotated with descriptive labels
so I put it in the json/[NAME OF YOUR PALEOGRAPHY]/Iconography folder. The folder names tell the script what type of comparative image library you are building, so you don't have to 
pass in a parameter.
Save the image that you are pulling the annotations from to the reference_images folder. **You must make these directories on your own**,
The rest will be created for you.
You can create multiple files, and they will all be processed when you run the script.

The script uses the json files to compile a master json file of all of the annotations in files under the json/ folder. 
For each annotation from an image, it will cut out the area  selected in makesense.ai, and create a new file with just that selected area. 
This will be saved under "Thumbnails." The label given to the area in Makesense.ai will be converted to unicode hieroglyphs if it is labeled as a
Gardiner sign list code and the json which contains it is placed in the Paloegraphy folder. If the Json containing the annotations
is placed in the Orthography folder, the label will be converted to unicode transliteration characters.

The master JSON file is named with a timestamp and saved off to "output json", while the original COCO json file
is moved to the "processed_json folder"

````
.
├── Consts.py
├── GardinerTool.py
├── LICENSE
├── README.md
├── json
│   └── [NAME OF YOUR PALEOGRAPHY]
│       ├── Iconography
│       │   └── sample.json
│       ├── Orthography
│       └── Paleography
├── outputjson
├── processed_json
├── reference_images
│   └── REFERENCE_IMAGE.jpg
├── requirements.txt
├── snip_characters.py
└── thumbnails
    └── sample-REFERENCE_IMAGE_Iconography_CFF9E.png


````
###Running the Script:

When you have your directories set up, your original images stored in the reference_images folder,  and your COCO Json files created and stored in the appropriate directory,

```
Python snip_characters.py
```

From here, you can use the master json file to insert the thumbnails of the images in a database of your chosing.

####Known Issues and Caveats
#####Requirements for Gardiner Codes
If you are using Gardiner Codes as your labels for an egyptological paleography, note that the codes must be in the format:Xy00z where X is an uppercase letter, y is an optional lowercase letter, the zeros are numbers (the second of which is optional) and the final z is an optional letter for a variant. If you enter something that isn't in this format, you will get an exception.

####I don't like the size of the resulting images
Image sizes can be changed in the Consts.py file, where the following are tuples of height and width.
````
    ICONOGRAPHY_SAMPLE_SIZE=(300,300)
    PALEOGRAPHY_SAMPLE_SIZE=(75,75)
    ORTHOGRAPHY_SAMPLE_SIZE=(100,100)
````
Some of the directories can also be changed in this file.

####The script is very slow at snipping large areas from the original image.
Known issue. The script uses Pillow and uses the get_pixel function to check if every pixel in an area is inside the selected
polygon. Python's lists are not the best datastructure for this, and the method is kind of slow anyway. I'm currently using
numpy's arrays to implement a faster version, but it's not a high priority.

####The master json file is in unicode.
The master json file needs to be in unicode to handle using glyphs as labels for areas. Originally, I was doing this on the backend script which 
imported the data into the database for my research, but it was just another set of command parameters for me to type
and now that it's part of this script, I can share the functionality with you! Just make sure you have the right fonts, and that whatever code you write to handle the master json file can deal with unicode.

### GardinerTool.py
####Purpose 
To help with the process of converting ascii representations of glyphs and transliterations into Unicode.

####Requirements
1. cltk (Classical Languages Toolkit)
2. The requirements and unicode fonts mentioned above.

####Usage
There are two scripts: get-glyph and get-translit One converts a gardiner signlist code into a unicode glyph, the other converst an ASCII Manuel de Codage string into transliteration characters in unicode.
#####get-glyph
````
python GardinerTool.py get-glyph B1
result is [unicode hieroglyph not supported in readme apparently]
````
#####get-translit
````
python GardinerTool.py get-translit "Ink sAH=k"
Result is [unicode translit characters not supported in readme apparently]
````
