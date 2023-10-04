from mastodon import Mastodon
import random
from pathlib import Path
import os
import re
from dotenv import load_dotenv
import sys
import requests
from datetime import datetime, timezone
import json


load_dotenv()

def debug(text):
    #print(text)
    pass

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

print("-------")

if (len(sys.argv)!=2 and len(sys.argv)!=3):
    print('ERROR: Wrong number of arguments.\nUsage: python picture-bot.py <imageFolder> <doIt[optional]>)')
    sys.exit()

#these values are read from a file called .env  (see README.MD)
bluesky_handle = os.getenv("BLUESKY_HANDLE")
bluesky_app_password = os.getenv("BLUESKY_APP_PASSWORD")
HASHTAGS = os.getenv("HASHTAGS")


errorMessage = 'Create a .env file like this:\BLUESKY_HANDLE=<your handle here>\BLUESKY_APP_PASSWORD=<your bluesky password here>'
if bluesky_handle is None:
    print('ERROR: No bluesky_handle found. ')
    print(errorMessage)
    sys.exit()
    
if bluesky_app_password is None:
    print('ERROR: No bluesky_app_password found. ')
    print(errorMessage)
    sys.exit()

dir = sys.argv[1] 

if not os.path.isdir(dir):
    print('ERROR: No valid directory: ' + dir)
    sys.exit()   

def transformFilename(f):
    if str(f).endswith('__1'):
        f = str(f).replace('__1', '');
    pattern = '(?P<prefix>.*)(?P<year>[0-9][0-9][0-9][0-9])-(?P<month>[0-9][0-9])(?P<postfix>.*)';
    m = re.compile(pattern).match(str(f));
    if m is None:
        return f
    f = m.group('prefix') + ' ' + str(int(m.group('month'))) + '/' + m.group('year') + ' ' + m.group('postfix');
    f = str(f).replace('  ', ' ');
    f = str(f).replace('_', ' ');
    f = str(f).strip();
    return f;




doIt = False
doIt = True

if len(sys.argv)==3:
    doIt = (sys.argv[2] == 'doIt')
    
RED_HEART = '\u2764';

statusText = ''

fileList = list(Path(dir).rglob("*.[jJ][pP][gG]"))

for file in list(fileList):
    #print('checking file ' + file.stem)
    if file.stem.endswith('__2') or file.stem.endswith('__3') or file.stem.endswith('__4'):
        fileList.remove(file)
        #print('removed')
    else:
        #print('ok')
        pass

debug(str(len(fileList)) + ' valid files found.');
if len(fileList)==0:
    print('ERROR: no files found in "' + dir + '"')
   
statusText = statusText[0:400]     

validfFileFound = False;
fileToUse = None;

retries = 0
while not validfFileFound:
    retries = retries+1
    rand = random.randint(0, len(fileList)-1)
    randomFile = fileList[rand]
    debug('file: ' + str(randomFile))    
    filenameUsed = str(randomFile) + '.usedbsky' + ('.real' if doIt else '.sim');
    debug('filenameUsed: ' + str(filenameUsed))
    if os.path.isfile(filenameUsed):
        debug('file was already used!');
        fileList.remove(randomFile);
        debug('Files for selection: ' + str(len(fileList)));
        continue;
    try:
        open(filenameUsed, 'w').close()
    except OSError:
        debug('Failed creating the file')
    else:
        debug('File created')
    validfFileFound = True
    fileToUse = randomFile

debug('retries: ' + str(retries))
debug('validFile: ' + fileToUse.stem)
debug('transformed: ' + transformFilename(fileToUse.stem))

statusText = transformFilename(fileToUse.stem);

filenamesToUse = []
if (fileToUse.name.endswith('__1.jpg')  
    or fileToUse.name.endswith('__2.jpg')
    or fileToUse.name.endswith('__3.jpg')
    or fileToUse.name.endswith('__4.jpg')):
    
    debug(str(fileToUse))
    filenameWithoutNumber = str(fileToUse)[:len(str(fileToUse))-7];
    debug('filenameWithoutNumber: ' + filenameWithoutNumber);
    
    for suffix in ['__1.jpg','__2.jpg','__3.jpg','__4.jpg']:
        newFile = filenameWithoutNumber + suffix;
        if os.path.isfile(newFile):
            filenamesToUse.append(newFile);
    for f in filenamesToUse:
        debug('  ' + f)
    

else:
    filenamesToUse.append(str(fileToUse));


statusText = statusText + ' ' + RED_HEART

if HASHTAGS is not None:
    statusText = statusText + "\n" + HASHTAGS

def postImage(filenamesForMastodon: list[str], statusTextForMastodon: str):

    mediaIds = []

    if doIt:
        
        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            timeout=10,
            json={"identifier": bluesky_handle, "password": bluesky_app_password},
        )
        resp.raise_for_status()
        session = resp.json()
        
        imgNumber = 0
        for f in filenamesForMastodon:
            basename = os.path.basename(f)
            print("basename: " + basename)
            imgNumber = imgNumber + 1
            #read image file:
            with open(f, "rb") as f:
                img_bytes = f.read()

            # this size limit is specified in the app.bsky.embed.images lexicon
            if len(img_bytes) > 1000000:
                raise Exception(
                    f"image file size too large. 1000000 bytes maximum, got: {len(img_bytes)}"
                )            
            #post image:
            success = False
            tries = 0
            while not success:
                tries = tries + 1
                try:
                    print("Trying to upload image [" + basename + "] - retries: " + str(tries))
                    resp = requests.post(
                        "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
                        timeout=5,
                        headers={
                            "Content-Type": "image/jpg",
                            "Authorization": "Bearer " + session["accessJwt"],
                        },
                        data=img_bytes,
                    )
                    resp.raise_for_status()
                    blob = resp.json()["blob"]
                    success = True
                    debug("Image posted successfully")
                    debug(blob)
                    mediaId = {
                        "alt": statusText + " Datei " + str(imgNumber),
                        "image": blob,
                        "size": len(img_bytes),
                    }   
                    debug("mediaId: " + str(mediaId))
                    mediaIds.append(mediaId)
                except Exception as e: # work on python 3.x
                    print('Failed: %s', e)                    
                    pass            
    
        debug(mediaIds)
    
    
        post = {
            "$type": "app.bsky.feed.post",
            "text": statusText ,
            "createdAt": now,
        }
        post["embed"] = {
            "$type": "app.bsky.embed.images",
            "images": mediaIds
        }
        
        
        json_formatted_str = json.dumps(post, indent=2)
        debug(json_formatted_str)        
        
        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": "Bearer " + session["accessJwt"]},
            json={
                "repo": session["did"],
                "collection": "app.bsky.feed.post",
                "record": post,
            },
        )
        debug(json.dumps(resp.json(), indent=2))
        resp.raise_for_status()        

if not doIt:
    print('=== SIMULATION MODE ONLY ====== ')
print('Posting Status: ' + ('' if doIt else ' (simulation mode)'))
print(statusText)

postImage(filenamesToUse, statusText)

print("-------")

    



