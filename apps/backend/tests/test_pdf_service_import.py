"""
AWD-H-109 regression: pdf_service.py must catch OSError from WeasyPrint
when native libs (libpango, libcairo, libharfbuzz) are absent on macOS.
"""
import sys
import types

import pytest


class TestWeasyPrintOSErrorFallbackH109:
    """pdf_service catches OSError in addition to ImportError on weasyprint absence."""

    def test_module_loads_when_weasyprint_raises_oserror(self):
        """If weasyprint raises OSError (e.g. libpango missing on macOS), module loads with WEASYPRINT_AVAILABLE=False."""
        fake_wp = types.ModuleType("weasyprint")

        def _raise_oserror(name):
            raise OSError("cannot load library 'libpango-1.0-0'")

        fake_wp.__getattr__ = _raise_oserror

        pdf_key = "apps.backend.services.pdf_service"
        wp_key = "weasyprint"

        saved_pdf = sys.modules.pop(pdf_key, None)
        saved_wp = sys.modules.pop(wp_key, None)
        try:
            sys.modules[wp_key] = fake_wp
            import apps.backend.services.pdf_service as pdf_mod  # noqa: PLC0415

            assert pdf_mod.WEASYPRINT_AVAILABLE is False
        finally:
            if saved_wp is not None:
                sys.modules[wp_key] = saved_wp
            else:
                sys.modules.pop(wp_key, None)
            if saved_pdf is not None:
                sys.modules[pdf_key] = saved_pdf
            else:
                sys.modules.pop(pdf_key, None)

    def test_module_loads_when_weasyprint_raises_importerror(self):
        """If weasyprint raises ImportError (module not installed), module loads with WEASYPRINT_AVAILABLE=False."""
        pdf_key = "apps.backend.services.pdf_service"
        wp_key = "weasyprint"

        saved_pdf = sys.modules.pop(pdf_key, None)
        saved_wp = sys.modules.pop(wp_key, None)
        try:
            # Setting sys.modules[key] = None causes ImportError on `import key`
            sys.modules[wp_key] = None  # type: ignore[assignment]
            import apps.backend.services.pdf_service as pdf_mod  # noqa: PLC0415

            assert pdf_mod.WEASYPRINT_AVAILABLE is False
        finally:
            if saved_wp is not None:
                sys.modules[wp_key] = saved_wp
            else:
                sys.modules.pop(wp_key, None)
            if saved_pdf is not None:
                sys.modules[pdf_key] = saved_pdf
            else:
                sys.modules.pop(pdf_key, None)
