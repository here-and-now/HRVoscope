# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_design.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

from charts import XYSeriesWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1226, 919)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(91, 745, 921, 101))
        self.verticalLayout_3 = QVBoxLayout(self.gridLayoutWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.hrv_ibi_chart = XYSeriesWidget(self.gridLayoutWidget)
        self.hrv_ibi_chart.setObjectName(u"hrv_ibi_chart")

        self.horizontalLayout.addWidget(self.hrv_ibi_chart)

        self.hr_chart = XYSeriesWidget(self.gridLayoutWidget)
        self.hr_chart.setObjectName(u"hr_chart")

        self.horizontalLayout.addWidget(self.hr_chart)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(30, 40, 861, 291))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(2)
        self.gridLayoutWidget_2 = QWidget(self.frame)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(10, 10, 831, 261))
        self.gridLayout = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.hrv_metrics_label = QLabel(self.gridLayoutWidget_2)
        self.hrv_metrics_label.setObjectName(u"hrv_metrics_label")
        font = QFont()
        font.setPointSize(12)
        self.hrv_metrics_label.setFont(font)

        self.horizontalLayout_3.addWidget(self.hrv_metrics_label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.hrv_metrics_time_1s_button = QPushButton(self.gridLayoutWidget_2)
        self.hrv_metrics_time_button_group = QButtonGroup(MainWindow)
        self.hrv_metrics_time_button_group.setObjectName(u"hrv_metrics_time_button_group")
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_1s_button)
        self.hrv_metrics_time_1s_button.setObjectName(u"hrv_metrics_time_1s_button")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hrv_metrics_time_1s_button.sizePolicy().hasHeightForWidth())
        self.hrv_metrics_time_1s_button.setSizePolicy(sizePolicy)
        self.hrv_metrics_time_1s_button.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.hrv_metrics_time_1s_button)

        self.hrv_metrics_time_5s_button = QPushButton(self.gridLayoutWidget_2)
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_5s_button)
        self.hrv_metrics_time_5s_button.setObjectName(u"hrv_metrics_time_5s_button")
        self.hrv_metrics_time_5s_button.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.hrv_metrics_time_5s_button)

        self.hrv_metrics_time_10s_button = QPushButton(self.gridLayoutWidget_2)
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_10s_button)
        self.hrv_metrics_time_10s_button.setObjectName(u"hrv_metrics_time_10s_button")
        self.hrv_metrics_time_10s_button.setCheckable(True)
        self.hrv_metrics_time_10s_button.setChecked(True)

        self.horizontalLayout_3.addWidget(self.hrv_metrics_time_10s_button)

        self.hrv_metrics_time_30s_button = QPushButton(self.gridLayoutWidget_2)
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_30s_button)
        self.hrv_metrics_time_30s_button.setObjectName(u"hrv_metrics_time_30s_button")
        self.hrv_metrics_time_30s_button.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.hrv_metrics_time_30s_button)

        self.hrv_metrics_time_1m_button = QPushButton(self.gridLayoutWidget_2)
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_1m_button)
        self.hrv_metrics_time_1m_button.setObjectName(u"hrv_metrics_time_1m_button")
        self.hrv_metrics_time_1m_button.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.hrv_metrics_time_1m_button)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.hrv_metrics_by_time_chart = XYSeriesWidget(self.gridLayoutWidget_2)
        self.hrv_metrics_by_time_chart.setObjectName(u"hrv_metrics_by_time_chart")

        self.gridLayout.addWidget(self.hrv_metrics_by_time_chart, 2, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1226, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.hrv_metrics_label.setText(QCoreApplication.translate("MainWindow", u"HRV metrics", None))
        self.hrv_metrics_time_1s_button.setText(QCoreApplication.translate("MainWindow", u"1s", None))
        self.hrv_metrics_time_5s_button.setText(QCoreApplication.translate("MainWindow", u"5s", None))
        self.hrv_metrics_time_10s_button.setText(QCoreApplication.translate("MainWindow", u"10s", None))
        self.hrv_metrics_time_30s_button.setText(QCoreApplication.translate("MainWindow", u"30s", None))
        self.hrv_metrics_time_1m_button.setText(QCoreApplication.translate("MainWindow", u"1m", None))
    # retranslateUi

