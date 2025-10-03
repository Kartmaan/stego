import numpy as np
from PIL import Image
import os
import argparse

# Used to indicate the end of hidden data
END_FILE_MARKER = b'END!'

# --- Data convertion functions ---

def bytes_to_bits(data_bytes):
    """Converts bytes to a list of bits (0 or 1)"""
    bits = []
    # For each byte in the input data, this loop :
    # 1. bin(byte) converts the byte to a binary string (e.g., 78 -> '0b1001110').
    # 2. [2:] removes the '0b' prefix ('1001110').
    # 3. zfill(8) pads it with leading zeros to make it 8 digits long ('01001110')
    # 4. Turns that string into a list of integers ([0, 1, 0, 0, 1, 1, 1, 0]).
    # 5. Adds this list of 8 bits to the end of the main bits list.
    for byte in data_bytes:
        bits.extend([int(b) for b in bin(byte)[2:].zfill(8)])
    return bits

def bits_to_bytes(bits):
    """Converts a list of bits (0 or 1) to bytes"""
    output_bytes = bytearray()

    # This loop iterates though the bits list, but not one bit at a time
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8] # list slicing to grab an 8-bit chunk from the list
        # This is a safety check. It ensures that we only process full 8-bit chunks.
        # If the total number of bits in the input list is not a perfect multiple of 8,
        # the last chunk will be shorter than 8 bits. This if statement causes those
        # incomplete chunks to be ignored.
        if len(byte_bits) == 8:
            byte_str = "".join(map(str, byte_bits))
            output_bytes.append(int(byte_str, 2))

    return bytes(output_bytes)

def encode_file(image_path, secret_file_path, output_image_path):
    """Hides the data of a secret file in the LSBs of an image"""
    # 1. Prepare the secret file data
    try:
        with open(secret_file_path, 'rb') as f:
            secret_data_bytes = f.read()
    except FileNotFoundError:
        print(f"Error: Secret file '{secret_file_path}' not found.")
        return False

    # Include file name (for decoding) and end marker
    file_name = os.path.basename(secret_file_path).encode('utf-8')

    # Structure des données cachées :
    # [File name] + b'|' + [File's data] + [End marker]
    payload_bytes = file_name + b'|' + secret_data_bytes + END_FILE_MARKER
    message_bits = bytes_to_bits(payload_bytes)

    # 2. Load the carrier image and convert it to a NumPy array
    img = Image.open(image_path).convert('RGB')
    data = np.array(img, dtype=np.uint8)

    # 3. Capacity check
    # Each byte can contain 1 bit
    max_bits = data.size

    if len(message_bits) > max_bits:
        print("Error: Secret file is too big")
        return False

    # 4. LSB insertion (same as text encoding)
    pixels_flat = data.flatten()

    for i, bit in enumerate(message_bits):
        current_byte = pixels_flat[i]

        # Delete the LSB (AND operator)
        new_byte = current_byte & 0b11111110

        # Insert the secret bit (OR with 0 or 1)
        new_byte |= bit

        pixels_flat[i] = new_byte

    # 5. Rebuild and save the image
    stego_data = pixels_flat.reshape(data.shape)
    stego_img = Image.fromarray(stego_data, 'RGB')
    stego_img.save(output_image_path)

    print(f"Encoding successful. {len(secret_data_bytes)} hidden bytes. Image saved as : {output_image_path}")
    return True

def decode_file(image_path, output_dir="extracted"):
    """Extracts the secret file from an image by reading the LSBs of the
    image"""
    # 1. Load the image and convert it to a NumPy array
    img = Image.open(image_path).convert('RGB')
    data = np.array(img, dtype=np.uint8)
    pixels_flat = data.flatten()

    # 2. LSB extraction and end marker detection
    secret_bits = []
    marker_bits = bytes_to_bits(END_FILE_MARKER)
    marker_len = len(marker_bits)

    # Iteration to extract the LSB's until the end of the image is reached
    # or the end marker is found
    for i in range(len(pixels_flat)):
        lsb = pixels_flat[i] & 0b00000001
        secret_bits.append(lsb)

    # Checks if the end of the message is reached
        if len(secret_bits) >= marker_len:
            if secret_bits[-marker_len:] == marker_bits:
                data_payload_bytes = bits_to_bytes(secret_bits[:-marker_len])
                break

    else:
        print("Error: End marker not found. No hidden data found.")
        return False

    # 3. Separation between file name and data

    separator = b'|'

    try:
        separator_index = data_payload_bytes.index(separator)
    except ValueError:
        print("Error : File name separator not found. Data corrupted")
        return False

    file_name = data_payload_bytes[:separator_index].decode('utf-8')
    file_data = data_payload_bytes[separator_index+1:]

    # 4. Save the data
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path = os.path.join(output_dir, file_name)

    with open(output_file_path, 'wb') as f:
        f.write(file_data)

    print(f"\nDecoding successful. Secret file saved as : {output_file_path} ({len(file_data)} bytes))")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="LSB steganography tool to hide and reveal files in PNG/BMP images.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help='Subcommand to execute: hide or reveal')

    # Hide command
    parser_hide = subparsers.add_parser('hide', help='Hide a file in an image',
                                        description="Usage: python stego.py hide <carrier_image> <secret_file> <output_stego_image>")
    parser_hide.add_argument('carrier_image', type=str, help='Path to the carrier image')
    parser_hide.add_argument('secret_file', type=str, help='Path to the secret file')
    parser_hide.add_argument('output_image', type=str, help='Path to the output stego image')

    # Reveal command
    parser_reveal = subparsers.add_parser('reveal', help='Reveal a file from an image',
                                          description="Usage: python stego.py reveal <image_stego>")
    parser_reveal.add_argument('image_stego', type=str, help='Path to the stego image')
    parser_reveal.add_argument('--output_dir', type=str, default='extracted', help='Path to the output stego image')

    # Parse arguments
    args = parser.parse_args()

    # Execute the selected command
    if args.command == 'hide':
        encode_file(args.carrier_image, args.secret_file, args.output_image)
    elif args.command == 'reveal':
        decode_file(args.image_stego, args.output_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()