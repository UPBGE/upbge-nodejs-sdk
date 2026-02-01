# JavaScript Examples for UPBGE

This directory contains example scripts demonstrating JavaScript usage in UPBGE.

## Available Examples

### JavaScript Examples

- **javascript_basic_movement.js** - Basic object movement example
  - Moves an object forward continuously
  - Demonstrates accessing controller and object properties

- **javascript_keyboard_control.js** - Keyboard input handling
  - Responds to W/A/S/D key presses
  - Moves object based on keyboard input
  - Requires a Keyboard sensor linked to the controller

- **javascript_sensor_actuator.js** - Working with sensors and actuators
  - Checks sensor state and activates actuators
  - Demonstrates collision detection
  - Shows how to iterate over hit objects

- **javascript_scene_access.js** - Accessing scene objects
  - Gets active camera
  - Finds objects by name (scene.get)
  - Calculates distances between objects
  - Iterates over all scene objects

- **javascript_raycast.js** - Raycasting
  - obj.rayCast(to, from?, dist?, prop?, face?, xray?, mask?)
  - obj.rayCastTo(other, dist?, prop?) → { object, point, normal }

- **javascript_vehicle_character.js** - Physics constraints
  - bge.constraints.setGravity, createVehicle, getVehicleConstraint, getCharacter
  - Vehicle: addWheel, setSteeringValue, applyEngineForce, applyBraking
  - Character: jump, walkDirection, setVelocity, onGround

## How to Use

1. Copy the example code into a JavaScript controller in UPBGE
2. Set up the required sensors/actuators as mentioned in each example
3. Run the game (Press P) to see the script in action

## Requirements

- UPBGE with the Node.js SDK add-on installed
- Node.js (bundled in SDK or system PATH)

## Notes

- All examples assume a basic understanding of JavaScript
- Sensor and actuator names in examples are placeholders - use your actual names

## See Also

- JavaScript API (types/bge.d.ts for editor hints)
- Python API Documentation (for reference, as APIs are similar)
