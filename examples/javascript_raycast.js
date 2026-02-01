// Raycast example for JavaScript controller
// obj.rayCast(to, from?, dist?, prop?, face?, xray?, mask?) - result in obj.lastRayCastResult next frame
// obj.rayCastTo(target, dist?, prop?) - result in obj.lastRayCastResult next frame

const cont = bge.logic.getCurrentController();
const obj = cont.owner;
const scene = bge.logic.getCurrentScene();

if (obj) {
    // Read previous frame's rayCast result (if we cast last frame)
    const lastHit = obj.lastRayCastResult;
    if (lastHit && lastHit.object) {
        console.log("Last hit: " + lastHit.object.name + " at " + lastHit.point);
    }

    // Raycast from object position downward (e.g. ground check); result available next frame
    const down = [obj.position[0], obj.position[1], obj.position[2] - 10];
    obj.rayCast(down, undefined, 15);

    // rayCastTo: check if another object is in range; result in lastRayCastResult next frame
    const target = scene.getObject("Target");
    if (target) {
        obj.rayCastTo(target, 30);
    }
}
