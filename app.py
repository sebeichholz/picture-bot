from mastodon import Mastodon
import random
from pathlib import Path
import os
import re
from dotenv import load_dotenv

load_dotenv()

#these values are read from a file called .env  (see README.MD)
mastodon_token = os.getenv("MASTODON_TOKEN")
mastodon_url = os.getenv("MASTODON_URL")

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

dir = '/Users/sebastian/_TEMP/kultmags/artikel';

RED_HEART = '\u2764';

doIt = False;
doUpload = False;

doIt = True;
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

print(len(fileList));

print('remaining fileList: ');
for file in fileList:
    print(' ' + file.stem)
   
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
    filenameUsed = str(randomFile) + '.used' + ('.real' if doIt else '.sim');
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

    '''
    String filenameWithAbsolutePathWithoutNumber = filenameWithAbsolutePath
        .replace("__1.jpg", "")
        .replace("__2.jpg", "")
        .replace("__3.jpg", "")
        .replace("__4.jpg", "");
    
    for (int i=1; i<=4; i++) {
        String a = filenameWithAbsolutePathWithoutNumber + "__" + i + ".jpg";
        if (new File(a).exists()) {
            filenamesToUse.add(new File(a).getAbsolutePath());
        }
    }
    '''
    

else:
    filenamesToUse.append(str(fileToUse));




mediaIds = []

if doUpload:
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
    



