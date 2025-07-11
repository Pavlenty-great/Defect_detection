import sys
import cv2
import os
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore
from GUI.ui_main_window import Ui_MainWindow
from loguru import logger

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setCentralWidget(self.ui.centralwidget)

        # Инициализация видеозахвата
        self.cap = cv2.VideoCapture(0)  # 0 - камера по умолчанию
        if not self.cap.isOpened():
            logger.error("Не удалось открыть камеру")
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось открыть камеру.  Проверьте подключение.")
            sys.exit()

        # Настройка таймера
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Обновление каждые 30 мс

        self.path_logs = Path(__file__).parent / "Logs"
        self.ui.log_path_edit.setText(str(self.path_logs))

        logger.add(sys.stderr, format="{time} {level} {message}\n", level="INFO")
        logger.add(os.path.join(self.path_logs, "app.log"), rotation="500 MB", level="DEBUG", encoding="utf8")

        self.setup_connections()

    def setup_connections(self):
        """Подключение сигналов (поступающих событий) к слотам (обработчикам событий)"""
        self.ui.sensivity_slider.valueChanged.connect(self.update_sensitivity_label)
        self.ui.save_button.clicked.connect(self.save_frame)
        self.ui.log_path_button.clicked.connect(self.choose_logs_path)

    def update_frame(self):
        """Обработка поступающих кадров и помещение их в QLabel (video_frame)"""
        ret, frame = self.cap.read()  # ret - булевская переменная (true, если кадр был успешно считан), frame - кадр видео в виде массива NumPy.
        if ret:
            # Преобразование кадра OpenCV в формат QImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape  # ch - количество цветовых компонентов (байт на пиксель)
            bytes_per_line = ch * w  # вычисление количества байт для хранения 1-й строки изображения
            q_image = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(q_image)  # QPixmap - класс, оптимизированный для отображения изображения на экране
            # Масштабирование
            pixmap = pixmap.scaled(self.ui.video_frame.width(), self.ui.video_frame.height(), QtCore.Qt.KeepAspectRatio)  # масштабируем изображение с сохранением пропорций (последний параметр)
            self.ui.video_frame.setPixmap(pixmap)

    def closeEvent(self, event):
        """Обработка закрытия окна приложения и освобождения ресурсов веб-камеры"""
        reply = QtWidgets.QMessageBox.question(
            self, 'Закрыть окно',
            'Вы уверены, что хотите закрыть окно?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.cap.release()
                logger.info("Ресурсы камеры успешно освобождены")
            except Exception as e:
                logger.exception(f"Ошибка при освобождении ресурсов камеры: {e}")
            event.accept()
        else:
            event.ignore()

    def save_frame(self):
        """Сохранение кадра при нажатии на элемент окна - save_button"""
        ret, frame = self.cap.read()
        if ret:
            save_folder = Path(__file__).parent / "Data" / "Defective image"

            timestamp = QtCore.QDateTime.currentDateTime().toString("yyyyMMdd_HHmmss") #  Формат: годМесяцДень_ЧасыМинутыСекунды
            filename = f"frame_{timestamp}.jpg"
            filepath = os.path.join(str(save_folder), filename)

            try:
                cv2.imwrite(filepath, frame)  # Сохраняем в BGR
                self.add_defective_board_info(filename, filepath)
                logger.info(f"Сохранен кадр бракованной платы: {filepath}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении кадра: {e}")
                logger.exception(f"Ошибка при сохранении кадра: {e}")  # логирование ошибок
        else:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", "Не удалось получить кадр.")
            logger.exception("Не удалось получить кадр для сохранения.")  # логирование ошибок

    def add_defective_board_info(self, filename, filepath):
        item = QtWidgets.QListWidgetItem(f"Имя: {filename}\nПуть: {filepath}")
        self.ui.defective_board_list.addItem(item)

    def choose_logs_path(self):
        """Выбор нового пути и замена старого."""
        new_path_logs = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для логов",
            str(self.path_logs)  # Начинаем с текущего пути (если он задан)
        )

        # Если пользователь выбрал путь (не нажал "Отмена")
        if new_path_logs:
            self.path_logs = new_path_logs
            self.ui.log_path_edit.setText(str(self.path_logs))

            self.configure_loguru(self.path_logs)

            logger.info(f"Путь к логам изменен на: {self.path_logs}")

    def configure_loguru(self, path_logs):
        """Перенастройка loguru: перемещение файлов логирования в новую папку."""
        logger.remove()
        logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")  # Добавить вывод в консоль
        logger.add(os.path.join(path_logs, "app.log"), rotation="500 MB", level="DEBUG", encoding="utf8")

    def update_sensitivity_label(self, value):
        """Отображение числового значения ползунка"""
        self.ui.sensitivity_value_label.setText(str(value))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())  # Запускаем цикл обработки событий