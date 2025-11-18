"""
Python MCD File Reader

This package provides a Python interface for reading Multi Channel Systems (MCS)
.mcd files using the Neuroshare API.

Example usage:
    >>> from neuroshare_mcd import MCDFile
    >>> with MCDFile('data.mcd') as mcd:
    ...     info = mcd.info()
    ...     data = mcd.get_analog_data(1)
"""

__version__ = "1.0.0"
__author__ = "BrainBox Project"
__all__ = ["MCDFile", "MCD2HDF5Converter", "print_mcd_info"]

from .neuroshare_mcd import MCDFile, MCD2HDF5Converter, print_mcd_info
