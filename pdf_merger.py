import sys
import argparse
from pypdf import PdfReader, PdfWriter, Transformation

# A4 dimensions in points (1 point = 1/72 inch)
A4_LANDSCAPE_WIDTH = 841.890
A4_LANDSCAPE_HEIGHT = 595.276

def create_pdf(input_path: str, output_path: str, crop_settings: dict, x_offset: float, y_offset: float):
    """
    Crops margins with individual per-edge control, creates a 2-up layout,
    and allows manual placement adjustments.

    Args:
        input_path: Path to the source PDF file.
        output_path: Path where the new PDF will be saved.
        crop_settings: A dictionary with crop percentages for top, bottom, left, right.
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
    print(f"Processing {num_pages} pages with custom crop settings...")
    print(f"Crop settings: Top={crop_settings['top']}%, Bottom={crop_settings['bottom']}%, Left={crop_settings['left']}%, Right={crop_settings['right']}%")

    target_width_per_page = A4_LANDSCAPE_WIDTH / 2
    target_height_per_page = A4_LANDSCAPE_HEIGHT

    for i in range(0, num_pages, 2):
        new_page = writer.add_blank_page(width=A4_LANDSCAPE_WIDTH, height=A4_LANDSCAPE_HEIGHT)

        # Process up to two pages for the new sheet
        for page_index_in_pair in range(2):
            current_page_num = i + page_index_in_pair
            if current_page_num >= num_pages:
                continue

            page = reader.pages[current_page_num]
            original_w = float(page.mediabox.width)
            original_h = float(page.mediabox.height)

            # --- NEW: Per-Edge Cropping Logic ---
            crop_top = original_h * (crop_settings['top'] / 100.0)
            crop_bottom = original_h * (crop_settings['bottom'] / 100.0)
            crop_left = original_w * (crop_settings['left'] / 100.0)
            crop_right = original_w * (crop_settings['right'] / 100.0)

            # Set the page's cropBox to the new, smaller area.
            page.cropbox.lower_left = (crop_left, crop_bottom)
            page.cropbox.upper_right = (original_w - crop_right, original_h - crop_top)

            # Scale and place using cropped dimensions
            cropped_w = float(page.cropbox.width)
            cropped_h = float(page.cropbox.height)
            scale = min(target_width_per_page / cropped_w, target_height_per_page / cropped_h)
            scaled_w, scaled_h = cropped_w * scale, cropped_h * scale

            # Calculate centered position + manual offset
            ty = (target_height_per_page - scaled_h) / 2 + y_offset
            
            # Position left or right page
            if page_index_in_pair == 0: # Left page
                tx = (target_width_per_page - scaled_w) / 2 + x_offset
            else: # Right page
                tx = (A4_LANDSCAPE_WIDTH / 2) + (target_width_per_page - scaled_w) / 2 + x_offset

            transform = Transformation().scale(sx=scale, sy=scale).translate(tx=tx, ty=ty)
            new_page.merge_transformed_page(page, transform)

    try:
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"✅ Success! Created '{output_path}' with {len(writer.pages)} pages.")
    except Exception as e:
        print(f"Error: Could not write to output file '{output_path}'.")
        print(e)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Professional PDF tool for 2-up conversion with per-edge margin control.")
    parser.add_argument("input_pdf", help="Source PDF file.")
    parser.add_argument("output_pdf", help="Output PDF file.")
    parser.add_argument("--crop_top", type=float, default=0.0, help="Percentage to crop from the top margin.")
    parser.add_argument("--crop_bottom", type=float, default=0.0, help="Percentage to crop from the bottom margin.")
    parser.add_argument("--crop_left", type=float, default=0.0, help="Percentage to crop from the left margin.")
    parser.add_argument("--crop_right", type=float, default=0.0, help="Percentage to crop from the right margin.")
    parser.add_argument("--x_offset", type=float, default=0.0, help="Horizontal shift in points (positive is right).")
    parser.add_argument("--y_offset", type=float, default=0.0, help="Vertical shift in points (positive is up).")
    
    args = parser.parse_args()
    
    crop_settings = {
        'top': args.crop_top,
        'bottom': args.crop_bottom,
        'left': args.crop_left,
        'right': args.crop_right
    }

    # Basic validation
    for edge, value in crop_settings.items():
        if not (0 <= value < 50):
            print(f"Error: Crop percentage for '{edge}' must be between 0 and 49.")
            sys.exit(1)
            
    create_pdf(args.input_pdf, args.output_pdf, crop_settings, args.x_offset, args.y_offset)

if __name__ == "__main__":
    main()
