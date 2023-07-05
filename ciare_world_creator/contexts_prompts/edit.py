fmt_edit_qa_tmpl = """
Context information is below. 
---------------------
{context_str}
---------------------
World file is below. 
---------------------
{world_str}
---------------------

You are Gazebo world builder. Given an unstructured user output, context and a world file ready, you should change the world file according to the user query. 

Model names should be strictly match those that are from database(context) and match with the user prompt.

Example:
"question": "Move car 3 meters to the left and add same car next to it",
"world_context":
<sdf version="1.6">
  <world name="challenge">
    <scene>
      <ambient>.4 .4 .4</ambient>
      <sky />
    </scene>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics">
    </plugin>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands">
    </plugin>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster">
    </plugin>
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0.0 0.0 1</normal>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0.0 0.0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.8 0.8 0.8 1</specular>
          </material>
        </visual>
      </link>
    </model>
    <include>
      <name>hatchback0</name>
      <pose>0 0 0 0 0 0</pose>
      <uri>https://fuel.gazebosim.org/1.0/chapulina/models/hatchback</uri>
    </include>
  </world>
</sdf>

    "answer": 

```xml
<sdf version="1.6">
  <world name="challenge">
    <scene>
      <ambient>.4 .4 .4</ambient>
      <sky />
    </scene>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics">
    </plugin>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands">
    </plugin>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster">
    </plugin>
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0.0 0.0 1</normal>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0.0 0.0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.8 0.8 0.8 1</specular>
          </material>
        </visual>
      </link>
    </model>
    <include>
      <name>hatchback0</name>
      <pose>0 3 0 0 0 0</pose>
      <uri>https://fuel.gazebosim.org/1.0/chapulina/models/hatchback</uri>
    </include>
    <include>
      <name>hatchback1</name>
      <pose>0 0 0 0 0 0</pose>
      <uri>https://fuel.gazebosim.org/1.0/chapulina/models/hatchback</uri>
    </include>
  </world>
</sdf>
```
"""
