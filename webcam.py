import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QMainWindow, QSlider, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QPainter, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl, QObject,pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel


class WebWindow(QMainWindow):
    def __init__(self, webcam_widget):  # Pass webcam_widget to WebWindow
        super().__init__()
        self.setWindowTitle("Nolen James Felten")
        self.webcam_widget = webcam_widget  # Store the webcam_widget reference

        self.browser = QWebEngineView()
        html_content = """
        !DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nolen James Felten</title>
            <style>
                body {
                    font-family: sans-serif;
                }
                .slider-container {
                    margin-top: 20px;
                }
                .slider-label {
                    display: inline-block;
                    width: 50px;
                    text-align: center;
                }
                .percent-input {
                    width: 40px;
                }
            </style>
        </head>
        <body>
            <div class="slider-container">
                <label for="transparencySlider">Transparency:</label>
                <input type="range" id="transparencySlider" min="0" max="100" value="100">
                <span class="slider-label">0%</span>
                <span class="slider-label" style="margin-left: 130px;">50%</span>
                <span class="slider-label" style="margin-left: 130px;">100%</span>
                <input type="text" id="percentInput" class="percent-input" value="100">
                <span>%</span>
            </div>

            <script src="qrc:///qtwebchannel/qwebchannel.js"></script> 

            <script>
                const slider = document.getElementById('transparencySlider');
                const percentInput = document.getElementById('percentInput');
                
                slider.addEventListener('input', () => {
                    const opacity = slider.value / 100;
                    percentInput.value = slider.value;

                    // Send the opacity value to Python using QWebChannel
                    new QWebChannel(qt.webChannelTransport, function (channel) {
                        if (channel.objects.bridge) {
                            channel.objects.bridge.setOpacity(opacity);
                        }
                    });
                });
            </script>
        </body>
        </html>
        """

        self.browser.setHtml(html_content)

        # Set up QWebChannel for communication with JavaScript
        channel = QWebChannel(self.browser.page())
        self.browser.page().setWebChannel(channel)
        bridge = Bridge(self.webcam_widget)  # Pass webcam_widget to Bridge
        channel.registerObject('bridge', bridge)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        event.ignore()  # Prevent the default close behavior (which would close the app)
        self.hide()  # Hide the window instead of closing it


class Bridge(QObject):  # Inherit from QObject
    def __init__(self, webcam_widget):
        super().__init__()
        self.webcam_widget = webcam_widget

    @pyqtSlot(float)
    def setOpacity(self, opacity):
        # Update the opacity of the webcam widget based on the slider value
        self.webcam_widget.setWindowOpacity(opacity)


class WebcamWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint | Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Variables to manage dragging
        self.is_dragging = False
        self.offset = QPoint()

        # Set up the webcam capture
        self.capture = cv2.VideoCapture(0)
        
        # Timer to update the frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms interval for ~30fps

        # Set up layout and label for displaying the webcam
        self.label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.web_window = None  # Initialize web_window as None


    def update_frame(self):
        # Capture frame-by-frame
        ret, frame = self.capture.read()
        if ret:
            # Adjust the white balance and color correction to reduce yellow hue
            frame = self.adjust_white_balance(frame)
            
            # Convert the frame to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert the frame to QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Create a circular mask for the webcam feed
            q_img = self.apply_circle_mask(q_img)
            
            # Display the image on the QLabel
            self.label.setPixmap(QPixmap.fromImage(q_img))

    def adjust_white_balance(self, frame):
        # Convert the frame from BGR to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        # Split LAB channels
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L-channel (contrast-limited adaptive histogram equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        # Merge the channels back
        limg = cv2.merge((cl, a, b))

        # Convert back to BGR color space
        final_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        

        return final_frame

    def apply_circle_mask(self, q_img):
        # Create a circular mask using QPainter
        size = min(q_img.width(), q_img.height())  # Ensure square for the mask
        result_img = QImage(size, size, QImage.Format_ARGB32)
        result_img.fill(Qt.transparent)  # Start with transparent background

        # Copy the center part of the webcam image into the circular area
        painter = QPainter(result_img)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        # Center crop the webcam feed to fit inside the circle
        crop_x = (q_img.width() - size) // 2
        crop_y = (q_img.height() - size) // 2
        painter.drawImage(0, 0, q_img, crop_x, crop_y, size, size)

        painter.end()
        return result_img

    # Mouse press event: Start dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    # Mouse move event: Update window position
    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.offset)
            event.accept()

    # Mouse release event: Stop dragging
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if (event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier)):
                self.open_web_window() 
            self.is_dragging = False
            event.accept()

    def open_web_window(self):
        if self.web_window is None:
            self.web_window = WebWindow(self)  # Pass self (webcam_widget) to WebWindow
            self.web_window.setAttribute(Qt.WA_DeleteOnClose, False)
            self.web_window.setParent(None)

        self.web_window.show()


    def closeEvent(self, event):
        # Release the capture on close
        self.capture.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamWidget()
    window.resize(400, 400)  # Resize to make the circle larger
    window.show()
    sys.exit(app.exec_())
