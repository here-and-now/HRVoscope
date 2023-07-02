from datetime import datetime
import numpy as np
import pandas as pd
from scipy import signal

from scipy.interpolate import interp1d

from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QComboBox,
    QSlider,
    QGroupBox,
    QFormLayout,
    QCheckBox,
    QFileDialog,
    QProgressBar,
    QGridLayout,
    QSizePolicy,
    QStylePainter
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QMargins, QSize, QDateTime, QPointF, QRectF
from PySide6.QtGui import QIcon, QLinearGradient, QBrush, QGradient, QColor
from PySide6.QtCharts import QLegend, QLegendMarker, QChartView, QChart, QSplineSeries, QValueAxis, QAreaSeries, QLineSeries, QScatterSeries, QDateTimeAxis
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter

from utils import BLUE, WHITE, GREEN, YELLOW, RED
class XYSeriesWidget(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot = QChart()
        self.legend = self.plot.legend()

        self.legend.setAlignment(Qt.AlignRight)

        self.legend.update()

        self.series_dict = {}
        self.axes = []
        self.main_axis = None

        self.setChart(self.plot)
        self.setInteractive(True)

    def add_series(self, series_name, x_values=None, y_values=None, x_range=[0, 200], y_range=[0, 200],
                   line_color=Qt.blue, pen_width=1, use_existing_yaxis=True):
        series = QSplineSeries()
        pen = series.pen()
        pen.setWidth(pen_width)
        pen.setColor(line_color)
        series.setPen(pen)

        if self.main_axis is None:
            axis_x = QDateTimeAxis()
            self.main_axis = axis_x
        else:
            axis_x = self.main_axis

        if use_existing_yaxis and len(self.axes) > 0:
            axis_y = self.axes[0][1]
        else:
            axis_y = QValueAxis()
            axis_y.setLabelFormat("%i")
            axis_y.setRange(y_range[0], y_range[1])
            self.axes.append((axis_x, axis_y))

        self.plot.addSeries(series)
        self.plot.addAxis(axis_x, Qt.AlignBottom)
        self.plot.addAxis(axis_y, Qt.AlignLeft if use_existing_yaxis else Qt.AlignRight)

        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        self.series_dict[series_name] = series

        self.plot.legend().markers(series)[0].setLabel(series_name)
        self.plot.legend().setVisible(True)

    def update_series_points(self, series_name, x_values, y_values):
        series = self.series_dict.get(series_name)
        if series is not None:
            axis_x, _ = self._get_axes_by_name(series_name)
            if axis_x:
                axis_x.setRange(x_values[0], x_values[-1])

            data = [QPointF(x.timestamp() * 1000, y) for x, y in zip(x_values, y_values)]
            series.replace(data)

    def update_series(self, series_name, x_values, y_values):
        series = self.series_dict.get(series_name)
        if series is not None:
            axis_x, _ = self._get_axes_by_name(series_name)
            if axis_x:
                x_min = QDateTime.fromMSecsSinceEpoch(int(x_values[0].timestamp() * 1000))
                x_max = QDateTime.fromMSecsSinceEpoch(int(x_values[-1].timestamp() * 1000))
                axis_x.setRange(x_min, x_max)

            data = [QPointF(int(x.timestamp() * 1000), y) for x, y in zip(x_values, y_values)]
            series.replace(data)

    def _get_axes_by_name(self, series_name):
        series_index = self._get_series_index_by_name(series_name)
        if series_index is not None and series_index < len(self.axes):
            return self.axes[series_index]
        return None, None

    def _get_series_index_by_name(self, series_name):
        series = self.series_dict.get(series_name)
        if series is not None:
            return list(self.series_dict.values()).index(series)
        return None
