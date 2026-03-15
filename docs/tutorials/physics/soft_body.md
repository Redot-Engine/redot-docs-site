:article_outdated: True

# Using SoftBody

Soft bodies (or *soft-body dynamics*) simulate movement, changing shape and other physical properties of deformable objects.
This can for example be used to simulate cloth or to create more realistic characters.

### Basic set-up

A [SoftBody3D ](class_SoftBody3D) node is used for soft body simulations.

We will create a bouncy cube to demonstrate the setup of a soft body.

Create a new scene with a ``Node3D`` node as root. Then, create a ``Softbody`` node. Add a ``CubeMesh`` in the ``mesh`` property of the node in the inspector and increase the subdivision of the mesh for simulation.

![Image](img/softbody_cube.png)

Set the parameters to obtain the type of soft body you aim for. Try to keep the ``Simulation Precision`` above 5, otherwise, the soft body may collapse.

![Image](img/softbody_cube_menu.png)

:::note

Play the scene to view the simulation.

:::tip

### Cloak simulation

Let's make a cloak in the Platformer3D demo.

:::note

Open the ``Player`` scene, add a ``SoftBody`` node and assign a ``PlaneMesh`` to it.

Open the ``PlaneMesh`` properties and set the size(x: 0.5 y: 1) then set ``Subdivide Width`` and ``Subdivide Depth`` to 5. Adjust the ``SoftBody``'s position. You should end up with something like this:

![Image](img/softbody_cloak_subdivide.png)

:::tip

Add a [BoneAttachment3D ](class_BoneAttachment3D) node under the skeleton node and select the Neck bone to attach the cloak to the character skeleton.

:::note

![Image](img/softbody_cloak_bone_attach.png)

To create pinned joints, select the upper vertices in the ``SoftBody`` node:

![Image](img/softbody_cloak_pinned.png)

The pinned joints can be found in ``SoftBody``'s ``Attachments`` property, choose the ``BoneAttachment`` as the ``SpatialAttachment`` for each pinned joints, the pinned joints are now attached to the neck.

![Image](img/softbody_cloak_pinned_attach.png)

Last step is to avoid clipping by adding the Kinematic Body `Player` to ``Parent Collision Ignore`` of the ``SoftBody``.

![Image](img/softbody_cloak_ignore.png)

Play the scene and the cloak should simulate correctly.

![Image](img/softbody_cloak_finish.png)

This covers the basic settings of softbody, experiment with the parameters to achieve the effect you are aiming for when making your game.

:::

:::

:::

:::

:::
