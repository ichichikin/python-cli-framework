import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from datetime import datetime, timezone
from decimal import *
from system.config import *


class TimeSeriesPlot:
    def __init__(self):
        self._data = {}
        self._markers = {}
        self._markers_text = {}
        self._data_max_elements = Config.PLOT_RESOLUTION

    # noinspection PyProtectedMember
    @classmethod
    def show_in_browser(cls, *timeseriesplots: 'TimeSeriesPlot') -> None:
        fig = make_subplots(rows=len(timeseriesplots), cols=1, shared_xaxes=True)
        for row, plot in enumerate(timeseriesplots):
            for name, sc in plot._data.items():
                for i, n in enumerate(list(sc.keys())):
                    if i % int(len(sc) / plot._data_max_elements + 1) != 0:
                        del sc[n]

            for name, sc in plot._data.items():
                name = name.split(" ")
                color = name[1] if len(name) > 1 else None
                name = name[0]

                if color:
                    fig.add_trace(
                        go.Scatter(
                            x=tuple(sc.keys()),
                            y=tuple(sc.values()),
                            mode='lines',
                            name=name,
                            line={'color': color},
                            yaxis="y" + str(row + 1)
                        )
                    )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=tuple(sc.keys()),
                            y=tuple(sc.values()),
                            mode='lines',
                            name=name,
                            yaxis="y" + str(row + 1)
                        )
                    )

            for name, sc in plot._markers.items():
                style_name = name
                name = name.split(" ")
                color = name[1] if len(name) > 1 else None
                name = name[0]
                size = 15

                if name.lower() == "buy":
                    name = "triangle-up"
                    color = "green"
                elif name.lower() == "sell":
                    name = "triangle-down"
                    color = "red"
                elif name.lower() == "close-buy":
                    name = "x"
                    color = "green"
                    # size = 8
                elif name.lower() == "close-sell":
                    name = "x"
                    color = "red"
                    # size = 8
                elif name.lower() == "none":
                    name = "circle-open"
                    color = "black"
                    # size = 8

                if color:
                    fig.add_trace(
                        go.Scatter(
                            x=tuple(sc.keys()),
                            y=tuple(sc.values()),
                            mode='markers',
                            marker_symbol=name,
                            name=style_name if style_name != "none" else "[untitled]",
                            text=tuple(plot._markers_text[style_name].values()),
                            marker_color=color,
                            marker_size=size,
                            opacity=0.8,
                            yaxis="y" + str(row + 1)
                        )
                    )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=tuple(sc.keys()),
                            y=tuple(sc.values()),
                            mode='markers',
                            marker_symbol=name,
                            name=style_name if style_name != "none" else "[untitled]",
                            text=tuple(plot._markers_text[style_name].values()),
                            marker_size=size,
                            opacity=0.8,
                            yaxis="y" + str(row + 1)
                        )
                    )
            fig.update_layout(
                **{
                    "yaxis" + str(row + 1): dict(
                        ticks='outside',
                        showline=True,
                        exponentformat="none",
                        fixedrange=False,
                        anchor="x",
                        domain=[1 - (row + 1) / len(timeseriesplots), 1 - row / len(timeseriesplots)]
                    ),
                }
            )

        fig.update_layout(
            height=Config.PLOT_HEIGHT * len(timeseriesplots),
            xaxis=dict(
                ticks='outside',
                showline=True,
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
            ),
            dragmode="zoom",
            hovermode="x",
            template="plotly_white"
        )

        pio.show(renderer="browser", fig=fig, config={'displaylogo': False})

    def add_data(self, name: str, timestamp: Decimal, value: Decimal) -> None:
        if name not in self._data:
            self._data[name] = {}
        self._data[name][datetime.fromtimestamp(float(timestamp), tz=timezone.utc)] = value

    def add_marker(self, timestamp: Decimal, value: Decimal, style: str = "none", text: str = "") -> None:
        if style not in self._markers:
            self._markers[style] = {}
        if datetime.fromtimestamp(float(timestamp), tz=timezone.utc) not in self._markers[style] or \
            self._markers[style][datetime.fromtimestamp(float(timestamp), tz=timezone.utc)] != value:
            self._markers[style][datetime.fromtimestamp(float(timestamp), tz=timezone.utc)] = value
            if style not in self._markers_text:
                self._markers_text[style] = {}
            self._markers_text[style][datetime.fromtimestamp(float(timestamp), tz=timezone.utc)] = text
        else:
            self._markers_text[style][datetime.fromtimestamp(float(timestamp), tz=timezone.utc)] = \
                self._markers_text[style][datetime.fromtimestamp(float(timestamp), tz=timezone.utc)] + "<br>" + text
