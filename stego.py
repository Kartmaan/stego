import numpy as np
from PIL import Image
import os
import argparse

# Used to indicate the end of hidden data
END_FILE_MARKER = b'END!'

def bytes_to_bits(data_bytes: bytes) -> list[int]:
    """Converts a sequence of bytes into a list of individual bits (0s and 1s).

    Each byte is converted into its 8-bit binary representation, and these
    bits are then appended to a list.

    Args:
        data_bytes (bytes): The input data as a bytes object.

    Returns:
        list[int]: A list of integers, where each integer is either 0 or 1,
                   representing the bits of the input bytes.
    """
    bits = []
    # For each byte in the input data, this loop :
    # 1. bin(byte) converts the byte to a binary string (e.g. '0b1001110').
    # 2. [2:] removes the '0b' prefix ('1001110').
    # 3. zfill(8) pads it with leading zeros to make it 8 digits long ('01001110')
    # 4. Turns that string into a list of integers ([0, 1, 0, 0, 1, 1, 1, 0]).
    # 5. Adds this list of 8 bits to the end of the main bits list.
    for byte in data_bytes:
        bits.extend([int(b) for b in bin(byte)[2:].zfill(8)])
    return bits

def bits_to_bytes(bits: list[int]) -> bytes:
    """Converts a list of individual bits (0s and 1s) into a sequence of bytes.

    The function processes the input list of bits in chunks of 8. Each 8-bit
    chunk is converted into a single byte. Incomplete chunks (less than 8 bits)
    at the end of the list are ignored.

    Args:
        bits (list[int]): A list of integers, where each integer is either 0 or 1,
                          representing the bits to be converted.

    Returns:
        bytes: A bytes object formed by concatenating the converted 8-bit chunks.
               Incomplete trailing bits are discarded.
    """
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

