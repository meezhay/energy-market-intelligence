# Small helper functions that don't naturally belong elsewhere will be in this file. For example, a function to normalize a column in a dataframe.

def min_max_scale(series, reverse=False):
    """
    Min-max normalize a pandas Series.

    Parameters
    ----------
    series : pandas.Series
    reverse : bool, default=False
        If True, larger original values receive smaller normalized scores.

    Returns
    -------
    pandas.Series
    """
    scaled = (series - series.min()) / (series.max() - series.min())

    if reverse:
        scaled = 1 - scaled

    return scaled
