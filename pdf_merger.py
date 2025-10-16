import sys
import argparse
from pypdf import PdfReader, PdfWriter, Transformation

# A4 dimensions in points (1 point = 1/72 inch)
A4_LANDSCAPE_WIDTH = 841.890
A4_LANDSCAPE_HEIGHT = 595.276

def create_pro_2_up_pdf(input_path: str, output_path: str, crop_percent: float, gutter_bias: float, x_offset: float, y_offset: float):
    """
    Crops margins asymmetrically, creates a 2-up layout, and allows manual
    placement adjustments for a professional result.

    Args:
        input_path: Path to the source PDF file.
        output_path: Path where the new PDF will be saved.
        crop_percent: The base percentage of margin to crop.
        gutter_bias: Multiplier for inner margin crop (1.0 is symmetric).
        x_offset: Manual horizontal shift in points.
        y_offset: Manual vertical shift in points.
    """
    try:
        reader = PdfReader(input_path)
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        sys.exit(1)

    writer = PdfWriter()
    num_pages = len(reader.pages)
    print(f"Processing {num_pages} pages with {crop_percent}% crop and {gutter_bias}x gutter bias...")

    target_width_per_page = A4_LANDSCAPE_WIDTH / 2
    target_height_per_page = A4_LANDSCAPE_HEIGHT

    for i in range(0, num_pages, 2):
        new_page = writer.add_blank_page(width=A4_LANDSCAPE_WIDTH, height=A4_LANDSCAPE_HEIGHT)

        # --- Process the left page (ODD page, e.g., 1, 3, 5...) ---
        if i < num_pages:
            page_left = reader.pages[i]
            original_w = float(page_left.mediabox.width)
            original_h = float(page_left.mediabox.height)

            # --- NEW: Asymmetric Cropping Logic ---
            base_crop_x = original_w * (crop_percent / 100.0)
            base_crop_y = original_h * (crop_percent / 100.0)

            # For an ODD page, the inner margin is on the RIGHT.
            crop_inner_x = base_crop_x * gutter_bias
            crop_outer_x = base_crop_x * (2.0 - gutter_bias) # Ensures total crop is consistent

            page_left.cropbox.lower_left = (crop_outer_x, base_crop_y)
            page_left.cropbox.upper_right = (original_w - crop_inner_x, original_h - base_crop_y)
            
            # Scale and place using cropped dimensions
            cropped_w = float(page_left.cropbox.width)
            cropped_h = float(page_left.cropbox.height)
            scale = min(target_width_per_page / cropped_w, target_height_per_page / cropped_h)
            scaled_w, scaled_h = cropped_w * scale, cropped_h * scale
            tx = (target_width_per_page - scaled_w) / 2 + x_offset
            ty = (target_height_per_page - scaled_h) / 2 + y_offset

            transform_left = Transformation().scale(sx=scale, sy=scale).translate(tx=tx, ty=ty)
            new_page.merge_transformed_page(page_left, transform_left)

        # --- Process the right page (EVEN page, e.g., 2, 4, 6...) ---
        if i + 1 < num_pages:
            page_right = reader.pages[i + 1]
            original_w = float(page_right.mediabox.width)
            original_h = float(page_right.mediabox.height)
            
            # --- NEW: Asymmetric Cropping Logic ---
            base_crop_x = original_w * (crop_percent / 100.0)
            base_crop_y = original_h * (crop_percent / 100.0)
            
            # For an EVEN page, the inner margin is on the LEFT.
            crop_inner_x = base_crop_x * gutter_bias
            crop_outer_x = base_crop_x * (2.0 - gutter_bias)

            page_right.cropbox.lower_left = (crop_inner_x, base_crop_y)
            page_right.cropbox.upper_right = (original_w - crop_outer_x, original_h - base_crop_y)
            
            # Scale and place
            cropped_w = float(page_right.cropbox.width)
            cropped_h = float(page_right.cropbox.height)
            scale = min(target_width_per_page / cropped_w, target_height_per_page / cropped_h)
            scaled_w, scaled_h = cropped_w * scale, cropped_h * scale
            tx = (A4_LANDSCAPE_WIDTH / 2) + (target_width_per_page - scaled_w) / 2 + x_offset
            ty = (target_height_per_page - scaled_h) / 2 + y_offset
            
            transform_right = Transformation().scale(sx=scale, sy=scale).translate(tx=tx, ty=ty)
            new_page.merge_transformed_page(page_right, transform_right)

    try:
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"✅ Success! Created '{output_path}' with {len(writer.pages)} pages.")
    except Exception as e:
        print(f"Error: Could not write to output file '{output_path}'.")
        print(e)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Pro PDF tool for cropping and 2-up conversion.")
    parser.add_argument("input_pdf", help="Source PDF file.")
    parser.add_argument("output_pdf", help="Output PDF file.")
    parser.add_argument("--crop", type=float, default=0.0, help="Base percentage of margin to crop from each side (e.g., 10).")
    parser.add_argument("--gutter_bias", type=float, default=1.0, help="Inner margin crop multiplier. >1.0 crops more from the center. (e.g., 1.8)")
    parser.add_argument("--x_offset", type=float, default=0.0, help="Horizontal shift in points (positive is right).")
    parser.add_argument("--y_offset", type=float, default=0.0, help="Vertical shift in points (positive is up).")
    
    args = parser.parse_args()
    if not (0 <= args.crop < 50):
        print("Error: Crop percentage must be between 0 and 49.")
        sys.exit(1)
    if not (0 <= args.gutter_bias <= 2):
        print("Error: Gutter bias must be between 0.0 and 2.0.")
        sys.exit(1)
        
    create_pro_2_up_pdf(args.input_pdf, args.output_pdf, args.crop, args.gutter_bias, args.x_offset, args.y_offset)

if __name__ == "__main__":
    main()
