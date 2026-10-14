# ROS2 and PIXI

## Usage

> It is extremely similar to Node.js and NPM. There are similar package managing tools and etc.

### Creating a Workspace

```bash
pixi init <name> --channel https://prefix.dev/robostack-jazzy
cd <name>
pixi add ros-jazzy-desktop
pixi add ros-dev-tools
```

The first command creates a workspace with name `<name>`. The supplementary commands set up basic desktop development workflows so that you can actually simulate stuff.

### Adding Packages

```bash
pixi add <package>
```

This adds certain packages to your workspace so you can use them anywhere. They are added to your own packages.

### Running Nodes

```bash
pixi run ros2 run <pkg> <node>
```

This runs a certain node (`<node>`), by entry point name (not file name), of a certain package (`<pkg>`).

### Running Visualization

```bash
pixi run rviz2
```

This runs a visualization in 3D with other parameters.

### Creating Your Own Packages

```bash
# cpp, create node
pixi run ros2 pkg create --build-type ament_cmake --node-name <node> <pkg>
# cpp, empty pkg
pixi run ros2 pkg create --build-type ament_cmake <pkg>

# py, create node
pixi run ros2 pkg create --build-type ament_python --node-name <node> <pkg>
# py, empty pkg
pixi run ros2 pkg create --build-type ament_python <pkg>
```

This is how you create your own packages.
