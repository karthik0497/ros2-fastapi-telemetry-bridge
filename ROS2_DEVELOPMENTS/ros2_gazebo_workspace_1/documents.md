Perfect setup. This is exactly the modern stack.

* ROS2 Jazzy
* Gazebo Harmonic (gz-sim 8)
* Ubuntu 24.04

One important thing before we start. You already have a workspace folder created at that path. We will build everything inside it.

> **Important:** Gazebo Harmonic uses a completely different plugin system than older Gazebo Classic. The old `libgazebo_ros_diff_drive.so` plugin does **NOT** work here. We use `gz::sim::systems::DiffDrive` instead. Most tutorials online still show the old way, which will not work on ROS2 Jazzy + Gazebo Harmonic. Throughout this project, we will follow the modern Gazebo Harmonic approach.

ros2_gazebo_workspace_1/
└── src/
    └── robot_description/
        ├── urdf/
        │   ├── common_properties.xacro  — materials, PI constant
        │   ├── inertia_macros.xacro     — box, cylinder, sphere formulas
        │   ├── base.xacro               — chassis link
        │   ├── wheels.xacro             — drive wheels + caster
        │   ├── gazebo.xacro             — plugins, friction, colours
        │   └── robot.xacro              — top level, includes all
        ├── launch/
        │   ├── display.launch.py        — RViz only
        │   ├── gazebo.launch.py         — Gazebo + bridge
        │   └── robot.launch.py          — everything together
        └── config/
            └── ros_gz_bridge.yaml       — bridge topic config

---

# PHASE 1 — Workspace & Robot Description Package

## Step 1 — Workspace Structure

Workspace:

```text
~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1
```

Create the `src` folder. In ROS2, all packages live inside `src`.

### Run

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1
mkdir src
ls
```

### Expected Output

```text
src
```

> **Note:** Do **NOT** run `colcon build` now. The only folder we create manually is `src`. The `build/`, `install/`, and `log/` directories will be created automatically after running `colcon build` later.

---

## Step 2 — Create the `robot_description` Package

This package will contain:

* URDF/Xacro files
* Launch files
* RViz configuration
* Gazebo worlds

Since this package contains only configuration files (no C++ or Python code), we use the `ament_cmake` build type.

### Run

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src
ros2 pkg create robot_description --build-type ament_cmake
```

### Expected Output

```text
going to create a new package
package name: robot_description
destination directory: .../src
package format: 3
version: 0.0.0
description: TODO
maintainer: ...
licenses: TODO
build type: ament_cmake
dependencies:
creating folder ./robot_description
creating ./robot_description/package.xml
creating source and include folder
creating type specific files
```

### Verify

```bash
ls
ls robot_description/
```

Expected:

```text
robot_description

CMakeLists.txt
include
package.xml
src
```

---

## Step 3 — Create the Standard Folder Structure

ROS2 description packages follow a standard folder layout. Create the required directories.

### Run

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description

mkdir urdf
mkdir launch
mkdir rviz
mkdir worlds
mkdir config
```

### Verify

```bash
find . -type d | sort
```

Expected Output

```text
.
./config
./include
./launch
./rviz
./src
./urdf
./worlds
```

### Folder Purpose

* `urdf/` → URDF and Xacro files
* `launch/` → Launch files
* `rviz/` → RViz configuration
* `worlds/` → Gazebo world files
* `config/` → YAML configuration files (bridge, parameters, etc.)

---

## Step 4 — Edit `package.xml`

`package.xml` declares the package name, dependencies, and build system.

### Open

```bash
gedit package.xml
```

Delete everything and replace it with:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
            schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>robot_description</name>
  <version>0.0.1</version>
  <description>Mobile robot URDF description and simulation launch files</description>
  <maintainer email="karthik@todo.com">karthik</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <!-- Robot description tools -->
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>joint_state_publisher</exec_depend>
  <exec_depend>joint_state_publisher_gui</exec_depend>
  <exec_depend>xacro</exec_depend>

  <!-- RViz -->
  <exec_depend>rviz2</exec_depend>

  <!-- Gazebo Harmonic -->
  <exec_depend>ros_gz_sim</exec_depend>
  <exec_depend>ros_gz_bridge</exec_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Save and close.

---

## Step 5 — Edit `CMakeLists.txt`

`CMakeLists.txt` tells ROS2 which folders should be installed during the build process.

### Open

```bash
gedit CMakeLists.txt
```

Delete everything and replace it with:

```cmake
cmake_minimum_required(VERSION 3.8)
project(robot_description)

find_package(ament_cmake REQUIRED)

