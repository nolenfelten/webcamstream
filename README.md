# Webcam Widget with Transparency and Circular Mask

This project demonstrates a PyQt5 application that integrates live webcam feed with a customizable circular mask and adjustable transparency using a web interface. The application allows you to drag the webcam feed around the screen, adjust its opacity via a slider, and opens a web window for further control.

## Features

1. **Webcam Feed**: Displays a live webcam feed using OpenCV, updated at approximately 30 FPS.
2. **Circular Mask**: The webcam feed is cropped to a circular shape using QPainter for a visually appealing display.
3. **Drag and Move**: The webcam window can be dragged around the screen by clicking and holding the left mouse button.
4. **Transparency Control**: A slider in the web window allows real-time adjustment of the webcam window's transparency.
5. **Web Interface**: The application provides a web interface with a transparency slider built with HTML and JavaScript. The web page interacts with Python via a QWebChannel.
6. **White Balance Adjustment**: Applies automatic white balance adjustments to the webcam feed using OpenCV to improve color accuracy and reduce yellow hues.
7. **Multi-window Interaction**: Opens a secondary window containing the web interface upon pressing `Ctrl + Shift` while dragging the main window.

## File Structure

- `main.py`: The main Python script containing the PyQt5 application, webcam widget, and web window functionality.
- `README.md`: This file, containing a brief overview of the application and its components.

## Prerequisites

- Python 3.7+
- PyQt5
- OpenCV
- PyQtWebEngine

## Installation

1. Clone the repository or download the source files.
2. Install the necessary Python packages:
   ```bash
   pip install pyqt5 opencv-python pyqtwebengine
   ```
3. Run the main script:
   ```bash
   python main.py
   ```

## How to Use

1. **Running the Application**: Launch the application by running the `main.py` file. The main window will show a live circular webcam feed.
2. **Drag to Move**: Click and drag the main window to move it across the screen.
3. **Transparency Adjustment**: Press `Ctrl + Shift` while dragging the window to open a web-based control window. Use the transparency slider to adjust the webcam window's opacity from 0% to 100%.
4. **Exit**: Close the application by closing the webcam window.

## Code Overview

- **WebcamWidget**: Handles the webcam feed display, drag-and-drop movement, and applying the circular mask using `QPainter`.
  - `update_frame()`: Captures frames from the webcam and converts them to display in the PyQt widget.
  - `adjust_white_balance()`: Reduces yellow hues in the frame by converting it to LAB color space and applying contrast-limited adaptive histogram equalization (CLAHE).
  - `apply_circle_mask()`: Applies a circular mask to the webcam feed for a unique display.
  
- **WebWindow**: Displays the web interface with the transparency slider, built using HTML, JavaScript, and QWebChannel for communication with Python.
  - Uses PyQt's `QWebEngineView` to render HTML content and handle JavaScript events.
  
- **Bridge**: Acts as the communication link between the web window's JavaScript and the Python backend, allowing for real-time transparency adjustments.

## Notes

- The application currently uses the default webcam (index 0). You can change the webcam index by modifying the line `self.capture = cv2.VideoCapture(0)` to use a different device.
- The window is set to be frameless and stay on top of other windows. You can adjust these settings by modifying the `setWindowFlags` in the `WebcamWidget` class.

## Future Enhancements

- Allow switching between multiple webcam sources.
- Add more controls in the web interface (e.g., brightness, contrast).
- Implement saving and loading of user settings for window position, opacity, etc.

## License

This project is open-source and available under the MIT License.
```

This `README.md` provides an overview of the application, installation steps, code breakdown, and instructions for use.
