import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource,  Button, Div, Slider
from bokeh.layouts import column, row

def initialise(N=1000, L=128.0, alpha=0.1, peak=1, c=1):
    dx = L / N
    dt = alpha / c * dx
    p = np.zeros((N + 1, 3))
    # initial conditions
    # pressure peak
    p[N // 2 - 1:N // 2 + 2, 0] = peak
    p[:, 1] = p[:, 0]
    return p, alpha, dx, dt

def evolve(p, alpha, n=1):
    # for i in range(1, p.shape[0] - 1):
        # p[i, n + 1] = alpha ** 2 * (p[i + 1, n] - 2 * p[i, n] + p[i - 1, n]) + 2 * p[i, n] - p[i, n - 1]
    p[1:-1,n+1] = alpha**2 * (p[2:, n] - 2 * p[1:-1, n] + p[:-2, n]) + 2 * p[1:-1, n] - p[1:-1, n - 1]

    # forget the past
    p[:, n - 1] = p[:, n]
    # swap present with future
    p[:, n] = p[:, n + 1]

def boundaries(p):
    p[0, :] = 0
    p[-1, :] = 0

def update_alpha(attrname, old, new):
    global alpha
    alpha = slider_alpha.value

L, N, tmax = 100.0, 200, 200.0
p, alpha, dx, dt = initialise(N, L, alpha=0.1)
x = np.arange(N + 1) * dx

source = ColumnDataSource(data=dict(x=x, y=p[:, 1]))
fig = figure(title="", min_width=200, min_height=200,
             x_axis_label="Position", y_axis_label="Pressure", x_range=(0, L), y_range=(-3.5, 3.5), sizing_mode="scale_both")
fig.line('x', 'y', source=source, line_width=2)

def update():
    evolve(p, alpha)
    boundaries(p)
    source.data = dict(x=x, y=p[:, 1])


def callback(event):
    x_pos = event.x
    y_pos = event.y
    closest_index = np.argmin(np.abs(x - x_pos))
    p[closest_index-1:closest_index+2, 1] += y_pos
    p[closest_index-1:closest_index+2, 0] += y_pos
    print(f"At x = {x_pos}, y = {y_pos}")

fig.toolbar.active_drag = None
fig.toolbar.active_scroll = None
fig.on_event('tap', callback)

# curdoc().add_periodic_callback(update, 15)

curdoc().title = "Wave Plot"

callback_id = None
def start():
    global callback_id
    if callback_id is None:
        callback_id = curdoc().add_periodic_callback(update, 20)

def stop():
    global callback_id
    if callback_id is not None:
        curdoc().remove_periodic_callback(callback_id)
        callback_id = None

def reset():
    global p, alpha, dx, dt
    p, alpha, dx, dt = initialise(N, L, alpha=0.1)
    source.data = dict(x=x, y=p[:, 1])


width = 300
start_button = Button(label="Run", button_type="success",width=width)
start_button.on_click(start)

stop_button = Button(label="Stop", button_type="danger",width=width)
stop_button.on_click(stop)

reset_button = Button(label="Reset", button_type="warning",width=width)
reset_button.on_click(reset)

slider_alpha = Slider(start=0.01, end=2.0, value=0.1, step=0.01, title="Courant number",width=width)
slider_alpha.on_change('value', update_alpha)

latex_content = r"""
<p>The <b>Courant number</b> \(\alpha = c\Delta t/ \Delta x \) determines the stability of the simulation. </p> <br>

<p> Take \(\alpha <1 \)  for a stable simulation.</p><br>

<p> The simulation is <b>interactive</b>: click on the graph to perturb the pressure profile.</p>
<img src="src/static/qr.png" alt="qr-code" style="width: 300px; height: 300px;">
"""

# qr = Div(text='<p> The courant number is $$\alpha = c\Delta t/\Delta x$$</p>',disable_math=False)
qr = Div(text=latex_content, width=width, height=100)
buttons = column(start_button, stop_button, reset_button,slider_alpha,qr)
layout = column(Div(text="<h2>  One-dimensional Wave Evolution </h2> "),row(fig, buttons,width=1000))

curdoc().add_root(layout)