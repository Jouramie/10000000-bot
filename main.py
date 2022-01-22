from time import sleep
from turtle import pu
from typing import List
import pyautogui
import cv2
import numpy as np
import keyword

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QVBoxLayout, QWidget

DISPLAY_RATIO = 1

def findWands():
    return [[int(w.left / DISPLAY_RATIO), int(w.top / DISPLAY_RATIO), int(w.width / DISPLAY_RATIO), int(w.height / DISPLAY_RATIO)]
     for w in pyautogui.locateAllOnScreen('wand.png') ] 

def testMouve():
    while True:
        print(pyautogui.position())
        pyautogui.moveRel(10, 10)


class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(2160)
        self.setFixedWidth(3840)

        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)


        self.toggle_btn = QPushButton("Exit", self)
        self.toggle_btn.setGeometry(200, 150, 100, 30)
        self.toggle_btn.clicked.connect(self.close)

        self.draw_btn = QPushButton("Draw rectangle", self)
        self.draw_btn.setGeometry(320, 150, 100, 30)
        self.draw_btn.clicked.connect(self.draw_rectangle)

        self.draw_btn = QPushButton("Remove rectangle", self)
        self.draw_btn.setGeometry(440, 150, 100, 30)
        self.draw_btn.clicked.connect(self.remove_rectangle)


        self.rectangles = findWands()

        self.start = 0
        

        """ self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter,
                QtCore.QSize(220, 32),
                QtWidgets.qApp.desktop().availableGeometry()
        ))"""

    def remove_rectangle(self):
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.rectangles.pop()
        self.update()

    def draw_rectangle(self):
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        rect = [np.random.randint(1920 - 150), np.random.randint(1080 - 100), np.random.randint(150), np.random.randint(100)]
        self.rectangles.append(rect)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.green, 1))
        painter.setBrush(QBrush(QColor(0, 255, 0, 80), Qt.BrushStyle.SolidPattern))
        for rect in self.rectangles:
            painter.drawRect(*rect)
        painter.end()
        print(self.rectangles)


if __name__ == '__main__':

    print(f"Failsafe points {pyautogui.FAILSAFE_POINTS}")

    print(list(pyautogui.locateAllOnScreen('wand.png')))
    
    app = QApplication(sys.argv)
    DISPLAY_RATIO = app.devicePixelRatio()
    print(f"ratio = {DISPLAY_RATIO}")
    main = Overlay()
    main.showMaximized()
    app.exec()




