# Generate-GPX-data-text-for-videos
Script for generating GPX-data subtext for videos.

<img width="1912" height="1041" alt="kuva" src="https://github.com/user-attachments/assets/a72bca21-8f04-4f37-b6ec-8678d3053a1d" />

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

<img width="416" height="778" alt="kuva" src="https://github.com/user-attachments/assets/d64d2899-6022-471b-b705-b499150a22f0" />

<img width="957" height="787" alt="kuva" src="https://github.com/user-attachments/assets/433ca0ee-a261-4666-a6dd-4f526b5ca5a8" />

<img width="376" height="232" alt="kuva" src="https://github.com/user-attachments/assets/ad426d6e-17d7-42e2-8dc1-2ce8afe02106" />


For testing purposes local VLC Player is a great tool: Select a subtext file from
the toolbar and off you go.

<img width="1531" height="883" alt="kuva" src="https://github.com/user-attachments/assets/fb53f574-a4c7-4ecb-abee-4c711f927084" />


Here is my Kotka Jukola 2026 video for review. Add finnish subtext to see the result. 
GPX data starts at 53 secs as seen in this Readme-file.
https://www.youtube.com/watch?v=FIUgAXnU45Q