# Install all resource folders
install(
  DIRECTORY
    urdf
    launch
    rviz
    worlds
    config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
```

Save and close.

### Why `install()` is Important

Without the `install()` command, `colcon build` will **not** copy your files into the `install/` directory.

ROS2 always loads resources from:

```text
install/share/robot_description/
```

—not directly from `src/`.

If these folders are not installed, launch files will not be able to find your Xacro files, RViz configuration, Gazebo worlds, or YAML configuration files.

---

## Step 6 — Verify Package Structure

Run:

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description
find . | sort
```

Expected Output:

```text
.
./CMakeLists.txt
./config
./include
./launch
./package.xml
./rviz
./src
./urdf
./worlds
```

---

## Step 7 — Build the Workspace

Return to the workspace root.

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1
```

Build the workspace:

```bash
colcon build
```

Source the workspace:

```bash
source install/setup.bash
```

### Workspace Structure After Build

```text
ros2_gazebo_workspace_1/
├── build/
├── install/
├── log/
└── src/
```


Perfect. Structure is exactly correct. Phase 1 complete.

---

## PHASE 2 — Step 5 : Create `common_properties.xacro`

This is the first xacro file we write. It is the foundation that every other xacro file will use.

**Why this file exists:**

Every xacro file in the project needs to share the same constants — PI value, colours, material definitions. Instead of defining these in every file (and risking mismatches), we define them once here and every other file includes this one.

**Go into the urdf folder:**
```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/urdf
```

**Create the file:**
```bash
gedit common_properties.xacro
```

**Type this exactly — read every comment, it explains each line:**

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!--
    This file contains:
    1. Mathematical constants
    2. Material colour definitions for RViz
    These are shared by all other xacro files via xacro:include
  -->

  <!-- ═══════════════════════════════════════════
       MATHEMATICAL CONSTANTS
       ═══════════════════════════════════════════ -->

  <!--
    xacro:property creates a named constant.
    ${PI} can now be used anywhere in any file that includes this one.
    We need PI because joint origins use radians, not degrees.
    90 degrees = PI/2 = 1.5708 radians
  -->
  <xacro:property name="PI" value="3.14159265358979"/>


  <!-- ═══════════════════════════════════════════
       MATERIAL DEFINITIONS FOR RVIZ
       ═══════════════════════════════════════════ -->

  <!--
    material defines a named colour for RViz visualisation.
    rgba = Red Green Blue Alpha, each value between 0.0 and 1.0
    Alpha 1.0 = fully opaque, 0.0 = fully transparent

    IMPORTANT: these material tags only affect RViz.
    Gazebo has its own separate colour system inside <gazebo reference> tags.
    We handle Gazebo colours in gazebo.xacro.
  -->

  <material name="white">
    <color rgba="1.0 1.0 1.0 1.0"/>
  </material>

  <material name="grey">
    <color rgba="0.5 0.5 0.5 1.0"/>
  </material>

  <material name="dark_grey">
    <color rgba="0.2 0.2 0.2 1.0"/>
  </material>

  <material name="black">
    <color rgba="0.1 0.1 0.1 1.0"/>
  </material>

  <material name="blue">
    <color rgba="0.0 0.0 0.8 1.0"/>
  </material>

  <material name="red">
    <color rgba="0.8 0.0 0.0 1.0"/>
  </material>

  <material name="green">
    <color rgba="0.0 0.8 0.0 1.0"/>
  </material>

  <material name="orange">
    <color rgba="1.0 0.5 0.0 1.0"/>
  </material>

</robot>
```

Save and close.

---

## PHASE 2 — Step 6 : Create `inertia_macros.xacro`

This is the second foundational file. It contains the inertia formulas as reusable macros.

**Why this file exists:**

Every link needs an `<inertial>` block with correct inertia values. The formulas for box, cylinder, and sphere are fixed physics equations. Instead of calculating and typing numbers manually for every link (wrong values break Gazebo), we write the formula once as a macro. When we call `<xacro:cylinder_inertia m="0.5" r="0.05" l="0.04"/>`, xacro computes the correct numbers automatically.

**Create the file:**
```bash
gedit inertia_macros.xacro
```

**Type this:**

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!--
    This file contains inertia calculation macros for three primitive shapes.

    What is a macro?
    A macro is a reusable block with parameters — exactly like a function.
    xacro:macro defines it. xacro:macro_name calls it.

    Why do we need inertia?
    Gazebo is a physics engine. It needs to know how hard it is to rotate
    each part around each axis. Without correct inertia values:
    - Robot shakes or vibrates on spawn
    - Robot floats or sinks into the ground
    - Robot flips over when it moves
    - Simulation is completely unrealistic

    The three macros below cover every shape in our AMR:
    - box_inertia    → chassis
    - cylinder_inertia → drive wheels
    - sphere_inertia   → caster wheel
  -->


  <!-- ═══════════════════════════════════════════
       BOX INERTIA
       params: m=mass(kg) x=length y=width z=height (all in metres)

       Formulas for a solid uniform box:
         ixx = m/12 * (y*y + z*z)
         iyy = m/12 * (x*x + z*z)
         izz = m/12 * (x*x + y*y)

       ixy, ixz, iyz are always 0 for symmetric shapes.
       ═══════════════════════════════════════════ -->
  <xacro:macro name="box_inertia" params="m x y z">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="${m}"/>
      <inertia
        ixx="${m/12.0*(y*y+z*z)}" ixy="0.0" ixz="0.0"
        iyy="${m/12.0*(x*x+z*z)}" iyz="0.0"
        izz="${m/12.0*(x*x+y*y)}"/>
    </inertial>
  </xacro:macro>


  <!-- ═══════════════════════════════════════════
       CYLINDER INERTIA
       params: m=mass(kg) r=radius(m) l=length(m)

       A cylinder in URDF is defined along its local Z axis.
       We rotate it 90deg to lie on its side (for wheels),
       but the inertia formula is always for the upright cylinder.

       Formulas for a solid uniform cylinder:
         ixx = m/12 * (3*r*r + l*l)
         iyy = m/12 * (3*r*r + l*l)
         izz = m/2  * r*r
       ═══════════════════════════════════════════ -->
  <xacro:macro name="cylinder_inertia" params="m r l">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="${m}"/>
      <inertia
        ixx="${m/12.0*(3*r*r+l*l)}" ixy="0.0" ixz="0.0"
        iyy="${m/12.0*(3*r*r+l*l)}" iyz="0.0"
        izz="${m/2.0*r*r}"/>
    </inertial>
  </xacro:macro>


  <!-- ═══════════════════════════════════════════
       SPHERE INERTIA
       params: m=mass(kg) r=radius(m)

       Formulas for a solid uniform sphere:
         ixx = iyy = izz = 2/5 * m * r*r

       All three axes are equal because a sphere is
       perfectly symmetric in all directions.
       ═══════════════════════════════════════════ -->
  <xacro:macro name="sphere_inertia" params="m r">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="${m}"/>
      <inertia
        ixx="${2.0/5.0*m*r*r}" ixy="0.0" ixz="0.0"
        iyy="${2.0/5.0*m*r*r}" iyz="0.0"
        izz="${2.0/5.0*m*r*r}"/>
    </inertial>
  </xacro:macro>

</robot>
```

Save and close.

---

## Verify both files exist

```bash
ls -la ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/urdf/
```

**Expected:**
```
common_properties.xacro
inertia_macros.xacro
```

**Quick syntax check — run this for each file:**
```bash
xacro common_properties.xacro
xacro inertia_macros.xacro
```

Both should output a small XML block with no errors. If you see `Error` anywhere paste it here.

---

Good — no errors. But I see two things to note.

**common_properties.xacro** — the `${PI}` property line is missing from the output. That means xacro processed it but the property tag itself produces no XML output (correct — properties are invisible in output). That is fine.

**inertia_macros.xacro** — the macros are also invisible in output. Also correct. Macros only produce output when they are called. The file compiled clean with no errors. Both files are good.

---

## PHASE 2 — Step 7 : Create `base.xacro`

This file defines the robot chassis — the main body. It is the most important link because everything else attaches to it.

**Why a separate file for the base?**

As your robot grows — you add sensors, arms, more links — keeping everything in one file becomes unmanageable. Splitting by responsibility (base, wheels, sensors, gazebo) means you can find and edit any part without touching the rest.

**Create the file:**
```bash
gedit base.xacro
```

**Type this exactly:**

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!--
    base.xacro defines:
    1. The base_footprint link  — a virtual zero-mass frame at ground level
    2. The base_link            — the physical chassis body
    3. The joint connecting them

    WHY base_footprint?
    Nav2 and many ROS2 navigation tools expect a frame called base_footprint
    that sits exactly at ground level (z=0). This is the point directly below
    the robot on the floor. base_link sits above it at the centre of the chassis.
    Having both is standard practice in mobile robotics.
  -->

  <!-- Include shared constants and inertia macros -->
  <!--
    xacro:include pulls another xacro file into this one.
    After this line, ${PI} and all inertia macros are available here.
    The filename is relative to this file's location.
  -->
  <xacro:include filename="common_properties.xacro"/>
  <xacro:include filename="inertia_macros.xacro"/>


  <!-- ═══════════════════════════════════════════
       ROBOT DIMENSIONS — change these properties
       to resize the entire robot automatically
       ═══════════════════════════════════════════ -->

  <!--
    All dimensions in metres. All masses in kilograms.
    Changing any value here updates the geometry, inertia,
    and joint positions automatically via ${} expressions.
  -->
  <xacro:property name="base_length"    value="0.40"/>  <!-- chassis x dimension -->
  <xacro:property name="base_width"     value="0.30"/>  <!-- chassis y dimension -->
  <xacro:property name="base_height"    value="0.10"/>  <!-- chassis z dimension -->
  <xacro:property name="base_mass"      value="4.0"/>   <!-- chassis mass in kg  -->


  <!-- ═══════════════════════════════════════════
       BASE FOOTPRINT LINK
       ═══════════════════════════════════════════ -->

  <!--
    base_footprint is a virtual link — it has no geometry, no mass, no inertia.
    It is purely a coordinate frame sitting at ground level (z=0).
    It is the root of the entire robot TF tree.
    ROS2 convention: base_footprint is the robot's floor-level reference frame.
  -->
  <link name="base_footprint"/>


  <!-- ═══════════════════════════════════════════
       BASE FOOTPRINT → BASE LINK JOINT
       ═══════════════════════════════════════════ -->

  <!--
    This joint connects base_footprint (floor level) to base_link (chassis centre).
    type="fixed" means no movement between them — they move as one rigid unit.

    origin xyz:
      x=0, y=0 — directly above footprint, no horizontal offset
      z = base_height/2 = 0.05m — lifts base_link to the vertical centre
          of the chassis. The chassis box is drawn centred on base_link,
          so its bottom face sits at z=0 (ground level). Correct.
  -->
  <joint name="base_footprint_joint" type="fixed">
    <parent link="base_footprint"/>
    <child  link="base_link"/>
    <origin xyz="0 0 ${base_height/2}" rpy="0 0 0"/>
  </joint>


  <!-- ═══════════════════════════════════════════
       BASE LINK — THE PHYSICAL CHASSIS
       ═══════════════════════════════════════════ -->

  <!--
    base_link is the physical body of the robot.
    Its origin sits at the geometric centre of the chassis box.
    All wheel joints are measured from this origin.
  -->
  <link name="base_link">

    <!--
      VISUAL — what RViz draws on screen.
      geometry box: size="x y z" in metres.
      origin: the geometry is centred on base_link origin, so xyz="0 0 0".
      material: references the name defined in common_properties.xacro.
    -->
    <visual>
      <geometry>
        <box size="${base_length} ${base_width} ${base_height}"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <material name="blue"/>
    </visual>

    <!--
      COLLISION — the hitbox Gazebo uses for physics.
      Same shape as visual here. For a simple box this is fine.
      For complex meshes you would use a simpler collision shape.
      No material tag — collision shapes have no colour.
    -->
    <collision>
      <geometry>
        <box size="${base_length} ${base_width} ${base_height}"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
    </collision>

    <!--
      INERTIAL — calls our box_inertia macro from inertia_macros.xacro.
      Parameters: m=mass, x=length, y=width, z=height
      The macro calculates all six inertia values automatically.
      We never type raw ixx/iyy/izz numbers — the formula does it.
    -->
    <xacro:box_inertia
      m="${base_mass}"
      x="${base_length}"
      y="${base_width}"
      z="${base_height}"/>

  </link>

</robot>
```

Save and close.

---

## Test this file immediately

```bash
xacro base.xacro
```

You should see XML output with no errors. Look for these specific things in the output:

1. A `<link name="base_footprint"/>` tag — empty, no geometry. Correct.
2. A `<joint name="base_footprint_joint" type="fixed">` with `<origin xyz="0 0 0.05"` — the 0.05 is `base_height/2` computed by xacro. Correct.
3. A `<link name="base_link">` with a `<box>` geometry and an `<inertial>` block with computed numbers.

The inertia numbers should be approximately:
```
ixx = 4/12*(0.09+0.01) = 0.0333
iyy = 4/12*(0.16+0.01) = 0.0567
izz = 4/12*(0.16+0.09) = 0.0833
```

Perfect output. Every value is exactly correct. Let me confirm what xacro computed:

```
joint origin z = 0.05        ✓  (base_height/2 = 0.10/2)
box size = 0.4 0.3 0.1       ✓  (our properties expanded correctly)
mass = 4.0                   ✓
ixx = 0.03333  ✓  (4/12*(0.09+0.01) = 0.0333)
iyy = 0.05666  ✓  (4/12*(0.16+0.01) = 0.0567)
izz = 0.08333  ✓  (4/12*(0.16+0.09) = 0.0833)
```

base.xacro is clean. Step 7 complete.

---

## PHASE 2 — Step 8 : Create `wheels.xacro`

This file defines both drive wheels and the caster wheel. This is where the xacro macro power really shows — we write the wheel description once and call it twice.

**Create the file:**
```bash
gedit wheels.xacro
```

**Type this exactly:**

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!--
    wheels.xacro defines:
    1. A reusable drive_wheel macro  — called twice for left and right
    2. The caster wheel link and joint

    WHY a macro for wheels?
    Left and right wheels are identical in shape, mass, and inertia.
    The only difference is their Y position (left = positive, right = negative)
    and their name. A macro lets us define the wheel once and instantiate
    it twice with different arguments. One change updates both wheels.
  -->

  <!-- Include shared files -->
  <xacro:include filename="common_properties.xacro"/>
  <xacro:include filename="inertia_macros.xacro"/>


  <!-- ═══════════════════════════════════════════
       WHEEL DIMENSIONS AND PLACEMENT
       ═══════════════════════════════════════════ -->

  <!--
    These properties define every physical aspect of the wheels.
    They are used inside the macro below via ${} expressions.
  -->

  <xacro:property name="wheel_radius"       value="0.05"/>   <!-- metres -->
  <xacro:property name="wheel_length"       value="0.04"/>   <!-- thickness of wheel -->
  <xacro:property name="wheel_mass"         value="0.3"/>    <!-- kg per wheel -->

  <!--
    wheel_separation: distance between left and right wheel centres (y axis).
    This MUST match the value in the Gazebo diff_drive plugin exactly.
    Our chassis is 0.30m wide. Wheels sit just outside: 0.30/2 + 0.04/2 = 0.17m
    So separation = 0.17 * 2 = 0.34m between centres.
    We define half-separation here: each wheel is 0.17m from robot centre.
  -->
  <xacro:property name="wheel_y_offset"     value="0.17"/>   <!-- half of separation -->

  <!--
    wheel_z_offset: how far below base_link origin the wheel centre sits.
    base_link origin is at the vertical centre of the chassis (height/2 above ground).
    Wheel centre must be at ground level (z=0 in world frame).
    Since base_link is at z=0.05 (half chassis height above ground),
    wheel centre must be 0.05m below base_link origin.
    So wheel_z_offset = -base_height/2 = -0.05m
  -->
  <xacro:property name="wheel_z_offset"     value="-0.05"/>

  <!-- Caster wheel dimensions -->
  <xacro:property name="caster_radius"      value="0.025"/>  <!-- metres -->
  <xacro:property name="caster_mass"        value="0.1"/>    <!-- kg -->

  <!--
    caster_x_offset: how far forward the caster sits from robot centre.
    Place it near the front edge of the chassis: base_length/2 - small margin.
    base_length = 0.40m, so front edge is at x=0.20. Place caster at x=0.15.
  -->
  <xacro:property name="caster_x_offset"    value="0.15"/>

  <!--
    caster_z_offset: caster centre below base_link origin.
    Caster radius = 0.025m. It must touch the ground (z=0 in world frame).
    base_link is at z=0.05 in world. So caster centre is at z=0.025 world.
    Offset from base_link = 0.025 - 0.05 = -0.025m
  -->
  <xacro:property name="caster_z_offset"    value="-0.025"/>


  <!-- ═══════════════════════════════════════════
       DRIVE WHEEL MACRO
       ═══════════════════════════════════════════ -->

  <!--
    params:
      prefix   — "left" or "right" — used in link name and joint name
      y_reflect — 1 for left wheel, -1 for right wheel
                  multiplied by wheel_y_offset to flip the Y position

    How the cylinder orientation works:
      A URDF cylinder is defined standing upright — its length runs along Z.
      We want the wheel lying on its side — length runs along Y (axle direction).
      So we rotate the visual and collision 90 degrees around X axis.
      rpy="${PI/2} 0 0" = 90 degrees around X = cylinder now lies along Y.
      The joint axis xyz="0 1 0" tells Gazebo to spin around Y — the wheel rolls.
  -->
  <xacro:macro name="drive_wheel" params="prefix y_reflect">

    <link name="${prefix}_wheel">

      <visual>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_length}"/>
        </geometry>
        <!--
          rpy="${PI/2} 0 0" rotates the cylinder 90deg around X.
          This makes the wheel stand upright (lying on its side like a real wheel).
          Without this rotation the cylinder would be a disc lying flat on the ground.
        -->
        <origin xyz="0 0 0" rpy="${PI/2} 0 0"/>
        <material name="dark_grey"/>
      </visual>

      <collision>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_length}"/>
        </geometry>
        <origin xyz="0 0 0" rpy="${PI/2} 0 0"/>
      </collision>

      <!--
        cylinder_inertia macro from inertia_macros.xacro.
        m = wheel_mass, r = wheel_radius, l = wheel_length
        The macro computes ixx, iyy, izz automatically.
      -->
      <xacro:cylinder_inertia
        m="${wheel_mass}"
        r="${wheel_radius}"
        l="${wheel_length}"/>

    </link>

    <!--
      DRIVE WHEEL JOINT
      type="continuous" — rotates forever with no limits.
      This is correct for drive wheels. Never use "revolute" for wheels
      because revolute has hard angle stops — wheels would stop turning.

      origin xyz:
        x = 0           — wheel is at the longitudinal centre of chassis
        y = y_reflect * wheel_y_offset
            left wheel:  y_reflect= 1 → y= +0.17 (left side)
            right wheel: y_reflect=-1 → y= -0.17 (right side)
        z = wheel_z_offset = -0.05 (below base_link at ground level)

      axis xyz="0 1 0" — wheel spins around Y axis.
      Combined with the rpy rotation of the visual, this is correct.
    -->
    <joint name="${prefix}_wheel_joint" type="continuous">
      <parent link="base_link"/>
      <child  link="${prefix}_wheel"/>
      <origin xyz="0 ${y_reflect * wheel_y_offset} ${wheel_z_offset}"
              rpy="0 0 0"/>
      <axis xyz="0 1 0"/>
      <!--
        dynamics: damping resists motion (simulates bearing friction).
        friction: static friction at the joint (separate from surface friction).
        These small values make simulation more stable and realistic.
      -->
      <dynamics damping="0.005" friction="0.05"/>
    </joint>

  </xacro:macro>


  <!-- ═══════════════════════════════════════════
       INSTANTIATE DRIVE WHEELS
       Call the macro twice — one line each.
       ═══════════════════════════════════════════ -->

  <!--
    left wheel:  prefix="left"  y_reflect= 1 → joint at y=+0.17
    right wheel: prefix="right" y_reflect=-1 → joint at y=-0.17
  -->
  <xacro:drive_wheel prefix="left"  y_reflect="1"/>
  <xacro:drive_wheel prefix="right" y_reflect="-1"/>


  <!-- ═══════════════════════════════════════════
       CASTER WHEEL
       ═══════════════════════════════════════════ -->

  <!--
    The caster is a passive support wheel — no motor, no joint limits.
    We model it as a sphere for two reasons:
    1. Spheres roll in any direction — just like a real caster swivels.
    2. Sphere contact physics in Gazebo is more stable than a cylinder caster.

    Joint type = fixed.
    A real caster swivels freely — but we model the swivel via physics,
    not a joint. Gazebo's contact model on a low-friction sphere
    naturally allows rotation in any direction. Fixed joint is correct here.
  -->
  <link name="caster_wheel">

    <visual>
      <geometry>
        <sphere radius="${caster_radius}"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <material name="black"/>
    </visual>

    <collision>
      <geometry>
        <sphere radius="${caster_radius}"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
    </collision>

    <!--
      sphere_inertia macro from inertia_macros.xacro.
      Small mass — caster is just a support ball, not a structural part.
    -->
    <xacro:sphere_inertia
      m="${caster_mass}"
      r="${caster_radius}"/>

  </link>

  <!--
    CASTER JOINT
    type="fixed" — no joint movement. Gazebo handles passive rolling
    through contact physics and the near-zero friction we set in gazebo.xacro.

    origin xyz:
      x = caster_x_offset = 0.15  (front of chassis)
      y = 0                        (centred left-right)
      z = caster_z_offset = -0.025 (caster centre is 2.5cm below base_link)
  -->
  <joint name="caster_wheel_joint" type="fixed">
    <parent link="base_link"/>
    <child  link="caster_wheel"/>
    <origin xyz="${caster_x_offset} 0 ${caster_z_offset}" rpy="0 0 0"/>
  </joint>

