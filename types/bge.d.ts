// SPDX-FileCopyrightText: 2024 UPBGE Authors
//
// SPDX-License-Identifier: GPL-2.0-or-later

/**
 * UPBGE Game Engine – type definitions for the JavaScript API.
 * For use in editors that support .d.ts (JSDoc / IntelliSense).
 */

declare namespace bge {
    /**
     * Render module - viewport / window size
     */
    namespace render {
        function getWindowWidth(): number;
        function getWindowHeight(): number;
    }
    
    /**
     * Constraints - physics vehicle, character, gravity
     */
    namespace constraints {
        function setGravity(x: number, y: number, z: number): void;
        function setGravity(vec: [number, number, number]): void;
        function createVehicle(chassis: GameObject): void;
        function vehicleApplyEngineForce(chassis: GameObject | string, wheelIndex: number, force: number): void;
        function vehicleSetSteeringValue(chassis: GameObject | string, wheelIndex: number, value: number): void;
        function vehicleAddWheel(chassis: GameObject | string, wheel: GameObject | string, connectionPoint: [number, number, number], downDir: [number, number, number], axleDir: [number, number, number], suspensionRestLength: number, wheelRadius: number, hasSteering: boolean): void;
        function vehicleApplyBraking(chassis: GameObject | string, wheelIndex: number, force: number): void;
        function characterJump(character: GameObject | string): void;
        function characterWalkDirection(character: GameObject | string, vec: [number, number, number]): void;
        function characterSetVelocity(character: GameObject | string, vec: [number, number, number], time: number, local?: boolean): void;
    }
    
    /**
     * Logic module - provides access to game logic, scenes, objects, etc.
     */
    namespace logic {
        /**
         * Get the current scene
         */
        function getCurrentScene(): Scene;
        
        /**
         * Get all scenes
         */
        function getSceneList(): Scene[];
        
        /**
         * Get scene by name
         */
        function getScene(name: string): Scene | null;
        
        /**
         * Get the current controller
         */
        function getCurrentController(): Controller | null;
        
        /**
         * Get the current object
         */
        function getCurrentObject(): GameObject | null;
        
        /**
         * Get keyboard input
         */
        function getKeyboardInput(): KeyboardInput;
        
        /**
         * Get mouse input
         */
        function getMouseInput(): MouseInput;
        
        /**
         * Get joystick input
         */
        function getJoystickInput(): JoystickInput;
        
        /**
         * Get the game engine
         */
        function getGameEngine(): GameEngine;
    }
    
    /**
     * Scene - represents a game scene
     */
    interface Scene {
        name: string;
        active: boolean;
        objects: GameObject[];
        
        /**
         * Get object by name
         */
        getObject(name: string): GameObject | null;
        
        /**
         * Get object by name (alias for getObject)
         */
        get(name: string): GameObject | null;
        
        /**
         * Add object to scene
         */
        addObject(object: GameObject): void;
        
        /**
         * Remove object from scene
         */
        removeObject(object: GameObject): void;
        
        /**
         * Active camera (get/set by GameObject)
         */
        activeCamera: GameObject | null;
    }
    
    /**
     * RayCast result (available on next frame via lastRayCastResult)
     */
    interface RayCastResult {
        object: GameObject | null;
        point: [number, number, number] | null;
        normal: [number, number, number] | null;
    }
    
    /**
     * GameObject - represents a game object
     */
    interface GameObject {
        name: string;
        position: [number, number, number];
        rotation: [number, number, number];
        scale: [number, number, number];
        
        /**
         * Get property value
         */
        getProperty(name: string): any;
        
        /**
         * Set property value
         */
        setProperty(name: string, value: any): void;
        
        /**
         * Get parent object
         */
        getParent(): GameObject | null;
        
        /**
         * Set parent object
         */
        setParent(parent: GameObject | null): void;
        
        /**
         * Get children objects
         */
        getChildren(): GameObject[];
        
        /**
         * Orient object to look at target (world position or GameObject)
         */
        lookAt(target: GameObject): void;
        
