import os
from .HeifImagePlugin import Image
from . import Const


class ImageConvert():
    def __init__(self):
        self._image_list = []
        self._count = 0

    def _mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def _find_image(self, sub_url):
        for direction_sub in os.listdir(sub_url):
            dir_sub = os.path.join(sub_url, direction_sub)
            if os.path.isfile(dir_sub):
                if direction_sub.find('.') > -1 and dir_sub.rsplit(".", 1)[1].upper() in Const.ext:
                    self._image_list.append(dir_sub)
            else:
                self._find_image(dir_sub)

    def find_all_image(self, sub_url):
        self._image_list = []
        self._find_image(sub_url)
        return self._image_list

    def convert(self, filepath, check, printf):
        try:
            image = Image.open(filepath)
            fmt = image.format
            if fmt == 'JPEG':
                printf(f'{filepath}  {fmt}\t图片跳过')
            else:
                self._count += 1

                if check:
                    new_path = filepath.rsplit(".", 1)[0] + '.jpg'
                    os.remove(filepath)
                else:
                    father_path, file_name = os.path.split(filepath)
                    save_dir = os.path.join(father_path, 'convert')
                    self._mkdir(save_dir)
                    new_path = os.path.join(save_dir, file_name.rsplit(".", 1)[0] + '.jpg')

                if image.mode != 'RGB':
                    image = image.convert("RGB")
                # https://www.osgeo.cn/pillow/handbook/image-file-formats.html#jpeg
                info = image.info
                exif = info.get('exif')
                icc_profile = info.get('icc_profile')
                if exif is not None and icc_profile is not None:
                    image.save(new_path, format='jpeg', quality=95, icc_profile=icc_profile, exif=exif)
                elif exif is not None:
                    image.save(new_path, format='jpeg', quality=95, exif=exif)
                elif icc_profile is not None:
                    image.save(new_path, format='jpeg', quality=95, icc_profile=icc_profile)
                else:
                    image.save(new_path, format='jpeg', quality=95)
                printf(f'{self._count} {filepath}  {fmt}\t->\t{new_path}')
        except Exception as e:
            printf(f'{filepath}  报错: {e}')

    def convert_all(self, file_path, flag, printf=print):
        if os.path.isfile(file_path):
            if file_path.rsplit(".", 1)[1].lower() in Const.ext:
                self.convert(file_path, flag, printf)
        else:
            for img in self.find_all_image(file_path):
                self.convert(img, flag, printf)

    def clear(self):
        self._image_list = []
        self._count = 0
