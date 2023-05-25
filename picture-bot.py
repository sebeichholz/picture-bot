from mastodon import Mastodon
import random
from pathlib import Path
import os
import re
from dotenv import load_dotenv
import sys

load_dotenv()

if (len(sys.argv)!=2 and len(sys.argv)!=3):
    print('ERROR: Wrong number of arguments.\nUsage: python picture-bot.py <imageFolder> <doIt[optional]>)')
    sys.exit()

#these values are read from a file called .env  (see README.MD)
mastodon_token = os.getenv("MASTODON_TOKEN")
mastodon_url = os.getenv("MASTODON_URL")

errorMessage = 'Create a .env file like this:\nMASTODON_TOKEN=<your token here>\nMASTODON_URL=<your mastodon server url here>'
if mastodon_token is None:
    print('ERROR: No mastodon-token found. ')
    print(errorMessage)
    sys.exit()
    
if mastodon_url is None:
    print('ERROR: No mastodon-URL found. ')
    print(errorMessage)
    sys.exit()

dir = sys.argv[1] #'/Users/sebastian/_TEMP/kultmags/artikel';

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
if len(sys.argv)==3:
    doIt = (sys.argv[2] == 'doIt')

print('doIt: ' + str(doIt))
    
RED_HEART = '\u2764';

doUpload = True;

statusText = ''

mastodon = Mastodon(api_base_url = mastodon_url, 
                    access_token = mastodon_token);

fileList = list(Path(dir).rglob("*.[jJ][pP][gG]"))

print(len(fileList))

for file in list(fileList):
    #print('checking file ' + file.stem)
    if file.stem.endswith('__2') or file.stem.endswith('__3') or file.stem.endswith('__4'):
        fileList.remove(file)
        #print('removed')
    else:
        #print('ok')
        pass

print(str(len(fileList)) + ' files found.');
if len(fileList)==0:
    print('ERROR: no files found in "' + dir + '"')
   
statusText = statusText[0:400]     

validfFileFound = False;
fileToUse = None;

retries = 0
while not validfFileFound:
    retries = retries+1
    print('')
    rand = random.randint(0, len(fileList)-1)
    randomFile = fileList[rand]
    print('file: ' + str(randomFile))    
    filenameUsed = str(randomFile) + '.usedmastodon' + ('.real' if doIt else '.sim');
    print('filenameUsed: ' + str(filenameUsed))
    if os.path.isfile(filenameUsed):
        print('file was already used!');
        fileList.remove(randomFile);
        print('Files for selection: ' + str(len(fileList)));
        continue;
    try:
        open(filenameUsed, 'w').close()
    except OSError:
        print('Failed creating the file')
    else:
        print('File created')
    validfFileFound = True
    fileToUse = randomFile

print('retries: ' + str(retries))
print('validFile: ' + fileToUse.stem)
print('transformed: ' + transformFilename(fileToUse.stem))

statusText = transformFilename(fileToUse.stem);

filenamesToUse = []
if (fileToUse.name.endswith('__1.jpg')  
    or fileToUse.name.endswith('__2.jpg')
    or fileToUse.name.endswith('__3.jpg')
    or fileToUse.name.endswith('__4.jpg')):
    
    print(str(fileToUse))
    filenameWithoutNumber = str(fileToUse)[:len(str(fileToUse))-7];
    print('filenameWithoutNumber: ' + filenameWithoutNumber);
    
    for suffix in ['__1.jpg','__2.jpg','__3.jpg','__4.jpg']:
        newFile = filenameWithoutNumber + suffix;
        if os.path.isfile(newFile):
            filenamesToUse.append(newFile);
    for f in filenamesToUse:
        print('  ' + f)
    

else:
    filenamesToUse.append(str(fileToUse));


mediaIds = []

if doUpload and doIt:
    for f in filenamesToUse:
        m1dict = mastodon.media_post(
            media_file=f, 
            mime_type='image/jpeg', 
            synchronous=True,
            description=Path(f).stem
        );
        mediaIds.append(m1dict.id)

if not doIt:
    print('=== SIMULATION MODE ONLY ====== ')
print('Posting Status: ' + ('' if doIt else ' (simulation mode)'))
print(statusText)

if doIt:
    mastodon.status_post(status=
        statusText + ' ' + RED_HEART
        , media_ids=mediaIds
    );
    



