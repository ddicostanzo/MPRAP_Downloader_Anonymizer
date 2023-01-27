import argparse
import os
from typing import Union
import random

# The directory the applications have been downloaded to
DOWNLOAD_PATH = r""


def rename_pdfs(app_path: Union[os.PathLike[str], str], shuffle_apps: bool = False) -> None:
    """
    Renames the applications with a ###_LastName, FirstName.pdf template
    :param app_path: The application path
    :param shuffle_apps: Flag to shuffle the applications before numbering
    :return: None
    """

    # Get all files in the folder
    files = os.listdir(app_path)
    FilesUnordered = {}

    # Loop through files to get the applicants' first and last names
    print('Ordering files')
    for f in files:
        f_no_ext = os.path.splitext(f)[0]
        last_name = f_no_ext.split('_')[1]
        first_name = f_no_ext.split('_')[0]
        last_name = last_name.split('-')[0]
        FilesUnordered[f] = f'{last_name}, {first_name}'

    # Sort the applications alphabetically by "last name, first name"
    FilesOrdered = FilesUnordered
    FilesOrdered = sorted(FilesOrdered.items(), key=lambda item: item[1])

    if shuffle_apps:
        list_files = list(FilesOrdered.items())
        random.shuffle(list_files)
        FilesOrdered = dict(list_files)

    i = 1
    for k, v in FilesOrdered:
        print(f'Working on file {i}/{len(FilesOrdered)}: {k}')
        # Prefix leading zeros to the application number
        numstr = f'{i:03}'
        # Create new file name
        newfile = numstr + '_' + v + '.pdf'
        # Rename the file
        os.rename(os.path.join(app_path, k), os.path.join(app_path, newfile))
        print(f'File saved to: {os.path.join(app_path, newfile)}')
        i = i + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--download_directory', type=str,
                        help='The directory where to download the applications to.')
    parser.add_argument('-s', '--shuffle', type=bool, default=False, help='Whether to shuffle the applications '
                                                                          'before numbering them. If this is set '
                                                                          'to False then the applications will be '
                                                                          'ordered by the applicant last name. '
                                                                          'The default is False.')
    args = parser.parse_args()

    if args.download_directory is None:
        assert SyntaxError('The download directory is a required argument.')
        exit()

    if not (os.path.exists(args.download_directory)):
        assert FileNotFoundError(f'The path provided does not exist: {args.download_directory}')
        exit()

    DOWNLOAD_PATH = args.download_directory
    shuffle = args.shuffle

    exit(rename_pdfs(DOWNLOAD_PATH, shuffle_apps=shuffle))