def encode_file(image_path: str, secret_file_path: str, output_image_path: str) -> bool:
    """Hides the data of a secret file in the LSBs (Least Significant Bits) of an image.

    This function embeds the content of a secret file, along with its filename and an
    end-of-file marker, into the LSBs of the pixel data of a carrier image.
    It supports PNG and BMP image formats due to their lossless compression.

    Args:
        image_path (str): The file path to the carrier image (e.g., 'carrier.png').
        secret_file_path (str): The file path to the secret file to be hidden (e.g., 'secret.txt').
        output_image_path (str): The file path where the steganographic image will be saved (e.g., 'stego_image.png').

    Returns:
        bool: True if the encoding was successful, False otherwise (e.g., file not found,
              unsupported image format, or secret file too large).
    """
    # ------------------------------------------------------------------------------
    # Step 1: Extension check
    # ------------------------------------------------------------------------------
    # Since LSB steganography is very sensitive to lossy compression, only .png and .bmp files are allowed
    if not (image_path.lower().endswith(('.png', '.bmp')) or output_image_path.lower().endswith(('.png', '.bmp'))):
        print("Error: Both carrier image and output image must be PNG or BMP files.")
        return False

    # ------------------------------------------------------------------------------
    # Step 2: Prepare the data from the secret file for embedding.
    # ------------------------------------------------------------------------------
    try:
        with open(secret_file_path, 'rb') as f:
            secret_data_bytes = f.read()
    except FileNotFoundError:
        print(f"Error: Secret file '{secret_file_path}' not found.")
        return False

    # Prepare the filename and the end-of-file marker for the payload.
    # Get the base name of the secret file and encode it to UTF-8 bytes.
    file_name = os.path.basename(secret_file_path).encode('utf-8')

    # Define the structure of the data to be hidden.
    # The payload consists of the filename, a separator, the file's data, and an end marker.
    # [File name] + b'|' + [File's data] + [End marker]
    payload_bytes = file_name + b'|' + secret_data_bytes + END_FILE_MARKER
    message_bits = bytes_to_bits(payload_bytes) # Convert the entire payload into a list of individual bits.

    # ------------------------------------------------------------------------------
    # Step 3: Load the carrier image and convert its pixel data into a NumPy array.
    # ------------------------------------------------------------------------------
    img = Image.open(image_path).convert('RGB') # Open the carrier image and convert it to RGB format
    data = np.array(img, dtype=np.uint8) # Convert the PIL Image object into a NumPy array of unsigned 8-bit integers.

    # ------------------------------------------------------------------------------
    # Step 4: Check if the carrier image has enough capacity to hide the secret data.
    # ------------------------------------------------------------------------------
    # Explanation: Each byte (pixel component) in the image can store one bit of secret data.
    max_bits = data.size

    # Compare the length of the secret message bits with the maximum capacity.
    if len(message_bits) > max_bits:
        print("Error: Secret file is too big")
        return False

    # ------------------------------------------------------------------------------
    # Step 5: Embed the secret bits into the LSBs of the image's pixel data.
    # ------------------------------------------------------------------------------
    pixels_flat = data.flatten() # Flatten the 3D NumPy array of pixel data into a 1D array for easier iteration.

    # Iterate through each bit of the secret message and its corresponding pixel component.
    for i, bit in enumerate(message_bits):
        current_byte = pixels_flat[i] # Get the current pixel component (byte) from the flattened array.

        # Clear the Least Significant Bit of the current byte. For this, we use a bitwise AND operation with a mask
        # (11111110) to set the LSB to 0.
        # Example :
        # Current byte = 10000111
        # Mask = 11111110
        # -> 10000111 & 11111110 = 10000110
        # Resetting the LSB prepares the byte for insertion of the secret bit, whether 0 or 1.
        # The purpose of the operation is therefore not to "change" the bit, but to ensure that it is zero.
        # This creates a reliable "empty space" for the next step, which is to insert the secret message bit with
        # the |= operation.
        new_byte = current_byte & 0b11111110

        # Insert the secret bit into the cleared LSB position.For this, we use a bitwise OR operation with the secret
        # bit (0 or 1) to set the LSB.
        # Example :
        # Current byte = 10000110
        # Secret bit = 00000001 (1)
        # -> 10000110 | 00000001 = 10000111
        # This operation is the final touch that writes the secret bit to the pixel's byte.
        # It works reliably because the previous step prepared the groundwork by setting the destination bit to 0.
        # The OR operation can then "turn on" this bit if it should be 1, or leave it "off" if it should be 0, without *
        # ever disturbing the other 7 more significant bits in the byte.
        new_byte |= bit

        # Update the pixel component in the flattened array with the new byte containing the hidden bit.
        pixels_flat[i] = new_byte

    # ------------------------------------------------------------------------------
    # Step 6: Reshape the modified pixel data back into an image and save it.
    # ------------------------------------------------------------------------------
    stego_data = pixels_flat.reshape(data.shape) # Reshape the flattened array back to the original 3D shape of the image.
    stego_img = Image.fromarray(stego_data) # Create a new PIL Image object from the modified NumPy array.
    stego_img.save(output_image_path) # Save the steganographic image to the specified output path.

    print(f"Encoding successful. {len(secret_data_bytes)} hidden bytes. Image saved as : {output_image_path}")
    return True

