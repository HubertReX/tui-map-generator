from copy import deepcopy
import json
import random
import math
import numpy as np
import string
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from sys import argv
from typing import cast
import struct
from rich.segment import Segment, Segments
from rich.style import Style
from rich_pixels import Pixels
from rich.console import Console
import pyrexpaint
from pathlib import Path

# Example usage:
HEIGHT_NIL: int = 0
HEIGHT_MIN: int = 1
HEIGHT_MAX: int = 16
# must be n^2 + 1
HEIGHT_MAP_SIZE = 65
ROUGHNESS: float = 16.0
# RANDOM_SCALAR: float = ROUGHNESS
RANDOM_SEED = 111
ALGORITHM_NAME = "diamond square"
COLOR_PALETTE = "landscape_16"
SCALE_UP = 10
# PRINT_FORMAT_LEN: int = 3
JSON_INDENT: int = 4
HEIGHT_TO_CHR_MAPPING = (
    list(string.ascii_letters) + list("#$%&*=,.~+@^") + list(map(chr, range(191, 255)))
)
MAPS_FOLDER: str = "maps"
MAP_NAME: str = "height_map"
XP_LEGEND_START_X = 17
XP_LEGEND_START_Y = 4
EXPORT_GLYPHS_LAYER = False

THeightMap = list[list[int]]
PALETTES_DICT = {}

####################################################################### utils ####################################################################


