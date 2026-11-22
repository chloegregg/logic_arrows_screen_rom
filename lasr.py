import arrows
from PIL import Image

# don't read this it's garbage

WALL_PALETTE = Image.new("P", (1, 1))
WALL_PALETTE.putpalette([
    190, 190, 190,
    190, 0, 0,
    95, 133, 190,
    190, 190, 0,
    0, 171, 0,
    190, 133, 19,
    152, 114, 171,
    0, 0, 0
])

def get_image_data(img: Image.Image, size: tuple[int, int], layout_brightness: float, gamma: float = 1.5, padding: int = 8) -> list[tuple[float, ...]]:
    img = img.convert("RGB").resize(size)
    res = Image.new("RGB", (size[0] + padding + 1, size[1] + padding + 1))
    for x in range(size[0] + padding + 1):
        for y in range(size[1] + padding + 1):
            res.putpixel((x, y), img.getpixel((min(max(x - padding, 0), size[0] - 1), min(max(y - padding, 0), size[1] - 1)))) # type: ignore
    return [tuple((c/255) ** gamma * layout_brightness for c in pix) for pix in res.getdata()] # type: ignore

def encode_image(img: Image.Image, size: tuple[int, int], layout: Image.Image, gamma: float = 1.5, padding: int = 8) -> list[list[bool]]:
    layout_data: list[tuple[float, ...]] = [tuple((c/255) for c in pix) for pix in layout.convert("RGB").getdata()] # type: ignore
    layout_brightness = min(sum(pix[c] for pix in layout_data) / len(layout_data) for c in range(3))
    data = get_image_data(img, size, layout_brightness, gamma, padding)
    

    dithered = []
    padded = (size[0] + padding + 1, size[1] + padding + 1)
    for y in range(padded[1]):
        dithered.append([])
        for x in range(padded[0]):
            colour = layout_data[(x - padding) % layout.width + (y - padding) % layout.height * layout.width]
            index = x + y * padded[0]
            if sum(d * c for d, c in zip(data[index], colour)) > 0.5:
                data[index] = tuple(d - c for d, c in zip(data[index], colour))
                dithered[-1].append(True)
            else:
                dithered[-1].append(False)
            
            if x < padded[0] - 1:
                data[index + 1] = tuple(d + 7/16 * s for d, s in zip(data[index + 1], data[index]))
                if y < padded[1] - 1:
                    data[index + 1 + padded[0]] = tuple(d + 1/16 * s for d, s in zip(data[index + 1 + padded[0]], data[index]))
            if y < padded[1] - 1:
                data[index + padded[0]] = tuple(d + 5/16 * s for d, s in zip(data[index + padded[0]], data[index]))
                if x > 0:
                    data[index - 1 + padded[0]] = tuple(d + 3/16 * s for d, s in zip(data[index - 1 + padded[0]], data[index]))
    return [
        [
            dithered[y + padding][x + padding]
            for x in range(size[0])
        ]
        for y in range(size[1])
    ]

def draw_dithered(dithered: list[list[bool]], layout: Image.Image) -> Image.Image:
    layout_data: list[tuple[int, ...]] = layout.convert("RGB").getdata() # type: ignore
    img = Image.new("RGB", (len(dithered[0]), len(dithered)), (0, 0, 0))
    for y in range(len(dithered)):
        for x in range(len(dithered[0])):
            if dithered[y][x]:
                img.putpixel((x, y), layout_data[x % layout.width + y % layout.height * layout.width])
    return img

