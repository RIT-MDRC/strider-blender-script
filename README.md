# Welcome to Blender script for strider bot

This is all of the blender script that will run within the blender python environment to allow us to grab data from the blender model during animation. The data will be then streamed to the robot to which then will be used to manipulate the robot according to the animation.

# Details of the setup
While this project can be run independently from blender, we only use the venv for the IDE tools and easy of scripting outside of blender. For actual installation of dependencies and running the script see further below.
It is also important to note that blender manages its own python environment and the blender python api is only available in python version 3.11, so just remember that every library have to be available for 3.11 before installation. This is also why this project is using the python environment 3.11.

# Installation
For scripting in vscode we use a different python package manager from pip called UV. To install uv see [here](https://docs.astral.sh/uv/getting-started/installation/).
Once installed, run `uv sync`. This will create both the virtual environment and install the dependencies in the root repository.

As mentioned in [setup](https://github.com/RIT-MDRC/strider-blender-script/blob/undefined/README.md#L5) this project will not actually be used to run outside of the blender environment other than debugging and type checking, meaning any changes made in the python environment here must be copied over to blender's environment, so the steps below is going to be for that purpose.

