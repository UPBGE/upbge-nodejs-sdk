/**
 * SPDX-FileCopyrightText: 2024 UPBGE Authors
 * SPDX-License-Identifier: GPL-2.0-or-later
 *
 * BGE Bridge for Node.js - UPBGE JavaScript SDK
 *
 * This bridge provides a JavaScript API that mimics UPBGE's BGE module.
 * All API calls are queued as commands and printed as JSON for the Python side to execute.
 *
 * Placeholders that will be replaced by Python:
 * - __PLACEHOLDER_CONTEXT__ : JSON string with BGE context
 * - __PLACEHOLDER_USER_CODE__ : User's JavaScript code
 */

const __BGE_CONTEXT__ = __PLACEHOLDER_CONTEXT__ || {};
let __bgeCommands = [];

function __bgeQueue(cmd) {
    __bgeCommands.push(cmd);
}

function __bgeQueueForObject(op, objName, extra) {
    const ctx = __BGE_CONTEXT__ || {};
    const payload = Object.assign({
        op,
        scene: ctx.scene_name || "",
        object: objName || ctx.object_name || ""
    }, extra || {});
    __bgeQueue(payload);
}

function __bgeMakeGameObject(name) {
    const ctx = __BGE_CONTEXT__ || {};
    const objName = name || ctx.object_name || "";
    return {
        name: objName,
        get position() {
            const objPositions = ctx.object_positions || {};
            if (objPositions[objName] && Array.isArray(objPositions[objName])) {
                return objPositions[objName].slice();
            }
            if (ctx.object_name === objName && ctx.position && Array.isArray(ctx.position)) {
                return ctx.position.slice();
            }
            return [0, 0, 0];
        },
        set position(v) {
            __bgeQueueForObject("setPosition", objName, {
                value: Array.from(v || [0, 0, 0])
            });
        },
        get rotation() {
            if (ctx.object_name === objName && ctx.rotation && Array.isArray(ctx.rotation)) {
                return ctx.rotation.slice();
            }
            return [0, 0, 0];
        },
        set rotation(v) {
            __bgeQueueForObject("setRotation", objName, {
                value: Array.from(v || [0, 0, 0])
            });
        },
        get scale() {
            if (ctx.object_name === objName && ctx.scale && Array.isArray(ctx.scale)) {
                return ctx.scale.slice();
            }
            return [1, 1, 1];
        },
        set scale(v) {
            __bgeQueueForObject("setScale", objName, {
                value: Array.from(v || [1, 1, 1])
            });
        },
        set localPosition(v) {
            __bgeQueueForObject("setLocalPosition", objName, {
                value: Array.from(v || [0, 0, 0])
            });
        },
        set localRotation(v) {
            __bgeQueueForObject("setLocalRotation", objName, {
                value: Array.from(v || [0, 0, 0])
            });
        },
        applyMovement(vec) {
            __bgeQueueForObject("applyMovement", objName, {
                vec: Array.from(vec || [0, 0, 0])
            });
        },
        getProperty(propName) {
            const props = (ctx.properties && ctx.object_name === objName) ? ctx.properties : null;
            if (props && Object.prototype.hasOwnProperty.call(props, propName)) {
                return props[propName];
            }
            return null;
        },
        setProperty(propName, value) {
            __bgeQueueForObject("setProperty", objName, {
                property: String(propName),
                value: value
            });
        },
        getParent() {
            if (ctx.object_name === objName && ctx.parent_name) {
                return __bgeMakeGameObject(ctx.parent_name);
            }
            return null;
        },
        setParent(parent) {
            const parentName = parent && parent.name ? parent.name : null;
            __bgeQueueForObject("setParent", objName, {
                parent: parentName
            });
        },
        getChildren() {
            if (ctx.object_name === objName && Array.isArray(ctx.children)) {
                return ctx.children.map(function(n) { return __bgeMakeGameObject(n); });
            }
            return [];
        },
        lookAt(target) {
            const targetName = target && target.name ? target.name : null;
            if (targetName) __bgeQueue({ op: "lookAt", object: objName, target: targetName });
        },
        rayCast(to, fromOpt, dist, prop, face, xray, mask) {
            const toArr = Array.isArray(to) && to.length >= 3 ? to : null;
            if (toArr) __bgeQueueForObject("rayCast", objName, {
                to: toArr,
                from: Array.isArray(fromOpt) && fromOpt.length >= 3 ? fromOpt : undefined,
                dist: typeof dist === "number" ? dist : 0,
                prop: typeof prop === "string" ? prop : "",
                face: !!face,
                xray: !!xray,
                mask: typeof mask === "number" ? mask : 0xFFFF,
            });
        },
        rayCastTo(target, dist, prop) {
            const ctx = __BGE_CONTEXT__ || {};
            let t = target;
            if (t && t.name) t = t.name;
            if (t != null) __bgeQueueForObject("rayCastTo", objName, {
                target: typeof t === "string" ? t : (Array.isArray(t) && t.length >= 3 ? t : undefined),
                dist: typeof dist === "number" ? dist : 0,
                prop: typeof prop === "string" ? prop : "",
            });
        },
        get lastRayCastResult() {
            const ctx = __BGE_CONTEXT__ || {};
            const results = ctx.rayCastResults || {};
            const r = results[objName];
            if (!r) return { object: null, point: null, normal: null };
            return {
                object: r.object ? __bgeMakeGameObject(r.object) : null,
                point: Array.isArray(r.point) ? r.point.slice() : null,
                normal: Array.isArray(r.normal) ? r.normal.slice() : null,
            };
        },
        setViewport(left, bottom, right, top) {
            __bgeQueueForObject("setViewport", objName, {
                left: parseInt(left, 10),
                bottom: parseInt(bottom, 10),
                right: parseInt(right, 10),
                top: parseInt(top, 10),
            });
        },
    };
}

