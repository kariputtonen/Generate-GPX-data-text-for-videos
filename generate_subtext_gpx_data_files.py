import gpxpy
import pandas as pd
import math
import sys
from datetime import datetime

# ----------------------------------------
# This script generates two commonly used subtext files for videos: .vtt and .srt
# vtt-file works with Youtube and VLC Player. 
# This script was first generated using AI. Reading and undestanding it is recommended.
# I use Garmin gpx data. Other watches may differ in file format.
# ----------------------------------------

SRT_FILE = "overlay.srt"
VTT_FILE = "overlay.vtt"


# ----------------------------------------
# Some fuctions
# ----------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def pace_to_mmss(pace_min_km):
    if pace_min_km is None:
        return "-"
    if isinstance(pace_min_km, float) and math.isnan(pace_min_km):
        return "-"
    if pace_min_km <= 0:
        return "-"
    minutes = int(pace_min_km)
    seconds = int((pace_min_km - minutes) * 60)
    return f"{minutes:02d}:{seconds:02d}/km"

# ----------------------------------------
# GPX parse
# ----------------------------------------

def parse_gpx(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)

    rows = []

    for track in gpx.tracks:
        for segment in track.segments:
            for p in segment.points:

                hr = None

                # Garmin TrackPointExtension
                if p.extensions:
                    for ext in p.extensions:
                        if "TrackPointExtension" in ext.tag:
                            for child in ext:
                                tag = child.tag.lower()
                                if tag.endswith("hr"):
                                    try:
                                        hr = int(child.text)
                                    except:
                                        hr = None

                rows.append({
                    "time": p.time,
                    "lat": p.latitude,
                    "lon": p.longitude,
                    "ele": p.elevation,
                    "hr": hr
                })

    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])
    return df


# ----------------------------------------
# Calculations
# ----------------------------------------

def compute_distances(df):
    distances = [0.0]
    for i in range(1, len(df)):
        d = haversine(df.lat[i-1], df.lon[i-1], df.lat[i], df.lon[i])
        distances.append(distances[-1] + d)
    df["dist_km"] = distances


def compute_speed_and_pace(df):
    df["speed_kmh"] = None
    df["pace_min_km"] = None

    for i in range(1, len(df)):
        dt = (df.time[i] - df.time[i-1]).total_seconds()
        if dt > 0:
            d = df.dist_km[i] - df.dist_km[i-1]
            speed = d / (dt / 3600)
            df.loc[i, "speed_kmh"] = speed
            if speed > 0:
                df.loc[i, "pace_min_km"] = 60 / speed


# ----------------------------------------
# Time stamps
# ----------------------------------------

