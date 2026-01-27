// SPDX-FileCopyrightText: 2024 UPBGE Authors
//
// SPDX-License-Identifier: GPL-2.0-or-later

/**
 * UPBGE Game Engine TypeScript Definitions
 * 
 * This file provides type definitions for the UPBGE JavaScript/TypeScript API.
 * Based on the UPBGE JavaScript API documentation.
 */

declare namespace bge {
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
         * Add object to scene
         */
        addObject(object: GameObject): void;
        
        /**
         * Remove object from scene
         */
        removeObject(object: GameObject): void;
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
    }
    
    /**
     * Controller - represents a logic controller
     */
    interface Controller {
        name: string;
        type: string;
        active: boolean;
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
