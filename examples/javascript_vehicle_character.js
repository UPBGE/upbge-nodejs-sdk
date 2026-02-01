// Vehicle and Character example for JavaScript controller
// Requires: dynamic/rigid body chassis, wheel objects, or character physics

const cont = bge.logic.getCurrentController();
const scene = bge.logic.getCurrentScene();
const obj = cont.owner;

// --- bge.constraints: gravity ---
bge.constraints.setGravity(0, 0, -9.81);

// --- Vehicle: createVehicle(chassis) once, then vehicle* commands with chassis object ---
// Create vehicle on first frame (e.g. when Always sensor is positive); chassis must have physics.
bge.constraints.createVehicle(obj);
// addWheel(chassis, wheel, connectionPoint, downDir, axleDir, suspensionRestLength, wheelRadius, hasSteering)
const wheelFL = scene.getObject("WheelFL") || scene.get("WheelFL");
if (wheelFL) bge.constraints.vehicleAddWheel(obj, wheelFL, [1, 1, 0], [0, 0, -1], [0, 1, 0], 0.5, 0.4, true);
// Steering and engine (call every frame as needed)
bge.constraints.vehicleSetSteeringValue(obj, 0, 0.2);
bge.constraints.vehicleSetSteeringValue(obj, 1, 0.2);
bge.constraints.vehicleApplyEngineForce(obj, 2, 500);
bge.constraints.vehicleApplyEngineForce(obj, 3, 500);

// --- Character: characterJump(obj), characterWalkDirection(obj, vec) ---
const charObj = scene.getObject("Player") || scene.get("Player");
if (charObj) {
    // bge.constraints.characterJump(charObj);  // call when e.g. space pressed
    bge.constraints.characterWalkDirection(charObj, [0, 0.1, 0]);
    // bge.constraints.characterSetVelocity(charObj, [0, 0, 5], 0.2, false);
}
