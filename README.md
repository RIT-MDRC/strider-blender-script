# Welcome to Blender script for strider bot

This is all of the blender script that will run within the blender python environment to allow us to grab data from the blender model during animation. The data will be then streamed to the robot to which then will be used to manipulate the robot according to the animation.

# Details of the setup
While this project can be run independently from blender, we only use the venv for the IDE tools and easy of scripting outside of blender. For actual installation of dependencies and running the script see further below.
It is also important to note that blender manages its own python environment and the blender python api is only available in python version 3.11, so just remember that every library have to be available for 3.11 before installation. This is also why this project is using the python environment 3.11.
This project also is in the form of blender addon the reason being that it is much easier to install packages this way. The blender doc also has a nice direction for how to do [this](https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html).


# Installation
For scripting in vscode we use a different python package manager from pip called UV. To install uv see [here](https://docs.astral.sh/uv/getting-started/installation/).
Once installed, run `uv sync`. This will create both the virtual environment and install the dependencies in the root repository.

As mentioned in [setup](https://github.com/RIT-MDRC/strider-blender-script/blob/undefined/README.md#L5) this project will not actually be used to run outside of the blender environment other than debugging and type checking, meaning any changes made in the python environment here must be copied over to blender's environment, so the steps below is going to be for that purpose.

The packages in the addons are installed in the form of wheels. This is slightly annoying to do, but should not be too much of a hassle other than a few long cli commands.
When you are installing a new package that is not already used in this project you will need to create a wheel:

1. Run `source .venv/bin/activate`(make sure you have already ran `uv sync` and have the virtual environment)

Make sure to replace the following commands' `<package-name>` with the actual name of the package:

2. Run `python3.11 -m pip download <pakage-name> --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_11_0_arm64`
3. Run `python3.11 -m pip download <pakage-name> --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_28_x86_64`
3. Run `python3.11 -m pip download <pakage-name> --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64`

The commands above should have made a few new files in the `./wheels/` directory, so you will need to add those in the `blender_manifest.toml` file. For example:
```toml
wheels = [
  # ... previous wheel files
  "./wheels/<package-name>-<package-version>-cp311-cp311-macosx_11_0_arm64.whl",
  "./wheels/<package-name>-<package-version>-py3-none-any.whl",
  "./wheels/<package-name>-<package-version>-cp311-cp311-win_amd64.whl",
  # ... more wheel files
]
```

Once the dependencies was installed and wheel files were created you will also need to build the extension for blender to use it and blender provides a build cli command:
Linux: https://docs.blender.org/manual/en/dev/advanced/command_line/launch/linux.html
MacOS: https://docs.blender.org/manual/en/dev/advanced/command_line/launch/macos.html
Windows: https://docs.blender.org/manual/en/dev/advanced/command_line/launch/windows.html

Then run the following command:
`blender --command extension build --source-dir <directory path to this repo> --output-dir <directory path to this repo>/dist`
or for MacOS
`Blender --command extension build --source-dir <directory path to this repo> --output-dir <directory path to this repo>/dist`

> [!NOTE]
> If any issue occur reference the blender doc: https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html 

Once this has been created you can then open blender to add the addon from this cloned repository.
Go `Edit > preferences > add-ons` then top right hand corner has a `▽` in blender 4.3 or 4.2 may have install button. Click `install from disk`. Pick the newly generated zip file. This may fail, but know that the library will be importable within the blender python environment, so don't worry. Eventually this will be fixed but if you want to just try out some stuff with a new library this is one way to do it. 