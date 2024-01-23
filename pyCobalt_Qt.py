import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QFileDialog

class CobaltDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Cobalt Downloader')

        # Widgets
        self.url_input = QLineEdit(self)
        self.audio_only_checkbox = QCheckBox("Audio Only", self)
        self.format_combobox = QComboBox(self)
        self.format_combobox.addItems(["mp3", "ogg", "wav", "opus"])
        self.video_format_combobox = QComboBox(self)
        self.video_format_combobox.addItems(["h264", "av1", "vp9"])
        self.video_resolution_combobox = QComboBox(self)
        self.video_resolution_combobox.addItems(["144", "240", "360", "480", "720", "1080", "1440", "2160"])
        self.download_button = QPushButton('Download', self)
        self.status_label = QLabel('', self)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Enter Media URL:', self))
        layout.addWidget(self.url_input)
        layout.addWidget(QLabel('Download Options:', self))
        layout.addWidget(self.audio_only_checkbox)
        layout.addWidget(QLabel('Audio Format:', self))
        layout.addWidget(self.format_combobox)
        layout.addWidget(QLabel('Video Format:', self))
        layout.addWidget(self.video_format_combobox)
        layout.addWidget(QLabel('Video Resolution:', self))
        layout.addWidget(self.video_resolution_combobox)
        layout.addWidget(self.download_button)
        layout.addWidget(self.status_label)

        # Signals and slots
        self.download_button.clicked.connect(self.download_media)

    def download_media(self):
        media_url = self.url_input.text()

        if not media_url:
            self.status_label.setText('Please enter a valid URL.')
            return

        # Cobalt API endpoint
        api_url = "https://co.wuk.sh/api/json"

        # Request headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Request body parameters
        request_body = {
            "url": media_url,
            "aFormat": self.format_combobox.currentText(),
        }

        # Check if it's an audio-only download
        if self.audio_only_checkbox.isChecked():
            request_body["isAudioOnly"] = True
        else:
            request_body["isAudioOnly"] = False
            request_body["vCodec"] = self.video_format_combobox.currentText()
            request_body["vQuality"] = self.video_resolution_combobox.currentText()

        # Make the POST request
        response = requests.post(api_url, json=request_body, headers=headers)

        # Check the status code
        if response.status_code == 200:
            # Process the response
            response_data = response.json()

            # Check the status in the response
            if response_data["status"] == "success":
                # Open file dialog to choose destination
                options = QFileDialog.Options()
                options |= QFileDialog.DontUseNativeDialog
                file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;" + f"{self.format_combobox.currentText().upper()} Files (*.{self.format_combobox.currentText()})", options=options)

                if file_path:
                    # Download the media from the provided URL
                    media_url = response_data["url"]
                    self.download_file(media_url, file_path)
                    self.status_label.setText(f"Download successful. Saved to: {file_path}")
                else:
                    self.status_label.setText('Download canceled.')
            else:
                error_message = self.parse_json_error(response_data)
                self.status_label.setText(f"Error: {response_data['status']} - {error_message}")
        else:
            self.status_label.setText(f"Error: {response.status_code} - {response.text}")

    def parse_json_error(self, response_data):
        # Parse JSON errors into a readable manner
        error_message = response_data.get("text", "Unknown error")
        if "errorDetails" in response_data:
            error_details = response_data["errorDetails"]
            for detail in error_details:
                error_message += f"\n{detail['field']}: {detail['message']}"
        return error_message

    def download_file(self, url, destination):
        with requests.get(url, stream=True) as response:
            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)


def main():
    app = QApplication(sys.argv)
    downloader_app = CobaltDownloaderApp()
    downloader_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