</robot>
```

Save and close.

---

## Test wheels.xacro immediately

```bash
xacro wheels.xacro
```

No errors expected. In the output, verify these specific values were computed correctly by xacro:

Left wheel joint origin y should be `0.17` (positive).
Right wheel joint origin y should be `-0.17` (negative).
Caster joint origin should be `xyz="0.15 0 -0.025"`.
Cylinder inertia izz should be approximately `0.000375` (= 0.3/2 * 0.0025).

Perfect. Every value is exactly right. Let me confirm:

```
left_wheel  joint y  =  0.17   ✓
right_wheel joint y  = -0.17   ✓
caster joint xyz     =  0.15 0 -0.025  ✓
wheel ixx = iyy      =  0.0002275  ✓  (0.3/12*(3*0.0025+0.0016))
wheel izz            =  0.000375   ✓  (0.3/2*0.0025)
caster ixx=iyy=izz   =  2.5e-05   ✓  (2/5*0.1*0.000625)
```

Step 8 complete. wheels.xacro is clean.

---

## PHASE 2 — Step 9 : Create `gazebo.xacro`

This is the most important file for Gazebo Harmonic. This is where we tell Gazebo how to simulate the robot — colours, friction, contact properties, and the differential drive motor controller.

**Critical note for your setup:**

You have Gazebo Harmonic (gz-sim 8). This uses a completely different plugin system from older Gazebo Classic. The old way was `libgazebo_ros_diff_drive.so` inside a `<gazebo>` tag. That does NOT work on your machine. Gazebo Harmonic uses `gz::sim::systems::DiffDrive` inside a `<gazebo>` tag with the new format. I will show you exactly the correct syntax.

**Create the file:**
```bash
gedit gazebo.xacro
```

**Type this exactly:**

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!--
    gazebo.xacro defines everything Gazebo-specific:
    1. Per-link colours visible in Gazebo (separate from RViz materials)
    2. Surface friction and contact properties per link
    3. The differential drive plugin — the simulated motor controller
    4. The joint state publisher plugin — publishes wheel positions

    WHY a separate file for Gazebo stuff?
    RViz and Gazebo have completely different systems for colours,
    physics properties, and plugins. Keeping them in one file mixes
    two concerns. gazebo.xacro is only read by Gazebo — RViz ignores
    every tag in this file. Keeping it separate means you can modify
    simulation behaviour without touching the robot description.

    GAZEBO HARMONIC NOTE:
    This file uses the Gazebo Harmonic (gz-sim 8) plugin format.
    The plugin system changed completely from Gazebo Classic.
    Do NOT use libgazebo_ros_diff_drive.so — that is Classic only.
  -->


  <!-- ═══════════════════════════════════════════
       GAZEBO COLOURS
       ═══════════════════════════════════════════ -->

  <!--
    gazebo reference="link_name" applies Gazebo-specific properties
    to that link. This is separate from the material tag inside <link>.
    The material tag only works in RViz. For Gazebo colours you must
    use these gazebo reference blocks.

    Gazebo Harmonic uses the <material> tag with a <diffuse> sub-tag
    for colours, specified as R G B A values (0.0 to 1.0).
  -->

  <gazebo reference="base_link">
    <material>
      <diffuse>0.0 0.0 0.8 1.0</diffuse>    <!-- blue — matches RViz colour -->
      <specular>0.1 0.1 0.1 1.0</specular>  <!-- slight shine -->
    </material>
  </gazebo>

  <gazebo reference="left_wheel">
    <material>
      <diffuse>0.2 0.2 0.2 1.0</diffuse>    <!-- dark grey -->
      <specular>0.1 0.1 0.1 1.0</specular>
    </material>
    <!--
      Surface friction properties for the drive wheels.
      mu  = Coulomb friction coefficient (main friction, along wheel rolling direction)
      mu2 = friction perpendicular to rolling direction (lateral)
      Higher mu = more grip. Rubber wheel on floor is typically 0.8 to 1.0.
      If wheels slip in simulation, increase these values.
      If robot vibrates, decrease them slightly.

      kp = contact stiffness (spring constant of ground contact)
      kd = contact damping (energy absorption on contact)
      High kp = hard surface. Low kp = soft/spongy surface.
      minDepth = minimum contact depth before collision is registered.
    -->
    <surface>
      <friction>
        <ode>
          <mu>0.8</mu>
          <mu2>0.8</mu2>
          <fdir1>1 0 0</fdir1>  <!-- primary friction direction = forward -->
          <slip1>0.0</slip1>    <!-- no slip in rolling direction -->
          <slip2>0.0</slip2>
        </ode>
      </friction>
      <contact>
        <ode>
          <kp>1000000.0</kp>
          <kd>100.0</kd>
          <min_depth>0.001</min_depth>
          <max_vel>1.0</max_vel>
        </ode>
      </contact>
    </surface>
  </gazebo>

  <gazebo reference="right_wheel">
    <material>
      <diffuse>0.2 0.2 0.2 1.0</diffuse>
      <specular>0.1 0.1 0.1 1.0</specular>
    </material>
    <surface>
      <friction>
        <ode>
          <mu>0.8</mu>
          <mu2>0.8</mu2>
          <fdir1>1 0 0</fdir1>
          <slip1>0.0</slip1>
          <slip2>0.0</slip2>
        </ode>
      </friction>
      <contact>
        <ode>
          <kp>1000000.0</kp>
          <kd>100.0</kd>
          <min_depth>0.001</min_depth>
          <max_vel>1.0</max_vel>
        </ode>
      </contact>
    </surface>
  </gazebo>

  <gazebo reference="caster_wheel">
    <material>
      <diffuse>0.1 0.1 0.1 1.0</diffuse>    <!-- black -->
      <specular>0.1 0.1 0.1 1.0</specular>
    </material>
    <!--
      Caster friction must be near zero.
      The caster must slide and rotate freely in any direction.
      High friction here causes the robot to resist turning —
      the caster drags instead of rolling freely.
      mu = 0.001 is effectively frictionless for simulation purposes.
    -->
    <surface>
      <friction>
        <ode>
          <mu>0.001</mu>
          <mu2>0.001</mu2>
        </ode>
      </friction>
      <contact>
        <ode>
          <kp>1000000.0</kp>
          <kd>100.0</kd>
          <min_depth>0.001</min_depth>
          <max_vel>1.0</max_vel>
        </ode>
      </contact>
    </surface>
  </gazebo>


  <!-- ═══════════════════════════════════════════
       GAZEBO HARMONIC PLUGINS
       ═══════════════════════════════════════════ -->

  <!--
    In Gazebo Harmonic, plugins go inside a <gazebo> tag (no reference attribute).
    The plugin tag uses the filename attribute with the full class name.

    DIFFERENTIAL DRIVE PLUGIN
    This plugin is the simulated motor controller for our two-wheel AMR.

    What it does:
    - Subscribes to /cmd_vel (geometry_msgs/Twist) — your velocity commands
    - Computes left and right wheel speeds from linear + angular velocity
    - Drives the left_wheel_joint and right_wheel_joint in simulation
    - Publishes /odom (nav_msgs/Odometry) — estimated robot position
    - Publishes /tf transform: odom → base_footprint

    Without this plugin:
    - The robot has wheels in the URDF but no motor
    - /cmd_vel does nothing
    - /odom is never published
    - The robot cannot move in Gazebo

    Key parameters:
    left_joint / right_joint — must match your joint names in wheels.xacro exactly
    wheel_separation — must equal 2 * wheel_y_offset = 2 * 0.17 = 0.34m
    wheel_radius — must match wheel_radius property in wheels.xacro = 0.05m
  -->
  <gazebo>
    <plugin
      filename="gz-sim-diff-drive-system"
      name="gz::sim::systems::DiffDrive">

      <!-- Joint names — must exactly match wheels.xacro joint names -->
      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>

      <!--
        Physical parameters — must match your URDF geometry exactly.
        wheel_separation = distance between left and right wheel centres
                         = 2 * wheel_y_offset = 2 * 0.17 = 0.34 metres
        wheel_radius     = wheel_radius property = 0.05 metres
      -->
      <wheel_separation>0.34</wheel_separation>
      <wheel_radius>0.05</wheel_radius>

      <!-- Velocity limits — prevents simulation instability -->
      <max_linear_acceleration>1.0</max_linear_acceleration>
      <max_angular_acceleration>2.0</max_angular_acceleration>
      <max_linear_velocity>2.0</max_linear_velocity>
      <max_angular_velocity>2.0</max_angular_velocity>

      <!--
        Topic names for ROS2 ↔ Gazebo communication.
        These are Gazebo-side topic names.
        ros_gz_bridge will map them to ROS2 topic names.
        We keep them matching standard ROS2 names for simplicity.
      -->
      <topic>cmd_vel</topic>
      <odom_topic>odom</odom_topic>
      <tf_topic>/tf</tf_topic>

      <!-- Frame IDs published in odometry message -->
      <frame_id>odom</frame_id>
      <child_frame_id>base_footprint</child_frame_id>

      <!-- Publish odometry at 50Hz -->
      <odom_publish_frequency>50</odom_publish_frequency>

    </plugin>


    <!--
      JOINT STATE PUBLISHER PLUGIN
      This plugin publishes the current angle of every joint in the robot
      to the /world/*/model/*/joint_state Gazebo topic.
      ros_gz_bridge maps this to ROS2 /joint_states topic.
      robot_state_publisher reads /joint_states to compute wheel TF frames.

      Without this plugin:
      - /joint_states is never published from Gazebo
      - robot_state_publisher cannot compute wheel positions
      - Wheel frames in RViz are frozen at zero rotation
    -->
    <plugin
      filename="gz-sim-joint-state-publisher-system"
      name="gz::sim::systems::JointStatePublisher">
    </plugin>

  </gazebo>

</robot>
```

