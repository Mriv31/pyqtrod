from matplotlib import pyplot as plt
from IPython import get_ipython
from IPython.display import display, Image
from io import BytesIO

ipython = get_ipython()


def dispinline():
    ipython.run_line_magic("matplotlib", "inline")
    plt.style.use("../PyQtRod/mr.mplstyle")  # my own style, can remove


def dispwidget():
    plt.style.use("../PyQtRod/mr_widget.mplstyle")  # my own style, can remove
    ipython.run_line_magic("matplotlib", "widget")
    plt.style.use("../PyQtRod/mr_widget.mplstyle")  # my own style, can remove


def fig2inline(fig):
    plt.close(fig)
    buff = BytesIO()
    fig.savefig(buff, format="png")
    buff.seek(0)
    display(Image(data=buff.getvalue()))
