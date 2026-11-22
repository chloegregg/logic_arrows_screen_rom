Basic command line tool for creating Logic Arrows Screen ROMs.

```
usage: lasr.py [-h] [-c] [-p PADDING] [-g GAMMA] [-v VERSION] [-w] [-l LAYOUT] [-o OUTPUT] width height file

positional arguments:
  width                 screen width in pixels
  height                screen height in pixels
  file                  source image path

options:
  -h, --help            show this help message and exit
  -c, --copy            copy code to clipboard
  -p PADDING, --padding PADDING
                        add padding around the edge of the image for better dithering
  -g GAMMA, --gamma GAMMA
                        gamma correction factor
  -v VERSION, --version VERSION
                        logic arrows map version
  -w, --walls           generate walls instead of rom
  -l LAYOUT, --layout LAYOUT
                        layout image path
  -o OUTPUT, --output OUTPUT
                        store a preview of the rom as an image at this path
```

Includes and uses a copy of https://github.com/kala-telo/arrows.py.

Depends on:
- `PIL` (`pillow`) for image processing
- `argparse` for command line arguments
- `pyperclip` for clipboard functionality (optional)
