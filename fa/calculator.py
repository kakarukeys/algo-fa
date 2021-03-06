def delta(frame):
    """ Returns deltas (diff with next value) of frame.

        >>> delta(pd.Series([3,2,8], index=[0,1,4]))
        0   -1
        1    6
        dtype: float64
    """
    return frame.diff().shift(-1).iloc[:-1]

forward_delta = delta

def backward_delta(frame):
    """ Returns deltas (diff with previous value) of frame.

        >>> backward_delta(pd.Series([3,2,8], index=[0,1,4]))
        1   -1
        4    6
        dtype: float64
    """
    return frame.diff().iloc[1:]

def derivative(frame, index_unit=1):
    """ Returns first-order derivative of frame.
        index_unit: optional divisor for deltas of index
        (used when delta_index is not suitable for division)

        >>> derivative(pd.Series([3,2,8], index=[0,1,4]))
        0   -1
        1    2
        dtype: float64
    """
    delta_frame = delta(frame)
    delta_index = delta(frame.index.to_series())
    return delta_frame.div(delta_index / index_unit, axis=0)

def translate_index(df, delta):
    """ add <delta> to index of <df> """
    return df.set_index(df.index + delta)

def get_deviations(frame):
    """ Returns how many sigmas does each value deviate from the mean of the column """
    return (frame - frame.mean()) / frame.std()
