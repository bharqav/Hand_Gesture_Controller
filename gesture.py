import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
from pynput.mouse import Button, Controller

class HandController:
    def __init__(self):
        self.mouse = Controller()
        self.screen_w, self.screen_h = pyautogui.size()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            model_complexity=0,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8,
            max_num_hands=2
        )
        self.draw_utils = mp.solutions.drawing_utils
        
        self.is_dragging = False
        self.ploc_x, self.ploc_y = 0, 0
        self.cloc_x, self.cloc_y = 0, 0
        self.zoom_base_dist = 0
        self.is_zooming = False
        self.swipe_cooldown = 0
        self.prev_x_swipe = 0
        self.screenshot_cooldown = 0
        
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

    def calculate_distance(self, p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    
    def calculate_angle(self, pt1, pt2, pt3):
        radians = np.arctan2(pt3[1] - pt2[1], pt3[0] - pt2[0]) - \
                  np.arctan2(pt1[1] - pt2[1], pt1[0] - pt2[0])
        angle = np.abs(np.degrees(radians))
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def get_fingers_up(self, landmarks):
        fingers = []
        

        thumb_angle = self.calculate_angle(landmarks[2], landmarks[3], landmarks[4])
        if thumb_angle > 150: 
            fingers.append(1) 
        else:
            fingers.append(0) 

        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        for tip, pip in zip(tips, pips):
            if landmarks[tip][1] < landmarks[pip][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def move_cursor_adaptive(self, x, y):
        dist = math.hypot(x - self.ploc_x, y - self.ploc_y)
        
        if dist < 0.003:
            return

        min_dist = 0.01
        max_dist = 0.2
        min_alpha = 0.05
        max_alpha = 0.6
        
        norm_dist = np.clip((dist - min_dist) / (max_dist - min_dist), 0, 1)
        alpha = min_alpha + norm_dist * (max_alpha - min_alpha)
        
        self.cloc_x = self.ploc_x + (x - self.ploc_x) * alpha
        self.cloc_y = self.ploc_y + (y - self.ploc_y) * alpha
        
        screen_x = np.interp(self.cloc_x, (0, 1), (0, self.screen_w))
        screen_y = np.interp(self.cloc_y, (0, 1), (0, self.screen_h))
        
        self.mouse.position = (screen_x, screen_y)
        self.ploc_x, self.ploc_y = self.cloc_x, self.cloc_y

    def handle_zoom(self, hand1_lms, hand2_lms, frame):
        p1 = hand1_lms[8] 
        p2 = hand2_lms[8]
        dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
        
        if not self.is_zooming:
            self.zoom_base_dist = dist
            self.is_zooming = True
        else:
            diff = dist - self.zoom_base_dist
            if abs(diff) > 0.05:
                pyautogui.keyDown('ctrl')
                if diff > 0:
                    pyautogui.scroll(100)
                    cv2.putText(frame, "Zoom In", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    pyautogui.scroll(-100)
                    cv2.putText(frame, "Zoom Out", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                pyautogui.keyUp('ctrl')
                self.zoom_base_dist = dist

    def process_frame(self, frame):
        frame_h, frame_w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks) == 2:
                h1 = [(lm.x, lm.y) for lm in results.multi_hand_landmarks[0].landmark]
                h2 = [(lm.x, lm.y) for lm in results.multi_hand_landmarks[1].landmark]
                self.handle_zoom(h1, h2, frame)
                return

            hand_landmarks = results.multi_hand_landmarks[0]
            self.draw_utils.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            lms = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
            pixel_lms = [(int(lm.x * frame_w), int(lm.y * frame_h)) for lm in hand_landmarks.landmark]
            
            fingers = self.get_fingers_up(lms) 
            
            index_x, index_y = lms[8]
            thumb_x, thumb_y = lms[4]
            
            pinch_dist = math.hypot(index_x - thumb_x, index_y - thumb_y)
            
            if fingers == [0, 0, 0, 0, 0]:
                if self.screenshot_cooldown == 0:
                    im = pyautogui.screenshot()
                    ts = int(time.time())
                    im.save(f'screenshot_{ts}.png')
                    cv2.putText(frame, "Screenshot Saved!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    self.screenshot_cooldown = 30
                else:
                    self.screenshot_cooldown -= 1

            elif fingers == [1, 1, 0, 0, 0]:
                if not self.is_dragging:
                    self.mouse.press(Button.right)
                    self.mouse.release(Button.right)
                    cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    time.sleep(0.3)

            elif fingers == [1, 0, 1, 0, 0]:
                self.mouse.press(Button.left)
                self.mouse.release(Button.left)
                cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                time.sleep(0.3)

            elif fingers == [1, 0, 0, 0, 1]:
                pyautogui.scroll(30) 
                cv2.putText(frame, "Scroll Up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            elif fingers == [0, 1, 0, 0, 1]:
                pyautogui.scroll(-30) 
                cv2.putText(frame, "Scroll Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            if pinch_dist < 0.04:
                if not self.is_dragging:
                    pyautogui.mouseDown()
                    self.is_dragging = True
                self.move_cursor_adaptive(index_x, index_y)
                cv2.putText(frame, "Dragging", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            elif self.is_dragging:
                pyautogui.mouseUp()
                self.is_dragging = False

            if fingers[1] == 1 and fingers[0] == 0 and fingers[4] == 0 and not self.is_dragging:
                self.move_cursor_adaptive(index_x, index_y)

            if fingers == [1, 1, 1, 1, 1]:
                curr_x = pixel_lms[0][0]
                if self.swipe_cooldown == 0:
                    if self.prev_x_swipe != 0:
                        diff_x = curr_x - self.prev_x_swipe
                        if diff_x > 50: 
                            pyautogui.hotkey('alt', 'tab')
                            self.swipe_cooldown = 20
                            cv2.putText(frame, "Swipe Right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        elif diff_x < -50:
                            pyautogui.hotkey('alt', 'shift', 'tab') 
                            self.swipe_cooldown = 20
                            cv2.putText(frame, "Swipe Left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    self.prev_x_swipe = curr_x
                else:
                    self.swipe_cooldown -= 1
            else:
                self.prev_x_swipe = 0

            if self.screenshot_cooldown > 0:
                self.screenshot_cooldown -= 1

    def run(self):
        cap = cv2.VideoCapture(0)
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)
                self.process_frame(frame)
                cv2.imshow('Gesture Controller', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    app = HandController()
    app.run()