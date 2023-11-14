# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_pacer.ui'
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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_PacerWidget(object):
    def setupUi(self, PacerWidget):
        if not PacerWidget.objectName():
            PacerWidget.setObjectName(u"PacerWidget")
        PacerWidget.resize(703, 491)
        self.verticalLayoutWidget = QWidget(PacerWidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(49, 19, 431, 421))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.pacer_view = QGraphicsView(self.verticalLayoutWidget)
        self.pacer_view.setObjectName(u"pacer_view")

        self.verticalLayout.addWidget(self.pacer_view)


        self.retranslateUi(PacerWidget)

        QMetaObject.connectSlotsByName(PacerWidget)
    # setupUi

    def retranslateUi(self, PacerWidget):
        PacerWidget.setWindowTitle(QCoreApplication.translate("PacerWidget", u"Form", None))
    # retranslateUi

