from eso_agent.fonts import DEJAVU, DEJAVU_BOLD, GLYPHS
from eso_agent.pdfutil import render_onepager_pdf, render_ts_pdf


def test_dejavu_fonts_shipped():
    assert DEJAVU.is_file()
    assert DEJAVU_BOLD.is_file()
    assert "ąčęėįšųūž" in GLYPHS


def test_ts_and_onepager_pdf_embed_dejavu():
    ts = render_ts_pdf("Prijungimo sąlygos", ["Sąlygos išduotos.", GLYPHS])
    one = render_onepager_pdf()
    for blob in (ts, one):
        assert blob[:4] == b"%PDF"
        assert b"DejaVu" in blob
