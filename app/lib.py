from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrase
from .models.metadata import Metadata
import numpy as np
def get_books_citations():
    items = {}
    citations = Citation.get_all()
    for c in citations: 
        c = c.citation.split("; ")[0]
        items[c] = True 
        c = c.split(".")[0]
        items[c] = True 
        c = c.split(" ")[:-1]
        items[" ".join(c)] = True 
    return sorted(list(items.keys()))

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    grey_value = int(150 - font_size)  
    grey_value = max(50, min(grey_value, 200))  
    return "rgb({0}, {0}, {0})".format(grey_value)

from matplotlib.colors import LinearSegmentedColormap

# Slice the colormap to focus on the darkest shades
blue_cmap = LinearSegmentedColormap.from_list(
    "custom_blues", plt.cm.Blues(np.linspace(0.7, 1, 100))
)
