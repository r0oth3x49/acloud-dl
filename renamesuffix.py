from pathlib import Path
import glob

path = Path('./')


for f in path.rglob('*.VIDEO_AUDIO*'):
    if f.is_file() and f.suffix in ['.VIDEO_AUDIO']:
        f.rename(f.with_suffix('.mp4')) # MediaInfo shows it as MPEG-4 AVC video and mp4 extension is supported better in Mac QuickTime
