import PySide6.QtWidgets as QtWidgets
from PySide6.QtCore import QTimer
import pandas as pd
import pyqtgraph as pg
import numpy as np
from scipy.interpolate import interp1d

from sensor import SensorClient
from pacer import Pacer
from ui import Ui_MainWindow
from pacer_ui import Ui_PacerWidget
from utils import BLUE, RED, get_ms_from_button_text

class View(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("HRVoscope")

        # Initialize pacer and its timer
        self.pacer = Pacer()
        self.pacer_timer = QTimer(self)
        self.pacer_timer.timeout.connect(self.update_pacer)
        self.pacer_timer.start(100)  # Update every 100 ms

        # Setup model and sensor client
        self.model = model
        self.sensor = SensorClient()
        self.sensor.connect_client(self.sensor)

        # Connect signals for dataframe updates
        self.sensor.hr_update.connect(self.model.update_hr_dataframe)
        self.sensor.ibi_update.connect(self.model.update_ibi_dataframe)

        # Connect signals for plotting
        self.model.hr_dataframe_update.connect(self.plot_hr)
        self.model.ibi_dataframe_update.connect(self.plot_ibi)
        self.model.ibi_dataframe_update.connect(self.plot_hrv_metrics)

        # Setup actions
        self.actionReset_data.triggered.connect(self.reset_data)
        self.actionPause_plot.triggered.connect(self.pause_plotting)
        self.actionResume_plot.triggered.connect(self.resume_plotting)

        # Initialize plot_paused flag
        self.plot_paused = False

        # Connect the pacerButton click event to the open_pacer_window method
        self.pacerButton.clicked.connect(self.open_pacer_window)

    def open_pacer_window(self):
        if not hasattr(self, 'pacer_window'):
            self.pacer_window = QtWidgets.QWidget()
            self.pacer_ui = Ui_PacerWidget()
            self.pacer_ui.setupUi(self.pacer_window)
            self.pacer_window.show()

            # Set the scene with explicit size
            scene = QtWidgets.QGraphicsScene(0, 0, self.pacer_ui.pacer_view.width(), self.pacer_ui.pacer_view.height())
            self.pacer_ui.pacer_view.setScene(scene)

    def update_pacer(self):
        if not hasattr(self, 'pacer_ui') or self.pacer_ui.pacer_view.scene() is None:
            return  # Ensure pacer_ui and scene are initialized

        breathing_rate = 12  # Replace with actual breathing rate
        x, y = self.pacer.update(breathing_rate)

        # Scale factors based on scene size
        scene = self.pacer_ui.pacer_view.scene()
        x_center, y_center = scene.width() / 2, scene.height() / 2
        scale_factor = min(scene.width(), scene.height()) / 4  # Adjust scale factor as needed

        # Apply scaling and centering
        x_scaled = x * scale_factor + x_center
        y_scaled = y * scale_factor + y_center

        # Debugging
        print(
            f"Ellipse position and size: x={min(x_scaled)}, y={min(y_scaled)}, width={max(x_scaled) - min(x_scaled)}, height={max(y_scaled) - min(y_scaled)}")

        scene.clear()
        ellipse = QtWidgets.QGraphicsEllipseItem(min(x_scaled), min(y_scaled), max(x_scaled) - min(x_scaled),
                                                 max(y_scaled) - min(y_scaled))
        scene.addItem(ellipse)

    def _plot_data(self, df, chart, name, color):
        if self.plot_paused or df.empty:
            return

        tw = self.time_window_for_plot()
        x = df.index.values
        y = df[name].values
        chart.plot(x, y, name=name, time_window=tw, pen=pg.mkPen(color=color, width=2))

    def plot_ibi(self, df):
        self._plot_data(df, self.hrv_ibi_chart, 'ibi', BLUE)

    def plot_hr(self, df):
        self._plot_data(df, self.hr_chart, 'hr', BLUE)

    def plot_hrv_metrics(self, df):
        if self.plot_paused or df.empty:
            return

        time_metrics_window = get_ms_from_button_text(self.hrv_metrics_time_button_group.checkedButton())
        df = self.model.calculate_hrv_metrics(time_metrics_window=time_metrics_window)
        tw = self.time_window_for_plot()

        if 'SDNN' in df and 'RMSSD' in df:
            df = df.dropna()
            x = df.index.values
            y_sdnn = df['SDNN'].values
            y_rmssd = df['RMSSD'].values
            self.hrv_metrics_by_time_chart.plot(x, y_sdnn, name='SDNN', time_window=tw, pen=pg.mkPen(color=RED, width=2))
            self.hrv_metrics_by_time_chart.plot(x, y_rmssd, name='RMSSD', time_window=tw, pen=pg.mkPen(color=BLUE, width=2))

    def time_window_for_plot(self):
        return get_ms_from_button_text(self.plot_time_window_button_group.checkedButton())

    def downsample_dataframe(self, df, target_points):
        if df.empty or len(df) <= target_points:
            return df

        df_downsampled = pd.DataFrame()
        for column in df.columns:
            x = df.index.values.astype(np.float64)
            f = interp1d(x, df[column], kind='linear')
            target_index = pd.date_range(start=df.index[0], end=df.index[-1], periods=target_points)
            target_x = target_index.values.astype(np.float64)
            interpolated_values = f(target_x)
            df_downsampled[column] = interpolated_values

        df_downsampled.index = target_index
        return df_downsampled

    def reset_data(self):
        self.model.initialize_dataframes()
        self.hr_chart.clear()
        self.hrv_ibi_chart.clear()
        self.ecg_chart.clear()
        self.acc_chart.clear()
        self.hrv_metrics_by_time_chart.clear()

    def pause_plotting(self):
        self.plot_paused = True

    def resume_plotting(self):
        self.plot_paused = False
