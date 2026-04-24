import sys
import os
from astropy.io import fits

def save_fits_header():
    # Check if a filename was provided in the command line
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <path_to_fits_file>")
        return

    input_file = sys.argv[1]

    # Verify the file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    try:
        # Open the FITS file
        with fits.open(input_file) as hdul:
            # Get the primary header (index 0)
            header = hdul[0].header
            
            # Create the output filename by swapping extension to .txt
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.txt"

            # Write the header to the text file
            with open(output_file, 'w') as f:
                f.write(repr(header))
            
            print(f"Success! Header saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    save_fits_header()