Save and close.

---

## Test gazebo.xacro

```bash
xacro gazebo.xacro
```

No errors expected. The output should show the two `<plugin>` blocks and all the `<gazebo reference>` blocks with friction values.

Check specifically that you see:
- `gz-sim-diff-drive-system` in the output
- `gz-sim-joint-state-publisher-system` in the output
- `<mu>0.8</mu>` for wheels
- `<mu>0.001</mu>` for caster

Perfect. Every plugin, friction value, and colour block is exactly correct.

```
gz-sim-diff-drive-system          ✓
gz-sim-joint-state-publisher-system ✓
wheel mu = 0.8                    ✓
caster mu = 0.001                 ✓
wheel_separation = 0.34           ✓
wheel_radius = 0.05               ✓
```

Step 9 complete. gazebo.xacro is clean.

---

## PHASE 2 — Step 10 : Create `robot.xacro`

This is the top-level file. It is the only file that ROS2 and Gazebo actually load directly. It does not define anything itself — it just includes all the other files in the correct order and wraps them inside a single `<robot>` tag.

Think of it as the main entry point. Every other xacro file is a module. This file assembles them.

**Create the file:**
```bash
gedit robot.xacro
```

**Type this exactly:**

```xml
<?xml version="1.0"?>
<robot name="amr_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!--
    robot.xacro is the TOP-LEVEL file.
    This is the ONLY file that launch files and Gazebo load directly.
    It does not define any links or joints itself.
    Its job is to include all other xacro files in the correct order.

    INCLUDE ORDER MATTERS:
    1. common_properties  — must come first, defines PI and materials
                            that all other files depend on
    2. inertia_macros     — must come before base and wheels,
                            both use the inertia macros
    3. base               — defines base_footprint and base_link
    4. wheels             — defines wheel links and joints,
                            attaches them to base_link
    5. gazebo             — adds Gazebo plugins and surface properties

    If you include a file that uses a macro before the file that
    defines that macro, xacro will throw an error.

    WHY name="amr_robot"?
    This name becomes the model name in Gazebo.
    It also appears in RViz and in ros2 topic list output.
    All other xacro files have <robot> tags too, but without name=
    because only one file should declare the robot name — this one.
  -->

  <!-- Step 1: Shared constants (PI) and RViz materials -->
  <xacro:include filename="$(find robot_description)/urdf/common_properties.xacro"/>

  <!-- Step 2: Inertia calculation macros -->
  <xacro:include filename="$(find robot_description)/urdf/inertia_macros.xacro"/>

  <!-- Step 3: Base chassis (base_footprint + base_link) -->
  <xacro:include filename="$(find robot_description)/urdf/base.xacro"/>

  <!-- Step 4: Wheels (left, right drive wheels + caster) -->
  <xacro:include filename="$(find robot_description)/urdf/wheels.xacro"/>

  <!-- Step 5: Gazebo plugins, colours, friction -->
  <xacro:include filename="$(find robot_description)/urdf/gazebo.xacro"/>

</robot>
```

