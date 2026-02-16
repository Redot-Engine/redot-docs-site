
# Variant class

## About

Variant is the most important datatype in Godot. A Variant takes up only 24
bytes on 64-bit platforms (20 bytes on 32-bit platforms) and can store almost
any engine datatype inside of it. Variants are rarely used to hold information
for long periods of time, instead they are used mainly for communication,
editing, serialization and generally moving data around.

A Variant can:

-  Store almost any datatype.
-  Perform operations between many variants (GDScript uses Variant as
   its atomic/native datatype).
-  Be hashed, so it can be compared quickly to other variants.
-  Be used to convert safely between datatypes.
-  Be used to abstract calling methods and their arguments (Godot
   exports all its functions through variants).
-  Be used to defer calls or move data between threads.
-  Be serialized as binary and stored to disk, or transferred via
   network.
-  Be serialized to text and use it for printing values and editable
   settings.
-  Work as an exported property, so the editor can edit it universally.
-  Be used for dictionaries, arrays, parsers, etc.

Basically, thanks to the Variant class, writing Godot itself was a much,
much easier task, as it allows for highly dynamic constructs not common
of C++ with little effort. Become a friend of Variant today.

:::note

All types within Variant except Nil and Object **cannot** be ``null`` and
must always store a valid value. These types within Variant are therefore
called *non-nullable* types.

One of the Variant types is *Nil* which can only store the value ``null``.
Therefore, it is possible for a Variant to contain the value ``null``, even
though all Variant types excluding Nil and Object are non-nullable.

:::

### References

-  [core/variant/variant.h ](https://github.com/godotengine/godot/blob/master/core/variant/variant.h)_

## List of variant types

These types are available in Variant:

+---------------------------------+---------------------------+
| Type                            | Notes                     |
+=================================+===========================+
| Nil (can only store ``null``)   | Nullable type             |
+---------------------------------+---------------------------+
| [class_bool](class_bool)               |                           |
+---------------------------------+---------------------------+
| [class_int](class_int)                |                           |
+---------------------------------+---------------------------+
| [class_float](class_float)              |                           |
+---------------------------------+---------------------------+
| [class_string](class_string)             |                           |
+---------------------------------+---------------------------+
| [class_vector2](class_vector2)            |                           |
+---------------------------------+---------------------------+
| [class_vector2i](class_vector2i)           |                           |
+---------------------------------+---------------------------+
| [class_rect2](class_rect2)              | 2D counterpart of AABB    |
+---------------------------------+---------------------------+
| [class_rect2i](class_rect2i)             |                           |
+---------------------------------+---------------------------+
| [class_vector3](class_vector3)            |                           |
+---------------------------------+---------------------------+
| [class_vector3i](class_vector3i)           |                           |
+---------------------------------+---------------------------+
| [class_transform2d](class_transform2d)        |                           |
+---------------------------------+---------------------------+
| [class_vector4](class_vector4)            |                           |
+---------------------------------+---------------------------+
| [class_vector4i](class_vector4i)           |                           |
+---------------------------------+---------------------------+
| [class_plane](class_plane)              |                           |
+---------------------------------+---------------------------+
| [class_quaternion](class_quaternion)         |                           |
+---------------------------------+---------------------------+
| [class_aabb](class_aabb)               | 3D counterpart of Rect2   |
+---------------------------------+---------------------------+
| [class_basis](class_basis)              |                           |
+---------------------------------+---------------------------+
| [class_transform3d](class_transform3d)        |                           |
+---------------------------------+---------------------------+
| [class_projection](class_projection)         |                           |
+---------------------------------+---------------------------+
| [class_color](class_color)              |                           |
+---------------------------------+---------------------------+
| [class_stringname](class_stringname)         |                           |
+---------------------------------+---------------------------+
| [class_nodepath](class_nodepath)           |                           |
+---------------------------------+---------------------------+
| [class_rid](class_rid)                |                           |
+---------------------------------+---------------------------+
| [class_object](class_object)             | Nullable type             |
+---------------------------------+---------------------------+
| [class_callable](class_callable)           |                           |
+---------------------------------+---------------------------+
| [class_signal](class_signal)             |                           |
+---------------------------------+---------------------------+
| [class_dictionary](class_dictionary)         |                           |
+---------------------------------+---------------------------+
| [class_array](class_array)              |                           |
+---------------------------------+---------------------------+
| [class_packedbytearray](class_packedbytearray)    |                           |
+---------------------------------+---------------------------+
| [class_packedint32array](class_packedint32array)   |                           |
+---------------------------------+---------------------------+
| [class_packedint64array](class_packedint64array)   |                           |
+---------------------------------+---------------------------+
| [class_packedfloat32array](class_packedfloat32array) |                           |
+---------------------------------+---------------------------+
| [class_packedfloat64array](class_packedfloat64array) |                           |
+---------------------------------+---------------------------+
| [class_packedstringarray](class_packedstringarray)  |                           |
+---------------------------------+---------------------------+
| [class_packedvector2array](class_packedvector2array) |                           |
+---------------------------------+---------------------------+
| [class_packedvector3array](class_packedvector3array) |                           |
+---------------------------------+---------------------------+
| [class_packedcolorarray](class_packedcolorarray)   |                           |
+---------------------------------+---------------------------+
| [class_packedvector4array](class_packedvector4array) |                           |
+---------------------------------+---------------------------+

## Containers: Array and Dictionary

Both [class_array](class_array) and [class_dictionary](class_dictionary) are implemented using
variants. A Dictionary can match any datatype used as key to any other datatype.
An Array just holds an array of Variants. Of course, a Variant can also hold a
Dictionary or an Array inside, making it even more flexible.

Modifications to a container will modify all references to
it. A Mutex should be created to lock it if
[multi-threaded access ](doc_using_multiple_threads) is desired.

### References

-  [core/variant/dictionary.h ](https://github.com/godotengine/godot/blob/master/core/variant/dictionary.h)_
-  [core/variant/array.h ](https://github.com/godotengine/godot/blob/master/core/variant/array.h)_