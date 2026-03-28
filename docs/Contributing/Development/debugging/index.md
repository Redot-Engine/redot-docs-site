
# Debugging and profiling

This section contains pages that provide guidance if you're looking at the
engine code trying to find an underlying issue or an optimization possibility.

.. toctree::
   :maxdepth: 1
   :name: toc-devel-cpp-debug-profiling

   using_cpp_profilers
   using_sanitizers
   macos_debug
   vulkan/index

## Debugging the editor

When working on the Redot editor keep in mind that by default the executable
will start in the Project Manager mode. Opening a project from the Project
Manager spawns a new process, which stops the debugging session. To avoid that
you should launch directly into the project using ``-e`` and ``--path`` launch
options.

For example, using ``gdb`` directly, you may do this:

```none
gdb Redot
> run -e --path ~/myproject

```

You can also run the editor directly from your project's folder. In that case,
only the ``-e`` option is required.

```none
cd ~/myproject
gdb Redot
> run -e

```

You can learn more about these launch options and other command line arguments
in the [command line tutorial](../../../tutorials/editor/command_line_tutorial.md).

If you're using a code editor or an IDE to debug Redot, check out our
[configuration guides](../configuring_an_ide/index.md), which cover the setup
process for building and debugging with your particular editor.