Save and close.

---

## Why `$(find robot_description)` instead of relative paths?

Notice that in the individual files we used `filename="common_properties.xacro"` (relative path). But in `robot.xacro` we use `filename="$(find robot_description)/urdf/..."` (package path).

Here is why:

When you run `xacro wheels.xacro` directly from the urdf folder, the relative path works because xacro looks in the same directory.

But when a launch file loads `robot.xacro`, it runs from a different working directory — the install folder. At that point relative paths break. `$(find robot_description)` tells xacro to ask ROS2 where the `robot_description` package is installed, then build the full path from there. This works from any directory.

This is why robot.xacro uses package paths but the individual files use relative paths — the individual files are always included by robot.xacro, so they inherit its resolved path context.

---

## Test robot.xacro

This test requires the workspace to be built first because `$(find robot_description)` needs the package to be installed. So we do a quick test with a direct path first:

```bash
xacro robot.xacro
```

You will likely see this error:
```
xacro: error: package 'robot_description' not found
```

That is expected — we have not built yet. This is fine. We will verify robot.xacro properly after building.

First verify all five urdf files exist:

```bash
ls -1 ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/urdf/
```

**Expected:**
```
base.xacro
common_properties.xacro
gazebo.xacro
inertia_macros.xacro
robot.xacro
wheels.xacro
```

---

## PHASE 3 — Step 11 : Build the workspace

Now we build for the first time. Building installs all files into the `install/` folder so ROS2 can find them.

**Run this — from the workspace root, not from inside src:**

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1
colcon build --symlink-install
```

**Why `--symlink-install`?**

Without this flag, every time you edit a launch file or xacro file, you must rebuild for the changes to take effect. With `--symlink-install`, colcon creates symbolic links from `install/` back to your `src/` files. Edit a file in `src/`, the change is immediately visible without rebuilding. Only needed when you add new files or change `CMakeLists.txt`.

**Expected output:**
```
Starting >>> robot_description
Finished <<< robot_description [some seconds]

