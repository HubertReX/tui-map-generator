#!/usr/bin/env python3
from copy import deepcopy
import json
import random
import math
from sys import argv
from typing import cast
import struct
from rich.segment import Segment, Segments
from rich.style import Style
# from rich.panel import Panel
from rich_pixels import Pixels
from rich.console import Console
import pyrexpaint
from pathlib import Path
import click
from trogon import tui
# Example usage:
HEIGHT_NIL: int = 0
HEIGHT_MIN: int = 1
HEIGHT_MAX: int = 16
# must be n^2 + 1
HEIGHT_MAP_SIZE = 65
ROUGHNESS: float = 16.0
RANDOM_SCALAR: float = ROUGHNESS
RANDOM_SEED = 111
COLOR_PALETTE = "landscape_16"

PRINT_FORMAT_LEN: int = 3
JSON_INDENT: int = 4
FIRST_MAP_CHAR: str = 'A'
MAPS_FOLDER: str = "maps"
MAP_NAME: str = "height_map"

THeightMap = list[list[int]]
PALETTES_DICT = {}

####################################################################### utils ####################################################################


def build_default_palettes():
    global PALETTES_DICT
    PALETTES_DICT = {
        "landscape_4": {
            "A": {"fg": (255, 255, 255), "bg": (000, 000, 255)},
            "B": {"fg": (255, 255, 255), "bg": (215, 175, 000)},
            "C": {"fg": (255, 255, 255), "bg": (000, 191, 000)},
            "D": {"fg": (000, 000, 000), "bg": (255, 255, 255)},
        },
        "landscape_8": {
            "A": {"fg": (255, 255, 255), "bg": (000, 000, 63)},
            "B": {"fg": (255, 255, 255), "bg": (000, 000, 255)},
            "C": {"fg": (255, 255, 255), "bg": (215, 175, 000)},
            "D": {"fg": (255, 255, 255), "bg": (000, 191, 000)},
            "E": {"fg": (255, 255, 255), "bg": (000, 63, 000)},
            "F": {"fg": (255, 255, 255), "bg": (138, 117, 88)},
            "G": {"fg": (000, 000, 000), "bg": (85,   85,  85)},
            "H": {"fg": (000, 000, 000), "bg": (255, 255, 255)},
        },
        "landscape_16": {
            "A": {"fg": (255, 255, 255), "bg": (000, 000, 63)},
            "B": {"fg": (255, 255, 255), "bg": (000, 000, 127)},
            "C": {"fg": (255, 255, 255), "bg": (000, 000, 191)},
            "D": {"fg": (255, 255, 255), "bg": (000, 000, 255)},
            "E": {"fg": (255, 255, 255), "bg": (215, 175, 000)},
            "F": {"fg": (255, 255, 255), "bg": (000, 191, 000)},
            "G": {"fg": (255, 255, 255), "bg": (000, 127, 000)},
            "H": {"fg": (255, 255, 255), "bg": (000, 63, 000)},
            "I": {"fg": (255, 255, 255), "bg": (81, 69, 52)},
            "J": {"fg": (255, 255, 255), "bg": (100, 85, 64)},
            "K": {"fg": (255, 255, 255), "bg": (119, 101, 76)},
            "L": {"fg": (255, 255, 255), "bg": (138, 117, 88)},
            "M": {"fg": (000, 000, 000), "bg": (85,   85,  85)},
            "N": {"fg": (000, 000, 000), "bg": (135, 135, 135)},
            "O": {"fg": (000, 000, 000), "bg": (150, 150, 150)},
            "P": {"fg": (000, 000, 000), "bg": (255, 255, 255)},
        },
    }

    no_shades = 16

    palette_definitions = {}
    palette_definitions["grey   "] = [1, 1, 1]
    palette_definitions["red    "] = [1, 0, 0]
    palette_definitions["green  "] = [0, 1, 0]
    palette_definitions["blue   "] = [0, 0, 1]
    palette_definitions["yellow "] = [1, 1, 0]
    palette_definitions["magenta"] = [1, 0, 1]
    palette_definitions["cyan   "] = [0, 1, 1]

    for key in palette_definitions:
        p = build_default_palette(no_shades, palette_definitions[key])
        PALETTES_DICT[f"{key.strip()}_{no_shades}"] = p

    no_shades_list = [32, 64, 128]
    for no_shades in no_shades_list:
        palette_name = "grey   "
        p = build_default_palette(no_shades, palette_definitions[palette_name])
        PALETTES_DICT[f"{palette_name.strip()}_{no_shades}"] = p


