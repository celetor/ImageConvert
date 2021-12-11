import os
from io import BytesIO
from PIL import Image
import pyheifx as pyheif
import whatimage


class ImageConvert():
    def __init__(self):
        self.ext = ['jpg', 'jpeg', 'png', 'bmp', 'heic', 'webp']
        self.image_list = []
        self.count = 0

    def _mkdir(self, path):
        _path = os.path.normpath(path)
        if not os.path.exists(_path):
            os.makedirs(_path)
        return _path

    def _find_image(self, sub_url):
        for dir_sub in os.listdir(sub_url):
            dir_sub = os.path.join(sub_url, dir_sub)
            if os.path.isfile(dir_sub):
                if dir_sub.rsplit(".", 1)[1].lower() in self.ext:
                    self.image_list.append(dir_sub)
            else:
                self._find_image(dir_sub)

    def find_all_image(self, sub_url):
        self.image_list = []
        self._find_image(sub_url)

    def convert(self, filepath, check, printf):
        with open(filepath, 'rb') as f:
            bytes_io = f.read()

        if check:
            new_path = filepath.rsplit(".", 1)[0] + '.jpg'
        else:
            father_path, file_name = os.path.split(filepath)
            save_dir = os.path.join(father_path, 'convert')
            self._mkdir(save_dir)
            new_path = os.path.join(save_dir, file_name.rsplit(".", 1)[0] + '.jpg')

        try:
            fmt = whatimage.identify_image(bytes_io)
            if fmt == 'jpeg':
                printf(f'{filepath}\t{fmt}图片跳过')
            elif fmt in ['bmp', 'png', 'webp']:
                if check:
                    os.remove(filepath)
                self.count += 1
                pi = Image.open(BytesIO(bytes_io))
                exif_data = pi.info.get('exif')
                exif_data = b'' if exif_data is None else exif_data
                pi = pi.convert("RGB")
                pi.save(new_path, format="jpeg", quality=100, exif=exif_data)
                printf(f'{self.count} {filepath}\t->\t{fmt} {new_path}')
            elif fmt in ['heic']:
                if check:
                    os.remove(filepath)
                self.count += 1
                heif_file = pyheif.read(bytes_io)
                exif_data = b''
                for metadata in heif_file.metadata:
                    if str(metadata['type']).lower() == 'exif':
                        exif_data = metadata['data']
                        break
                pi = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )
                # http://cn.voidcc.com/question/p-qzogslmj-ve.html
                pi.save(new_path, format="jpeg", quality=100, exif=exif_data)
                printf(f'{self.count} {filepath}\t->\t{fmt} {new_path}')
            else:
                printf(f'{filepath}\t{fmt}无法转换跳过')
        except Exception as e:
            printf(f'{filepath}\t报错: {e}')

    def convert_all(self, file_path, flag, printf=print):
        if os.path.isfile(file_path):
            if file_path.rsplit(".", 1)[1].lower() in self.ext:
                self.convert(file_path, flag, printf)
        else:
            self.find_all_image(file_path)
            for img in self.image_list:
                self.convert(img, flag, printf)

    def clear(self):
        self.image_list = []
        self.count = 0
