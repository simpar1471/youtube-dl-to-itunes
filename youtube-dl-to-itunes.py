# youtube-dl-to-itunes.py is free to download, use, edit, burn, slander, and love. Use it
# kindly. copyright(ish) Simon Parker, 2021

import os
import re
import subprocess
import time
import moviepy.editor as mp
import pytube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from mutagen.easyid3 import EasyID3

# ALTER THESE VARIABLES
music_folder = os.path.expanduser(r"~\Music")  # Defaults to C:\Users\[CURRENT_USER]\Music
run_itunes = 1  # 1 to run iTunes, any other value not to run iTunes
album_info_dict = {}


def main():
    videolist_paths: list[str] = get_currdir_videolists()
    for videolist_path in videolist_paths:
        # Command line argument parsing + attributing to easily accessed variables
        text_path = videolist_path
        print("Input text file: '%s'" % text_path)
        # Read text file, split into lists of lists of strings
        with open(text_path, "r") as videos_list:
            text_data: list[str] = videos_list.readlines()
        validate_text_file(text_data)
        text_data: list[list[str]] = split_text_file(text_path)
        # Determine parsing method via first line of .txt file
        parsing_method: int = set_parsing_method(text_data)
        # Set the values in album_info_dict
        set_album_info(text_data)
        # Skips this video list if an album already exists at album_folder.
        if skip_if_album_exists():
            continue
        print("\n'%s' will be downloaded to '%s'." % (album_info_dict.get("album_name"),
                                                      album_info_dict.get("album_folder")))
        track_lengths = get_tracklengths(text_data, parsing_method)
        if parsing_method == 1:
            download_individual(text_data)
        elif parsing_method == 2:
            download_playlist(text_data)
        if parsing_method != 3:
            make_mp3s(text_data, track_lengths, parsing_method)
        elif parsing_method == 3:
            download_album(text_data)
            convert_to_mp3(os.path.join(album_info_dict.get("album_folder"), "%s.mp4" %
                                        clean_file_pathorname(album_info_dict.get("album_name"))))
            album_runtime: str = text_data[0][3]
            extract_album_subclips(text_data, album_runtime)
        else:
            raise Exception("Incorrectly formatted .txt input. See help for information on formatting")
        if run_itunes == 1:
            play_all_songs()
    print("\nAll mp3s downloaded.")


def get_currdir_videolists() -> list[str]:
    curr_wd = os.getcwd()
    filelist: list[str] = []
    for file in os.listdir(curr_wd):
        if "videolist" in file:
            filelist.append(os.path.abspath(file))
    return filelist


# Sets album info that is accessed throughout the script.
def set_album_info(text_file):
    album_info_dict["artist_name"] = text_file[0][0]
    album_info_dict["album_name"] = text_file[0][1]
    album_info_dict["album_folder"]: str = os.path.join(music_folder,
                                                        clean_file_pathorname(album_info_dict.get("artist_name")),
                                                        clean_file_pathorname(album_info_dict.get("album_name")))


# Skips onto the next videolist if an album exists at the output path.
def skip_if_album_exists() -> bool:
    if os.path.exists(album_info_dict.get("album_folder")):
        print("A folder already exists at %s. Check that '%s' is not already downloaded.\n\n" %
              (album_info_dict.get("album_folder"), album_info_dict.get("album_name")))
        time.sleep(3)
        return True


# Splits a text file into a list of lists of strings. These nested lists contain the data required to download/annotate
# each mp3.
def split_text_file(textfile_path) -> list[list[str]]:
    with open(textfile_path, "r") as videos_textfile:
        videos_list = videos_textfile.readlines()
    # Split each string at the colon
    for line in range(0, len(videos_list)):
        videos_list[line] = videos_list[line].replace("\n", "")
        videos_list[line] = videos_list[line].split(" : ")
    return videos_list


# Returns true if first line of .txt file is correctly formatted for either. Not foolproof.
def validate_text_file(textfile: list[str]) -> bool:
    textfile_str01 = textfile[0]
    if re.search("[\w\s]+( : )[\w\s]+(^.*)+", textfile_str01):
        return True
    elif re.search("[\w\s]+( : )[\w\s]+( : )[\w\s]+(^.*)+", textfile_str01):
        return True
    elif re.search("[\w\s]+( : )[\w\s]+( : )[\w\s]+( : )((\d+):(\d+))", textfile_str01):
        return True


def set_parsing_method(input_list):
    if len(input_list[0]) == 2:
        print("Parsing as set of videos with URLs.")
        return 1  # option 1 = individual videos
    elif len(input_list[0]) == 3:
        print("Parsing as playlist.")
        return 2  # option 2 = playlist
    elif len(input_list[0]) == 4:
        print("Parsing as an album in single video.")
        return 3  # option 3 = album video
    else:
        raise Exception("The text file is formatted incorrectly.")


