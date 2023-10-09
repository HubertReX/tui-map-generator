#!/usr/bin/env python3
from tui_map_generator.diamond_square import (
    DiamondSquare,
    HEIGHT_MAP_SIZE,
    HEIGHT_MAX,
    MAP_NAME,
    ROUGHNESS,
    SCALE_UP,
    COLOR_PALETTE,
    PALETTES_DICT,
)
import random
import click
from trogon import tui


@tui(
    command="tui",
    help="Open terminal UI to set generation parameters. This will lunch a beautiful 'graphic-like' interface, but it's still a terminal application. Try it!",
)
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
    "--printout/--no-printout",
    default=True,
    help="Print height map to console (default True).",
)
@click.option(
    "--export-xp-filename",
    "-x",
    "export_xp",
    type=str,
    # is_flag=True,
    # default=MAP_NAME,
    help="File name (without extension) to export map using Rexpaint file format (.xp).",
)
@click.option(
    "--export-json-filename",
    "-j",
    "export_json",
    type=str,
    # is_flag=True,
    # default=MAP_NAME,
    help="File name (without extension) to export map using json format (.json).",
)
@click.option(
    "--export-png-filename",
    "-i",
    "export_png",
    type=str,
    # is_flag=True,
    # default=MAP_NAME,
    help="File name (without extension) to export map PNG file format (.png).",
)
@click.option(
    "--scale-up",
    "-u",
    "scale_up",
    type=click.IntRange(min=1),
    default=SCALE_UP,
    help="Map size scale up factor used while saving to PNG files (see --export-png-filename). With default value of 1 you end up with one pixel per height map value which means a really tiny image. With scale up = 5, each height map point results in 5x5 pixels rectangle. Linear scaling is used in order to preserve exact height values (no interpolation).",
)
@click.option(
    "--seed",
    "-s",
    "random_seed",
    type=int,
    help="Seed for random number generator. Skip to get random maps with each run. If you like the results make sure to note currently used seed. Use explicit value to generate the same map multiple times, still being able to fine tune it (e.g. change roughness level or palette).",
)
@click.command(
    help="Generate height map using diamond square algorithm. Add 'generate --help' to your command to get more help the parameters or use 'tui' command instead 'generate'."
)
def generate(
    map_size: str,
    roughness: float,
    random_seed: int | None,
    height_max: int | None,
    palette: str,
    printout: bool,
    export_xp: str,
    export_json: str,
    export_png: str,
    scale_up: int,
):
    map_size_int: int = int(map_size)
    if random_seed is None:
        random_seed_int = random.randint(0, 10000)
    else:
        random_seed_int = random_seed

    if height_max is None:
        height_max = HEIGHT_MAX
    map_name = MAP_NAME

    ds = DiamondSquare(
        map_size_int,
        roughness=roughness,
        random_seed=random_seed_int,
        height_max=height_max,
        map_name=map_name,
        palette=palette,
    )

    ds.generate()

    if printout:
        ds.print_height_map()

    if export_xp:
        ds.map_name = export_xp
        ds.save_to_xp()

    if export_json:
        ds.map_name = export_json
        ds.save_to_json()

    if export_png:
        ds.map_name = export_png
        ds.save_to_png(scale_up)


if __name__ == "__main__":
    generate()
    # dungeon
    # python ds.py 129 7 4 6627
    # mono tunnel
    # python ds.py 129 10 2 6627
    # python diamond_square.py 65 16.0 10 landscape_16 1881
