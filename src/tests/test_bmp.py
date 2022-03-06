from src.EA_Image.Bmp import BmpHeader, BmpImg


def test_bmp_header_init():
    bmp_header = BmpHeader(10, 100)

    assert bmp_header.bmp_magic == b"BM"
    assert bmp_header.bmp_size == 10
    assert bmp_header.offset_im_data == 100


def test_bmp_img_init():
    bmp_image = BmpImg(10, 20, 8, b"imgdata", b"palette")

    assert bmp_image.bmp_width == 10
    assert bmp_image.bmp_height == 20
    assert bmp_image.bmp_bpp == 8
    assert bmp_image.bmp_data == b"imgdata"
    assert bmp_image.bmp_palette == b"palette"