def get_tracklengths(videos_list: list[list[str]], p_method: int) -> list[str]:
    tracklengths: list[str] = []
    if p_method == 1:  # Individual videos
        for line in range(1, len(videos_list)):
            yt_url = videos_list[line][0]
            lengthstring = convert_secs_to_hours_mins_secs(pytube.YouTube(yt_url).length)
            tracklengths.append(lengthstring)
    if p_method == 2:  # Playlist
        playlist_url = videos_list[0][2]
        playlist = pytube.Playlist(playlist_url)
        for video in playlist.videos:
            tracklengths.append(convert_secs_to_hours_mins_secs(video.length))
    if p_method == 3:  # Single video (album)
        for line in range(1, len(videos_list)):
            if line != len(videos_list) - 1:
                tracklengths.append(
                    convert_secs_to_hours_mins_secs(convert_timestamp_into_secs(videos_list[line + 1][1]) -
                                                    convert_timestamp_into_secs(videos_list[line][1])))
            else:
                tracklengths.append(
                    convert_secs_to_hours_mins_secs(convert_timestamp_into_secs(videos_list[0][3]) -
                                                    convert_timestamp_into_secs(videos_list[line][1])))
    return tracklengths


def download_video(video, mp4_name):
    video.streams.get_by_itag(140).download(output_path=album_info_dict.get("album_folder"), filename=mp4_name)


# Makes string usable for file paths/names in Windows. Unsure of requirements for Mac OS/Linux.
def clean_file_pathorname(dirty_name: str) -> str:
    clean_name = re.sub(r'[",.<>:/\\|?*]', "", dirty_name)
    return clean_name


def download_individual(videos_list: list[list[str]]):
    album_length = len(videos_list)
    for line in range(1, album_length):
        yt_url = videos_list[line][0]
        song_name = clean_file_pathorname(videos_list[line][1])
        print("\nDownloading '%s' from YouTube with URL %s." % (song_name, yt_url))
        yt = pytube.YouTube(yt_url)  # Make YouTube object with pytube
        mp4_name = "%s.mp4" % song_name  # Set the name for the new .mp4 file
        download_video(yt, mp4_name)  # Download 128kbps .mp4 stream


def download_playlist(videos_list: list[list[str]]):
    album_length = len(videos_list)
    playlist_url = videos_list[0][2]
    playlist = pytube.Playlist(playlist_url)
    for line in range(1, album_length):
        yt = playlist.videos[line - 1]  # Get YouTube object from playlist
        song_name = videos_list[line][0]
        print("\nDownloading song '%s' from YouTube." % song_name)
        # Set the name for the new .mp4 file
        mp4_name = "%s.mp4" % clean_file_pathorname(song_name)
        download_video(yt, mp4_name)  # Download 128kbps .mp4 stream


def download_album(videos_list: list[list[str]]):
    yt_url = videos_list[0][2]
    print("\nDownloading '%s' from YouTube with URL %s." % (album_info_dict.get("album_name"), yt_url))
    yt = pytube.YouTube(yt_url)  # Make YouTube object with pytube
    mp4_name = "%s.mp4" % clean_file_pathorname(album_info_dict.get("album_name"))  # Set the name for the new .mp4 file
    download_video(yt, mp4_name)  # Download 128kbps .mp4 stream


# Taken from https://www.geeksforgeeks.org/python-program-to-convert-seconds-into-hours-minutes-and-seconds/
def convert_secs_to_hours_mins_secs(seconds):
    seconds = seconds % (24 * 3600)
    # hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)
    # return "%d:%02d:%02d" % (hour, minutes, seconds)


# Converts time in hh:mm:ss or mm:ss or ss format to seconds
def convert_timestamp_into_secs(timestamp):
    times = timestamp.split(":")
    if len(times) == 3:
        return 3600 * int(times[0]) + 60 * int(times[1]) + int(times[2])
    elif len(times) == 2:
        return 60 * int(times[0]) + int(times[1])


def convert_to_mp3(mp4_path):
    mp3_path = mp4_path.replace(".mp4", "_before.mp3")
    with mp.AudioFileClip(mp4_path) as video_clip_as_audio:
        video_clip_as_audio.write_audiofile(mp3_path, verbose=True)
    if os.path.exists(mp4_path):
        os.remove(mp4_path)
    return mp3_path


