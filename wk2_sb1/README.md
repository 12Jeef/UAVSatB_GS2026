# Color Me Impressed

## Usage
Through command line, after `python3 main.py` place your image files to parse. Optionally, put `-o`, which will tell the program to place all the output images into a certain directory.

For testing purposes, since `tmp` is gitignore'd, use `-o tmp`. The folder will not be created, so be wary of that (idk why it isn't, I'm lazy).

## Code
Constants at the top for modification. Here is how colors are split up:

| Color | Hue range | Saturation range | Value range |
| - | - | - | - |
| Black | any | any | low |
| Gray | any | low | mid |
| White | any | low | high |
| Red/yellow/etc | depends | high | mid-high |

I think this should comprehensively cover all of the HSV 3d space. But I am not sure. It's hard to visualize...

Provided are certain thresholds:
- `SHADE_S_THRESH`: difference between low and high saturation (shade vs. color)
- `BLACK_V_THRESH`: what determines low value
- `WHITE_V_THRESH`: what determines high value
