"""
RapidP pywebview runtime bridge.

This backend re-exports the standard RapidP tkinter runtime API and provides
pywebview helpers for serverless mode execution.
"""

from rp_runtime.gui import *  # noqa: F401,F403

try:
    import webview
except ImportError:
    webview = None


def run_web_app(title="RapidP App", html=None, width=1024, height=768):
    """Run a simple pywebview window in serverless mode (http_server=False)."""
    if webview is None:
        raise RuntimeError(
            "pywebview is not installed. Install with: pip install pywebview"
        )

    content = html or (
        "<html><body style='font-family:sans-serif'>"
        "<h3>RapidP pywebview backend</h3>"
        "<p>Running in serverless mode.</p>"
        "</body></html>"
    )
    webview.create_window(title, html=content, width=width, height=height)
    webview.start(http_server=False)

