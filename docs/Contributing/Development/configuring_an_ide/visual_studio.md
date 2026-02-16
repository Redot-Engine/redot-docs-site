
# Visual Studio

[Visual Studio Community ](https://visualstudio.microsoft.com)_ is a Windows-only IDE
by [Microsoft ](https://microsoft.com) that's free for individual use or non-commercial use within organizations.
It has many useful features, such as memory view, performance view, source
control and more.

## Importing the project

Visual Studio requires a solution file to work on a project. While Godot does not come
with the solution file, it can be generated using SCons.

- Navigate to the Godot root folder and open a Command Prompt or PowerShell window.
- | Run ``scons platform=windows vsproj=yes dev_build=yes`` to generate the solution with debug symbols.
  | The ``vsproj`` parameter signals that you want Visual Studio solution generated.
  | The ``dev_build`` parameter makes sure the debug symbols are included, allowing to e.g. step through code using breakpoints.
- You can now open the project by double-clicking on the ``godot.sln`` in the project root
  or by using the **Open a project or solution** option inside of the Visual Studio.
- Use the **Build** top menu to build the project.

:::warning

in the installer:

![Image](img/vs_1_install_cpp_package.png)

:::

## Debugging the project

Visual Studio features a powerful debugger. This allows the user to examine Godot's
source code, stop at specific points in the code, inspect the current execution context,
and make live changes to the codebase.

You can launch the project with the debugger attached using the **Debug &gt; Start Debugging**
option from the top menu. However, unless you want to debug the Project Manager specifically,
you'd need to configure debugging options first. This is due to the fact that when the Godot
Project Manager opens a project, the initial process is terminated and the debugger gets detached.

- To configure the launch options to use with the debugger use **Project &gt; Properties**
  from the top menu:

![Image](img/vs_2_project_properties.png)

- Open the **Debugging** section and under **Command Arguments** add two new arguments:
  the ``-e`` flag opens the editor instead of the Project Manager, and the ``--path`` argument
  tells the executable to open the specified project (must be provided as an *absolute* path
  to the project root, not the ``project.godot`` file; if the path contains spaces be sure to pass it inside double quotation marks).

![Image](img/vs_3_debug_command_line.webp)

To learn more about command line arguments, refer to the
[command line tutorial ](doc_command_line_tutorial).

Even if you start the project without a debugger attached it can still be connected to the running
process using **Debug &gt; Attach to Process...** menu.

To check that everything is working, put a breakpoint in ``main.cpp`` and press :kbd:`F5` to
start debugging.

![Image](img/vs_4_debugging_main.png)

If you run into any issues, ask for help in one of
[Godot's community channels ](https://godotengine.org/community)_.