def seconds_to_srt_time(sec):
    if sec < 0:
        sec = 0
    ms = int((sec - int(sec)) * 1000)
    s = int(sec) % 60
    m = (int(sec) // 60) % 60
    h = int(sec) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def seconds_to_vtt_time(sec):
    if sec < 0:
        sec = 0
    ms = int((sec - int(sec)) * 1000)
    s = int(sec) % 60
    m = (int(sec) // 60) % 60
    h = int(sec) // 3600
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


# ----------------------------------------
# SRT + VTT generation
# ----------------------------------------

def write_subtitles(df, srt_path, vtt_path, offset):
    t0 = df.time.min()

    with open(srt_path, "w", encoding="utf-8", newline="\n") as srt, \
         open(vtt_path, "w", encoding="utf-8", newline="\n") as vtt:

        vtt.write("WEBVTT\n\n")

        for i in range(len(df) - 1):
            start_sec = (df.time[i] - t0).total_seconds() + offset
            end_sec   = (df.time[i+1] - t0).total_seconds() + offset

            dist = df.dist_km[i]
            pace_str = pace_to_mmss(df.pace_min_km[i])

            hr = df.hr[i]
            if hr is None or (isinstance(hr, float) and math.isnan(hr)):
                hr_str = "-"
            else:
                hr_str = f"{int(hr)}bpm"

            ele = df.ele[i]
            if ele is None or (isinstance(ele, float) and math.isnan(ele)):
                ele_str = "-"
            else:
                ele_str = f"{ele:.0f}m"

            text = (
                f"{dist:.2f}km\t"
                f"{pace_str}\t"
                f"{hr_str}\t"
                f"Alt:{ele_str}"
            )

            # --- SRT ---
            srt.write(f"{i+1}\n")
            srt.write(f"{seconds_to_srt_time(start_sec)} --> {seconds_to_srt_time(end_sec)}\n")
            srt.write(text + "\n\n")

            # --- VTT ---
            vtt.write(f"{seconds_to_vtt_time(start_sec)} --> {seconds_to_vtt_time(end_sec)}\n")
            vtt.write(text + "\n\n")


# ----------------------------------------
# Usage
# ----------------------------------------

def print_usage():
    print("\nKÄYTTÖ:")
    print("  python generate_subtext_gpx_data_files.py <GPX_FILE> <VIDEO_OFFSET_SECONDS>")
    print("\nESIMERKKI:")
    print("  python generate_subtext_gpx_data_files.py Kotka_jukola_2026.gpx 53")
    print("\nTämä skripti tuottaa:")
    print("  - overlay.srt")
    print("  - overlay.vtt (YouTube-yhteensopiva)\n")

# ------------------------------------------
# Smoothing functions
# It's questionable if these are useful for orienteering videos due to rapid changes: runn, walk, run, walk, stand still...
# But maybe by changing this value to bigger you may get other results: window_seconds=1
# ------------------------------------------

def smooth_moving_average(df, window_seconds=1):
    """
    Tasaa nopeus, syke ja korkeus liukuvalla keskiarvolla.
    window_seconds = kuinka monta sekuntia keskiarvoa käytetään.
    """
    # Muutetaan aika sekunneiksi alusta
    t0 = df.time.min()
    df["t_sec"] = (df.time - t0).dt.total_seconds()

    # Lasketaan näytepisteiden määrä
    # (GPX:ssä pisteväli on yleensä 1 s)
    window_points = max(1, int(window_seconds))

    df["speed_kmh"] = df["speed_kmh"].rolling(window_points, center=True).mean()
    df["pace_min_km"] = df["pace_min_km"].rolling(window_points, center=True).mean()
    df["ele"] = df["ele"].rolling(window_points, center=True).mean()
    df["hr"] = df["hr"].rolling(window_points, center=True).mean()

    return df


def smooth_median(df, window_points=3):
    """
    Median-suodatin poistaa yksittäiset piikit.
    """
    df["speed_kmh"] = df["speed_kmh"].rolling(window_points, center=True).median()
    df["pace_min_km"] = df["pace_min_km"].rolling(window_points, center=True).median()
    df["ele"] = df["ele"].rolling(window_points, center=True).median()
    df["hr"] = df["hr"].rolling(window_points, center=True).median()
    return df


# ----------------------------------------
# Main program
# ----------------------------------------

def main():
    if len(sys.argv) != 3:
        print_usage()
        return

    GPX_FILE = sys.argv[1]

    try:
        VIDEO_OFFSET_SECONDS = float(sys.argv[2])
    except:
        print("\nVirhe: VIDEO_OFFSET_SECONDS ei ole numero.\n")
        print_usage()
        return

    print(f"\nLuetaan GPX: {GPX_FILE}")
    print(f"Aikasiirto videolle: {VIDEO_OFFSET_SECONDS} sekuntia\n")

    df = parse_gpx(GPX_FILE)
    compute_distances(df)
    compute_speed_and_pace(df)
    # Tasoitukset
    df = smooth_median(df, window_points=3)
    df = smooth_moving_average(df, window_seconds=1)

    write_subtitles(df, SRT_FILE, VTT_FILE, VIDEO_OFFSET_SECONDS)

    print("Valmis! Kirjoitettu:")
    print(f" - {SRT_FILE}")
    print(f" - {VTT_FILE}\n")


if __name__ == "__main__":
    main()
