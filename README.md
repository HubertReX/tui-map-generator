# TUI Map Generator

Height map 🗺 generator using diamond square 💎🔷 with TUI 🖥️ interface.

TODO: image

## What for?

This tool allows you to generate height maps using **diamond square** algorithm for your games or other projects. With several parameters you can customize the size, roughness and color palette. Generated map can be saved as:

TODO: implement
- **png** plain image
- **json** file with formatting
- **xp** Rexpaint image editor

### TUI interface

To make it easier to use, there is a **TUI** interface. This gives you a '_graphical_'-like user interface in the terminal (hence the name **TUI**). This way you can use it in a console without any kind of graphical interface. And yes, the mouse works too! 🐭

### The Game

I'm personally using this tool to generate maps for my game called [**SSiS**](https://hubertnafalski.itch.io/ssis). It's part of an bigger tool called **Config Editor** written using amazing library called [Textual](https://textual.textualize.io/). [Below[#Inspirations]] more on that. However, the currently released version of my game is not yet using maps generated with this method. You can follow me on [itch.io](https://hubertnafalski.itch.io) to get notified when it's released.

### Compatibility

All platforms should work, but I've tested it only on **MacOS**. If you have any problems, please create an issue.

- **Linux** ❓ (should work, not tested)
- **Windows** ❓ (should work, not tested)
- **MacOS** works fine ✅

## Installation

### Public repository

```bash
TODO: not yet published on PyPI

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
tui-map-generator generate --help
```

To quickly see how it works, skip all parameters (use default) and write this command:

```bash
tui-map-generator generate
```


### 2. TUI interface

write this command to start TUI interface:

```bash
tui-map-generator tui
```

## Examples

TODO

## Under the hood

### Libraries

Here are some some of the libraries used in this project:

- rich - to get beautiful colors and formatting in the terminal
- rich_pixels - to render map in the terminal
- click - to create command line interface
- trogon - to create TUI interface (with wonderful [Textual](https://textual.textualize.io/) library)

### Inspirations

This implementation is based on this article: [link](todo)

