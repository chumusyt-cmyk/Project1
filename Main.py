import os
import sys
import yt_dlp
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import *



class DownloadThread(QThread):
    ProgressChanged = pyqtSignal(int)
    Started = pyqtSignal()
    Finished = pyqtSignal()

    def __init__(self, link, savePath):
        super().__init__()
        self.link = link
        self.savePath = savePath

    def checkLink(self):
        linkStroke = self.link.lower()

        if "youtube.com" in linkStroke or "youtu.be" in linkStroke:
            return "youtube"
        
        elif "tiktok.com" in linkStroke:
            return "tiktok"
        
        elif "vimeo.com" in linkStroke:
            return "vimeo"
        
        elif "instagram.com" in linkStroke:
            return "instagram"
        
        elif "soundcloud.com" in linkStroke:
            return "soundcloud"
        
        elif "x.com" in linkStroke:
            return "x"
        
        elif "facebook.com" in linkStroke:
            return "facebook"
        
        elif "reddit.com" in linkStroke:
            return "reddit"
        
        elif "vk.com" in linkStroke:
            return "vk"
        
        elif "bandcamp.com" in linkStroke:
            return "bandcamp"
        
        elif "mixcloud.com" in linkStroke:
            return "mixcloud"
        
        elif "BBC.com" in linkStroke:
            return "bbc"

    def run(self):
        platform = self.checkLink()
        custom_name = getattr(self, 'custom_name', '').strip()

        if custom_name:
            filename_template = f'{self.savePath}/{custom_name}.%(ext)s'
            filename_template = self.get_unique_filename(self.savePath, filename_template, 'mp4')
        else:
            if platform == "youtube":
                filename_template = f'{self.savePath}/%(title)s.%(ext)s'

            elif platform in ["tiktok", "vimeo", "instagram", "x", "facebook", "reddit", "vk", "bbc"]:
                filename_template = f'{self.savePath}/%(creator)s - %(id)s.%(ext)s'

            elif platform in ["soundcloud", "bandcamp", "mixcloud"]:
                filename_template = f'{self.savePath}/%(title)s.%(ext)s'

            else:
                return

        if platform == "youtube":
            ydl_opts = {
                'outtmpl': filename_template,
                'format': 'bestvideo+bestaudio',
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'progress_hooks': [self.progress],
            }
        
        elif platform in ["tiktok", "vimeo", "instagram", "x", "facebook", "reddit", "vk"]:
            ydl_opts = {
                'outtmpl': filename_template,
                'format': 'best',
                'progress_hooks': [self.progress],
            }

        elif platform in ["soundcloud", "bandcamp", "mixcloud"]:
            ydl_opts = {
                'outtmpl': filename_template,
                'format': 'bestaudio/best',
                'merge_output_format': 'mp3',
                'progress_hooks': [self.progress],
            }

        elif platform == "bbc":
            ydl_opts = {
                'outtmpl': filename_template,
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'progress_hooks': [self.progress],
                'geo_bypass': True,
                'geo_bypass_country': 'GB', 
            }

        else:
            return

        self.Started.emit()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.link])

    def progress(self, d):
        if d.get("status") == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            percent = int(downloaded / total * 100)
            self.ProgressChanged.emit(percent)

        elif d.get("status") == "finished":
            self.ProgressChanged.emit(100)
            self.Finished.emit()

    def get_unique_filename(self, base_path, name_template, ext):
        full_path = name_template % {'ext': ext} if '%' in name_template else name_template
        base, extension = os.path.splitext(full_path)
        counter = 1

        while os.path.exists(full_path):
            full_path = f"{base} ({counter}){extension}"
            counter += 1

        return full_path