function __bgeMakeScene(sceneNameOrData) {
    const ctx = __BGE_CONTEXT__ || {};
    let sceneName = "";
    let objectNames = [];
    if (typeof sceneNameOrData === "string") {
        sceneName = sceneNameOrData;
        const scenes = ctx.scenes || [];
        for (let i = 0; i < scenes.length; i++) {
            if (scenes[i].name === sceneName) {
                objectNames = Array.isArray(scenes[i].objects) ? scenes[i].objects.slice() : [];
                break;
            }
        }
    } else if (sceneNameOrData && sceneNameOrData.name) {
        sceneName = sceneNameOrData.name;
        objectNames = Array.isArray(sceneNameOrData.objects) ? sceneNameOrData.objects.slice() : [];
    } else {
        sceneName = ctx.scene_name || "";
        const scenes = ctx.scenes || [];
        for (let i = 0; i < scenes.length; i++) {
            if (scenes[i].name === sceneName) {
                objectNames = Array.isArray(scenes[i].objects) ? scenes[i].objects.slice() : [];
                break;
            }
        }
    }
    const objList = objectNames.map(function(n) { return __bgeMakeGameObject(n); });
    return {
        name: sceneName,
        active: true,
        get objects() { return objList; },
        getObject(objName) {
            return __bgeMakeGameObject(objName);
        },
        get(objName) {
            return __bgeMakeGameObject(objName);
        },
        addObject(object) {
            const oname = object && object.name ? object.name : null;
            if (oname) __bgeQueue({ op: "sceneAddObject", scene: sceneName, object: oname });
        },
        removeObject(object) {
            const oname = object && object.name ? object.name : null;
            if (oname) __bgeQueue({ op: "sceneRemoveObject", scene: sceneName, object: oname });
        },
        get activeCamera() {
            const ctx = __BGE_CONTEXT__ || {};
            if (ctx.scene_name !== sceneName) return null;
            const name = ctx.active_camera_name;
            return name ? __bgeMakeGameObject(name) : null;
        },
        set activeCamera(cam) {
            const name = cam && cam.name ? cam.name : null;
            if (name) __bgeQueue({ op: "setActiveCamera", scene: sceneName, object: name });
        },
    };
}

