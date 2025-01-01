import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QWidget, QMessageBox, QGraphicsScene, QGraphicsView, QGraphicsTextItem, QGraphicsLineItem, QGraphicsPixmapItem, QFileDialog, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QPixmap, QFont
from math import cos, sin, radians
from subnetting import CIDR, VLSM 

class SubnettingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subnetting Tool")
        self.setGeometry(200, 200, 900, 700)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Algorithm selection
        self.algorithm_label = QLabel("Chọn thuật toán:")
        self.algorithm_label.setFont(QFont("Arial", 12))
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setFont(QFont("Arial", 12))
        self.algorithm_combo.addItems(["CIDR", "VLSM"])
        layout.addWidget(self.algorithm_label)
        layout.addWidget(self.algorithm_combo)

        # Input IP and mask
        self.input_label = QLabel("Nhập địa chỉ IP và mặt nạ mạng (VD: 192.168.1.0/24):")
        self.input_label.setFont(QFont("Arial", 12))
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Arial", 12))
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)

        # Additional input for CIDR/VLSM
        self.extra_input_label = QLabel("Nhập số mạng con hoặc danh sách yêu cầu host:")
        self.extra_input_label.setFont(QFont("Arial", 12))
        self.extra_input_field = QLineEdit()
        self.extra_input_field.setFont(QFont("Arial", 12))
        layout.addWidget(self.extra_input_label)
        layout.addWidget(self.extra_input_field)

        # Run button
        self.run_button = QPushButton("Tính toán")
        self.run_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.run_button.setStyleSheet("background-color: #5cb85c; color: white; border-radius: 5px;")
        self.run_button.clicked.connect(self.run_algorithm)
        layout.addWidget(self.run_button)

        # Export button
        self.export_button = QPushButton("Xuất file kết quả")
        self.export_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.export_button.setStyleSheet("background-color: #0275d8; color: white; border-radius: 5px;")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)  # Vô hiệu hóa ban đầu
        layout.addWidget(self.export_button)

        # Topology button
        self.topology_button = QPushButton("Xem gợi ý Topology mạng")
        self.topology_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.topology_button.setStyleSheet("background-color: #f0ad4e; color: white; border-radius: 5px;")
        self.topology_button.clicked.connect(self.show_topology)
        self.topology_button.hide()  # Ẩn nút ban đầu
        layout.addWidget(self.topology_button)

        # Output area
        self.output_area = QTextEdit()
        self.output_area.setFont(QFont("Consolas", 12))
        self.output_area.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Network Topology Visualization
        self.topology_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.topology_view.setScene(self.scene)
        self.topology_view.setStyleSheet("border: 1px solid #ccc; background-color: #e9ecef;")
        layout.addWidget(self.topology_view)
        self.topology_view.hide()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_algorithm(self):
        algorithm = self.algorithm_combo.currentText()
        ip_mask = self.input_field.text().strip()
        extra_input = self.extra_input_field.text().strip()

        if not ip_mask:
            QMessageBox.warning(self, "Lỗi", "Hãy nhập địa chỉ IP và mặt nạ mạng.")
            return

        try:
            ip, mask = ip_mask.split('/')
            mask = int(mask)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Địa chỉ IP hoặc mặt nạ mạng không hợp lệ.")
            return

        try:
            if algorithm == "CIDR":
                num_subnets = int(extra_input)
                cidr = CIDR(ip, mask)
                subnets = cidr.calculate_subnets(num_subnets)
            elif algorithm == "VLSM":
                host_requirements = list(map(int, extra_input.split(',')))
                vlsm = VLSM(ip, mask)
                subnets = vlsm.calculate_subnets(host_requirements)

            self.display_output(subnets)
            self.export_button.setEnabled(True)
            self.topology_button.show() 

        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def display_output(self, subnets):
        self.output_area.clear()
        for i, subnet in enumerate(subnets):
            self.output_area.append(f"Mạng con {i + 1}:")
            for key, value in subnet.items():
                self.output_area.append(f"  {key}: {value}")
            self.output_area.append("")

        self.visualize_topology(subnets)

    def visualize_topology(self, subnets):
        self.scene.clear()

        center_x, center_y = 450, 300
        radius = 200

        router_pixmap = QPixmap("router.png").scaled(80, 60)
        router_item = QGraphicsPixmapItem(router_pixmap)
        router_item.setPos(center_x - 40, center_y - 30)
        self.scene.addItem(router_item)

        router_label = QGraphicsTextItem("Router")
        router_label.setFont(QFont("Arial", 12, QFont.Bold))
        router_label.setPos(center_x - 25, center_y + 40)
        self.scene.addItem(router_label)

        num_switches = len(subnets)
        angle_step = 360 / num_switches

        for i, subnet in enumerate(subnets):
            network_address = subnet.get('Địa chỉ mạng', 'N/A')

            angle = radians(angle_step * i)
            x = center_x + radius * cos(angle)
            y = center_y + radius * sin(angle)

            switch_pixmap = QPixmap("switch.png").scaled(70, 45)
            switch_item = QGraphicsPixmapItem(switch_pixmap)
            switch_item.setPos(x - 35, y - 25)
            self.scene.addItem(switch_item)

            switch_label = QGraphicsTextItem(f"Switch {i + 1}")
            switch_label.setFont(QFont("Arial", 10, QFont.Bold))
            switch_label.setPos(x - 30, y + 30)
            self.scene.addItem(switch_label)

            line = QGraphicsLineItem(center_x, center_y, x, y)
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)

            network_label = QGraphicsTextItem(f"Net: {network_address}")
            network_label.setFont(QFont("Arial", 10))
            network_label.setPos(x - 50, y + 50)
            self.scene.addItem(network_label)

    def export_results(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu kết quả", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.output_area.toPlainText())
            QMessageBox.information(self, "Thành công", f"Kết quả đã được lưu tại: {file_path}")

    def show_topology(self):    
        topology_dialog = TopologyDialog(self.scene, self)
        topology_dialog.exec_()

class TopologyDialog(QDialog):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gợi ý Topology Mạng")
        self.setGeometry(300, 300, 800, 600)

        # Tạo layout cho dialog
        layout = QVBoxLayout()

        # Thêm GraphicsView để hiển thị scene
        self.topology_view = QGraphicsView()
        self.topology_view.setScene(scene)
        self.topology_view.setStyleSheet("border: 1px solid #ccc; background-color: #e9ecef;")
        layout.addWidget(self.topology_view)

        # Đặt layout cho QDialog
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SubnettingApp()
    window.show()
    sys.exit(app.exec_())
