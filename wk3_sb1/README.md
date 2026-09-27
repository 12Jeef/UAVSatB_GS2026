# Blob Detection

## Usage

`test_stream.py` - Runs color blob detection on live camera stream. Cycle through the colors using the left/right arrow keys.

`test_images.py` - Runs color blob detection with circle thresholding on the provided images. I only coded in `objects.jpg`, `polka_dots_1.png`, and `polka_dots_2.jpg` because I'm lazy.

## Code

The core of everything is in `detect.py`. This bit of code runs similar logic to Week 2 Skill Booster 1: Color Me Impressed. It does HSV conversion and thresholding/masking. It provides built-in thresholding (`Color`) and a more generalized interface (`Filter`). Here's how it generally works:
1. Take in a frame, convert to HSV
2. Determine HSV ranges to mask
3. `|` (bitwise or) individual masks from `cv2::inRange`
4. Erode and dilate (removes speckles)
5. Detect contours

I opted to not use OpenCV's `SimpleBlobDetector` because we can do cooler things with raw contours. Here, we are simply running a score calculation for circularity using area and perimeter. There is a way to determine "rectangularity" (I've implemented it before once) but it is not shown here, since polka dots aren't quite rectangular.