def build_default_palette(no_shades: int, colors: list[int]) -> dict[str, dict]:
    step = 255 // no_shades
    p = {}
    for x in range(no_shades):
        p[chr(ord(FIRST_MAP_CHAR) + x)] = {
            "fg": (255, 255, 255),
            "bg": (x*step*colors[0], x*step*colors[1], x*step*colors[2])
        }
    return p


build_default_palettes()
################################################################### main class ########################################################################


class DiamondSquare:

    def __init__(
        self,
        map_size: int,
        height_min: int = HEIGHT_MIN,
        height_max: int = HEIGHT_MAX,
        roughness: float = ROUGHNESS,
        random_seed: int = RANDOM_SEED,
        height_nil: int = HEIGHT_NIL,
        map_name: str = MAP_NAME,
        palette: str = COLOR_PALETTE,

    ):
        self.map_size = map_size
        self.height_min = height_min
        self.height_max = height_max
        self.roughness = roughness
        self.random_seed = random_seed
        self.height_nil = height_nil
        self.map_name = map_name
        self.legend_layer = None

        self.height_map: THeightMap = self.init_height_map()
        self.map_str = {}
        self.load_legend_from_xp()

        if palette in PALETTES_DICT:
            self.palette = palette
        else:
            self.palette = COLOR_PALETTE

        # self.palette = self.palette16_dict["landscape_16"]

        self.build_palette()

    def build_palette(self):
        self.palette_dict = PALETTES_DICT[self.palette]
        self.mapping = {}
        for symbol in self.palette_dict:
            fg_r, fg_g, fg_b = self.palette_dict[symbol]['fg']
            bg_r, bg_g, bg_b = self.palette_dict[symbol]['bg']
            self.mapping[symbol] = Segment("  ", Style.parse(f"rgb({fg_r},{fg_g},{fg_b}) on rgb({bg_r},{bg_g},{bg_b})"))
        return self.mapping

    def init_height_map(self) -> THeightMap:
        random.seed(self.random_seed)

        height_map = []
        for i in range(self.map_size):
            height_map.append([self.height_nil] * self.map_size)

        return height_map

    def round_and_clamp(self, value: float) -> int:
        result = math.floor(value) if abs(math.ceil(value) - value) > abs(value - math.floor(value)) else math.ceil(value)

        if result < self.height_min:
            return self.height_min
        if result > self.height_max:
            return self.height_max

        return result

    def random_value(self, roughness: float) -> float:
        return random.randint(-1, 1) * roughness

    def generate(self) -> THeightMap:
        random.seed(self.random_seed)
        self.init_height_map()
        self.build_palette()
        self.diamond_square()
        return self.height_map

    def diamond_square(self) -> THeightMap:
        random_scalar: float = self.roughness

        self.height_map[0][0] = random.randint(self.height_min, self.height_max)
        self.height_map[0][-1] = random.randint(self.height_min, self.height_max)
        self.height_map[-1][0] = random.randint(self.height_min, self.height_max)
        self.height_map[-1][-1] = random.randint(self.height_min, self.height_max)

        chunk_size = self.map_size - 1
        while chunk_size > 1:
            chunk_size_half = chunk_size // 2
            for y in range(0, self.map_size - 1, chunk_size):
                for x in range(0, self.map_size - 1, chunk_size):
                    sum_of_neighbors = self.height_map[y][x]
                    sum_of_neighbors += self.height_map[y][x + chunk_size]
                    sum_of_neighbors += self.height_map[y + chunk_size][x]
                    sum_of_neighbors += self.height_map[y + chunk_size][x + chunk_size]

                    # self.height_map[y + chunk_size_half][x + chunk_size_half] = self.round(
                    #     (sum_of_neighbors / 4) + self.random_value(random_scalar))
                    self.height_map[y + chunk_size_half][x + chunk_size_half] = self.round_and_clamp(
                        (self.height_map[y][x] + self.height_map[y][x + chunk_size] + self.height_map[y + chunk_size]
                         [x] + self.height_map[y + chunk_size][x + chunk_size]) / 4 + self.random_value(random_scalar)
                    )

            for y in range(0, self.map_size, chunk_size_half):
                for x in range((y + chunk_size_half) % chunk_size, self.map_size, chunk_size):
                    # if x == 0:
                    #     x = chunk_size
                    sum_ = 0
                    count = 0
                    if x - chunk_size_half > 0:
                        sum_ += self.height_map[y][x - chunk_size_half]
                        count += 1
                    if x + chunk_size_half < self.map_size:
                        sum_ += self.height_map[y][x + chunk_size_half]
                        count += 1
                    if y - chunk_size_half > 0:
                        sum_ += self.height_map[y - chunk_size_half][x]
                        count += 1
                    if y + chunk_size_half < self.map_size:
                        sum_ += self.height_map[y + chunk_size_half][x]
                        count += 1
                    self.height_map[y][x] = self.round_and_clamp(sum_ / count + self.random_value(random_scalar))

            chunk_size = chunk_size // 2
            random_scalar = max(random_scalar / 2, 0.1)

        return self.height_map

    def convert_to_str(self) -> list[str]:

        self.map_str = []
        for row in self.height_map:
            new_row = ""
            for col in row:
                c = chr(-1 + ord(FIRST_MAP_CHAR) + col)
                new_row += c
            self.map_str.append(new_row)
        return self.map_str

    def print_height_map(self):
        console = Console()
        print(f"Map size    : {self.map_size}")
        print(f"Min height  : {self.height_min}")
        print(f"Max height  : {self.height_max}")
        print(f"Roughness   : {self.roughness}")
        print(f"Random seed : {self.random_seed}")
        print(f"Palette     : {self.palette}")
        # for color in self.mapping:
        console.print(self.get_palette_preview())
        console.print("\nHeight map  :")

        self.grid = "\n".join(self.convert_to_str())
        pixels = Pixels.from_ascii(self.grid, self.mapping)
        # console.print(Panel(pixels, title="Map"))
        console.print(pixels)
        console.print("")

    def get_palette_preview(self, palette: str | None = None):
        if palette is None or palette == self.palette:
            return Segments(list(self.mapping.values()))

        old_palette = self.palette
        old_mapping = self.mapping
        self.palette = palette
        result = self.build_palette()
        self.palette = old_palette
        self.mapping = old_mapping
        return Segments(list(result.values()))

    def save_to_json(self):
        if len(self.map_str) == 0:
            self.convert_to_str()

        file_name = Path(MAPS_FOLDER) / f"{self.map_name}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(self.map_str, f, indent=JSON_INDENT)

    def save_to_xp(self):
        if len(self.map_str) == 0:
            self.convert_to_str()

        self.save_palette()
        if self.legend_layer is None:
            self.load_legend_from_xp()
        new_legend = deepcopy(self.legend_layer)

        settings_list = []
        settings_list.append(str(self.map_size))
        settings_list.append("diamond square")
        settings_list.append(self.palette)
        settings_list.append(str(self.random_seed))
        settings_list.append(str(self.height_max))
        settings_list.append(str(self.roughness))

        for j, setting in enumerate(settings_list):
            tile = new_legend.tiles[self.xp_pos(5+j, 15, new_legend)]
            for i, c in enumerate(setting):
                # print(i, c)
                tile = deepcopy(tile)
                tile.ascii_code = c
                new_legend.tiles[self.xp_pos(5+j, 15+i, new_legend)] = tile

        # file_name = f"..\\REXPaint\\images\\{self.map_name}.xp" # windows setup
        # file_name = f"{MAPS_FOLDER}\\{self.map_name}.xp"  # macos setup
        file_name = Path(MAPS_FOLDER) / f"{self.map_name}.xp"  # macos setup
        with open(file_name, 'wb') as fp:
            fp.write(struct.pack('i', 1))  # version
            fp.write(struct.pack('i', 3))  # layers
            fp.write(struct.pack('i', len(self.height_map[0])))
            fp.write(struct.pack('i', len(self.height_map)))
            # write background color layer
            for x in range(len(self.height_map)):
                for y in range(len(self.height_map[0])):
                    ch_int = -1 + ord(FIRST_MAP_CHAR) + self.height_map[y][x]
                    ch_str = chr(ch_int)
                    fp.write(struct.pack('i', ch_int))
                    # fp.write(struct.pack('i', ord(" ")))
                    # fp.write(struct.pack('BBBBBB', *self.palette_dict[ch_str]["fg"], *self.palette_dict[ch_str]["bg"]))
                    fp.write(struct.pack('BBBBBB', *self.palette_dict[ch_str]["bg"], *self.palette_dict[ch_str]["bg"]))
            # write ASCII code layer
            fp.write(struct.pack('i', len(self.height_map[0])))
            fp.write(struct.pack('i', len(self.height_map)))
            for x in range(len(self.height_map)):
                for y in range(len(self.height_map[0])):
                    ch_int = -1 + ord(FIRST_MAP_CHAR) + self.height_map[y][x]
                    ch_str = chr(ch_int)
                    fp.write(struct.pack('i', ch_int))
                    # fp.write(struct.pack('i', ord(" ")))
                    # fp.write(struct.pack('BBBBBB', *self.palette_dict[ch_str]["fg"], *self.palette_dict[ch_str]["bg"]))
                    fp.write(struct.pack('BBBBBB', 255, 255, 255, 0, 0, 0))
            # write legend layer
            fp.write(struct.pack('i', new_legend.width))
            fp.write(struct.pack('i', new_legend.height))
            for tile in new_legend.tiles:

                fp.write(struct.pack('i', ord(tile.ascii_code)))
                # fp.write(struct.pack('BBBBBB', *self.palette_dict[ch_str]["fg"], *self.palette_dict[ch_str]["bg"]))
                fp.write(struct.pack('BBBBBB', tile.fg_r, tile.fg_g, tile.fg_b, tile.bg_r, tile.bg_g, tile.bg_b))
        print(f"Saved map '{self.map_name}' to {file_name}.")

    def save_palette(self):
        palette_size = len(self.palette_dict)
        file_name = Path(MAPS_FOLDER) / f"{self.palette}_{palette_size}_SSiS.txt"
        bg_colors_line = ""
        fg_colors_line = ""

        # Rexpaint palette color format is {r,g,b}\t
        for c in self.palette_dict:
            fg_r, fg_g, fg_b = self.palette_dict[c]['fg']
            fg_colors_line += f"{{{fg_r},{fg_g},{fg_b}}}\t"
            bg_r, bg_g, bg_b = self.palette_dict[c]['bg']
            bg_colors_line += f"{{{bg_r},{bg_g},{bg_b}}}\t"

        # Rexpaint requires 16 colors per line in the palette
        if palette_size < 16:
            fg_colors_line += "{0,0,0}\t" * (16 - len(self.palette_dict))
            bg_colors_line += "{0,0,0}\t" * (16 - len(self.palette_dict))

        # Rexpaint requires 12 lines in the palette, last line without new line
        with open(file_name, "w", encoding="utf-8") as f:
            f.writelines([f"{fg_colors_line}\n" for _ in range(6)])
            f.writelines([f"{bg_colors_line}\n" for _ in range(5)])
            f.writelines(f"{bg_colors_line}")  # no new line at the end of file

        print(f"Saved palette '{self.palette}' to {file_name}. Copy to Rexpaint under data\\palette folder.")

    def xp_pos(self, x, y, layer):
        return (y * layer.height) + x

    def load_legend_from_xp(self):
        # file_name = f"..\\REXPaint\\images\\{self.map_name}.xp" # windows setup

        # file_name = f"{MAPS_FOLDER}\\{self.map_name}.xp"  # macos setup
        file_name = Path(MAPS_FOLDER) / "legend.xp"
        legend_layers = pyrexpaint.load(str(file_name))

        if len(legend_layers) > 0:
            self.legend_layer = legend_layers[0]
            for tile in self.legend_layer.tiles:
                c = cast(bytes, tile.ascii_code).decode('cp437')
                c = c.replace(chr(0), "")
                tile.ascii_code = c

    def load_from_xp(self):
        # file_name = f"..\\REXPaint\\images\\{self.map_name}.xp" # windows setup

        # file_name = f"{MAPS_FOLDER}\\{self.map_name}.xp"  # macos setup
        file_name = Path(MAPS_FOLDER) / f"{self.map_name}.xp"
        self.image_layers = pyrexpaint.load(str(file_name))

        if len(self.image_layers) > 0:
            self.xp_layer = self.image_layers[0]
            self.map_size = max(self.xp_layer.width, self.xp_layer.height)
            self.height_map = []
            color_index = 1
            colors_map = {}
            p = {}
            for i in range(self.xp_layer.width):
                row: list[int] = []
                for j in range(self.xp_layer.height):
                    tile = self.xp_layer.tiles[self.xp_pos(i, j, self.xp_layer)]
                    fg = tile.fg_r, tile.fg_g, tile.fg_b
                    bg = tile.bg_r, tile.bg_g, tile.bg_b
                    color_id = (fg, bg)
                    if color_id not in colors_map:
                        colors_map[color_id] = color_index
                        p[color_index] = {"fg": fg, "bg": bg}
                        # val = color_index
                        color_index += 1
                    else:
                        pass
                        # val = colors_map[color_id]

                    char = cast(bytes, tile.ascii_code).decode('cp437')  # encode('cp437').decode("utf-8")

                    char = char.replace(chr(0), "")
                    # console.print(char, end="")
                    val = ord(char) - ord(FIRST_MAP_CHAR) + 1
                    row.append(val)
                # console.print("")
                self.height_map.append(row)

            # self.palette16_dict["custom"] = p
            # self.palette = "custom"
            # self.build_palette()
            # self.generate()


