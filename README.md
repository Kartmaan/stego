# Stego - LSB Steganography Tool

This project is a simple command-line tool, written in Python, for hiding files in images using the Least Significant Bit (LSB) steganography technique.

## How it works

LSB steganography is a technique that involves modifying the least significant bit of each color component (Red, Green, Blue) of a pixel in an image to store data. These modifications are so minimal that they are imperceptible to the naked eye.

This script takes a secret file, converts it to a sequence of bits, and inserts those bits into the LSBs of the pixels in a carrier image. To ensure data integrity, the original file name and an end-of-file marker are also embedded.

## Features

*   **Hide a file** : Embed any file type into a PNG or BMP image.
*   **Reveal a file** : Extract the hidden file from a steganography image.
*   **Data Security**: The original file name is preserved during extraction.

## Requirements

Make sure you have Python 3.10+ installed. The necessary libraries can be installed via `pip`:

```sh
pip install -r requirements.txt
```

Dependencies :
*   `numpy`
*   `pillow`

## Usage

The script is used in the command line with two main subcommands: `hide` and `reveal`.

### Hide a file

To hide a file in an image :

```sh
python stego.py hide <carrier_image> <secret_file> <output_image>
```

**Example :**

```sh
python stego.py hide cat.png password.txt cat2.png
```

### Reveal a file

To extract a hidden file from an image :

```sh
python stego.py reveal <stegano_image> [--output_dir <output_directory>]
```

**Example :**

```sh
python stego.py reveal cat2.png
```

If the output directory is not specified, the extracted files will be saved in a folder named `extracted` by default. The name of this folder can be changed by adding the --output_dir option.

```sh
python stego.py reveal cat2.png --output_dir stego_files
```

## Limitations

*   **Image formats**: To avoid data loss due to compression, only images in **PNG** and **BMP** formats are supported.
*   **File size**: The file to be hidden must be small enough to fit in the carrier image. The script will warn you if the image does not have sufficient capacity.