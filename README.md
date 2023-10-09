# TUI Map Generator

Height map 🗺 generator using **diamond square** 💎🔷 with TUI 🖥️ interface.

![maps/example_01.png](https://raw.githubusercontent.com/HubertReX/tui-map-generator/main/maps/example_01.png)

## What for?

This tool allows you to generate height maps using **diamond square** algorithm for your games or other projects. This is not a trivial task as it might seem at the beginning. Height map is not just random numbers - it needs to look 'organic', should be generated automatically and should be customizable, yet deterministic. See [**#Inspirations**](#inspirations) for more on that.

With several parameters you can customize the size, roughness and color palette. Generated map can be saved as:

- **png** plain image
- **json** file with formatting
- **xp** Rexpaint image editor

### TUI interface

To make it easier to use, there is a **TUI** interface. This gives you a '_graphical_'-like user interface in the terminal (hence the name **TUI**). This way you can use it in a console without any kind of graphical interface. And yes, the mouse works too! 🐭

![maps/screenshot_01_tui.png](https://raw.githubusercontent.com/HubertReX/tui-map-generator/main/maps/screenshot_01_tui.png)

### The Game

I'm personally using this tool to generate maps for my game called [**SSiS**](https://hubertnafalski.itch.io/ssis). It's part of an bigger tool called **Config Editor** written using amazing library called [Textual](https://textual.textualize.io/). However, the currently released version of my game is not yet using maps generated with this method. You can follow me on [itch.io](https://hubertnafalski.itch.io) to get notified when it's released.

### Compatibility

All platforms should work, but I've tested it only on **MacOS**. If you have any problems, please create an issue.

- **Linux** ❓ (should work, not tested)
- **Windows** ❓ (should work, not tested)
- **MacOS** works fine ✅

## Installation

### Public repository

```bash
pip install tui-map-generator
```

or

```bash
pipx install tui-map-generator
```

to have it in isolated environment.

### From source

You need to have **Python >3.8** installed and the **poetry** library. Check-out this repository, open the project folder in a terminal and run:

```bash
poetry install
poetry run python src/tui_map_generator generate
# or
poetry run python src/tui_map_generator tui
```

On MacOs I had to add folder with the source file to the PATH variable to make it work with **trogon** (python script run with out python command need to be in PATH to skip the './' prefix):

```bash
export PATH=$PATH:~/<your projects folder>/tui-map-generator/src/tui_map_generator
```

## Usage

There are two ways to use this tool:

### 1. Plain command line

write this command to see all available options:

```bash
python3 -m tui-map-generator generate --help
```

to see something like this:

```bash
Usage: python3 -m tui-map-generator generate [OPTIONS]

  Generate height map using diamond square algorithm. Add 'generate --help' to
  your command to get more help the parameters or use 'tui' command instead
  'generate'.

Options:
  -s, --seed INTEGER              Seed for random number generator. Skip to
                                  get random maps with each run. If you like
                                  the results make sure to note currently used
                                  seed. Use explicit value to generate the
                                  same map multiple times, still being able to
                                  fine tune it (e.g. change roughness level or
                                  palette).
  -u, --scale-up INTEGER RANGE    Map size scale up factor used while saving
                                  to PNG files (see --export-png-filename).
                                  With default value of 1 you end up with one
                                  pixel per height map value which means a
                                  really tiny image. With scale up = 5, each
                                  height map point results in 5x5 pixels
                                  rectangle. Linear scaling is used in order
                                  to preserve exact height values (no
                                  interpolation).  [x>=1]
  -i, --export-png-filename TEXT  File name (without extension) to export map
                                  PNG file format (.png).
  -j, --export-json-filename TEXT
                                  File name (without extension) to export map
                                  using json format (.json).
  -x, --export-xp-filename TEXT   File name (without extension) to export map
                                  using Rexpaint file format (.xp).
  --printout / --no-printout      Print height map to console (default True).
  -h, --height INTEGER RANGE      Maximum height value (min is always 1). In
                                  order to properly display in console, max
                                  height must be lower or equal the number of
                                  colors in selected palette (the biggest
                                  palette is 128). While exporting to files,
                                  max height is not limited.  [x>=2]
  -r, --roughness FLOAT RANGE     Roughness level - how rapidly values change
                                  near by (the higher value the more 'ragged'
                                  map). Best results when in range of ~3.0 to
                                  MAX_HEIGHT.  [x>=1.0]
  -p, --palette [landscape_4|landscape_8|landscape_16|grey_16|red_16|green_16|blue_16|yellow_16|magenta_16|cyan_16|grey_32|grey_64|grey_128]
                                  Name of one of available color palettes. A
                                  palette is a set of colors to represent map
                                  height values.
  -m, --map-size [9|17|33|65|129]
                                  Map size (for diamond square size must be
                                  n^2 + 1). If you need different size, pick
                                  bigger value and cut to desired size.
  --help                          Show this message and exit.
```

To quickly see how it works, skip all parameters (use default) and write this command:

```bash
python3 -m tui-map-generator generate
```

### 2. TUI interface

write this command to start TUI interface:

```bash
python3 -m tui-map-generator tui
```

## Examples

## maps/example_01

Map size: 65

Algorithm: diamond square

Max height: 16

Roughness: 16.0

Random seed: 2994

Palette: landscape_16

![maps/example_01.png](https://raw.githubusercontent.com/HubertReX/tui-map-generator/main/maps/example_01.png)

## maps/example_02

Map size: 129

Algorithm: diamond square

Max height: 64

Roughness: 64.0

Random seed: 4948

Palette: grey_64

![maps/example_02.png](https://raw.githubusercontent.com/HubertReX/tui-map-generator/main/maps/example_02.png)

## maps/example_03

Map size: 33

Algorithm: diamond square

Max height: 8

Roughness: 3.0

Random seed: 6956

Palette: landscape_8

![maps/example_03.png](https://raw.githubusercontent.com/HubertReX/tui-map-generator/main/maps/example_03.png)

## Under the hood

### Libraries

Here are some some of the libraries used in this project:

- [**rich**](https://pypi.org/project/rich/) - to get beautiful colors and formatting in the terminal (but this is much more powerful tool - check it out! 🚀)
- [**rich_pixels**](https://pypi.org/project/rich-pixels/) - to render map in the terminal (but this tool is also capable of displaying images in console)
- [**click**](https://pypi.org/project/click/) - to create command line interface
- [**trogon**](https://pypi.org/project/trogon/) - to create TUI interface with wonderful [**Textual**](https://textual.textualize.io/) library - this one is beyond amazing! 🤯 My understanding of the full power of terminal apps has expanded a lot since I've found it. Just as a teaser - **Textual** apps can be even run in [web browser](https://pypi.org/project/textual_web/)

### Inspirations

This implementation is based on [example-diamond-square](https://github.com/klaytonkowalski/example-diamond-square) project written in **Lua** using **Defold** engine. See the author him self, explaining the whole **diamond square** 💎🔷 algorithm: [YouTube video](https://www.youtube.com/watch?v=4GuAV1PnurU&ab_channel=WhiteBoxDev). More on the process of building my implementation can be found on my [blogpost](https://hubertnafalski.itch.io/ssis/devlog/618072/002-detours-in-the-game-development).
