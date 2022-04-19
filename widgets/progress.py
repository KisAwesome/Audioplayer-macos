from PyQt6 import QtCore, QtGui, QtWidgets
import os


def humanbytes(B):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B/KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B/MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B/GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B/TB)


class ProgressBar(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(540, 121)
        self.main = Form
      
        Form.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(30, 60, 491, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(30, 20, 500, 16))
        Form.setWindowIcon(QtGui.QIcon('icon.png'))
        self.label.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        self.label.setObjectName("label")
        self.Form = Form

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def refresh(self, progress):
        if progress['status'] == 'finished':
            return self.Form.hide()
        title = os.path.basename(progress['filename'])[:-5]
        downloaded = humanbytes(progress['downloaded_bytes'])
        total = progress['_total_bytes_str']
        speed_str = progress.get('_speed_str', 'done')
        _eta_str = progress.get('_eta_str', '00:00')
        self.label.setText(
            f'Downloading {title} {downloaded} out of {total} at {speed_str} ETA {_eta_str}')
        self.progressBar.setValue(int(float(progress['_percent_str'][:-1])))

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate(
            "Form", ""))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = ProgressBar()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
