from typing import Union, List

import fitz
import os
from os import PathLike
import ocrmypdf
import argparse

# Directory of the applications
APPLICATION_DIRECTORY = ''

# Directory of the OCR'd applications so originals are not overwritten
# This isn't functioning well right now
# OCR_DIRECTORY = ''

# Output directory of anonymized files
OUT_DIRECTORY = ''


def get_applicant_name(page: fitz.Page) -> List[str]:
    """
    This function finds the candidate's name and returns each name as a list to use during anonymization
    :param page: The first page of the application
    :return: List[str] with each element being a portion of the candidate name
    """
    assert(isinstance(page, fitz.Page))
    words = page.get_text_blocks()
    string = words[1][4]
    return string.split(': ')[1].replace('\n', '').split(' ')


# def ocr_pdf(directory: Union[str, PathLike[str]]) -> None:
#     """
#     Work in progress for using Python to OCR the text in the document.
#     Would need Tesserect to be installed to run
#     :param directory: the directory of the PDFs to run OCR on
#     :return: None
#     """
#     if not os.path.exists(OCR_DIRECTORY):
#         os.mkdir(OCR_DIRECTORY)
#
#     for f in sorted(os.listdir(directory)):
#         new_name = f.split('.pdf')[0]
#         new_name += '_ocr.pdf'
#         if new_name.upper() in [x.upper() for x in list(sorted(os.listdir(directory)))] or '_ocr.pdf' in f:
#             continue
#
#         print(f'OCR beginning on: {new_name} ')
#
#         ocrmypdf.ocr(os.path.join(directory, f), os.path.join(OCR_DIRECTORY, new_name)
#                      , deskew=True, skip_text=True, output_type='pdf', optimize=1
#                      , rotate_pages=True, rotate_pages_threshold=0.25, oversample=300)


def anon_pdf(file: Union[str, PathLike[str]], out_dir: Union[str, PathLike[str]]) -> None:
    """
    Anonymizes the PDF provided
    :param file: the pdf file path
    :param out_dir: the output directory to write the de-identified file
    :return: None
    """

    # Make the output directory if it doesn't exist already
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    doc = fitz.open(file, filetype='pdf')

    # Setup search words and their replacement words. The keys are the words to search
    # with the values as their replacements
    replace_words = {'male': None, "female": None, ' he ': 'they', ' she ': 'they',
                     ' him ': 'them', ' her ': 'their', ' hers ': 'theirs', ' his ': 'theirs'}

    # Standard locations to remove identifying information from
    idx_app = [[1, 4, 5], [1, 3, 4, 5, 6, 7, 8, 9, 10, 12, -2]]

    # Get the name of the applicant and add it to the replacement word list
    names = get_applicant_name(doc.load_page(0))
    for n in names:
        replace_words[n] = None

    # Loop through all pages and replace the identifying content
    for pagenum in range(doc.page_count):
        redaction_count = 0
        page = doc[pagenum]

        if pagenum in [0, 1]:
            for idx in idx_app[pagenum]:
                words = page.get_text_blocks()
                word = words[idx]
                new_rect = fitz.Rect(word[0], word[1], word[2], word[3])
                page.add_redact_annot(new_rect)
                redaction_count += 1
        else:
            for word, replacement in replace_words.items():

                words = page.get_text_blocks()
                # If there are no words on the page continue
                if len(words) == 0:
                    continue

                rects = page.search_for(word)

                # If there are no rectangles, this means the word wasn't found, skip page for this word
                if len(rects) == 0:
                    continue

                # For each rectangle demarcating a word, apply a redaction.
                for rect in rects:
                    # This margin is how much to move the originally found rectangle
                    # and can be edited as needed
                    margin = [-2, -1, -2, -6]

                    new_rect = fitz.Rect(rect[0] - margin[0],
                                         rect[1] - margin[1],
                                         rect[2] + margin[2],
                                         rect[3] + margin[3])

                    # If the replacement word exists, add the replacement here, otherwise just blank
                    # out the word, i.e., replacement = None
                    page.add_redact_annot(new_rect, text=replacement)

                    redaction_count += 1

        # If redactions have been applied, apply them
        if redaction_count > 0:
            try:
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE )
            except RuntimeError:
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
            except ValueError:
                pass

    # By using the "RenamePDFs" script, the first item in the file name should be the applicant number
    applicant_number = file.split('_')[1].split('/')[1]
    out_file = os.path.join(out_dir, applicant_number + '.pdf')

    print(f'Saving file: {out_file}')

    doc.save(out_file, garbage=4, deflate=True, deflate_images=True,
             deflate_fonts=True, clean=True, pretty=True)
    del doc


def main():
    # Running this script as the main will anonymize all files in the directory
    for f in os.listdir(APPLICATION_DIRECTORY):
        # Checks that the files have been labeled with "OCR". This is important to make sure images are
        # converted to readable text.
        if "OCR" in f:
            print(f"Anonymizing file: {f}")
            anon_pdf(os.path.join(APPLICATION_DIRECTORY, f), OUT_DIRECTORY)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--application_directory', type=str,
                        help='The directory where the applications that have had OCR run are stored.')
    parser.add_argument('-o', '--output_directory', type=str,
                        help='The location where to store the anonymized files.')
    args = parser.parse_args()

    if args.application_directory is None:
        assert SyntaxError("You must supply the directory where the applications reside.")
        exit()

    if not(os.path.exists(args.application_directory)):
        assert NotADirectoryError('The supplied application_directory argument is not a valid directory.')
        exit()

    APPLICATION_DIRECTORY = args.application_directory

    if args.output_directory is None:
        assert SyntaxError("You must supply an output directory.")
        exit()

    OUT_DIRECTORY = args.output_directory

    if not (os.path.exists(args.output_directory)):
        print(f'The output directory does not exist. Creating:{OUT_DIRECTORY}')
        os.mkdir(OUT_DIRECTORY)

    exit(main())