        /**
         * Set viewport for camera (left, bottom, right, top in pixels)
         */
        setViewport(left: number, bottom: number, right: number, top: number): void;
        
        /**
         * Ray cast to point [x,y,z]; result in lastRayCastResult next frame
         */
        rayCast(to: [number, number, number], from?: [number, number, number] | null, dist?: number, prop?: string, face?: boolean, xray?: boolean, mask?: number): void;
        
        /**
         * Ray cast toward target (GameObject or [x,y,z]); result in lastRayCastResult next frame
         */
        rayCastTo(target: GameObject | [number, number, number], dist?: number, prop?: string): void;
        
        /**
         * Last rayCast/rayCastTo result (from previous frame)
         */
        readonly lastRayCastResult: RayCastResult;
    }
    
    /**
     * Actuator reference (name only; use with activate/deactivate)
     */
    interface ActuatorRef {
        name: string;
    }
    
    /**
     * Sensor entry (positive, type, hitObjectList for collision)
     */
    interface SensorEntry {
        positive: boolean;
        type: number;
        hitObjectList?: Array<{ name: string }>;
    }
    
    /**
     * Controller - represents a logic controller
     */
    interface Controller {
        name: string;
        type: string;
        active: boolean;
        owner: GameObject;
        sensors: { [sensorName: string]: SensorEntry };
        actuators: { [actuatorName: string]: ActuatorRef };
        activate(actuator: ActuatorRef | string): void;
        deactivate(actuator: ActuatorRef | string): void;
    }
    
    /**
     * Keyboard input
     */
    interface KeyboardInput {
        /**
         * Check if key is pressed
         */
        isPressed(key: number): boolean;
        
        /**
         * Check if key was just pressed
         */
        isJustPressed(key: number): boolean;
        
        /**
         * Check if key was just released
         */
        isJustReleased(key: number): boolean;
    }
    
    /**
     * Mouse input
     */
    interface MouseInput {
        /**
         * Get mouse position
         */
        getPosition(): [number, number];
        
        /**
         * Check if mouse button is pressed
         */
        isPressed(button: number): boolean;
        
        /**
         * Check if mouse button was just pressed
         */
        isJustPressed(button: number): boolean;
        
        /**
         * Check if mouse button was just released
         */
        isJustReleased(button: number): boolean;
        
        /**
         * Get mouse wheel delta
         */
        getWheelDelta(): number;
    }
    
    /**
     * Joystick input
     */
    interface JoystickInput {
        /**
         * Get number of connected joysticks
         */
        getJoystickCount(): number;
        
        /**
         * Check if button is pressed
         */
        isPressed(joystick: number, button: number): boolean;
        
        /**
         * Get axis value
         */
        getAxis(joystick: number, axis: number): number;
    }
    
    /**
     * Game engine
     */
    interface GameEngine {
        /**
         * Get frame rate
         */
        getFrameRate(): number;
        
        /**
         * Get current frame
         */
        getCurrentFrame(): number;
        
        /**
         * Get time since start
         */
        getTimeSinceStart(): number;
        
        /**
         * End game
         */
        endGame(): void;
        
        /**
         * Restart game
         */
        restartGame(): void;
    }
    
    /**
     * Types module - provides type definitions and utilities
     */
    namespace types {
        /**
         * Vector3 - 3D vector
         */
        interface Vector3 {
            x: number;
            y: number;
            z: number;
            
            /**
             * Add another vector
             */
            add(other: Vector3): Vector3;
            
            /**
             * Subtract another vector
             */
            subtract(other: Vector3): Vector3;
            
            /**
             * Multiply by scalar
             */
            multiply(scalar: number): Vector3;
            
            /**
             * Get length
             */
            length(): number;
            
            /**
             * Normalize
             */
            normalize(): Vector3;
        }
        
        /**
         * Create Vector3
         */
        function Vector3(x: number, y: number, z: number): Vector3;
    }
}

// Export for use in modules
export { bge };
