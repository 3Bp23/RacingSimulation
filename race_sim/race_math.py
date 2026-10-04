import numpy as np

def smootherstep(x, edge0=0.0, edge1=1.0):
    """
    Ken Perlin's smootherstep function.
    Returns 0 for x <= edge0, 1 for x >= edge1, and a C2 continuous smooth
    curve between 0 and 1 for edge0 < x < edge1.
    """
    x = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)

def asymmetric_gaussian(x, mu, sigma_left, sigma_right):
    """
    Returns an asymmetric Gaussian bump peaking at mu.
    """
    sigma = np.where(x < mu, sigma_left, sigma_right)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)

def smooth_blend(x, edge0, edge1):
    """
    Returns a smooth blend factor: 0 before edge0, 1 after edge1.
    """
    return smootherstep(x, edge0, edge1)

def bump_profile(x, start, peak, end):
    """
    Constructs a smooth bump that starts rising around `start`,
    peaks at `peak`, and returns to 0 around `end`.
    Implemented via asymmetric gaussian but scaled/shifted to roughly
    fit these bounds (3 sigma).
    """
    sigma_left = (peak - start) / 3.0
    sigma_right = (end - peak) / 3.0
    # Avoid div by zero
    sigma_left = max(sigma_left, 1e-5)
    sigma_right = max(sigma_right, 1e-5)

    return asymmetric_gaussian(x, peak, sigma_left, sigma_right)
