import sys
from PyQt5 import QtWidgets, QtCore
from ui_main_window import Ui_MainWindow  # Импортируем сгенерированный класс

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setCentralWidget(self.ui.centralwidget) # Устанавливаем центральный виджет
        # Дополнительная инициализация (например, подключение сигналов)
        self.setup_connections() #  Вызываем setup_connections()

    def setup_connections(self):
        #Подключаем сигналы к слотам (обработчикам событий)
        self.ui.log_path_button.clicked.connect(self.choose_log_path) # Пример
        self.ui.sensivity_slider.valueChanged.connect(self.update_sensitivity_label)

    def choose_log_path(self):
        # Ваша логика выбора пути
        print("Выбор пути...")

    def update_sensitivity_label(self, value):
        self.ui.sensitivity_value_label.setText(str(value))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()  # Создаем экземпляр главного окна
    window.show()          # Показываем окно
    sys.exit(app.exec_())  # Запускаем цикл обработки событий