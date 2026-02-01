// Keyboard control (apenas movimento do player)
// Setup: no Cubo, Always + Keyboard no mesmo controller com este script.

const cont = bge.logic.getCurrentController();
const obj = cont.owner;
const kb = bge.logic.getKeyboardInput();
const speed = 0.05;

if (kb.isPressed(bge.events.WKEY)) obj.applyMovement([0, 0, speed]);
if (kb.isPressed(bge.events.SKEY)) obj.applyMovement([0, 0, -speed]);
if (kb.isPressed(bge.events.AKEY)) obj.applyMovement([-speed, 0, 0]);
if (kb.isPressed(bge.events.DKEY)) obj.applyMovement([speed, 0, 0]);
