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


def get_filename(name, imagefile, annotation_id, category, outpath):
    imagename = os.path.splitext(imagefile)[0] # get the second part of the path, which is the filename
    # string might have translit characters in it, so we need to strip that out.
    category = "".join(c for c in category if c.isalnum())
    return f"{outpath}{name}-{imagename}_{category}_{annotation_id}.png"


# accessing the pixel array through pillow is slow, but works.
def copy_slow(inputimg, outputimg, bbox, region):
    pixels = inputimg.load()
    outpixels = outputimg.load()
    for bx in range(0, bbox["w"]):
        for by in range(0, bbox["h"]):
            pt = Point(bbox["x"] + bx, bbox["y"] + by)
            if region.contains(pt):
                outpixels[bx, by] = pixels[bx + bbox["x"], by + bbox["y"]]


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


def process_image(artefactname, inputjson, outputjson, imageinfo, outputdir, thumbsize):
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
            cat_id = None
            cat_label = None
            for category in inputjson["categories"]:
                if category["id"] == annotation["category_id"]:
                    cat_id = category["id"]
                    cat_label = category["name"]
                    break
            # generate a unique-ish filename for the new image thumbnail.
            outname = get_filename(
                artefactname, imagename, annotation["id"], cat_label, outputdir
            )
            process_area(imgrgba, annotation, outname, thumbsize)
            area_entry = {"thumbnail": outname, "origin": imagename, "label": cat_label}
            outputjson.append(area_entry)


def init(args):
    outjson = {"artefact": args.name, "paleography": []}
    cocojson = {}
    thumbsize = [200, 200] if not args.t else [args.t[0], args.t[1]]
    with open(args.input) as f:
        cocojson = json.load(f)
    for item in cocojson["images"]:
        process_image(
            outjson["artefact"],
            cocojson,
            outjson["paleography"],
            item,
            args.output,
            thumbsize,
        )
    timestamp=datetime.now().strftime("%m-%d-%y_%H-%M")
    outfilename=f"{args.name}_{timestamp}.json"
    with open(outfilename,'w') as f:
        json.dump(outjson,f)
    
    


parser = argparse.ArgumentParser()
parser.add_argument("input", help="Path of Input JSON file.")
parser.add_argument("output", help="Path where the output images ought to go.")
parser.add_argument("name", help="What artifact is this associated with?")
parser.add_argument(
    "--t",
    "--thumbnail",
    help="Override default thumbnail size of 200x200",
    nargs=2,
    type=int,
)
args = parser.parse_args()
init(args)
