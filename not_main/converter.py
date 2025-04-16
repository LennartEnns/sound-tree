import numpy as np
from common import DIST_MODES

def split_array_linear_and_max(arr: np.ndarray, n_chunks: int) -> list[np.float64]:
    k, m = divmod(len(arr), n_chunks)
    return [np.max(arr[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]) for i in range(n_chunks)]

def split_array_exponential_and_max(data: np.ndarray, num_chunks: int, base: float = 1.15) -> list[np.float64]:
    """
    Divide `data` into `num_chunks` where chunk sizes grow exponentially based on `base`.
    Each chunk gets at least one element. Apply max to each chunk.
    
    Args:
        data (list): The list to divide.
        num_chunks (int): Number of chunks.
        base (float): The base of the exponential growth (e.g., 2.0 for doubling).
        
    Returns:
        List of maxima. (np.float64)
    """
    if num_chunks <= 0 or base <= 0:
        raise ValueError("num_chunks and base must be positive.")
    if num_chunks > len(data):
        raise ValueError("Number of chunks cannot exceed length of data.")
    
    # Generate exponential weights
    weights = [base ** i for i in range(num_chunks)]
    total_weight = sum(weights)
    
    # Calculate actual chunk sizes
    total_length = len(data)
    raw_sizes = [w / total_weight * total_length for w in weights]
    
    # Round sizes while preserving total length
    sizes = [max(1, int(round(s))) for s in raw_sizes]
    
    # Adjust for rounding errors
    size_diff = sum(sizes) - total_length
    while size_diff != 0:
        for i in range(len(sizes)):
            if size_diff == 0:
                break
            if size_diff > 0 and sizes[i] > 1:
                sizes[i] -= 1
                size_diff -= 1
            elif size_diff < 0:
                sizes[i] += 1
                size_diff += 1
    
    # Split data
    chunks = []
    idx = 0
    for size in sizes:
        chunks.append(np.max(data[idx : (idx + size)]))
        idx += size
        
    return chunks


def apply_color_scaling_array(array, colors):
    result = []
    for (element, color) in zip(array, colors):
        result.append((int(element * color[0]), int(element * color[1]), int(element * color[2])))
    return result

def rgb_to_hex(rgb):
    return '{:02x}{:02x}{:02x}'.format(*[int(x) for x in rgb])

def rgb_array_to_hex(array):
    hex_colors = []
    for element in array:
        hex_colors.append(rgb_to_hex(element))
    return hex_colors

# Main conversion function.
# Converts normalized array with 0 - 1 floats to a hex code list
def convert(arr: np.ndarray, n_chunks: int, distMode: str, normalized_rgbs: list = None):
    if normalized_rgbs is None:
        normalized_rgbs = [(0,0,255) for _ in range(n_chunks)]
    maxima = split_array_exponential_and_max(arr, n_chunks) if distMode == DIST_MODES.MUSIC \
        else split_array_exponential_and_max(arr, n_chunks, 1.2) if distMode == DIST_MODES.HUMAN \
        else split_array_linear_and_max(arr, n_chunks)
    rgbs = apply_color_scaling_array(maxima, normalized_rgbs)
    hex_colors = rgb_array_to_hex(rgbs)
    return hex_colors
