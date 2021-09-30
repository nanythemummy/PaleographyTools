import re, os.path, argparse, unicodedata
from cltk.corpus.egyptian.transliterate_mdc import mdc_unicode


def getUnicodeForMdCTranslitString(inputstring):
    inunicode=inputstring.encode().decode("utf-8")
    uc= mdc_unicode(inunicode)
    print(f"Result is {uc}")
    return uc

def transliterationSort(listofstrings):
    #takes a list of strings and sorts it in the order of appearance of the items in the hieroglyphic egyptian dictionary.
    #this expects a list or dict keyed by a unicode transliteration char, not mdc.
    alphabet=[' ','.', '⸗', '-', 'ꜣ', 'i', '҆', 'i', '҆', 'j', 'y', 'ꜥ', 'w', 'b', 'p', 'f', 'm', 'n', 'r', 'h', 'ḥ', 'ḫ', 'ẖ', 's',
     'z', 'š', 'q', 'K', 'k', 'g', 't', 'ṯ', 'd', 'ḏ']
    awithnums = ["{num}".format(num=n) for n in range(0, 9)] + alphabet
    weights = [n for n in range(0,len(awithnums))]
    alphabethash=dict(zip(awithnums,weights))
    retlist= sorted(listofstrings, key=lambda word: [alphabethash[a.lower()] for a in word])
    return retlist

def getUnicodeFromGardinerString(inputstring):
    listofchars = inputstring.split('-')
    outputchars=[]
    
    #unicode remembers each gardiner character as a part of the name of the glyph, but it is
    #in a slightly different format wherein the glyph number is padded with up to 2 zeroes.
    #While the variant is given as a lowercase letter in the signlist in JSESH, it's stored
    #as a capital here.

    patt = re.compile('(?P<category>[A-Za-z]{1,3})(?P<glyph>[0-9]{1,3})(?P<variant>[a-z]+){0,1}')
    for item in listofchars:
        try:
            res=patt.match(item).groupdict()
        except AttributeError  as e:
            print(f"received attribute error {e}. \nPerhaps you ought to make sure \"{item}\" is a code of format Xy00z. (See Readme)")
            raise e

        res["variant"]='' if not res["variant"] else res["variant"]
        #prepare the normalized name of the glyph for searching the unicode db.
        gcode=''.join([res["category"],res["glyph"].zfill(3),res["variant"].upper()])
        unicodesearch = f"EGYPTIAN HIEROGLYPH {gcode}"
        try:
            unicodeglyph=unicodedata.lookup(unicodesearch)
        except KeyError as e:
            print(f"{item} does not seem to have been a real Gardiner Signlist Code. Error received:{e} ")
            raise e

        if unicodeglyph:
            outputchars.append(unicodeglyph)
    finalunicode=''.join(outputchars)
    print(f"result is {finalunicode}")
    return finalunicode

def getGardinerStringFromUnicode(characters):
    #Given a unicode hieroglyph, get the Gardiner Signlist Code. If multiple characters are provided, this will return
    #a comma seperated string.

    gardinersigns=[]
    patt = re.compile('EGYPTIAN HIEROGLYPH (?P<category>[A-Za-z])0+(?P<glyph>[1-9]{1,3})(?P<variant>[a-z]{0,1})')
    for char in list(characters):
        udata = unicodedata.name(char)
        res=patt.match(udata).groupdict()
        if res['variant']:
            res['variant']=res['variant'].lower()
        else:
            res['variant']=''
        code = f"{res['category']}{res['glyph']}{res['variant']}"
        gardinersigns.append(code)
    gsigns=",".join(gardinersigns)
    return gsigns

def parseGetUnicodeFromGardinerString(args):
    return getUnicodeFromGardinerString(args.inputstring)

def parseGetTranslitForMdCString(args):
    return getUnicodeForMdCTranslitString(args.inputstring)


if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="Gardiner Tools")
    subparsers = parser.add_subparsers(help='Sub-command help')

    gtouparser=subparsers.add_parser('get-glyph', help="Get unicode values for a list of - seperated gardiner codes")
    gtouparser.add_argument("inputstring", help="The string of - seperated gardiner codes you want as unicode.")
    gtouparser.set_defaults(func=parseGetUnicodeFromGardinerString)
    gtranslitparser=subparsers.add_parser('get-translit', help="Get the translation font unicode equivalent of an MdC string. ")
    gtranslitparser.add_argument("inputstring",help="A string in Manuel de Codage.(MdC)")
    gtranslitparser.set_defaults(func=parseGetTranslitForMdCString)
    galphabettest=subparsers.add_parser("test_alphabet", help="test alphabet")
    galphabettest.set_defaults(func=transliterationSort(listofstrings=['ꜥhꜥ','ꜣšꜣ','šri҆','ḫ.t nb.t nfr.t','mḥy.t',' ꜣqꜥ','ni҆w.ty']))
    args = parser.parse_args()
    if hasattr(args,"func"):
        args.func(args)
    else:
        parser.print_help()