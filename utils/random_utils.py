def unit_conversion(unit):
    """
    Convert unit identifier to its corresponding duration in seconds.

    Parameters
    ----------
    unit : str
        A string representing a unit of time (e.g., 'scale_02', 'scale_24').

    Returns
    -------
    float
        The duration in seconds corresponding to the input unit.
    """
    if unit == "scale_02":
        return 0.2
    if unit == "scale_04":
        return 0.4
    if unit == "scale_06":
        return 0.6
    if unit == "scale_2":
        return 2.0
    if unit == "scale_4":
        return 4.0
    if unit == "scale_6":
        return 6.0
    if unit == "scale_12":
        return 12.0
    if unit == "scale_24":
        return 24.0
    return 60.0

def str_to_number(val):
    try:
        # Tenta converter para inteiro
        return int(val)
    except ValueError:
        try:
            # Tenta converter para float
            return float(val)
        except ValueError:
            # Retorna o valor original se não for um número
            return val