def decode_file(image_path: str, output_dir: str = "extracted") -> bool:
    """Extracts a hidden file from a steganographic image by reading the LSBs
    of its pixel data.

    The function searches for an end-of-file marker to determine the extent
    of the hidden data. It then reconstructs the original filename and file
    content, saving the extracted file to the specified output directory.

    Args:
        image_path (str): The file path to the steganographic image
                          (e.g., 'stego_image.png').
        output_dir (str, optional): The directory where the extracted file
                                    will be saved. Defaults to "extracted".

    Returns:
        bool: True if the decoding was successful and a file was extracted,
              False otherwise (e.g., end marker not found, data corrupted).
    """
    # ------------------------------------------------------------------------------
    # Step 1: Load the image and convert it to a NumPy array
    # ------------------------------------------------------------------------------
    img = Image.open(image_path).convert('RGB')
    data = np.array(img, dtype=np.uint8)
    pixels_flat = data.flatten() # Flatten the 3D NumPy array of pixel data into a 1D array for easier iteration.

    # ------------------------------------------------------------------------------
    # Step 2: LSB extraction and end marker detection
    # ------------------------------------------------------------------------------
    secret_bits = [] # Initialize an empty list to store the extracted secret bits.
    marker_bits = bytes_to_bits(END_FILE_MARKER) # Convert the end-of-file marker bytes into a list of bits.
    marker_len = len(marker_bits) # Get the length of the end-of-file marker in bits.

    # Iteration to extract the LSB's until the end of the image is reached
    # or the end marker is found
    for i in range(len(pixels_flat)):
        lsb = pixels_flat[i] & 0b00000001 # Extract the Least Significant Bit (LSB) from the current pixel component.
        secret_bits.append(lsb) # Append the extracted LSB to the list of secret bits.

    # Checks if the end of the message is reached
        if len(secret_bits) >= marker_len:
            # Check if the last 'marker_len' bits match the end-of-file marker.
            if secret_bits[-marker_len:] == marker_bits:
                # Convert the extracted secret bits (excluding the marker) back into bytes.
                data_payload_bytes = bits_to_bytes(secret_bits[:-marker_len])
                break # Exit the loop as the end marker has been found.

    # Print an error if the loop finishes without finding the marker.
    else:
        print("Error: End marker not found. No hidden data found.")
        return False # Return False to indicate decoding failure.

    # ------------------------------------------------------------------------------
    # Step 3: Separation between file name and data
    # ------------------------------------------------------------------------------
    separator = b'|' # Define the separator byte used to distinguish the filename from the file data.

    # Find the index of the separator byte within the payload.
    try:
        separator_index = data_payload_bytes.index(separator)
    except ValueError:
        print("Error : File name separator not found. Data corrupted")
        return False

    # Extract the filename bytes and decode them to a UTF-8 string.
    file_name = data_payload_bytes[:separator_index].decode('utf-8')

    # Extract the actual file data, which comes after the separator.
    file_data = data_payload_bytes[separator_index+1:]

    # ------------------------------------------------------------------------------
    # Step 4: Save the data
    # ------------------------------------------------------------------------------
    if not os.path.exists(output_dir): # Check if the output directory exists.
        os.makedirs(output_dir) # Create the output directory if it doesn't exist.

    output_file_path = os.path.join(output_dir, file_name) # Construct the full path for the extracted file.

    with open(output_file_path, 'wb') as f: # Open the output file in binary write mode.
        f.write(file_data) # Write the extracted file data to the file.

    print(f"\nDecoding successful. Secret file saved as : {output_file_path} ({len(file_data)} bytes))")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="LSB steganography tool to hide and reveal files in PNG/BMP images.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help='Subcommand to execute: hide or reveal')

    # ------------------------------------------------------------------------------
    # Hide command
    # ------------------------------------------------------------------------------
    parser_hide = subparsers.add_parser('hide', help='Hide a file in an image',
                                        description="Usage: python stego.py hide <carrier_image> <secret_file> <output_stego_image>")
    parser_hide.add_argument('carrier_image', type=str, help='Path to the carrier image')
    parser_hide.add_argument('secret_file', type=str, help='Path to the secret file')
    parser_hide.add_argument('output_image', type=str, help='Path to the output stego image')

    # ------------------------------------------------------------------------------
    # Reveal command
    # ------------------------------------------------------------------------------
    parser_reveal = subparsers.add_parser('reveal', help='Reveal a file from an image',
                                          description="Usage: python stego.py reveal <image_stego>")
    parser_reveal.add_argument('image_stego', type=str, help='Path to the stego image')
    parser_reveal.add_argument('--output_dir', type=str, default='extracted', help='Path to the output stego image')

    # ------------------------------------------------------------------------------
    # Parse arguments and execute the selected command
    # ------------------------------------------------------------------------------
    args = parser.parse_args()

    if args.command == 'hide':
        encode_file(args.carrier_image, args.secret_file, args.output_image)
    elif args.command == 'reveal':
        decode_file(args.image_stego, args.output_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()