Summary: 1 packages finished [...]
```

If you see any errors paste them here.

After build succeeds run:

```bash
source install/setup.bash
```

**Why source?**

`source install/setup.bash` loads your workspace into the current shell session. It tells ROS2 where your packages are. Without this, `$(find robot_description)` fails, `ros2 launch robot_description ...` fails, and nothing works. You must run this in every new terminal you open.

Now test robot.xacro properly:

```bash
xacro src/robot_description/urdf/robot.xacro
```

**Expected:** Full robot XML output with all links — base_footprint, base_link, left_wheel, right_wheel, caster_wheel — and all plugins. No errors.

Perfect. robot.xacro compiled completely clean. All five links present, both plugins present, all friction values correct.

Now confirm the build succeeded. Run this:

```bash
ls ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/install/robot_description/share/robot_description/urdf/
```

**Expected — all five xacro files listed:**
```
base.xacro
common_properties.xacro
gazebo.xacro
inertia_macros.xacro
robot.xacro
wheels.xacro
```

If that looks correct, run:

```bash
source ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/install/setup.bash
```

Then verify ROS2 can find the package:

```bash
ros2 pkg prefix robot_description
```

**Expected:**
```
/home/karthik/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/install/robot_description
```

---

## PHASE 3 — Step 12 : Create the display launch file

Now we write the first launch file. This one starts robot_state_publisher and RViz so you can see your robot in 3D without Gazebo.

**Why this launch file first?**

Before adding Gazebo complexity, we verify the URDF is correct visually. If the robot looks wrong in RViz — wheels in wrong position, chassis wrong size — we fix it here before Gazebo makes debugging harder.

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/launch
gedit display.launch.py
```

**Type this exactly:**

```python
import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ─── Package path ───────────────────────────────────────────
    #
    # get_package_share_directory finds the installed package location.
    # This is the install/robot_description/share/robot_description/ folder.
    # We use this to build paths to our xacro and rviz files.
    #
    pkg = get_package_share_directory('robot_description')

    # ─── Process xacro file ─────────────────────────────────────
    #
    # xacro.process_file() compiles robot.xacro into plain URDF XML.
    # It returns an XML document object. .toxml() converts it to a string.
    # This string is what robot_state_publisher needs as its parameter.
    #
    # We do this at launch time, not at build time.
    # Every time you launch, the latest xacro files are compiled fresh.
    # This means edits to xacro files take effect on next launch
    # without rebuilding (because we used --symlink-install).
    #
    xacro_file = os.path.join(pkg, 'urdf', 'robot.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # ─── Launch argument for RViz config ────────────────────────
    #
    # DeclareLaunchArgument creates a launch argument that can be
    # overridden from the command line:
    #   ros2 launch robot_description display.launch.py use_rviz:=false
    #
    # LaunchConfiguration reads the value of that argument at runtime.
    #
    use_rviz_arg = DeclareLaunchArgument(
        name='use_rviz',
        default_value='true',
        description='Launch RViz if true'
    )
    use_rviz = LaunchConfiguration('use_rviz')

    # ─── Robot State Publisher node ─────────────────────────────
    #
    # robot_state_publisher does two things:
    # 1. Publishes /robot_description topic (the full URDF XML string)
    #    RViz reads this to know what shape to draw.
    # 2. Reads /joint_states topic (wheel angles) and publishes /tf
    #    /tf tells RViz where each link is in 3D space.
    #
    # Without robot_state_publisher:
    # - RViz cannot show the robot model
    # - No TF frames exist for any link
    # - Navigation cannot work
    #
    # parameters: robot_description is passed as a string parameter.
    # use_sim_time false here because we are not running Gazebo yet.
    # When we add Gazebo, this becomes true.
    #
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False,
        }]
    )

    # ─── Joint State Publisher GUI node ─────────────────────────
    #
    # joint_state_publisher_gui opens a small window with sliders.
    # One slider per moving joint (left_wheel_joint, right_wheel_joint).
    # Moving a slider publishes to /joint_states.
    # robot_state_publisher reads /joint_states and updates /tf.
    # Result: you can rotate wheels manually in RViz to verify joints work.
    #
    # This node is only for testing. When Gazebo runs, Gazebo publishes
    # /joint_states via the JointStatePublisher plugin instead.
    # We will remove this node from the Gazebo launch file.
    #
    jsp_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
    )

    # ─── RViz2 node ─────────────────────────────────────────────
    #
    # rviz2 is the 3D visualizer.
    # We do not pass a config file yet — RViz opens with defaults.
    # You will add displays manually in this step to understand them.
    # In a later step we create a saved config file.
    #
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
    )

    return LaunchDescription([
        use_rviz_arg,
        rsp_node,
        jsp_gui_node,
        rviz_node,
    ])
```

Save and close.

---

## Rebuild to install the launch file

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1
colcon build --symlink-install
source install/setup.bash
```

---

## Launch and verify in RViz

```bash
ros2 launch robot_description display.launch.py
```

Three things should open:
- A terminal with robot_state_publisher output
- A small Joint State Publisher GUI window with two sliders
- RViz2 window (empty for now)

**In RViz, do these steps manually:**

**Step A** — Set Fixed Frame:
In the top left panel, find `Fixed Frame`. Change it from `map` to `base_footprint`. Press Enter.

**Step B** — Add RobotModel display:
Click `Add` button (bottom left). Select `RobotModel`. Click OK.
In the RobotModel display, set `Description Topic` to `/robot_description`.
Your robot should appear — blue box chassis, two dark grey wheels, black caster sphere.

**Step C** — Add TF display:
Click `Add` again. Select `TF`. Click OK.
You should see coordinate frame axes on every link.

**Step D** — Test the sliders:
In the Joint State Publisher GUI window, move the left wheel slider.
The left wheel should rotate in RViz in real time.

**Tell me what you see:**
1. Does the robot appear in RViz?
2. Are both wheels visible on the sides?
3. Is the caster visible at the front?
4. Do the sliders rotate the wheels?

Before moving to Gazebo, confirm two things quickly. Just answer yes or no:

1. Is `/robot_state_publisher` in your `ros2 node list` output?
2. Does the blue chassis + two wheels appear in RViz?

If both yes — close the current launch with `Ctrl+C` and we start Phase 4.

---

## PHASE 4 — Step 13 : Create `gazebo.launch.py`

This launch file starts Gazebo Harmonic, spawns the robot into it, and sets up the bridge between Gazebo and ROS2.

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/launch
gedit gazebo.launch.py
```

**Type this exactly:**

```python
import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():

    # ─── Package paths ───────────────────────────────────────────
    #
    # We need two package paths:
    # 1. Our robot_description package — for the xacro file
    # 2. ros_gz_sim package — for the Gazebo launch file
    #
    pkg_robot = get_package_share_directory('robot_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # ─── Compile xacro → URDF string ────────────────────────────
    #
    # Same as display.launch.py — compile robot.xacro at launch time.
    # This string is passed to robot_state_publisher AND used to
    # spawn the robot into Gazebo.
    #
    xacro_file = os.path.join(pkg_robot, 'urdf', 'robot.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # ─── Launch Arguments ────────────────────────────────────────
    world_arg = DeclareLaunchArgument(
        name='world',
        default_value='empty',
        description='Gazebo world name'
    )

    # ─── Robot State Publisher ───────────────────────────────────
    #
    # use_sim_time: True — CRITICAL difference from display.launch.py.
    # When Gazebo runs, it publishes its own clock to /clock topic.
    # use_sim_time=True tells ALL nodes to use Gazebo clock instead
    # of system clock. Without this, TF timestamps mismatch Gazebo
    # time and transforms go stale — robot freezes in RViz.
    #
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }]
    )

    # ─── Gazebo Sim ──────────────────────────────────────────────
    #
    # We include the standard Gazebo launch file from ros_gz_sim.
    # This starts the Gazebo Harmonic simulator.
    #
    # gz_args:
    #   -r = run immediately (do not pause on start)
    #   -v4 = verbosity level 4 (shows plugin loading messages)
    #   empty.sdf = the world file to load (empty world with ground plane)
    #
    # We do NOT start our own gz_sim process — we use the one
    # provided by ros_gz_sim which has proper ROS2 integration.
    #
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r -v4 empty.sdf'}.items()
    )

    # ─── Spawn robot into Gazebo ─────────────────────────────────
    #
    # ros_gz_sim provides a create node that spawns a robot into Gazebo.
    # It reads the robot description from the /robot_description topic
    # (published by robot_state_publisher above) and creates the model
    # in the running Gazebo simulation.
    #
    # Arguments:
    #   -topic /robot_description  — read URDF from this ROS2 topic
    #   -entity amr_robot          — name of the model in Gazebo
    #   -x -y -z                   — spawn position in world frame
    #   -z 0.1 means 10cm above ground — prevents robot spawning
    #   inside the ground plane which causes physics explosions
    #
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_robot',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'amr_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0',
        ]
    )

    # ─── ROS GZ Bridge ───────────────────────────────────────────
    #
    # This is the most important node for ROS2 ↔ Gazebo communication.
    #
    # Gazebo and ROS2 are two separate systems with different
    # middleware (Gazebo uses gz-transport, ROS2 uses DDS).
    # They cannot talk to each other directly.
    # ros_gz_bridge is the translator between them.
    #
    # Each entry in the config list is one bridge:
    # format: gz_topic_name@ros2_msg_type[gz_msg_type
    #   [ = data flows FROM Gazebo TO ROS2
    #   ] = data flows FROM ROS2 TO Gazebo
    #   @ = bidirectional
    #
    # Bridges we need:
    # 1. /clock          — Gazebo simulation time → ROS2
    #                      All ROS2 nodes need this for use_sim_time
    # 2. /cmd_vel        — ROS2 → Gazebo
    #                      Your velocity commands drive the robot
    # 3. /odom           — Gazebo → ROS2
    #                      Odometry from diff_drive plugin
    # 4. /tf             — Gazebo → ROS2
    #                      Transforms from diff_drive plugin (odom→base_footprint)
    # 5. /joint_states   — Gazebo → ROS2
    #                      Wheel joint angles → robot_state_publisher
    #
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            # Clock — Gazebo sim time to ROS2
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',

            # cmd_vel — ROS2 commands to Gazebo diff_drive plugin
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',

            # Odometry — Gazebo diff_drive → ROS2
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',

            # TF — Gazebo diff_drive publishes odom→base_footprint transform
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',

            # Joint states — Gazebo JointStatePublisher → ROS2
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        parameters=[{
            'use_sim_time': True,
        }]
    )

    return LaunchDescription([
        world_arg,
        rsp_node,
        gazebo,
        spawn_robot,
        bridge,
    ])
```

