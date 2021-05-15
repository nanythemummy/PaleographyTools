# This script loads a coco json file of an annotated 2d image, and generates thumbnails for each selected area. Annotated
# json can be generated with https://www.makesense.ai/ and exported to coco json. The json file goes in the json folder
# the image it references goes in the image folder, and the script is run with the json as a parameter. The result is
# a collection of small thumbnails taken from the picture based on the selection, and a json mapping the annotation to
# each file. These can then be added to a paleography database where a database table might contain characters, their meanings
# and a link to the original image.

import os.path, json
import argparse
from datetime import datetime
from PIL import Image
from shapely.geometry import Point
from shapely.geometry import Polygon
from Consts import Consts
from GardinerTool import *
import random, string


def get_filename(name, imagefile, category):
    outpath=os.path.join(os.getcwd(),Consts.OUTPUT_THUMBNAIL_DIR)
    imagename = os.path.splitext(imagefile)[0] # get the second part of the path, which is the filename
    # string might have translit characters in it, so we need to strip that out.
    uniquish_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase+string.digits) for _ in range(5))
    category = ''.join(c for c in category if c.isalnum())
    return os.path.join(outpath,f"{name}-{imagename}_{category}_{uniquish_id}.png")


# accessing the pixel array through pillow is slow, but works.
def copy_slow(inputimg, outputimg, bbox, region):
    pixels = inputimg.load()
    outpixels = outputimg.load()
    for bx in range(0, bbox["w"]):
        for by in range(0, bbox["h"]):
            pt = Point(bbox["x"] + bx, bbox["y"] + by)
            if region.contains(pt):
                try:
                    outpixels[bx, by] = pixels[bx + bbox["x"], by + bbox["y"]]
                except IndexError as e:
                    print(f"Error with boundingbox: Did you rotate the image and forget to save properly? {bbox}")
                    raise e




# This function takes a handle to a large image and an array of segmentation values from a cocojson file. It will copy the area specified by
# the paths in the segmentation values and paste them into a thumbnail image with the outputfile name.
def process_area(imagehandle, areainfo, outputfilename, thumbsize):
    segs = areainfo["segmentation"][0]
    # merge every even item(x) with every odd one(y)ls. Syntax for slicing is list[start:end:stride]
    coords = [(round(x[0]), round(x[1])) for x in zip(segs[::2], segs[1::2])]
    bbox = {
        "x": round(areainfo["bbox"][0]),
        "y": round(areainfo["bbox"][1]),
        "w": round(areainfo["bbox"][2]),
        "h": round(areainfo["bbox"][3]),
    }
    region = Polygon(coords)
    outimg = Image.new("RGBA", (bbox["w"], bbox["h"]))
    copy_slow(imagehandle, outimg, bbox, region)
    outimg.thumbnail((thumbsize[0], thumbsize[1]))
    outimg.save(f"{outputfilename}")

def getLabelForType(jsonlabel,type):
    if type==Consts.PALEOGRAPHY_TYPE:
        return getUnicodeFromGardinerString(jsonlabel)
    elif type==Consts.ORTHOGRAPHY_TYPE:
        return getUnicodeForMdCTranslitString(jsonlabel)
    else: #iconography
        return jsonlabel

def getThumbsizeForType(type):
    if type==Consts.PALEOGRAPHY_TYPE:
        return Consts.PALEOGRAPHY_SAMPLE_SIZE
    elif type==Consts.ICONOGRAPHY_TYPE:
        return Consts.ICONOGRAPHY_SAMPLE_SIZE
    else:
        return Consts.ORTHOGRAPHY_SAMPLE_SIZE

def process_image(artefactname, inputjson, outputjson, imageinfo, type):
    imagename, w, h, iid = (
        imageinfo["file_name"],
        imageinfo["width"],
        imageinfo["height"],
        imageinfo["id"],
    )
    # get the information for the annotation from the json file.

    with Image.open(f"reference_images/{imagename}") as img:
        imgrgba = img.convert("RGBA")
        for annotation in inputjson["annotations"]:
            if not annotation["image_id"] == iid:
                continue
            # find the category for it.
            cat_label = None
            for category in inputjson["categories"]:
                try:
                    if category["id"] == annotation["category_id"]:
                        cat_label = getLabelForType(category["name"], type)
                        break
                except KeyError as e:
                    print(f"error{e} : Did you forget to assign a label to an annotation?")
                    raise e
            # generate a unique-ish filename for the new image thumbnail.
            outname = get_filename(
                artefactname, imagename, type
            )
            process_area(imgrgba, annotation, outname, getThumbsizeForType(type))
            area_entry = {"thumbnail": outname, "origin": imagename, "label": cat_label}
            outputjson.append(area_entry)

def processJSONFiles(dir,outjson,artifactname,type):
    with os.scandir(dir) as it:
        for f in it:
            if os.path.isfile(f):
                fullpath=os.path.join(dir,f)
                extension=os.path.splitext(os.path.join(fullpath))[1]
                if extension == ".json":
                    with open(fullpath) as jsonfile:
                        cocojson = json.load(jsonfile)
                        for item in cocojson["images"]:
                            process_image(artifactname,cocojson,outjson,item,type)
                    outname=os.path.join(os.path.join(os.getcwd(),Consts.USED_JSON_DIRECTORY),f.name)
                    os.rename(fullpath,outname)



def processPaleographyType(dir,outjson,aname):

    types=[Consts.ORTHOGRAPHY_TYPE,Consts.PALEOGRAPHY_TYPE,Consts.ICONOGRAPHY_TYPE]
    with os.scandir(dir) as it:
        for f in it:
            if os.path.isdir(os.path.join(dir, f)):
                if f.name in types:
                    typename=f.name
                    outjson[typename]=[]
                    processJSONFiles(os.path.join(dir,typename),outjson[typename],aname,typename)

def processArtifacts(outjson):
    jsondir = os.path.join(os.getcwd(), "json")
    with os.scandir(jsondir) as it:
        for f in it:
            if os.path.isdir(os.path.join(jsondir,f)):
                artifactname=f.name
                outjson[artifactname] = {}
                processPaleographyType(os.path.join(jsondir, artifactname), outjson[artifactname],artifactname)

def setupDirs():
    current = os.getcwd()
    thumbsdir= os.path.join(current, Consts.OUTPUT_THUMBNAIL_DIR)
    jsondir=os.path.join(current,Consts.OUTPUT_JSON_DIRECTORY)
    usedjsondir=os.path.join(current,Consts.USED_JSON_DIRECTORY)
    if not os.path.exists(thumbsdir):
        os.mkdir(thumbsdir)
    if not os.path.exists(jsondir):
        os.mkdir(jsondir)
    if not os.path.exists(usedjsondir):
        os.mkdir(usedjsondir)

def init():
    setupDirs()
    #process directories
    outjson = {}
    processArtifacts(outjson)
    timestamp=datetime.now().strftime("%m-%d-%y_%H-%M")
    outfilename=f"Paleography_{timestamp}.json"
    outdir = os.path.join(os.path.join(os.getcwd(),Consts.OUTPUT_JSON_DIRECTORY),outfilename)
    with open(outdir,'w') as f:
        json.dump(outjson,f,ensure_ascii=False)
    
    

if __name__=="__main__":
    init()
