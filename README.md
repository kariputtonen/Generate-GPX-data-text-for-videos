# Generate-GPX-data-text-for-videos
Script for generating GPX-data subtext for videos.

This script generates two commonly used subtext files for videos: .vtt and .srt
vtt-file works with Youtube and VLC Player. 
This script was first generated using AI. Reading and undestanding it is recommended.
I use Garmin gpx data. Other watches may differ in file format.

Usage:

python generate_subtext_gpx_data_files.py <GPX_FILE> <VIDEO_OFFSET_SECONDS>

<VIDEO_OFFSET_SECONDS> is time from the video start until the GPX (clock) starts.

for example:

python generate_subtext_gpx_data_files.py Kotka_jukola_2026.gpx 53

After generating the files you may add the subtext file for your videos.
Youtube: Subtexts -> Send file -> overlay.vtt

For testing purposes local VLC Player is a great tool: Select a subtext file from
the toolbar and off you go.

Here is my Kotka Jukola 2026 video for review. Add finnish subtext to see the result. 
GPX data starts at 53 secs as seen in this Readme-file.
https://www.youtube.com/watch?v=FIUgAXnU45Q