Save and close.

---

## Rebuild

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1
colcon build --symlink-install
source install/setup.bash
```

---

## Launch Gazebo

```bash
ros2 launch robot_description gazebo.launch.py
```

This will:
1. Start Gazebo Harmonic with an empty world
2. Start robot_state_publisher
3. Spawn the AMR robot into Gazebo
4. Start the bridge

**Expected:** Gazebo window opens. After a few seconds the robot appears in the world — blue box with two wheels and a caster.

**In a second terminal check:**
```bash
source ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/install/setup.bash
ros2 topic list
```

You should see these topics:
```
/clock
/cmd_vel
/joint_states
/odom
/robot_description
/tf
/tf_static
```

## Quick verification before RViz — drive the robot

Open a new terminal:

```bash
source ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/install/setup.bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.0}}" --once
```

Does the robot move forward in Gazebo? Tell me yes or no.

Then stop it:
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}" --once
```

Try turning:
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.5}}" --once
```

Does it rotate?

---

## While Gazebo is running — open RViz alongside it

Open another new terminal:

```bash
source ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/install/setup.bash
rviz2
```

In RViz do these steps:

**Step A** — Fixed Frame: set to `odom` (not base_footprint — when Gazebo runs, odom is the root frame published by the diff_drive plugin)

**Step B** — Add RobotModel: Click Add → RobotModel → set Description Topic to `/robot_description`

**Step C** — Add TF: Click Add → TF

**Step D** — Add Odometry: Click Add → Odometry → set Topic to `/odom`

Good question. Let me explain both things clearly.

---

## The config folder — what goes there

The `config/` folder holds the **ros_gz_bridge configuration file**. Right now we defined the bridge topics directly inside `gazebo.launch.py` as a long list of arguments. That works, but as the project grows it becomes messy.

The cleaner way is a YAML config file in `config/` that the bridge reads. Let us create it now.

```bash
gedit ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/config/ros_gz_bridge.yaml
```

Type this:

```yaml
# ros_gz_bridge.yaml
# Defines all topic bridges between Gazebo and ROS2
#
# format of each entry:
#   ros_topic_name: the topic name in ROS2
#   gz_topic_name:  the topic name in Gazebo (sometimes different)
#   ros_type_name:  ROS2 message type
#   gz_type_name:   Gazebo message type
#   direction:      GZ_TO_ROS / ROS_TO_GZ / BIDIRECTIONAL

- ros_topic_name: /clock
  gz_topic_name: /clock
  ros_type_name: rosgraph_msgs/msg/Clock
  gz_type_name: gz.msgs.Clock
  direction: GZ_TO_ROS

- ros_topic_name: /cmd_vel
  gz_topic_name: /cmd_vel
  ros_type_name: geometry_msgs/msg/Twist
  gz_type_name: gz.msgs.Twist
  direction: ROS_TO_GZ

- ros_topic_name: /odom
  gz_topic_name: /odom
  ros_type_name: nav_msgs/msg/Odometry
  gz_type_name: gz.msgs.Odometry
  direction: GZ_TO_ROS

- ros_topic_name: /tf
  gz_topic_name: /tf
  ros_type_name: tf2_msgs/msg/TFMessage
  gz_type_name: gz.msgs.Pose_V
  direction: GZ_TO_ROS

- ros_topic_name: /joint_states
  gz_topic_name: /joint_states
  ros_type_name: sensor_msgs/msg/JointState
  gz_type_name: gz.msgs.Model
  direction: GZ_TO_ROS
```

Save and close.

---

## Now update gazebo.launch.py to use this config file

Open the launch file:

```bash
gedit ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/launch/gazebo.launch.py
```

Find the bridge node section — it currently looks like this:

```python
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        parameters=[{
            'use_sim_time': True,
        }]
    )
```

**Replace that entire bridge node block with this:**

```python
    # Path to bridge config file
    bridge_config = os.path.join(pkg_robot, 'config', 'ros_gz_bridge.yaml')

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        parameters=[{
            'config_file': bridge_config,
            'use_sim_time': True,
        }]
    )
```

Save and close.

---

## Why the config file is better

Two reasons.

First, readability. The YAML file clearly shows direction (`GZ_TO_ROS`, `ROS_TO_GZ`) which the inline argument format (`[` and `]` and `@`) hides behind cryptic symbols.

Second, maintainability. When you add a LIDAR sensor later, you just add one entry to the YAML. You do not touch the launch file at all.

---

## Rebuild and relaunch

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1
colcon build --symlink-install
source install/setup.bash
```

Kill the current Gazebo launch with `Ctrl+C` first, then:

```bash
ros2 launch robot_description gazebo.launch.py
```

In a second terminal verify topics are still all present:

```bash
source ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/install/setup.bash
ros2 topic list
```

You should see the same 7 topics as before. Paste the output and confirm Gazebo opened with the robot. Then we move to the final launch file — `robot.launch.py` which combines everything including RViz into one single launch command.




Great question. This is the most important concept to understand before moving forward. Let me explain exactly how each topic flows in your system right now.

---

Perfect mindset. That initial confusion is normal — it clears automatically as you use it more. Let's keep building.

---

## PHASE 4 — Step 14 : Create `robot.launch.py`

This is the final launch file. One command starts everything — Gazebo, RViz, robot_state_publisher, bridge, all together.

```bash
gedit ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/launch/robot.launch.py
```

Type this:

```python
import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    # ─── Package path ────────────────────────────────────────────
    pkg = get_package_share_directory('robot_description')

    # ─── Include display.launch.py ───────────────────────────────
    #
    # Instead of rewriting robot_state_publisher and RViz nodes,
    # we include the launch file we already wrote.
    # IncludeLaunchDescription pulls another launch file in.
    # This is the ROS2 way of reusing launch files — like calling
    # a function instead of copying code.
    #
    display_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'display.launch.py')
        )
    )

    # ─── Include gazebo.launch.py ────────────────────────────────
    #
    # This starts Gazebo, spawns the robot, and starts the bridge.
    # We wrap it in a TimerAction with a small delay.
    #
    # WHY the delay?
    # robot_state_publisher must publish /robot_description BEFORE
    # the spawn node tries to read it. If both start at exactly the
    # same time, spawn_robot sometimes starts before /robot_description
    # is available and fails silently — robot never appears in Gazebo.
    # A 2 second delay gives robot_state_publisher time to start up.
    #
    gazebo_launch = TimerAction(
        period=2.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg, 'launch', 'gazebo.launch.py')
                )
            )
        ]
    )

    return LaunchDescription([
        display_launch,
        gazebo_launch,
    ])
```

Save and close.

---

## But wait — display.launch.py has a conflict

When `robot.launch.py` includes both `display.launch.py` and `gazebo.launch.py`, there is a problem.

`display.launch.py` starts `robot_state_publisher` with `use_sim_time: False`.
`gazebo.launch.py` also starts `robot_state_publisher` with `use_sim_time: True`.

Two robot_state_publisher nodes running = conflict.

We need to fix `display.launch.py` so it does not start robot_state_publisher on its own when called from `robot.launch.py`. The cleanest way is to add a launch argument to control this.

