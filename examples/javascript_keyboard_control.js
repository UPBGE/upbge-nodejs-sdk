// Keyboard control example for JavaScript controller
// Configure the Keyboard sensor in the Logic Editor to the desired key (e.g. A).
// The controller runs only when that key is pressed, so no key check is needed here.

const cont = bge.logic.getCurrentController();
const obj = cont.owner;

const speed = 0.1;
// Movement for this key (e.g. A = left). Use one sensor+controller per direction if needed.
obj.applyMovement([-speed, 0, 0]);
