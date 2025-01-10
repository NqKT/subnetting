import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QWidget, QMessageBox, QGraphicsScene, QGraphicsView, QGraphicsTextItem, QGraphicsLineItem, QGraphicsPixmapItem, QFileDialog, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QPixmap, QFont
from math import cos, sin, radians
from subnetting import *

class SubnettingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subnetting Tool")
        self.setGeometry(200, 200, 900, 700)
        self.initUI()

    def initUI(self):
        self.start_screen()

    def start_screen(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Đặt hình nền với lớp phủ mờ
        self.central_widget.setStyleSheet("""
            background-image: url('bg.webp');
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        """)

        # Thêm lớp phủ mờ cho toàn bộ widget
        overlay = QLabel(self.central_widget)
        overlay.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.7); /* Lớp phủ màu trắng, mờ 70% */
            position: absolute;
            border-radius: 10px;
        """)
        overlay.setGeometry(0, 0, self.width(), self.height())

        layout = QVBoxLayout()

        title_label = QLabel()
        title_label.setText("""
            <p style="
                font-size: 28px; 
                font-weight: bold; 
                color: #44a3e3; 
                background-color: rgba(203, 243, 244, 0.8); 
                border-radius: 10px; 
                padding: 10px; 
                text-align: center; 
                -webkit-text-stroke: 1px black;">Welcome to the Subnetting Tool</p>
        """)
        title_label.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #ffa1a1; 
            background-color: rgba(240, 243, 244, 0.8); /* Nền trong suốt */
            border: 2px solid black; /* Viền đen */
            border-radius: 10px;
            padding: 10px;
            text-align: center;
        """)

        title_label.setAlignment(Qt.AlignCenter)

        start_button = QPushButton("Start")
        start_button.setStyleSheet("""
            font-size: 18px;
            padding: 8px 20px;
            color: white;
            background-color: #2E86C1;
            border: none;
            border-radius: 10px;
        """)
        start_button.clicked.connect(self.subnetting_screen)

        layout.addWidget(title_label)
        layout.addWidget(start_button)

        self.central_widget.setLayout(layout)

    def subnetting_screen(self):
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

        # File input button
        self.file_button = QPushButton("Nhập từ file")
        self.file_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.file_button.setStyleSheet("background-color: #6c757d; color: white; border-radius: 5px;")
        self.file_button.clicked.connect(self.load_from_file)
        layout.addWidget(self.file_button)

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
        self.export_button.hide()  # Ẩn nút ban đầu
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
        self.guidance_area = QTextEdit()
        self.guidance_area.setReadOnly(True)
        layout.addWidget(self.output_area)
        layout.addWidget(self.guidance_area)

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

    def load_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    if len(lines) < 3:
                        raise ValueError("File không đúng định dạng. Vui lòng kiểm tra nội dung.")

                    # Lấy giá trị từ file
                    algorithm = lines[0].strip()
                    ip_mask = lines[1].strip()
                    extra_input = lines[2].strip()

                    # Kiểm tra thuật toán hợp lệ
                    if algorithm not in ["CIDR", "VLSM"]:
                        raise ValueError("Thuật toán không hợp lệ. Chỉ chấp nhận CIDR hoặc VLSM.")

                    # Gán giá trị lên giao diện
                    self.algorithm_combo.setCurrentText(algorithm)
                    self.input_field.setText(ip_mask)
                    self.extra_input_field.setText(extra_input)

            except Exception as e:
                QMessageBox.warning(self, "Lỗi", str(e))

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

            ip_address = Subnetting(ip, mask)
            if ip == ip_address.network_address:
                reply = QMessageBox.information(self, "Thông báo", f"Đây là địa chỉ mạng. Bạn vẫn sẽ chia mạng từ địa chỉ {ip} chứ?", QMessageBox.Ok | QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    return
            elif ip == ip_address.broadcast_address:
                reply = QMessageBox.information(self, "Thông báo", f"Đây là địa chỉ broadcast. Bạn vẫn sẽ chia mạng từ địa chỉ {ip} chứ?", QMessageBox.Ok | QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    return
            else:
                reply = QMessageBox.information(self, "Thông báo", f"Đây là địa chỉ trạm. Bạn vẫn sẽ chia mạng từ địa chỉ {ip} chứ?", QMessageBox.Ok | QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    return

        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Địa chỉ IP hoặc mặt nạ mạng không hợp lệ.")
            return

        try:
            ip, mask = ip_mask.split('/')
            mask = int(mask)
            if algorithm == "CIDR":
                num_subnets = int(extra_input)
                cidr = CIDR(ip, mask)
                subnets = cidr.calculate_subnets(num_subnets)
                network_address = cidr.network_address
                broadcast_address = cidr.broadcast_address 
                total = 1 << (32 - mask)
                max_per_subnet = total // num_subnets
                new_mask = cidr.prefix_length     
                station_part = 32 - new_mask           

                if ip == network_address:
                    type_address = "mạng"
                elif ip == broadcast_address:
                    type_address = "quảng bá"
                else:
                    type_address = "trạm"
                guidance = (
                    f"Ta có, {ip}/{mask} là địa chỉ {type_address}.\n"
                    f"=> Địa chỉ mạng là {network_address}, mạng này có phạm vi là 2^(32-{mask}) = {total}.\n"
                    f"Với yêu cầu {num_subnets} mạng thì mỗi mạng sẽ có phạm vi tối đa là ({total}/{num_subnets}) = {max_per_subnet}.\n"
                    f"Vì tối đa chỉ {max_per_subnet} nên mỗi mạng con sẽ có phạm vi {1 << (station_part)} = 2^{station_part} địa chỉ.\n"
                    f"=> Mỗi mạng sẽ cần {station_part} bit phần trạm.\n"
                    f"=> Số bit phần mạng là 32 - {station_part} = {new_mask}. Do đó, có các mạng con mới /{new_mask}."
                )
                                    
            elif algorithm == "VLSM":
                host_requirements = list(map(int, extra_input.split(',')))
                vlsm = VLSM(ip, mask)
                subnets = vlsm.calculate_subnets(host_requirements)
                network_address = vlsm.network_address
                broadcast_address = vlsm.broadcast_address 
                
                if ip == network_address:
                    type_address = "mạng"
                elif ip == broadcast_address:
                    type_address = "quảng bá"
                else:
                    type_address = "trạm"

                guidance = (
                    f"Ta có, {ip}/{mask} là địa chỉ {type_address}.\n"
                    f"=> Địa chỉ mạng {network_address}/{mask} này có số bit phần trạm là 32 - {mask} = {32 - mask}bit.\n"
                    f"Theo VLSM, việc chia mạng sẽ bắt đầu từ yêu cầu lớn nhất trước.\n"
                    f"Nên các yêu cầu sẽ được sắp xếp lại theo thứ tự {', '.join(map(str, host_requirements))}.\n"
                )


            self.display_output(subnets)            
            self.guidance_area.setPlainText(guidance)
            font = QFont("Arial", 10)
            self.guidance_area.setFont(font)
            self.export_button.show()
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
        router_radius = 150
        switch_radius = 100

        router_pixmap = QPixmap("router.png").scaled(80, 60)
        switch_pixmap = QPixmap("switch.png").scaled(70, 45)

        num_subnets = len(subnets)
        max_switches_per_router = 3

        num_routers = (num_subnets + max_switches_per_router - 1) // max_switches_per_router

        routers = []

        # Tạo các router và đặt vị trí của chúng
        for r in range(num_routers):
            x_router = center_x + router_radius * (r * 2 - num_routers + 1)
            y_router = center_y

            router_item = QGraphicsPixmapItem(router_pixmap)
            router_item.setPos(x_router - 40, y_router - 30)
            self.scene.addItem(router_item)

            router_label = QGraphicsTextItem(f"Router {r + 1}")
            router_label.setFont(QFont("Arial", 12, QFont.Bold))
            router_label.setPos(x_router - 30, y_router + 40)
            self.scene.addItem(router_label)

            routers.append((x_router, y_router))

        # Vẽ đường nối giữa các router
        for r in range(num_routers - 1):
            x_router1, y_router1 = routers[r]
            x_router2, y_router2 = routers[r + 1]

            line = QGraphicsLineItem(x_router1, y_router1, x_router2, y_router2)
            line.setPen(QPen(Qt.black, 2, Qt.DashLine))
            self.scene.addItem(line)

        # Phân bố switch cho từng router
        for i, subnet in enumerate(subnets):
            router_index = i // max_switches_per_router
            x_router, y_router = routers[router_index]

            switch_angle = radians(100 * (i % max_switches_per_router) - 70) 
            x_switch = x_router + switch_radius * cos(switch_angle)
            y_switch = y_router + switch_radius * sin(switch_angle)

            switch_item = QGraphicsPixmapItem(switch_pixmap)
            switch_item.setPos(x_switch - 35, y_switch - 25)
            self.scene.addItem(switch_item)

            switch_label = QGraphicsTextItem(f"Switch {i + 1}")
            switch_label.setFont(QFont("Arial", 10, QFont.Bold))
            switch_label.setPos(x_switch - 30, y_switch + 30)
            self.scene.addItem(switch_label)

            # Vẽ đường nối giữa router và switch
            line = QGraphicsLineItem(x_router, y_router, x_switch, y_switch)
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)

            # Hiển thị thông tin mạng của switch
            network_address = subnet.get('Địa chỉ mạng', 'N/A')
            network_label = QGraphicsTextItem(f"Net: {network_address}")
            network_label.setFont(QFont("Arial", 10))
            network_label.setPos(x_switch - 50, y_switch + 50)
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
