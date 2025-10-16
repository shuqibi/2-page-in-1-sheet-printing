# 2-page-in-1-sheet-printing



# PDF Page Saver

This Python script transforms any PDF into a compact, paper-saving format by cropping unnecessary margins and arranging two pages side-by-side on a single landscape A4 sheet. It's perfect for printing academic papers where you want to maximize readability while minimizing paper usage. The script provides controls to asymmetrically crop "gutter" margins.

## Example Output

Here is a before-and-after comparison showing how a standard academic paper is transformed into a compact, print-ready format.

![Example Output](example.png)

*(To create this image, take a screenshot of your original PDF next to the output from this script and save it as `example.png` in this repository.)*


### Example Command

```bash
python pdf.py input.pdf output.pdf --crop 8 --x_offset -43 --y_offset -80 --gutter_bias 1.2