def build_default_palettes():
    global PALETTES_DICT
    PALETTES_DICT = {
        "landscape_4": {
            HEIGHT_TO_CHR_MAPPING[0]: {"fg": (255, 255, 255), "bg": (000, 000, 255)},
            HEIGHT_TO_CHR_MAPPING[1]: {"fg": (255, 255, 255), "bg": (215, 175, 000)},
            HEIGHT_TO_CHR_MAPPING[2]: {"fg": (255, 255, 255), "bg": (000, 191, 000)},
            HEIGHT_TO_CHR_MAPPING[3]: {"fg": (000, 000, 000), "bg": (255, 255, 255)},
        },
        "landscape_8": {
            HEIGHT_TO_CHR_MAPPING[0]: {"fg": (255, 255, 255), "bg": (000, 000, 63)},
            HEIGHT_TO_CHR_MAPPING[1]: {"fg": (255, 255, 255), "bg": (000, 000, 255)},
            HEIGHT_TO_CHR_MAPPING[2]: {"fg": (255, 255, 255), "bg": (215, 175, 000)},
            HEIGHT_TO_CHR_MAPPING[3]: {"fg": (255, 255, 255), "bg": (000, 191, 000)},
            HEIGHT_TO_CHR_MAPPING[4]: {"fg": (255, 255, 255), "bg": (000, 63, 000)},
            HEIGHT_TO_CHR_MAPPING[5]: {"fg": (255, 255, 255), "bg": (138, 117, 88)},
            HEIGHT_TO_CHR_MAPPING[6]: {"fg": (000, 000, 000), "bg": (85, 85, 85)},
            HEIGHT_TO_CHR_MAPPING[7]: {"fg": (000, 000, 000), "bg": (255, 255, 255)},
        },
        "landscape_16": {
            HEIGHT_TO_CHR_MAPPING[0]: {"fg": (255, 255, 255), "bg": (000, 000, 63)},
            HEIGHT_TO_CHR_MAPPING[1]: {"fg": (255, 255, 255), "bg": (000, 000, 127)},
            HEIGHT_TO_CHR_MAPPING[2]: {"fg": (255, 255, 255), "bg": (000, 000, 191)},
            HEIGHT_TO_CHR_MAPPING[3]: {"fg": (255, 255, 255), "bg": (000, 000, 255)},
            HEIGHT_TO_CHR_MAPPING[4]: {"fg": (255, 255, 255), "bg": (215, 175, 000)},
            HEIGHT_TO_CHR_MAPPING[5]: {"fg": (255, 255, 255), "bg": (000, 191, 000)},
            HEIGHT_TO_CHR_MAPPING[6]: {"fg": (255, 255, 255), "bg": (000, 127, 000)},
            HEIGHT_TO_CHR_MAPPING[7]: {"fg": (255, 255, 255), "bg": (000, 63, 000)},
            HEIGHT_TO_CHR_MAPPING[8]: {"fg": (255, 255, 255), "bg": (81, 69, 52)},
            HEIGHT_TO_CHR_MAPPING[9]: {"fg": (255, 255, 255), "bg": (100, 85, 64)},
            HEIGHT_TO_CHR_MAPPING[10]: {"fg": (255, 255, 255), "bg": (119, 101, 76)},
            HEIGHT_TO_CHR_MAPPING[11]: {"fg": (255, 255, 255), "bg": (138, 117, 88)},
            HEIGHT_TO_CHR_MAPPING[12]: {"fg": (000, 000, 000), "bg": (85, 85, 85)},
            HEIGHT_TO_CHR_MAPPING[13]: {"fg": (000, 000, 000), "bg": (135, 135, 135)},
            HEIGHT_TO_CHR_MAPPING[14]: {"fg": (000, 000, 000), "bg": (150, 150, 150)},
            HEIGHT_TO_CHR_MAPPING[15]: {"fg": (000, 000, 000), "bg": (255, 255, 255)},
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
    step = round(255 / no_shades)
    p = {}
    for x in range(no_shades):
        p[HEIGHT_TO_CHR_MAPPING[x]] = {
            "fg": (255, 255, 255),
            "bg": (x * step * colors[0], x * step * colors[1], x * step * colors[2]),
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
        self.console = Console()
        self.map_size = map_size
        self.height_min = height_min
        self.height_max = height_max
        self.roughness = roughness
        self.random_seed = random_seed
        self.height_nil = height_nil
        self.map_name = map_name
        self.xp_legend_layer = None
        self.txt_legend_dict = {}
        self.height_map: THeightMap = self.init_height_map()
        self.map_str = {}
        self.load_legend_from_xp()

        if palette in PALETTES_DICT:
            self.palette = palette
        else:
            self.palette = COLOR_PALETTE

        self.build_palette()
        self.export_glyphs = EXPORT_GLYPHS_LAYER

    def build_palette(self):
        self.palette_dict = PALETTES_DICT[self.palette]
        self.mapping = {}
        for symbol in self.palette_dict:
            fg_r, fg_g, fg_b = self.palette_dict[symbol]["fg"]
            bg_r, bg_g, bg_b = self.palette_dict[symbol]["bg"]
            self.mapping[symbol] = Segment(
                "  ",
                Style.parse(f"rgb({fg_r},{fg_g},{fg_b}) on rgb({bg_r},{bg_g},{bg_b})"),
            )
        return self.mapping

    def init_height_map(self) -> THeightMap:
        random.seed(self.random_seed)

        height_map = []
        for i in range(self.map_size):
            height_map.append([self.height_nil] * self.map_size)

        return height_map

    def round_and_clamp(self, value: float) -> int:
        result = (
            math.floor(value)
            if abs(math.ceil(value) - value) > abs(value - math.floor(value))
            else math.ceil(value)
        )

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
        if len(self.palette_dict) < self.height_max:
            raise Exception(
                f"Palette '{self.palette}' has only {len(self.palette_dict)} colors. Max height must be lower or equal to the number of colors in selected palette."
            )
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

                    self.height_map[y + chunk_size_half][
                        x + chunk_size_half
                    ] = self.round_and_clamp(
                        (
                            self.height_map[y][x]
                            + self.height_map[y][x + chunk_size]
                            + self.height_map[y + chunk_size][x]
                            + self.height_map[y + chunk_size][x + chunk_size]
                        )
                        / 4
                        + self.random_value(random_scalar)
                    )

            for y in range(0, self.map_size, chunk_size_half):
                for x in range(
                    (y + chunk_size_half) % chunk_size, self.map_size, chunk_size
                ):
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
                    self.height_map[y][x] = self.round_and_clamp(
                        sum_ / count + self.random_value(random_scalar)
                    )

            chunk_size = chunk_size // 2
            random_scalar = max(random_scalar / 2, 0.1)

        return self.height_map

    def convert_to_str(self) -> list[str]:
        self.map_str = []
        for row in self.height_map:
            new_row = ""
            for col in row:
                new_row += HEIGHT_TO_CHR_MAPPING[col - 1]
            self.map_str.append(new_row)
        return self.map_str

    def print_height_map(self):
        padding = 15

        self.generate_legend_dict()
        for key in self.txt_legend_dict:
            self.console.print(
                f"[bold]{key:{padding}}[/]: [magenta]{self.txt_legend_dict[key]}[/]"
            )

        self.console.print(self.get_palette_preview())
        self.console.print(f"\n[bold]{'Height map':{padding}}[/]:")

        self.grid = "\n".join(self.convert_to_str())
        pixels = Pixels.from_ascii(self.grid, self.mapping)

        self.console.print(pixels)
        self.console.print("\n")

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
        # if len(self.map_str) == 0:
        #     self.convert_to_str()

        self.generate_legend_dict()
        data = {
            "parameters": self.txt_legend_dict,
            "height_map": self.height_map,
            # "glyph_map": self.map_str,
        }

        maps_folder = self.fix_maps_folder()
        file_name = maps_folder / f"{self.map_name}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=JSON_INDENT)

        self.console.print(f"Map saved to '[bold]{file_name}[/]'.")

    def fix_maps_folder(self):
        maps_folder = Path(MAPS_FOLDER)
        if not maps_folder.exists():
            maps_folder.mkdir()
        return maps_folder

    def save_to_png(self, scale_up: int = SCALE_UP):
        maps_folder = self.fix_maps_folder()
        file_name = maps_folder / f"{self.map_name}.png"

        size = len(self.height_map[0])
        img = np.zeros((size, size, 3), dtype=np.uint8)

        for x in range(len(self.height_map)):
            for y in range(len(self.height_map[0])):
                height = self.height_map[y][x]
                ch_str = HEIGHT_TO_CHR_MAPPING[height - 1]

                img[y][x] = self.palette_dict[ch_str]["bg"]

        new_size = size * scale_up
        img_resized = Image.fromarray(img).resize((new_size, new_size), Image.NEAREST)
        metadata = PngInfo()
        metadata.add_text("Title", f"{self.map_name} - height map")
        metadata.add_text("Software", "tui-map-generator")
        metadata.add_text(
            "Comment",
            "Visit https://github.com/HubertReX/tui-map-generator to learn more",
        )
        self.generate_legend_dict()
        for key in self.txt_legend_dict:
            metadata.add_text(key, str(self.txt_legend_dict[key]))

        description_list = [
            "Height map generated using tui-map-generator by Hubert Nafalski"
        ]
        for key in self.txt_legend_dict:
            description_list.append(f"{key:15}: {self.txt_legend_dict[key]}")

        metadata.add_text(
            "Description",
            "\n".join(description_list),
        )
        img_resized.save(file_name, pnginfo=metadata)
        # img_resized.show()
        self.console.print(f"Map saved to '[bold]{file_name}[/]'.")

    def generate_legend_dict(self):
        self.txt_legend_dict[f"Map size"] = self.map_size
        self.txt_legend_dict[f"Algorithm"] = ALGORITHM_NAME
        self.txt_legend_dict[f"Max height"] = self.height_max
        self.txt_legend_dict[f"Roughness"] = self.roughness
        self.txt_legend_dict[f"Random seed"] = self.random_seed
        self.txt_legend_dict[f"Palette"] = self.palette

    def save_to_xp(self):
        layers_no = 2

        if self.export_glyphs:
            layers_no += 1

        # if len(self.map_str) == 0:
        #     self.convert_to_str()

        # self.save_palette()

        if self.xp_legend_layer is None:
            self.load_legend_from_xp()

        if self.xp_legend_layer is None:
            raise Exception(
                f"Rexpaint file with legend template not found. Perhaps your installation of tui_map_generator has been corrupted. Try to reinstall it."
            )
        legend_layer = deepcopy(self.xp_legend_layer)
        self.generate_legend_dict()
        for j, (label, value) in enumerate(self.txt_legend_dict.items()):
            self.text_to_tiles(0, XP_LEGEND_START_Y + j, legend_layer, label)
            self.text_to_tiles(
                XP_LEGEND_START_X, XP_LEGEND_START_Y + j, legend_layer, str(value)
            )

        maps_folder = self.fix_maps_folder()
        file_name = maps_folder / f"{self.map_name}.xp"
        with open(file_name, "wb") as fp:
            # write header
            fp.write(struct.pack("i", 1))  # version
            fp.write(struct.pack("i", layers_no))  # layers
            fp.write(struct.pack("i", len(self.height_map[0])))
            fp.write(struct.pack("i", len(self.height_map)))

            # write background color layer (1)
            for x in range(len(self.height_map)):
                for y in range(len(self.height_map[0])):
                    ch_str = HEIGHT_TO_CHR_MAPPING[self.height_map[y][x] - 1]
                    ch_int = ord(ch_str)
                    if self.export_glyphs:
                        fp.write(struct.pack("i", ch_int))
                    else:
                        fp.write(struct.pack("i", ord(" ")))
                    fp.write(
                        struct.pack(
                            "BBBBBB",
                            *self.palette_dict[ch_str]["bg"],
                            *self.palette_dict[ch_str]["bg"],
                        )
                    )

            # write ASCII code mapped height layer (2)
            if self.export_glyphs:
                fp.write(struct.pack("i", len(self.height_map[0])))
                fp.write(struct.pack("i", len(self.height_map)))
                for x in range(len(self.height_map)):
                    for y in range(len(self.height_map[0])):
                        ch_str = HEIGHT_TO_CHR_MAPPING[self.height_map[y][x] - 1]
                        ch_int = ord(ch_str)
                        fp.write(struct.pack("i", ch_int))
                        # white letters on black background
                        fp.write(struct.pack("BBBBBB", 255, 255, 255, 0, 0, 0))

            # write legend layer (3)
            fp.write(struct.pack("i", legend_layer.width))
            fp.write(struct.pack("i", legend_layer.height))
            for tile in legend_layer.tiles:
                fp.write(struct.pack("i", ord(tile.ascii_code)))
                fp.write(
                    struct.pack(
                        "BBBBBB",
                        tile.fg_r,
                        tile.fg_g,
                        tile.fg_b,
                        tile.bg_r,
                        tile.bg_g,
                        tile.bg_b,
                    )
                )

        self.console.print(f"Map saved to '[bold]{file_name}[/]'.")

    def text_to_tiles(self, start_x, start_y, layer, text):
        tile = layer.tiles[self.xp_pos(start_y, start_x, layer)]

        for i, c in enumerate(text):
            tile = deepcopy(tile)
            tile.ascii_code = c
            layer.tiles[self.xp_pos(start_y, start_x + i, layer)] = tile

    def save_palette(self):
        palette_size = len(self.palette_dict)
        maps_folder = self.fix_maps_folder()
        file_name = maps_folder / f"{self.palette}_{palette_size}_SSiS.txt"
        bg_colors_line = ""
        fg_colors_line = ""

        # Rexpaint palette color format is {r,g,b}\t
        for c in self.palette_dict:
            fg_r, fg_g, fg_b = self.palette_dict[c]["fg"]
            fg_colors_line += f"{{{fg_r},{fg_g},{fg_b}}}\t"
            bg_r, bg_g, bg_b = self.palette_dict[c]["bg"]
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

        self.console.print(
            f"Color palette saved to '[bold]{file_name}[/]'. Copy to [bold]Rexpaint[/]] installation under '[bold]data\\palette[/]' folder."
        )

    def xp_pos(self, x, y, layer):
        return (y * layer.height) + x

    def load_legend_from_xp(self):
        file_name = Path(__file__).parent / Path(MAPS_FOLDER) / "legend.xp"
        if not file_name.exists():
            raise Exception(
                f"Rexpaint file with legend template '{file_name}' not found. Perhaps your installation of tui_map_generator has been corrupted. Try to reinstall it."
            )
        legend_layers = pyrexpaint.load(str(file_name))

        if len(legend_layers) > 0:
            self.xp_legend_layer = legend_layers[0]
            for tile in self.xp_legend_layer.tiles:
                c = cast(bytes, tile.ascii_code).decode("cp437")
                c = c.replace(chr(0), "")
                tile.ascii_code = c

    def load_from_xp(self):
        maps_folder = self.fix_maps_folder()
        file_name = maps_folder / f"{self.map_name}.xp"
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

                    char = cast(bytes, tile.ascii_code).decode(
                        "cp437"
                    )  # encode('cp437').decode("utf-8")

                    char = char.replace(chr(0), "")
                    # console.print(char, end="")
                    val = HEIGHT_TO_CHR_MAPPING.index(char) + 1
                    row.append(val)
                self.height_map.append(row)

            # self.palette16_dict["custom"] = p
            # self.palette = "custom"
            # self.build_palette()
            # self.generate()


if __name__ == "__main__":
    ds = DiamondSquare(HEIGHT_MAP_SIZE, map_name="test_01")
    # ds.load_from_xp()
    ds.export_glyphs = True
    ds.generate()
    ds.save_to_xp()
    ds.save_to_png()
    ds.save_to_json()
    ds.print_height_map()

    # bg_r, bg_g, bg_b = ds.palette_dict[symbol]["bg"]
