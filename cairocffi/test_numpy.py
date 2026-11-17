import math

import numpy
import pytest

import cairocffi as cairo


def test_numpy():
    data = numpy.zeros((200, 200, 4), dtype=numpy.uint8)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200, data=data)
    cr = cairo.Context(surface)
    cr.set_source_rgb(1.0, 1.0, 1.0)
    cr.paint()
    cr.arc(100, 100, 80, 0, 2*math.pi)
    cr.set_line_width(3)
    cr.set_source_rgb(1.0, 0.0, 0.0)
    cr.stroke()


def test_numpy_uint32_length_is_counted_in_bytes():
    # 16 uint32 elements are 64 bytes: the size must be computed from
    # nbytes, not from the number of elements (which would give 16).
    data = numpy.zeros((4, 4), dtype=numpy.uint32)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4, data=data)
    assert surface.get_stride() == 16
    assert surface.get_width() == 4
    assert surface.get_height() == 4


def test_numpy_buffer_is_zero_copy():
    data = numpy.zeros((4, 16), dtype=numpy.uint8)
    surface = cairo.ImageSurface(cairo.FORMAT_A8, 16, 4, data=data)
    surface.get_data()[0:1] = b'\x7f'
    assert data[0, 0] == 0x7F
    cr = cairo.Context(surface)
    cr.paint()
    assert data.all()  # cairo drew straight into the numpy storage


def test_numpy_non_contiguous_array_rejected():
    data = numpy.zeros((8, 8), dtype=numpy.uint32)[::2, ::2]
    assert not data.flags.c_contiguous
    with pytest.raises(ValueError):
        cairo.ImageSurface(cairo.FORMAT_ARGB32, 2, 2, data=data)


def test_numpy_readonly_array_rejected():
    data = numpy.zeros((4, 4), dtype=numpy.uint32)
    data.setflags(write=False)
    with pytest.raises(ValueError):
        cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4, data=data)