```bash
gedit ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/launch/display.launch.py
```

Find this line near the top of `generate_launch_description()`:

```python
    use_rviz_arg = DeclareLaunchArgument(
```

Add a new argument block just before it:

```python
    # Controls whether this launch file starts robot_state_publisher.
    # When called standalone: use_rsp=true (default) — starts RSP.
    # When called from robot.launch.py: gazebo.launch.py handles RSP.
    # So robot.launch.py passes use_rsp:=false to this file.
    use_rsp_arg = DeclareLaunchArgument(
        name='use_rsp',
        default_value='true',
        description='Start robot_state_publisher if true'
    )
    use_rsp = LaunchConfiguration('use_rsp')
```

Then find the `rsp_node` definition and replace it with a conditional version. Find:

```python
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False,
        }]
    )
```

Replace with:

```python
    from launch.conditions import IfCondition
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        condition=IfCondition(use_rsp),
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False,
        }]
    )
```

Then in the `return LaunchDescription([...])` at the bottom, add `use_rsp_arg`:

```python
    return LaunchDescription([
        use_rsp_arg,
        use_rviz_arg,
        rsp_node,
        jsp_gui_node,
        rviz_node,
    ])
```

Save and close.

---

Now update `robot.launch.py` to pass `use_rsp:=false` to display launch:

```bash
gedit ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/src/robot_description/launch/robot.launch.py
```

Replace the `display_launch` block with:

```python
    display_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'display.launch.py')
        ),
        launch_arguments={
            'use_rsp': 'false',
        }.items()
    )
```

Save and close.

---

## Rebuild

```bash
cd ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1
colcon build --symlink-install
source install/setup.bash
```

---

## Final launch — one command for everything

Kill any running launch first with `Ctrl+C`. Then:

```bash
ros2 launch robot_description robot.launch.py
```

Wait about 5 seconds for everything to start. You should see:
- Gazebo opens with robot
- RViz opens

In RViz set Fixed Frame to `odom`, add RobotModel with topic `/robot_description`, add TF display.

In a second terminal drive the robot:

```bash
source ~/Documents/ROS2_DEVELOPMENTS/ros2_gazebo_workspace_1/install/setup.bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3}, angular: {z: 0.3}}" --rate 10
```

Robot should move in Gazebo and RViz simultaneously.

---
## The big picture — two separate worlds

Your system has two completely separate middleware systems running simultaneously.

```
┌─────────────────────┐         ┌─────────────────────┐
│      ROS2 world     │         │    Gazebo world      │
│   (DDS middleware)  │         │  (gz-transport)      │
│                     │◄──────►│                      │
│  your ROS2 nodes    │  BRIDGE │  physics simulation  │
│  rviz, nav2, etc    │         │  diff_drive plugin   │
└─────────────────────┘         └─────────────────────┘
```

They cannot talk directly. The bridge sits in the middle and translates every message.

---

## Each topic explained — who publishes, who subscribes

---

### /clock

```
Gazebo sim engine
      │  publishes sim time every tick
      │  gz.msgs.Clock
      ▼
  ros_gz_bridge  (GZ_TO_ROS)
      │  converts to rosgraph_msgs/msg/Clock
      ▼
  ROS2 /clock topic
      │
      ├──► robot_state_publisher  (uses sim time for TF timestamps)
      ├──► ros_gz_bridge itself   (timestamps its own messages)
      └──► rviz2                  (syncs display to sim time)
```

Direction: Gazebo → ROS2 only. No one sends time back to Gazebo.

Why needed: Without this, all ROS2 nodes use wall clock time. Gazebo uses its own sim time. Timestamps mismatch and TF transforms appear stale — robot freezes in RViz even while moving in Gazebo.

---

### /cmd_vel

```
You (or Nav2 later)
      │  publishes geometry_msgs/msg/Twist
      │  {linear: {x: 0.3}, angular: {z: 0.0}}
      ▼
  ROS2 /cmd_vel topic
      │
      ▼
  ros_gz_bridge  (ROS_TO_GZ)
      │  converts to gz.msgs.Twist
      ▼
  Gazebo /cmd_vel topic
      │
      ▼
  DiffDrive plugin inside Gazebo
      │  reads linear.x and angular.z
      │  computes left wheel speed and right wheel speed
      │  applies torque to left_wheel_joint and right_wheel_joint
      ▼
  Robot moves in Gazebo physics simulation
```

Direction: ROS2 → Gazebo only. Gazebo never sends velocity commands back to ROS2.

Why needed: This is how you drive the robot. Without this bridge, your `ros2 topic pub /cmd_vel` command stays inside ROS2 world and Gazebo never sees it.

---

### /odom

```
DiffDrive plugin inside Gazebo
      │  calculates robot position by integrating wheel rotations
      │  publishes nav_msgs/Odometry every 20ms (50Hz)
      │  contains: position x,y,z + orientation + velocity
      ▼
  Gazebo /odom topic (gz.msgs.Odometry)
      │
      ▼
  ros_gz_bridge  (GZ_TO_ROS)
      │  converts to nav_msgs/msg/Odometry
      ▼
  ROS2 /odom topic
      │
      ├──► RViz Odometry display  (draws the path trail)
      └──► Nav2 later             (uses position for navigation)
```

Direction: Gazebo → ROS2 only. Odometry is an output — the simulation tells you where the robot thinks it is.

---

### /tf

```
DiffDrive plugin inside Gazebo
      │  publishes transform: odom frame → base_footprint frame
      │  this tells ROS2 where the robot is relative to its start point
      ▼
  Gazebo /tf topic (gz.msgs.Pose_V)
      │
      ▼
  ros_gz_bridge  (GZ_TO_ROS)
      │  converts to tf2_msgs/msg/TFMessage
      ▼
  ROS2 /tf topic
      │
      ▼
  robot_state_publisher
      │  adds wheel transforms: base_footprint → left_wheel
      │                         base_footprint → right_wheel
      │                         base_footprint → caster_wheel
      ▼
  Complete TF tree in ROS2:
      odom → base_footprint → base_link → left_wheel
                                        → right_wheel
                                        → caster_wheel
      │
      ▼
  RViz reads this tree to position every link in 3D space
```

Direction: Gazebo → ROS2. The DiffDrive plugin owns the odom→base_footprint transform. robot_state_publisher owns the base_footprint→wheels transforms. Both contribute to the same /tf topic.

---

### /joint_states

```
JointStatePublisher plugin inside Gazebo
      │  reads actual joint angles from physics simulation
      │  left_wheel_joint current angle in radians
      │  right_wheel_joint current angle in radians
      │  publishes gz.msgs.Model
      ▼
  ros_gz_bridge  (GZ_TO_ROS)
      │  converts to sensor_msgs/msg/JointState
      ▼
  ROS2 /joint_states topic
      │
      ▼
  robot_state_publisher
      │  reads wheel angles
      │  computes forward kinematics
      │  publishes updated TF for wheel frames
      ▼
  Wheel frames rotate in RViz as wheels spin in Gazebo
```

Direction: Gazebo → ROS2. This is the feedback loop — Gazebo tells ROS2 what the joints are actually doing.

---

## The complete data flow diagram

```
YOU
 │
 │  ros2 topic pub /cmd_vel
 ▼
ROS2 /cmd_vel ──► BRIDGE ──► Gazebo DiffDrive plugin
                                    │
                         ┌──────────┼──────────┐
                         ▼          ▼          ▼
                    wheels spin   /odom      /tf
                         │          │          │
                         ▼          ▼          ▼
                    JointState   BRIDGE      BRIDGE
                    Publisher       │          │
                         │          ▼          ▼
                         ▼      ROS2 /odom  ROS2 /tf
                       BRIDGE       │          │
                         │          ▼          ▼
                         ▼        RViz       robot_state_publisher
                   ROS2             │          │
                   /joint_states    │          ▼
                         │          │      more /tf frames
                         ▼          │          │
                   robot_state_     └──────────┘
                   publisher                   │
                         │                     ▼
                         └──────────────► RViz renders
                                         robot moving
```

---

## The bidirectional case — when would @ be used?

In your current bridge config you have `GZ_TO_ROS` and `ROS_TO_GZ`. Bidirectional (`@` in the old format, `BIDIRECTIONAL` in YAML) means the bridge listens on both sides and forwards in both directions.

You would use bidirectional for something like a service or a topic that both systems need to read and write. In mobile robotics this is rare. Most data flows one way — commands go in, sensor data comes out.

---

