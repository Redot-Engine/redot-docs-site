
# Building from source

.. highlight:: shell

Redot prides itself on being very easy to build, by C++ projects' standards.
[Redot uses the SCons build system](doc_faq_why_scons), and after the initial
setup compiling the engine for your current platform should be as easy as running

```
scons

```

But you will probably need to use at least some of the available options to configure
the build to match your specific needs, be it a custom engine fork, a lightweight build
stripped of extra modules, or an executable targeting engine development.

The articles below should help you navigate configuration options available, as well as
prerequisites required to compile Redot exactly the way you need.

.. rubric:: Basics of building Redot
   :heading-level: 2

Let's start with basics, and learn how to get Redot's source code, and then which options
to use to compile it regardless of your target platform.
