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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

from charts import XYSeriesWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1226, 919)
        self.actionReset_data = QAction(MainWindow)
        self.actionReset_data.setObjectName(u"actionReset_data")
        self.actionPause_plot = QAction(MainWindow)
        self.actionPause_plot.setObjectName(u"actionPause_plot")
        self.actionResume_plot = QAction(MainWindow)
        self.actionResume_plot.setObjectName(u"actionResume_plot")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.hrv_metrics_label = QLabel(self.centralwidget)
        self.hrv_metrics_label.setObjectName(u"hrv_metrics_label")
        font = QFont()
        font.setPointSize(12)
        self.hrv_metrics_label.setFont(font)

        self.horizontalLayout_3.addWidget(self.hrv_metrics_label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)

        self.hr_chart = XYSeriesWidget(self.centralwidget)
        self.hr_chart.setObjectName(u"hr_chart")

        self.gridLayout.addWidget(self.hr_chart, 4, 2, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_4.addWidget(self.label)

        self.hrv_metrics_time_1s_button = QPushButton(self.centralwidget)
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

        self.horizontalLayout_4.addWidget(self.hrv_metrics_time_1s_button)

        self.hrv_metrics_time_5s_button = QPushButton(self.centralwidget)
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_5s_button)
        self.hrv_metrics_time_5s_button.setObjectName(u"hrv_metrics_time_5s_button")
        self.hrv_metrics_time_5s_button.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.hrv_metrics_time_5s_button)

        self.hrv_metrics_time_10s_button = QPushButton(self.centralwidget)
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_10s_button)
        self.hrv_metrics_time_10s_button.setObjectName(u"hrv_metrics_time_10s_button")
        self.hrv_metrics_time_10s_button.setCheckable(True)
        self.hrv_metrics_time_10s_button.setChecked(True)

        self.horizontalLayout_4.addWidget(self.hrv_metrics_time_10s_button)

        self.hrv_metrics_time_30s_button = QPushButton(self.centralwidget)
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_30s_button)
        self.hrv_metrics_time_30s_button.setObjectName(u"hrv_metrics_time_30s_button")
        self.hrv_metrics_time_30s_button.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.hrv_metrics_time_30s_button)

        self.hrv_metrics_time_1m_button = QPushButton(self.centralwidget)
        self.hrv_metrics_time_button_group.addButton(self.hrv_metrics_time_1m_button)
        self.hrv_metrics_time_1m_button.setObjectName(u"hrv_metrics_time_1m_button")
        self.hrv_metrics_time_1m_button.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.hrv_metrics_time_1m_button)


        self.gridLayout.addLayout(self.horizontalLayout_4, 0, 2, 1, 1)

        self.hrv_ibi_chart = XYSeriesWidget(self.centralwidget)
        self.hrv_ibi_chart.setObjectName(u"hrv_ibi_chart")

        self.gridLayout.addWidget(self.hrv_ibi_chart, 4, 1, 1, 1)

        self.hrv_metrics_by_time_chart = XYSeriesWidget(self.centralwidget)
        self.hrv_metrics_by_time_chart.setObjectName(u"hrv_metrics_by_time_chart")

        self.gridLayout.addWidget(self.hrv_metrics_by_time_chart, 2, 1, 1, 2)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.plot_window_button_30s = QPushButton(self.centralwidget)
        self.plot_time_window_button_group = QButtonGroup(MainWindow)
        self.plot_time_window_button_group.setObjectName(u"plot_time_window_button_group")
        self.plot_time_window_button_group.addButton(self.plot_window_button_30s)
        self.plot_window_button_30s.setObjectName(u"plot_window_button_30s")
        self.plot_window_button_30s.setCheckable(True)

        self.horizontalLayout_6.addWidget(self.plot_window_button_30s)

        self.plot_window_button_1m = QPushButton(self.centralwidget)
        self.plot_time_window_button_group.addButton(self.plot_window_button_1m)
        self.plot_window_button_1m.setObjectName(u"plot_window_button_1m")
        self.plot_window_button_1m.setCheckable(True)
        self.plot_window_button_1m.setChecked(False)

        self.horizontalLayout_6.addWidget(self.plot_window_button_1m)

        self.plot_window_button_3m = QPushButton(self.centralwidget)
        self.plot_time_window_button_group.addButton(self.plot_window_button_3m)
        self.plot_window_button_3m.setObjectName(u"plot_window_button_3m")
        self.plot_window_button_3m.setCheckable(True)

        self.horizontalLayout_6.addWidget(self.plot_window_button_3m)

        self.plot_window_button_5m = QPushButton(self.centralwidget)
        self.plot_time_window_button_group.addButton(self.plot_window_button_5m)
        self.plot_window_button_5m.setObjectName(u"plot_window_button_5m")
        self.plot_window_button_5m.setCheckable(True)

        self.horizontalLayout_6.addWidget(self.plot_window_button_5m)

        self.plot_window_button_10m = QPushButton(self.centralwidget)
        self.plot_time_window_button_group.addButton(self.plot_window_button_10m)
        self.plot_window_button_10m.setObjectName(u"plot_window_button_10m")
        self.plot_window_button_10m.setCheckable(True)

        self.horizontalLayout_6.addWidget(self.plot_window_button_10m)

        self.plot_window_button_30m = QPushButton(self.centralwidget)
        self.plot_time_window_button_group.addButton(self.plot_window_button_30m)
        self.plot_window_button_30m.setObjectName(u"plot_window_button_30m")
        self.plot_window_button_30m.setCheckable(True)

        self.horizontalLayout_6.addWidget(self.plot_window_button_30m)

        self.plot_window_button_all = QPushButton(self.centralwidget)
        self.plot_time_window_button_group.addButton(self.plot_window_button_all)
        self.plot_window_button_all.setObjectName(u"plot_window_button_all")
        self.plot_window_button_all.setCheckable(True)
        self.plot_window_button_all.setChecked(True)

        self.horizontalLayout_6.addWidget(self.plot_window_button_all)


        self.gridLayout.addLayout(self.horizontalLayout_6, 6, 2, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.pacerButton = QPushButton(self.centralwidget)
        self.pacerButton.setObjectName(u"pacerButton")

        self.horizontalLayout.addWidget(self.pacerButton)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1226, 22))
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuSettings.addAction(self.actionReset_data)
        self.menuSettings.addAction(self.actionPause_plot)
        self.menuSettings.addAction(self.actionResume_plot)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionReset_data.setText(QCoreApplication.translate("MainWindow", u"Reset data", None))
        self.actionPause_plot.setText(QCoreApplication.translate("MainWindow", u"Pause plot", None))
        self.actionResume_plot.setText(QCoreApplication.translate("MainWindow", u"Resume plot", None))
        self.hrv_metrics_label.setText(QCoreApplication.translate("MainWindow", u"HRV metrics", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Calculate HRV over:", None))
        self.hrv_metrics_time_1s_button.setText(QCoreApplication.translate("MainWindow", u"1s", None))
        self.hrv_metrics_time_5s_button.setText(QCoreApplication.translate("MainWindow", u"5s", None))
        self.hrv_metrics_time_10s_button.setText(QCoreApplication.translate("MainWindow", u"10s", None))
        self.hrv_metrics_time_30s_button.setText(QCoreApplication.translate("MainWindow", u"30s", None))
        self.hrv_metrics_time_1m_button.setText(QCoreApplication.translate("MainWindow", u"1m", None))
        self.plot_window_button_30s.setText(QCoreApplication.translate("MainWindow", u"30s", None))
        self.plot_window_button_1m.setText(QCoreApplication.translate("MainWindow", u"1m", None))
        self.plot_window_button_3m.setText(QCoreApplication.translate("MainWindow", u"3m", None))
        self.plot_window_button_5m.setText(QCoreApplication.translate("MainWindow", u"5m", None))
        self.plot_window_button_10m.setText(QCoreApplication.translate("MainWindow", u"10m", None))
        self.plot_window_button_30m.setText(QCoreApplication.translate("MainWindow", u"30m", None))
        self.plot_window_button_all.setText(QCoreApplication.translate("MainWindow", u"All", None))
        self.pacerButton.setText(QCoreApplication.translate("MainWindow", u"Pacer", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

