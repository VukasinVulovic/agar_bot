import math

def scale(val, src, dst):
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

def mag_vec(vec):
    return math.sqrt(vec[0]*vec[0] + vec[1] * vec[1])

def div_vec(vec1, vec2):
    return (vec1[0] / vec2[0], vec1[1] / vec2[1])

def mul_vec(vec1, vec2):
    return (vec1[0] * vec2[0], vec1[1] * vec2[1])

def sub_vec(vec1, vec2):
    return (vec1[0] - vec2[0], vec1[1] - vec2[1])

def add_vec(vec1, vec2):
    return (vec1[0] + vec2[0], vec1[1] + vec2[1])

def dis_vec(vec1, vec2):
    return abs(vec1[0] - vec2[0]) + abs(vec1[1] - vec2[1])

def norm_vec(vec):
    m = mag_vec(vec)
    
    if m > 0:
        return div_vec(vec, (m, m))

    return vec

def flatten_array(arr):
    flat_list = []
    
    for row in arr:
        flat_list += row
    
    return flat_list