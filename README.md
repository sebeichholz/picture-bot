# picture-bot
Small python app that publishes a randomly selected image from a local folder to bluesky

# features
1. scan a given directory (and recursive all subdirectories) for image files and select one random image
2. post this image to mastodon, uses file name as posted text
3. up to four images per toot
4. some sort of intelligent text replacement (from "1991-10" in the filename it makes "10/1991" in the post)
5. create empty marker file for used image (ends with ".used.real"), so this image will not be used again until you delete this marker file
6. optional: simulation mode to check what the app would do

# usage
1. (clone repository)
2. create a file ".env" (or copy it from .evn.tpl) and enter these lines:

    ```
    BLUESKY_HANDLE = "<youd bluesky handle>"
    BLUESKY_APP_PASSWORD = "<your app password>"

    #optional choose one ore more Hashtags that will be appended at the end of the post:
    HASHTAGS="<yout hashtags here, e.g. '#Retrogames #Retrogaming'>"
    ```
    

# use multiple image for one toot
If you want to use more than one image in a tweet (e.g. if you have multiple files/pages for one thing) name them (up to four) like this:
1. myfile__1.jpg
2. myfile__2.jpg
3. myfile__3.jpg
4. myfile__4.jpg