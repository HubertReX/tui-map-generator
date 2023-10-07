# add folder with the script to the PATH variable in order to run it from anywhere
# this also fixes problem with trogon which runs script without './' prefix and fails
# export PATH=$PATH:~/Documents/Projects/tui-map-generator/src/tui_map_generator
#  or 
# export PATH=$PATH:.
poetry run python src/tui_map_generator generate
# poetry shell
# python -m src/tui_map_generator generate