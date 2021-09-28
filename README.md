# youtube-dl-to-itunes
Download mp4s from YouTube.com, convert the resulting mp4 to mp3, then attribute these mp3s with user-provided metadata. If desired, automatically play your songs in iTunes for future use. Utilises the Python packages [pytube](https://github.com/pytube/pytube/), [moviepy](https://github.com/Zulko/moviepy) and [mutagen](https://github.com/quodlibet/mutagen).
Provided in the public domain, etc. etc., so copy/modify as you wish. Written for Windows in Python 3.9 and Powershell.
## USAGE
To use on **Windows**: 
1. Populate a folder with text files formatted as follows:
   1. Downloading an album as separate videos:
      ```
      ALBUM_NAME : ARTIST_NAME
      SONG1_NAME : SONG1_URL
      SONG2_NAME : SONG2_URL
      SONG3_NAME : SONG3_URL
      ```
   2. Downloading an album using a playlist:
      ```
      ALBUM_NAME : ARTIST_NAME : PLAYLIST_URL      
      SONG1_NAME : SONG1_START
      SONG2_NAME : SONG2_START
      SONG3_NAME : SONG3_START
      ```
   3. Downloading an album from a single video with timestamps:
      ```
      ALBUM_NAME : ARTIST_NAME : VIDEO_URL : ALBUM_RUNTIME
      SONG1_NAME : SONG1_START
      SONG2_NAME : SONG2_START
      SONG3_NAME : SONG3_START
      ```
2. Open (or install + open) [Powershell](https://docs.microsoft.com/en-us/powershell/scripting/windows-powershell/install/installing-windows-powershell?view=powershell-7.1) and run the following command: Also open (or install + open) [Powershell](https://docs.microsoft.com/en-us/powershell/scripting/windows-powershell/install/installing-windows-powershell?view=powershell-7.1) and run the following command:
       
       Set-ExecutionPolicy RemoteSigned
3. Install pytube, moviepy and mutagen using pip:

          pip install pytube moviepy mutagen

4. Download [iTunes](https://www.apple.com/uk/itunes/download/index.html) if you want `youtube-dl-to-itunes.py` to open your new mp3 files in iTunes.
5. Download [youtube-dl-to-itunes.py](), place it in this folder, and run it. By default it will both attempt to download your mp3s to the home Music folder (i.e. `C:\Users\CURRENTUSER\Music`) open iTunes. 

#### For security:
When you no longer want Powershell scripts to run, use `Set-ExecutionPolicy Restricted` in Powershell. 
## DESCRIPTION
**Benefits:** This script is a lightweight method by which to download songs from YouTube and incorporate them into your
iTunes library. Each text file takes up ~1kb, so you can transiently store 50 albums as just 50kb before running this script.

**Limitations:** Lacks the spotify-based metadata retrieval employed by projects like [spotDL](https://github.com/spotDL/spotify-downloader), or the thorough functionality of tools like [youtube-dl](https://github.com/ytdl-org/youtube-dl). 
The script is not as optimised as I'd like, which may be addressed in future commits. Currently, it's as functional as I need it.
### Disclaimer:
I do **not** condone music piracy 🏴‍☠️. Use this tool to retrieve albums you have in physical format, 
or for tracks for which no other distribution method exists.