const bge = {
    render: {
        getWindowWidth() {
            const ctx = __BGE_CONTEXT__ || {};
            return typeof ctx.windowWidth === "number" ? ctx.windowWidth : 0;
        },
        getWindowHeight() {
            const ctx = __BGE_CONTEXT__ || {};
            return typeof ctx.windowHeight === "number" ? ctx.windowHeight : 0;
        },
    },
    constraints: {
        setGravity(x, y, z) {
            const vec = Array.isArray(x) ? x : (arguments.length >= 3 ? [x, y, z] : [0, 0, -9.81]);
            if (vec.length >= 3) __bgeQueue({ op: "setGravity", vec: [Number(vec[0]), Number(vec[1]), Number(vec[2])] });
        },
        createVehicle(chassis) {
            const name = chassis && chassis.name ? chassis.name : null;
            if (name) __bgeQueue({ op: "createVehicle", scene: (__BGE_CONTEXT__ && __BGE_CONTEXT__.scene_name) || "", object: name });
        },
        vehicleApplyEngineForce(chassis, wheelIndex, force) {
            const name = chassis && chassis.name ? chassis.name : chassis;
            if (name != null) __bgeQueue({ op: "vehicleApplyEngineForce", object: name, wheelIndex: parseInt(wheelIndex, 10), force: Number(force) });
        },
        vehicleSetSteeringValue(chassis, wheelIndex, value) {
            const name = chassis && chassis.name ? chassis.name : chassis;
            if (name != null) __bgeQueue({ op: "vehicleSetSteeringValue", object: name, wheelIndex: parseInt(wheelIndex, 10), value: Number(value) });
        },
        vehicleAddWheel(chassis, wheel, connectionPoint, downDir, axleDir, suspensionRestLength, wheelRadius, hasSteering) {
            const cName = chassis && chassis.name ? chassis.name : chassis;
            const wName = wheel && wheel.name ? wheel.name : wheel;
            if (cName && wName != null) __bgeQueue({ op: "vehicleAddWheel", object: cName, wheel: wName, attachPos: Array.isArray(connectionPoint) ? connectionPoint : [0,0,0], downDir: Array.isArray(downDir) ? downDir : [0,0,-1], axleDir: Array.isArray(axleDir) ? axleDir : [0,1,0], suspensionRestLength: Number(suspensionRestLength) || 0.5, wheelRadius: Number(wheelRadius) || 0.4, hasSteering: !!hasSteering });
        },
        vehicleApplyBraking(chassis, wheelIndex, force) {
            const name = chassis && chassis.name ? chassis.name : chassis;
            if (name != null) __bgeQueue({ op: "vehicleApplyBraking", object: name, wheelIndex: parseInt(wheelIndex, 10), force: Number(force) });
        },
        characterJump(character) {
            const name = character && character.name ? character.name : character;
            if (name) __bgeQueue({ op: "characterJump", scene: (__BGE_CONTEXT__ && __BGE_CONTEXT__.scene_name) || "", object: name });
        },
        characterWalkDirection(character, vec) {
            const name = character && character.name ? character.name : character;
            const v = Array.isArray(vec) && vec.length >= 3 ? vec : [0, 0, 0];
            if (name) __bgeQueue({ op: "characterWalkDirection", scene: (__BGE_CONTEXT__ && __BGE_CONTEXT__.scene_name) || "", object: name, vec: [Number(v[0]), Number(v[1]), Number(v[2])] });
        },
        characterSetVelocity(character, vec, time, local) {
            const name = character && character.name ? character.name : character;
            const v = Array.isArray(vec) && vec.length >= 3 ? vec : [0, 0, 0];
            if (name) __bgeQueue({ op: "characterSetVelocity", scene: (__BGE_CONTEXT__ && __BGE_CONTEXT__.scene_name) || "", object: name, value: [Number(v[0]), Number(v[1]), Number(v[2])], time: Number(time) || 0.2, local: !!local });
        },
    },
    logic: {
        getCurrentScene() {
            return __bgeMakeScene();
        },
        getSceneList() {
            const scenes = (__BGE_CONTEXT__ && __BGE_CONTEXT__.scenes) || [];
            return scenes.map(function(s) { return __bgeMakeScene(s); });
        },
        getScene(name) {
            if (!name) return __bgeMakeScene();
            return __bgeMakeScene(name);
        },
        getCurrentController() {
            const ctx = __BGE_CONTEXT__ || {};
            const sensors = ctx.sensors || {};
            const actuatorNames = Array.isArray(ctx.actuators) ? ctx.actuators : [];
            const actuators = {};
            actuatorNames.forEach(function(n) { actuators[n] = { name: n }; });
            return {
                name: ctx.controller_name || "",
                type: "PYTHON",
                active: true,
                owner: __bgeMakeGameObject(),
                get sensors() { return sensors; },
                get actuators() { return actuators; },
                activate(actuator) {
                    const name = (typeof actuator === "string") ? actuator : (actuator && actuator.name);
                    if (name) __bgeQueue({ op: "activate", scene: ctx.scene_name || "", object: ctx.object_name || "", actuator: name });
                },
                deactivate(actuator) {
                    const name = (typeof actuator === "string") ? actuator : (actuator && actuator.name);
                    if (name) __bgeQueue({ op: "deactivate", scene: ctx.scene_name || "", object: ctx.object_name || "", actuator: name });
                },
            };
        },
        getCurrentObject() {
            return __bgeMakeGameObject();
        },
        // As funções de input ainda não estão conectadas ao engine real;
        // expomos stubs baseados em contexto para expansão futura.
        getKeyboardInput() {
            const kb = (__BGE_CONTEXT__ && __BGE_CONTEXT__.keyboard) || {};
            return {
                isPressed(key) {
                    return Array.isArray(kb.pressed) ? kb.pressed.includes(key) : false;
                },
                isJustPressed(key) {
                    return Array.isArray(kb.justPressed) ? kb.justPressed.includes(key) : false;
                },
                isJustReleased(key) {
                    return Array.isArray(kb.justReleased) ? kb.justReleased.includes(key) : false;
                },
            };
        },
        getMouseInput() {
            const m = (__BGE_CONTEXT__ && __BGE_CONTEXT__.mouse) || {};
            return {
                getPosition() {
                    return Array.isArray(m.position) ? m.position.slice() : [0, 0];
                },
                isPressed(button) {
                    return Array.isArray(m.pressed) ? m.pressed.includes(button) : false;
                },
                isJustPressed(button) {
                    return Array.isArray(m.justPressed) ? m.justPressed.includes(button) : false;
                },
                isJustReleased(button) {
                    return Array.isArray(m.justReleased) ? m.justReleased.includes(button) : false;
                },
                getWheelDelta() {
                    return typeof m.wheelDelta === "number" ? m.wheelDelta : 0;
                },
            };
        },
        getJoystickInput() {
            const j = (__BGE_CONTEXT__ && __BGE_CONTEXT__.joystick) || {};
            return {
                getJoystickCount() {
                    return typeof j.count === "number" ? j.count : 0;
                },
                isPressed(joystick, button) {
                    const pressed = j.buttonsPressed || {};
                    const list = pressed[String(joystick)] || [];
                    return Array.isArray(list) ? list.includes(button) : false;
                },
                getAxis(joystick, axis) {
                    const axes = j.axes || {};
                    const list = axes[String(joystick)] || [];
                    if (!Array.isArray(list)) return 0;
                    return typeof list[axis] === "number" ? list[axis] : 0;
                },
            };
        },
        getGameEngine() {
            const e = (__BGE_CONTEXT__ && __BGE_CONTEXT__.engine) || {};
            return {
                getFrameRate() {
                    return typeof e.frame_rate === "number" ? e.frame_rate : 0;
                },
                getCurrentFrame() {
                    return typeof e.current_frame === "number" ? e.current_frame : 0;
                },
                getTimeSinceStart() {
                    return typeof e.time_since_start === "number" ? e.time_since_start : 0;
                },
                endGame() {
                    __bgeQueue({ op: "endGame" });
                },
                restartGame() {
                    __bgeQueue({ op: "restartGame" });
                },
            };
        },
    },
    // Blender/UPBGE use GHOST key codes (sensor.inputs); A=23 confirmed, others guessed
    events: {
        AKEY: 23,
        DKEY: 26,
        WKEY: 45,
        SKEY: 41,
        UPARROWKEY: 82,
        DOWNARROWKEY: 84,
        LEFTARROWKEY: 80,
        RIGHTARROWKEY: 79,
        SPACEKEY: 32,
        ACTIVE: 1,
        JUST_ACTIVATED: 2,
        JUST_RELEASED: 3,
    },
    types: {
        Vector3(x, y, z) {
            return {
                x: x,
                y: y,
                z: z,
                add(other) {
                    return bge.types.Vector3(x + other.x, y + other.y, z + other.z);
                },
                subtract(other) {
                    return bge.types.Vector3(x - other.x, y - other.y, z - other.z);
                },
                multiply(scalar) {
                    return bge.types.Vector3(x * scalar, y * scalar, z * scalar);
                },
                length() {
                    return Math.sqrt(x * x + y * y + z * z);
                },
                normalize() {
                    const len = this.length();
                    if (len === 0) return bge.types.Vector3(0, 0, 0);
                    return bge.types.Vector3(x / len, y / len, z / len);
                },
            };
        },
    },
};
global.bge = bge;
