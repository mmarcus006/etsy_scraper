"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_html():
    """Provide sample HTML for testing parsers."""
    return """
    <html>
        <body>
            <div class="product">
                <h2>Sample Product</h2>
                <span class="price">$29.99</span>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary data directory for tests."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir