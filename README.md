# Stego - LSB Steganography Tool

<!-- TOC -->
* [Stego - LSB Steganography Tool](#stego---lsb-steganography-tool)
  * [How it works](#how-it-works)
  * [Features](#features)
  * [Requirements](#requirements)
  * [Usage](#usage)
    * [Hide a file](#hide-a-file)
    * [Reveal a file](#reveal-a-file)
  * [Limitations](#limitations)
  * [To learn more about the LSB technique](#to-learn-more-about-the-lsb-technique)
    * [1. Understanding the Least Significant Bit (LSB)](#1-understanding-the-least-significant-bit-lsb)
      * [Binary Weight System](#binary-weight-system)
      * [Minimal Impact](#minimal-impact)
    * [2. LSB Implementation in Digital Images](#2-lsb-implementation-in-digital-images)
      * [Pixel Structure (RGB)](#pixel-structure-rgb)
      * [The Hiding Process (1-Bit LSB)](#the-hiding-process-1-bit-lsb)
    * [3. Storage Capacity Calculation](#3-storage-capacity-calculation)
      * [1-Bit LSB Capacity Formula](#1-bit-lsb-capacity-formula)
      * [N-Bit LSB Capacity (Higher Capacity)](#n-bit-lsb-capacity-higher-capacity)
    * [4. Strengths and Weaknesses](#4-strengths-and-weaknesses)
<!-- TOC -->

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

## To learn more about the LSB technique
The **Least Significant Bit (LSB)** technique is one of the simplest and most common methods used in **steganography**, the art of concealing a secret message or file within another seemingly innocuous file (the *cover* medium). This technique primarily exploits the subtle nature of digital media, particularly images and audio files, where minor data alterations go unnoticed by the human senses.

![Danger management](/assets/lsb_example.png)

---

### 1. Understanding the Least Significant Bit (LSB)

The LSB is the binary digit in a number that has the lowest weight or smallest value.

#### Binary Weight System
In any binary number (a sequence of 0s and 1s), each bit position corresponds to a power of 2:

| Bit Position | $\mathbf{2^7}$ | $\mathbf{2^6}$ | $\mathbf{2^5}$ | $\mathbf{2^4}$ | $\mathbf{2^3}$ | $\mathbf{2^2}$ | $\mathbf{2^1}$ | $\mathbf{2^0}$ (LSB) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Value | 128 | 64 | 32 | 16 | 8 | 4 | 2 | **1** |

#### Minimal Impact
The **LSB** is the bit furthest to the right (the $2^0$ position). Changing its value (from 0 to 1 or 1 to 0) results in a decimal change of **only $\pm 1$**.

| Binary | Decimal Value | Change in Decimal Value |
| :---: | :---: | :---: |
| **$1001011\mathbf{0}$** | 150 | $\text{Original value}$ |
| **$1001011\mathbf{1}$** | 151 | $+1$ |

This minimal change is the core reason the LSB technique works: it allows data modification with negligible perceptual difference.

---

### 2. LSB Implementation in Digital Images

In digital images, the LSB technique focuses on substituting the LSB of a pixel's color components with the secret message bits.

#### Pixel Structure (RGB)
A typical color image uses the **RGB (Red, Green, Blue)** model, where each pixel's color is defined by three 8-bit values (one byte per channel), ranging from 0 to 255.

* **1 Pixel** = (Red Byte, Green Byte, Blue Byte)
* **Capacity** = 3 Bytes/Pixel = **24 bits/Pixel**

#### The Hiding Process (1-Bit LSB)

The most common LSB method involves using the single least significant bit from each color channel (R, G, and B) to store the secret data. This yields a capacity of **3 secret bits per pixel**.

1.  **Select the Cover Image:** Ensure the image format is non-lossy (e.g., **BMP, PNG**) since lossy formats (like JPEG) discard LSBs during compression.
2.  **Convert Secret Message:** The secret file (text, image, archive) is converted into a binary stream of 0s and 1s.
3.  **Embed Data:**
    * Iterate through the cover image's pixels.
    * For the first pixel, take the first three bits of the secret message.
    * Replace the LSB of the **Red** byte with the **1st secret bit**.
    * Replace the LSB of the **Green** byte with the **2nd secret bit**.
    * Replace the LSB of the **Blue** byte with the **3rd secret bit**.
    * Continue this process until the entire secret message is embedded.

| Channel | Original 8-bit value | LSB | Secret Bit to Embed | Modified 8-bit value |
| :---: | :---: | :---: | :---: | :---: |
| **Red** | $1011001\mathbf{0}$ | $\mathbf{0}$ | $\mathbf{1}$ | $1011001\mathbf{1}$ |
| **Green** | $0100110\mathbf{1}$ | $\mathbf{1}$ | $\mathbf{0}$ | $0100110\mathbf{0}$ |
| **Blue** | $1110011\mathbf{0}$ | $\mathbf{0}$ | $\mathbf{1}$ | $1110011\mathbf{1}$ |

The resulting pixel color has changed by a maximum of one intensity level per channel (e.g., from 178 to 179), a difference that is perceptually insignificant.

---

### 3. Storage Capacity Calculation

The maximum capacity for a secret message is directly calculated from the dimensions and the number of bits used per pixel.

#### 1-Bit LSB Capacity Formula
For an $W \times H$ RGB image using 1-bit LSB substitution:

$$\text{Max Capacity (in Bytes)} = \frac{\text{Width} \times \text{Height} \times 3}{8}$$

* **Example:** A $1024 \times 768$ image has a capacity of $\frac{1024 \times 768 \times 3}{8} \approx 294,912 \text{ bytes (288 KB)}$.

#### N-Bit LSB Capacity (Higher Capacity)
The technique can be extended to use the **$N$ least significant bits** (e.g., 2-bit LSB or 3-bit LSB) to increase capacity, though this leads to a more noticeable visual distortion.

$$\text{Max Capacity (in Bits)} = \text{Width} \times \text{Height} \times \text{Channels} \times N$$

---

### 4. Strengths and Weaknesses

| Type | Strengths | Weaknesses |
| :--- | :--- | :--- |
| **Security** | **High Fidelity:** The modified image (*stego-image*) is visually identical to the original image (*cover-image*). | **Vulnerability:** Highly susceptible to **steganalysis** (detection) and post-processing attacks (e.g., JPEG compression destroys the LSB data). |
| **Simplicity** | **Easy to Implement:** The logic involves simple bitwise operations (AND, OR, XOR) on image bytes. | **Limited Capacity:** While large, the capacity is often limited by the need to maintain low distortion and avoid statistical detection. |