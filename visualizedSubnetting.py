import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QWidget, QMessageBox, QGraphicsScene, QGraphicsView, QGraphicsTextItem, QGraphicsLineItem, QGraphicsPixmapItem, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QPixmap
from math import cos, sin, radians
from subnetting import *  # Giả sử bạn đã có các lớp CIDR và VLSM

class SubnettingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subnetting Tool")
        self.setGeometry(200, 200, 800, 600)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Algorithm selection
        self.algorithm_label = QLabel("Chọn thuật toán:")
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["CIDR", "VLSM"])
        layout.addWidget(self.algorithm_label)
        layout.addWidget(self.algorithm_combo)

        # Input IP and mask
        self.input_label = QLabel("Nhập địa chỉ IP và mặt nạ mạng (VD: 192.168.1.0/24):")
        self.input_field = QLineEdit()
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)

        # Additional input for CIDR/VLSM
        self.extra_input_label = QLabel("Nhập số mạng con hoặc danh sách yêu cầu host:")
        self.extra_input_field = QLineEdit()
        layout.addWidget(self.extra_input_label)
        layout.addWidget(self.extra_input_field)

        # Run button
        self.run_button = QPushButton("Thực hiện")
        self.run_button.clicked.connect(self.run_algorithm)
        layout.addWidget(self.run_button)

        # Topology view option
        self.show_topology_checkbox = QPushButton("Xem Topology Mạng")
        self.show_topology_checkbox.setCheckable(True)
        self.show_topology_checkbox.setVisible(False)  # Ẩn nút này ban đầu
        layout.addWidget(self.show_topology_checkbox)

        # Output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Network Topology Visualization
        self.topology_view = QGraphicsView()
        self.scene = QGraphicsScene()  # Tạo một scene mới cho đồ họa
        self.topology_view.setScene(self.scene)
        layout.addWidget(self.topology_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Khi nhấn nút "Xem Topology Mạng"
        self.show_topology_checkbox.clicked.connect(self.show_topology)

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
                self.display_output(subnets)
                self.show_topology_checkbox.setVisible(True)  # Hiển thị nút khi có kết quả

            elif algorithm == "VLSM":
                host_requirements = list(map(int, extra_input.split(',')))
                vlsm = VLSM(ip, mask)
                subnets = vlsm.calculate_subnets(host_requirements)
                self.display_output(subnets)
                self.show_topology_checkbox.setVisible(True)  # Hiển thị nút khi có kết quả

        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def display_output(self, subnets):
        self.output_area.clear()
        for i, subnet in enumerate(subnets):
            self.output_area.append(f"Mạng con {i + 1}:")
            for key, value in subnet.items():
                self.output_area.append(f"  {key}: {value}")
            self.output_area.append("")

        # Hiển thị sơ đồ mạng
        self.visualize_topology(subnets)

    def visualize_topology(self, subnets):
        self.scene.clear()  # Xóa các đối tượng hiện tại trong scene

        center_x, center_y = 400, 200  # Vị trí trung tâm cho router
        radius = 150  # Bán kính vòng tròn để đặt switch

        # Thêm router vào trung tâm
        router_pixmap = QPixmap("router.png").scaled(60, 41)
        router_item = QGraphicsPixmapItem(router_pixmap)
        router_item.setPos(center_x - 30, center_y - 25)  # Vị trí của router
        self.scene.addItem(router_item)
        
        router = QGraphicsTextItem("Router")
        router.setPos(center_x - 20, center_y + 20)
        self.scene.addItem(router)

        # Vẽ switch và các kết nối
        num_switches = len(subnets)
        angle_step = 360 / num_switches  # Tính góc để phân phối đều các switch

        for i, subnet in enumerate(subnets):
            # Địa chỉ mạng từ dữ liệu subnet
            network_address = subnet.get('Địa chỉ mạng', 'N/A')

            # Tính toán góc để đặt switch
            angle = angle_step * i
            x = center_x + radius * cos(radians(angle))
            y = center_y + radius * sin(radians(angle))

            # Thêm switch
            switch_pixmap = QPixmap("switch.png").scaled(60, 35)
            switch_item = QGraphicsPixmapItem(switch_pixmap)
            switch_item.setPos(x - 25, y - 20)
            self.scene.addItem(switch_item)

            switch = QGraphicsTextItem(f"Switch {i}")
            switch.setPos(x - 20, y + 5)
            self.scene.addItem(switch)
            # Thêm đường kết nối từ router đến switch
            
            line = QGraphicsLineItem(center_x, center_y, x, y)
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)

            # Hiển thị địa chỉ mạng gần switch
            network_address_label = QGraphicsTextItem(f"Net {i}: {network_address}")
            address_x = x - 25
            address_y = y + 20  # Đặt dưới switch
            network_address_label.setPos(address_x - 20, address_y)
            self.scene.addItem(network_address_label)

    def show_topology(self):
        # Hiển thị Topology trong cửa sổ mới
        topology_window = TopologyWindow(self)
        topology_window.exec_()

class TopologyWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Network Topology")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()

        # Tạo QGraphicsView để hiển thị topology
        self.topology_view = QGraphicsView(parent.scene)  # Truyền scene từ SubnettingApp
        layout.addWidget(self.topology_view)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SubnettingApp()
    window.show()
    sys.exit(app.exec_())