def make_mp3s(videos_list: list[list[str]], track_lengths: list[str], p_method: int):
    song_name: str = ""
    for line in range(1, len(videos_list)):
        if p_method == 1:  # Individual videos
            song_name = videos_list[line][1]
        elif p_method == 2:  # Playlist
            song_name = videos_list[line][0]
        mp4_path = os.path.join(album_info_dict.get("album_folder"), "%s.mp4" % clean_file_pathorname(song_name))
        mp3_path = convert_to_mp3(mp4_path)
        track_num = r"%d/%d" % (line, len(videos_list) - 1)
        track_length = track_lengths[line - 1]
        # Maybe this will fix iTunes issue of doubling mp3 length
        ffmpeg_extract_subclip(mp3_path,
                               0,
                               convert_timestamp_into_secs(track_length),
                               targetname=mp3_path.replace("_before", ""))
        os.remove(mp3_path)
        # Edit .mp3 ID3 tags
        change_mp3_attributes(mp3_path.replace("_before", ""), song_name, album_info_dict.get("artist_name"),
                              album_info_dict.get("album_name"), track_num, track_length)


def extract_album_subclips(videos_list: list[list[str]], album_runtime: str):
    album_length = len(videos_list)
    album_video_path = os.path.join(album_info_dict.get("album_folder"), "%s_before.mp3" %
                                    clean_file_pathorname(album_info_dict.get("album_name")))
    for line in range(1, album_length):
        # Set song times, track number and track length
        song_name = videos_list[line][0]
        song_start = videos_list[line][1]
        if line == album_length - 1:
            song_end = album_runtime
        else:
            song_end = videos_list[line + 1][1]
        track_num = r"%d/%d" % (line, album_length - 1)
        track_length = convert_secs_to_hours_mins_secs(convert_timestamp_into_secs(song_end) -
                                                       convert_timestamp_into_secs(song_start))
        song_path = os.path.join(album_info_dict.get("album_folder"), "%s.mp3" % clean_file_pathorname(song_name))
        print("Splitting track no. %s: '%s'. Track spans from %s to %s" % (track_num, song_name, song_start, song_end))
        ffmpeg_extract_subclip(album_video_path,
                               convert_timestamp_into_secs(song_start),
                               convert_timestamp_into_secs(song_end),
                               targetname=song_path)
        # Edit .mp3 ID3 tags
        change_mp3_attributes(song_path, song_name, album_info_dict.get("artist_name"),
                              album_info_dict.get("album_name"), track_num, track_length)
    os.remove(album_video_path)


def change_mp3_attributes(mp3_path: str, song: str, artist: str, album: str, tracknumber: str, tracklength: str):
    print("| SONG NAME:", song,
          "| ARTIST:", artist,
          "| ALBUM:", album,
          "| TRACK NUMBER:", tracknumber, " |")
    # Note for future edits: see valid EasyID3 keys with print(EasyID3.valid_keys.keys())
    audio = EasyID3(mp3_path)
    audio["title"] = song
    audio["artist"] = artist
    audio["album"] = album
    audio["tracknumber"] = tracknumber
    audio["length"] = tracklength
    audio["composer"] = u""  # set as empty
    audio.save()


def play_all_songs():
    ps1_path = os.path.join(album_info_dict.get("album_folder"), "play_all_songs.ps1")
    powershell_script = open(ps1_path, "w")
    powershell_script.write(
        r"# Set-ExecutionPolicy Restricted" "\n"
        r"# Set-ExecutionPolicy RemoteSigned" "\n"
        r"ExecutionPolicy Bypass" "\n"
        r'Write-Host "Playing all music in folder"' "\n"
        r"# Search for iTunes COM object -->" "\n"
        r'Get-CimInstance Win32_COMSetting|Select-Object ProgId, Caption|Where-Object Caption -ILike "*itunes*"' "\n"
        r"" "\n"
        r"# Instantiate a new iTunes.Application.1 object" "\n"
        r"$itunes = New-Object -ComObject iTunes.Application.1" "\n"
        r"$itunes.Mute = $True" "\n"
        r"" "\n"
        r"# For each file in album folder, play using iTunes IF file extension is .mp3" "\n"
        r'$fileext = ".mp3"' "\n"
        r"Foreach ($file IN Get-ChildItem $PSScriptRoot)" "\n"
        r"{" "\n"
        r'    $filename = $PSScriptRoot+"\"+$file' "\n"
        r"    if ($filename.contains($fileext))" "\n"
        r"    {" "\n"
        r"        Write-Host $filename" "\n"
        r"        $itunes.PlayFile($filename)" "\n"
        r"    }" "\n"
        r"}" "\n"
        r"Start-Sleep -Seconds 1" "\n"
        r"$itunes.Quit()")
    powershell_script.close()
    subprocess.run([r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                    '& "%s"' % ps1_path])
    os.remove(ps1_path)


if __name__ == "__main__":
    main()
