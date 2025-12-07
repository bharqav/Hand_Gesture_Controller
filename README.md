
# Hand Gesture Controller

<p align="center">
  <img src="https://dummyimage.com/900x200/000/fff&text=Hand+Gesture+Controller" alt="Project Banner"/>
</p>

A real time gesture based desktop control system that allows complete hands free interaction through a standard webcam. This system replaces physical mouse usage by translating hand gestures into precise cursor actions, enabling a new style of human computer interaction.

---

## Contents

1. Overview
2. Features
3. Architecture Diagram
4. Technical Breakdown
5. Requirements
6. Running the Project
7. Future Improvements

---

## Overview

The Hand Gesture Controller uses the MediaPipe hand landmark model to detect twenty one keypoints on the hand in real time. Every frame is processed to determine finger states, joint angles, and relative distances.
This information is mapped to system actions using PyAutoGUI and Pynput, enabling a fully touch free workflow.


The system is optimized for stability, low latency, and smooth gesture transitions under varied lighting and hand orientation conditions.

---

## Features Table

| Feature Name       | Description                                                                                   |
| ------------------ | --------------------------------------------------------------------------------------------- |
| Cursor Control     | Smooth, adaptive cursor movement based on index fingertip tracking with dynamic interpolation |
| Click Actions      | Finger configuration recognition for left click and right click events                        |
| Drag Mode          | Pinch gesture initiates drag state and holds until gesture ends                               |
| Scrolling          | Finger combinations mapped to vertical scrolling for natural page control                     |
| Two Hand Zoom      | Distance between hands used for continuous zoom in and zoom out                               |
| Window Navigation  | Full hand swipe mapped to task switching with cooldown logic                                  |
| Screenshot Capture | Closed hand gesture triggers instant screenshot saving with timestamp                         |

---

## Architecture Diagram

```
                       Webcam Input
                              |
                              v
                  OpenCV Frame Processing
                              |
                              v
                MediaPipe Hand Landmark Model
                              |
                              v
                 Landmark Extraction and Analysis
                (angles, finger states, distances)
                              |
                              v
         Gesture Classification and State Management
                              |
                              v
                Action Mapping Through PyAutoGUI
                           and Pynput
                              |
                              v
                 Real Time Desktop Interaction
```

---

## Technical Breakdown

Cursor module
Converts normalized landmark points into screen coordinates and applies interpolation that adapts to hand velocity for smooth pointer motion.

Gesture classifier
Calculates joint angles and inter point distances to determine finger states and identify gestures with high reliability.

State engine
Maintains states for actions that require continuity such as drag mode, zoom mode, swipe cooldown, and screenshot gating.

Rendering module
Displays landmarks on the frame through OpenCV for easier debugging and demonstration.

Action layer
Maps recognized gestures to operating system events using PyAutoGUI and Pynput, enabling pointer control, clicking, scrolling, zooming, and task switching.

---

## Requirements

Python version three point eight or newer
OpenCV
MediaPipe
PyAutoGUI
Pynput
NumPy

---

## Running the Project

```
python gesture.py
```

A webcam window will open and gesture recognition will begin automatically.

---

## Future Improvements

Calibration tools for personalized gesture thresholds
Support for multiple monitor environments
Expanded gesture vocabulary for additional system controls
Improved handling of left hand and mirrored gestures
Optional graphical configuration interface