@tui()
@click.option(
    "--map-size",
    "-m",
    "map_size",
    type=click.Choice(["9", "17", "33", "65", "129"], case_sensitive=False),
    # required=True,
    default=str(HEIGHT_MAP_SIZE),
    help="Map size (for diamond square size must be n^2 + 1). If you need different size, pick bigger value and cut to desired size.",
)
@click.option(
    "--palette",
    "-p",
    type=click.Choice(list(PALETTES_DICT.keys()), case_sensitive=True),
    default=COLOR_PALETTE,
    help="Name of one of available color palettes. A palette is a set of colors to represent map height values.",
)
@click.option(
    "--roughness",
    "-r",
    type=click.FloatRange(min=1.0),
    default=ROUGHNESS,
    help="Roughness level - how rapidly values change near by (the higher value the more 'ragged' map). Best results when in range of ~3.0 to MAX_HEIGHT.",
)
@click.option(
    "--height",
    "-h",
    "height_max",
    type=click.IntRange(min=2),
    default=HEIGHT_MAX,
    help="Maximum height value (min is always 1). In order to properly display in console, max height must be lower or equal the number of colors in selected palette (the biggest palette is 128). While exporting to files, max height is not limited.",
)
@click.option(
    '--print/--no-print',
    default=True,
    help="Print height map to console (default True)."
)
@click.option(
    '--export-xp-filename',
    '-x',
    'export_xp',
    type=str,
    # is_flag=True,
    default=MAP_NAME,
    help="File name (without extension) to export map using Rexpaint file format (.xp)."
)
@click.option(
    '--export-json-filename',
    '-j',
    'export_json',
    type=str,
    # is_flag=True,
    default=MAP_NAME,
    help="File name (without extension) to export map using json format (.json)."
)
@click.option(
    "--seed",
    "-s",
    "random_seed",
    type=int,
    help="Seed for random number generator. Skip to get random maps with each run. If you like the results make sure to note currently used seed. Use explicit value to generate the same map multiple times, still being able to fine tune it (e.g. change roughness level or palette).",
)
@click.command()
def generate(
    map_size: str,
    roughness: float,
    random_seed: int | None,
    height_max: int | None,
    palette: str,
    print: bool,
    export_xp: str,
    export_json: str,
):
    map_size_int: int = int(map_size)
    if random_seed is None:
        random_seed_int = random.randint(0, 10000)
    else:
        random_seed_int = random_seed
    if height_max is None:
        height_max = HEIGHT_MAX
    # roughness = 16.0
    # height_max = 16
    # palette = "landscape_16"
    map_name = MAP_NAME
    # if export_xp:
    #     map_name = export_xp
    ds = DiamondSquare(
        map_size_int,
        roughness=roughness,
        random_seed=random_seed_int,
        height_max=height_max,
        map_name=map_name,
        palette=palette
    )
    ds.generate()
    if export_xp:
        ds.map_name = export_xp
        ds.save_to_xp()
    if export_json:
        ds.map_name = export_json
        ds.save_to_json()
    if print:
        ds.print_height_map()


if __name__ == "__main__":
    generate()
    # dungeon
    # python ds.py 129 7 4 6627
    # mono tunnel
    # python ds.py 129 10 2 6627
    # python diamond_square.py 65 16.0 10 landscape_16 1881
