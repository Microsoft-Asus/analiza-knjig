import argparse
import requests
import sys
import os
import csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download',
                        '-d',
                        help='Download page given url, name and directory',
                        nargs=3,
                        required=True)

    args = parser.parse_args()

    if args.download:
        name, directory, url = tuple(args.download)
        download_page(url, name, directory)


def create_folder(path):
    '''Create folder if it doesn't exist.'''
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)


def download_page(url, file_name, directory, force=False):
    '''Save page at url to file_name.'''
    path = os.path.join(directory, file_name + '.html')
    try:
        print('Saving {}... '.format(url), end='')
        sys.stdout.flush()
        if os.path.isfile(path) and not force:
            print("Page already saved!")
            return
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('Failed to download page.')
    else:
        create_folder(path)
        with open(path, 'w', encoding='utf-8') as page_file:
            page_file.write(r.text)
            print('Page saved!')


def read_file(file_name, directory):
    with open(os.path.join(directory, file_name + '.html'),
              'r',
              encoding='utf-8') as page_file:
        return page_file.read()


def write_csv(dictionaries, field_names, file_name, directory):
    path = os.path.join(directory, file_name + '.csv')
    create_folder(path)
    with open(path, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for dictionary in dictionaries:
            writer.writerow(dictionary)


if __name__ == '__main__':
    main()
