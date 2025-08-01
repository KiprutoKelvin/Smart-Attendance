import os
os.environ["QT_QPA_PLATFORM"] = "xcb"  # Fix for Qt plugin error (Wayland)
import sys

import check_camera
import capture_image
import train_image
import recognize


def title_bar():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\t***** Face Recognition Attendance System *****")


def checkCamera():
    check_camera.camer()
    input("Enter any key to return to main menu...")

def CaptureFaces():
    capture_image.takeImages()
    input("Enter any key to return to main menu...")

def Trainimages():
    train_image.TrainImages()
    input("Enter any key to return to main menu...")

def recognizeFaces():
    recognize.recognize_attendence()
    input("Enter any key to return to main menu...")

def mainMenu():
    while True:
        title_bar()
        print()
        print(10 * "*", "WELCOME MENU", 10 * "*")
        print("[1] Check Camera")
        print("[2] Capture Faces")
        print("[3] Train Images")
        print("[4] Recognize & Attendance")
        print("[5] Auto Mail")
        print("[6] Quit")

        try:
            choice = int(input("Enter Choice: "))
            if choice == 1:
                checkCamera()
            elif choice == 2:
                CaptureFaces()
            elif choice == 3:
                Trainimages()
            elif choice == 4:
                recognizeFaces()
            elif choice == 5:
                os.system("python3 automail.py")
                input("Enter any key to return to main menu...")
            elif choice == 6:
                print("Thank You")
                sys.exit()
            else:
                print("Invalid Choice. Enter 1-6")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 6.")

# main driver
mainMenu()
