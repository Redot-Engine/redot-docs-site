
# KDevelop

[KDevelop ](https://www.kdevelop.org) is a free, open source IDE for all desktop platforms.

## Importing the project

- From the KDevelop's main screen select **Open Project**.

![Image](img/kdevelop_newproject.png)

   KDevelop's main screen.

- Navigate to the Godot root folder and select it.
- On the next screen, choose **Custom Build System** for the **Project Manager**.

![Image](img/kdevelop_custombuild.png)

- After the project has been imported, open the project configuration by right-clicking
  on it in the **Projects** panel and selecting **Open Configuration..** option.

![Image](img/kdevelop_openconfig.png)

- Under **Language Support** open the **Includes/Imports** tab and add the following paths:

```none
.  // A dot, to indicate the root of the Godot project
core/
core/os/
core/math/
drivers/
platform/<your_platform>/  // Replace <your_platform> with a folder
                              corresponding to your current platform

```

![Image](img/kdevelop_addincludes.png)

- Apply the changes.
- Under **Custom Build System** add a new build configuration with the following settings:

  +-----------------+------------------------------------------------------------------------------+
  | Build Directory | *blank*                                                                      |
  +-----------------+------------------------------------------------------------------------------+
  | Enable          | **True**                                                                     |
  +-----------------+------------------------------------------------------------------------------+
  | Executable      | **scons**                                                                    |
  +-----------------+------------------------------------------------------------------------------+
  | Arguments       | See [doc_introduction_to_the_buildsystem](doc_introduction_to_the_buildsystem) for a full list of arguments. |
  +-----------------+------------------------------------------------------------------------------+

![Image](img/kdevelop_buildconfig.png)

- Apply the changes and close the configuration window.

## Debugging the project

- Select **Run &gt; Configure Launches...** from the top menu.

![Image](img/kdevelop_configlaunches.png)

- Click **Add** to create a new launch configuration.
- Select **Executable** option and specify the path to your executable located in
  the ``&lt;Godot root directory&gt;/bin`` folder. The name depends on your build configuration,
  e.g. ``godot.linuxbsd.editor.dev.x86_64`` for 64-bit LinuxBSD platform with
  ``platform=editor`` and ``dev_build=yes``.

![Image](img/kdevelop_configlaunches2.png)

If you run into any issues, ask for help in one of
[Godot's community channels ](https://godotengine.org/community)_.