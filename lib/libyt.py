import eyed3
from eyed3.id3.frames import ImageFrame
import os
import youtube_dl
from PIL import Image


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def download_mp3(url, basepath, hook=None):
    try:
        ydl_opts = {
            'nocheckcertificate':True,
            'verbose': False,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'postprocessor_args': [
                '-ar', '16000'
            ],
            'prefer_ffmpeg': True,
            'keepvideo': False,
            'noplaylist': True,
            'outtmpl': f'{basepath}/%(title)s.%(ext)s',
            'writethumbnail': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if callable(hook):
                ydl.add_progress_hook(hook)
            info = ydl.extract_info(url)
            for x,y in info.items():
                print(f'{x}:{y}')

    except youtube_dl.utils.DownloadError as error:
        if 'Unable to download' in error.msg:
            return -2, {'status': 'finished'}
        return -1, {'status': 'finished'}

    file_types = ['JPG', 'PNG', 'GIF', 'WEBP',
                  'TIFF', 'PSD', 'RAW', 'BMP', 'HEIF', 'INDD', 'JPEG', 'JFIF']

    title = info['title']
    image_dir = None
    for file_type in file_types:
        if os.path.exists(f'{basepath}/{title}.{file_type}'):
            image_dir = f'{basepath}/{title}.{file_type}'
            break

    if image_dir:
        image = Image.open(image_dir).convert('RGB')
        image = crop_center(image, 720, image.height)
        image.save(f'{basepath}/cover.jpg', 'jpeg')

        audiofile = eyed3.load(f'{basepath}/{title}.mp3')
        if (audiofile.tag == None):
            audiofile.initTag()

        audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(
            f'{basepath}/cover.jpg', 'rb').read(), 'image/jpeg')
        audiofile.tag.save()

    song = eyed3.load(f'{basepath}/{title}.mp3').tag

    song.title = info['track'] or info['title']

    song.artist = info['artist'] or info['creator']
    if info['album']:
        song.album = info['album']


    os.remove(f'{basepath}/cover.jpg')
    os.remove(image_dir)

    song.save()

    if info['track']:
        track = info['track']
        os.rename(f'{basepath}/{title}.mp3', f'{basepath}/{track}.mp3')

    return 0, info


if __name__ == "__main__":
    download_mp3(input('url>'), '.', lambda x: x)