class CreateApp(QWidget):

    def __init__(self):
        super().__init__()

        self.savePath = ""
        self.thread = None

        self.setWindowTitle("Project")
        self.resize(500, 650)
        self.MakeWindowCenter()

        #Widgets----
        self.modeButton = QComboBox()
        self.modeButton.addItems(["Video Downloader"])
        self.modeButton.setFont(QFont("Georgia", 10))
        self.modeButton.setFixedHeight(26)

        self.themeButton = QComboBox()
        self.themeButton.addItems(["Light", "Dark"])
        self.themeButton.currentIndexChanged.connect(self.changeTheme)
        self.themeButton.setFont(QFont("Georgia", 10))
        self.themeButton.setFixedHeight(26)

        self.linkInput = QLineEdit()
        self.linkInput.setPlaceholderText("https://www.youtube.com/watch?v=example-example=example=0")
        self.linkInput.setFont(QFont("Georgia", 10))
        self.linkInput.setFixedHeight(27)

        self.acceptButton = QPushButton("Download video")
        self.acceptButton.clicked.connect(self.download)
        self.acceptButton.setFont(QFont("Georgia", 10))
        self.acceptButton.setFixedSize(140, 40)

        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(lambda: (self.linkInput.setText(""), self.nameInput.setText("")))
        self.clearButton.setFont(QFont("Georgia", 10))
        self.clearButton.setFixedSize(140, 40)

        self.folderButton = QPushButton("Select folder")
        self.folderButton.clicked.connect(self.selectFolder)
        self.folderButton.setFont(QFont("Georgia", 10))
        self.folderButton.setFixedSize(140, 40)

        self.statusLabel = QLabel("No folder selected.")
        self.statusLabel.setFont(QFont("Georgia", 10, QFont.Bold))
        self.statusLabel.setAlignment(Qt.AlignCenter)

        self.saveOption = QCheckBox("Save folder for next sessions")
        self.saveOption.setFont(QFont("Georgia", 10))

        self.loadingBar = QProgressBar()
        self.loadingBar.setAlignment(Qt.AlignCenter)
        self.loadingBar.setValue(0)
        self.loadingBar.hide()

        self.supportButton = QPushButton("Suported platforms")
        self.supportButton.clicked.connect(lambda: QMessageBox.information(self, "Information", "WE SUPPORT: Youtube, Tiktok, Twitter, BBC, Vimeo, Facebook, Reddit, Instagram, Soundcloud, Mixedcloud, Bandcamp, Vk"))
        self.supportButton.setFont(QFont("Georgia", 10))
        self.supportButton.setFixedSize(250, 33)

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("exapmle2381Q (not important)")
        self.nameInput.setFont(QFont("Georgia", 10))
        self.nameInput.setFixedHeight(25)

        self.saveNameOption = QCheckBox("Save file name for next session")
        self.saveNameOption.setFont(QFont("Georgia", 10))

        self.saveLinkOption = QCheckBox("Save link for next session")
        self.saveLinkOption.setFont(QFont("Georgia", 10))

        self.BannerLabel = QLabel(self)
        self.BannerLabel.setGeometry(QRect(0, 0, 600, 400))
        self.movie = QMovie("Banner.gif")
        self.BannerLabel.setMovie(self.movie)
        self.movie.start()

        #Layouts----
        mainLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        mainLayout.addWidget(self.modeButton)
        mainLayout.addWidget(self.themeButton)
        mainLayout.addWidget(self.statusLabel)

        mainLayout.addWidget(self.loadingBar)
        mainLayout.addWidget(self.linkInput)
        mainLayout.addWidget(self.nameInput)

        buttonLayout.addWidget(self.acceptButton)
        buttonLayout.addWidget(self.clearButton)
        buttonLayout.addWidget(self.folderButton)

        mainLayout.addWidget(self.saveOption)
        mainLayout.addWidget(self.saveNameOption)
        mainLayout.addWidget(self.saveLinkOption)

        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(self.supportButton, alignment=Qt.AlignCenter)
        mainLayout.addWidget(self.BannerLabel)

        mainLayout.setSpacing(19)
        mainLayout.setAlignment(Qt.AlignTop)

        self.setLayout(mainLayout)
        self.changeTheme(0)

    def MakeWindowCenter(self):
        qr = self.frameGeometry()
        centerPosition = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(centerPosition)
        self.move(qr.topLeft())

    def changeTheme(self, index):
        if index == 0:
            app.setPalette(QApplication.style().standardPalette())
            app.setStyleSheet("")
        else:
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, Qt.white)
            app.setPalette(dark_palette)

            app.setStyleSheet("""
                QLabel, QPushButton, QLineEdit, QComboBox, QMessageBox {
                    color: white;
                    background-color: #353535;
                }
                QLineEdit, QComboBox {
                    background-color: #353535;
                    selection-background-color: #2980b9;
                    selection-color: white;
                    border: 1px solid #555555;
                    border-radius: 4px; 
                }
                QPushButton {
                    background-color: #444444;
                    border: 1px solid #555555;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QMessageBox QLabel {
                    color: white;
                }
                QMessageBox {
                    background-color: #353535;
                }
            """)
            
    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select the folder where we will upload the video.")

        if folder:
            self.savePath = folder
            self.statusLabel.setText(f"Folder: {folder}")
        else:
            QMessageBox.warning(self, "Error!?", "We have trouble with folder path.")
            QSound.play("Error.wav")

    def download(self):
        if not self.savePath:
            QMessageBox.warning(self, "Error!?", "You didn't select a folder.")
            QSound.play("Error.wav")
            return

        linkText = self.linkInput.text().strip()

        supported_domains = [
            "tiktok.com", "vimeo.com", "instagram.com", 
            "x.com", "facebook.com", "reddit.com", 
            "youtube.com", "youtu.be", "soundcloud.com",
            "vk.com", "bandcamp.com", "mixcloud.com",
            "BBC.com"
        ]
        
        if not any(domain in linkText for domain in supported_domains):
            QMessageBox.warning(self, "Error!?", "We don't support this platform.")
            QSound.play("Error.wav")
            return
        
        self.statusLabel.setText("Downloading...")
        self.loadingBar.setValue(0)

        self.thread = DownloadThread(linkText, self.savePath)
        self.thread.custom_name = self.nameInput.text().strip()

        self.thread.Started.connect(lambda: self.loadingBar.show())
        self.thread.Finished.connect(self.finishProgress)
        self.thread.ProgressChanged.connect(self.loadingBar.setValue)

        self.thread.finished.connect(self.finish)
        self.thread.start()
        
    def finish(self):
        self.statusLabel.setText("Download complete!")
        QSound.play("Finish.wav")
        
        if not self.saveOption.isChecked():
            self.savePath = ""
            QTimer.singleShot(2000, lambda: self.statusLabel.setText("No folder selected."))
        else:
            QTimer.singleShot(2000, lambda: self.statusLabel.setText(self.savePath))

        if not self.saveNameOption.isChecked():
            self.nameInput.setText("")

        if not self.saveLinkOption.isChecked():
            self.linkInput.setText("")

    def finishProgress(self):
        QTimer.singleShot(2000, lambda: (self.loadingBar.hide(), self.loadingBar.setValue(0)))

    def toggleVideo(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CreateApp()
    window.show()
    sys.exit(app.exec_())
