
from imghdr import what
from os import walk, mkdir, path, listdir, getenv
from datetime import datetime
from shutil import copy2
from argparse import ArgumentParser


from PIL.ExifTags import GPSTAGS, TAGS
from PIL import Image, ExifTags
from geopy.geocoders import Here
from dotenv import load_dotenv


load_dotenv()  # Loading vars in env file


def prepare_arguments():

    # Adding arguments
    parser = ArgumentParser()

    parser.add_argument("-S", "--src",
                        help="The source folder where images exist")
    parser.add_argument("-D", "--dir",
                        help="The dir folder where images should be copied to")
    args = parser.parse_args()

    if not args.src and not args.S:
        raise ValueError("No source folder was provided")
    if not args.dir and not args.D:
        raise ValueError("No dir folder was provided")

    return args


# Get location information from image file and assgin correct labels to the geotagging dict


def get_geotagging(exif):
    geotagging = {}

    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                return None
            else:
                for (key, val) in GPSTAGS.items():
                    if key in exif[idx]:
                        geotagging[val] = exif[idx][key]
    return geotagging


def prepare_files(src_folder):
    files = []
    # get only files and ignore directories
    files_names = onlyfiles = [f for f in listdir(
        src_folder) if path.isfile(path.join(src_folder, f))]

    for filename in files_names:
        file_path = src_folder + '/' + filename
        file_type = what(file_path)

        if file_type == 'jpeg' or file_type == 'png':
            image_exif = Image.open(file_path).getexif()
            date_string = image_exif.get(36867)

            if date_string:
                date = datetime.strptime(date_string, "%Y:%m:%d %H:%M:%S")
                x = {
                    'geotagging': get_geotagging(image_exif),
                    'path': file_path,
                    'year': datetime.strftime(date, '%Y'),
                    'month': datetime.strftime(date, '%B')
                }

                files.append(x)
    return files


def copy_files(files, dir_folder):
    for f in files:
        target_year_dir = dir_folder + '/' + f['year']
        target_month_dir = target_year_dir + '/' + f['month']

        if path.exists(target_year_dir):
            if path.exists(target_month_dir):
                copy2(f['path'], target_month_dir)
            else:
                mkdir(target_month_dir)
                copy2(f['path'], target_month_dir)
        else:
            mkdir(target_year_dir)
            mkdir(target_month_dir)
            copy2(f['path'], target_month_dir)


def main():
    args = prepare_arguments()

    files = prepare_files(args.src)
    copy_files(files, args.dir)


main()
