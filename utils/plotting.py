"""
Utility functions for plotting and visualization.
"""

import matplotlib.pyplot as plt
import backtrader as bt


def customize_plot(fig):
    """
    Customize a backtrader plot figure.
    
    Args:
        fig: Matplotlib figure object
    """
    # Customize the figure
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Adjust figure size
    fig.set_size_inches(12, 8)
    
    # Customize title and labels
    ax = fig.axes[0]
    ax.set_title('Price Analysis', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price', fontsize=12)
    
    # Customize grid
    ax.grid(True, alpha=0.3)
    
    # Customize tick labels
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')


def save_plot(fig, filename='analysis.png'):
    """
    Save a plot to a file.
    
    Args:
        fig: Matplotlib figure object
        filename: Output filename
    """
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {filename}")
