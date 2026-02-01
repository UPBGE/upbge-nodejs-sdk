// Keyboard control example for JavaScript controller
// Requires: Keyboard sensor named "Keyboard" and linked to this controller

const cont = bge.logic.getCurrentController();
const obj = cont.owner;

const keyboard = cont.sensors["Keyboard"];

if (keyboard && keyboard.events && keyboard.events.length > 0) {
    const speed = 0.1;
    const ACTIVE = bge.events.ACTIVE;
    const JUST_ACTIVATED = bge.events.JUST_ACTIVATED;
    for (const keyEvent of keyboard.events) {
        const key = keyEvent[0];
        const status = keyEvent[1];
        if (status !== ACTIVE && status !== JUST_ACTIVATED) continue;
        if (key === bge.events.WKEY) obj.applyMovement([0, 0, -speed]);
        if (key === bge.events.SKEY) obj.applyMovement([0, 0, speed]);
        if (key === bge.events.AKEY) obj.applyMovement([-speed, 0, 0]);
        if (key === bge.events.DKEY) obj.applyMovement([speed, 0, 0]);
    }
}