def dithered_to_rom(dithered: list[list[bool]], version: int = 5) -> arrows.Map:
    map = arrows.Map()
    map.version = version

    for x in range(len(dithered[0])):
        map.get(x*3, -1).type = arrows.ArrowType.BlueArrow
        map.get(x*3, -1).direction = arrows.Direction.East
        map.get(x*3 + 2, -1).type = arrows.ArrowType.BlueArrow
        map.get(x*3 + 2, -1).direction = arrows.Direction.North
    for y in range(0, len(dithered), 2):
        offset = 0 if y % 4 == 0 else 1
        for x in range(len(dithered[0])):
            map.get(x*3 + offset, y).direction = arrows.Direction.East
            if dithered[y][x] and dithered[y + 1][x]:
                map.get(x*3 + offset, y).type = arrows.ArrowType.SplitterUpRightLeft
            elif dithered[y][x]:
                map.get(x*3 + offset, y).type = arrows.ArrowType.SplitterUpRight
                map.get(x*3 + offset, y).direction = arrows.Direction.North
            elif dithered[y + 1][x]:
                map.get(x*3 + offset, y).type = arrows.ArrowType.SplitterUpRight
            else:
                map.get(x*3 + offset, y).type = arrows.ArrowType.Arrow
                
            map.get(x*3 + offset + 1, y).type = arrows.ArrowType.BlueArrow
            map.get(x*3 + offset + 1, y).direction = arrows.Direction.East

            if offset:
                map.get(x*3, y+1).type = arrows.ArrowType.BlueArrow
                map.get(x*3, y+1).direction = arrows.Direction.East
                map.get(x*3 + 1, y+1).type = arrows.ArrowType.Diagonal
                map.get(x*3 + 1, y+1).direction = arrows.Direction.East
                map.get(x*3 + 2, y+2).type = arrows.ArrowType.Delay
                map.get(x*3 + 2, y+2).direction = arrows.Direction.North
            else:
                map.get(x*3, y+1).type = arrows.ArrowType.Delay
                map.get(x*3, y+1).direction = arrows.Direction.East
                map.get(x*3 + 1, y+1).type = arrows.ArrowType.Arrow
                map.get(x*3 + 1, y+1).direction = arrows.Direction.East
            map.get(x*3 + 2, y+1).type = arrows.ArrowType.BlueArrow
            map.get(x*3 + 2, y+1).direction = arrows.Direction.North

        if offset:
            map.get(-1, y).type = arrows.ArrowType.BlueSplitterRightUp
        else:
            map.get(-1, y).type = arrows.ArrowType.SplitterUpRight
        map.get(-1, y).direction = arrows.Direction.East
        map.get(-1, y+1).type = arrows.ArrowType.Delay
        map.get(-1, y+1).direction = arrows.Direction.West
        map.get(-2, y+1).type = arrows.ArrowType.Arrow
        map.get(-2, y+1).direction = arrows.Direction.South
        map.get(-2, y+2).type = arrows.ArrowType.Arrow
        map.get(-2, y+2).direction = arrows.Direction.East
    return map

def image_to_walls(img: Image.Image, version: int = 5) -> arrows.Map:
    colours = list(img.getdata()) # type: ignore

    map = arrows.Map()
    map.version = version

    for y in range(img.height):
        for x in range(img.width):
            map.get(x, y).type = arrows.ArrowType.Wall
            map.get(x, y).color = colours[x + y * img.width]
    return map

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("width", type=int, help="screen width in pixels")
    parser.add_argument("height", type=int, help="screen height in pixels")
    parser.add_argument("file", type=str, help="source image path")
    parser.add_argument("-c", "--copy", action="store_true", help="copy code to clipboard")
    parser.add_argument("-p", "--padding", type=int, default=8, help="add padding around the edge of the image for better dithering")
    parser.add_argument("-g", "--gamma", type=float, default=1.5, help="gamma correction factor")
    parser.add_argument("-v", "--version", type=int, default=5, help="logic arrows map version")
    parser.add_argument("-w", "--walls", action="store_true", help="generate walls instead of rom")
    parser.add_argument("-l", "--layout", type=str, help="layout image path")
    parser.add_argument("-o", "--output", type=str, help="store a preview of the rom as an image at this path")
    args = parser.parse_args()
    
    img = Image.open(args.file)
    size = (args.width, args.height)
    if args.walls:
        quant = img.resize(size).quantize(palette=WALL_PALETTE)
        code = image_to_walls(quant, version=args.version).export()
        if args.output is not None:
            quant.save(args.output)
    else:
        if args.layout:
            layout = Image.open(args.layout)
        else:
            layout = Image.new("RGB", (3, 3))
            layout.putdata([255, 255 << 8, 255 << 16,  255 << 8, 255 << 16, 255,  255 << 16, 255, 255 << 8])
        dithered = encode_image(img, size, layout, padding=args.padding, gamma=args.gamma)
        code = dithered_to_rom(dithered, version=args.version).export()
        if args.output is not None:
            draw_dithered(dithered, layout).save(args.output)
    if args.copy:
        import pyperclip
        pyperclip.copy(code)
    else:
        print(code)
