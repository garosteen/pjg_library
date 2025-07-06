# pjg_library

A Python library for generative art utilities, designed to work with vpype and vsketch.

## Installation

This library is designed to be installed in development mode alongside your generative art tools.

### Prerequisites

- Python 3.12 (required for vpype/vsketch compatibility)
- pipx for managing Python applications

### Setup

1. **Install Python 3.12** (if using pyenv):
   ```bash
   pyenv install 3.12.11
   ```

2. **Install vpype and vsketch with pipx**:
  To get the path to the correct Python version, run:
  ```bash
  pyenv prefix 3.12
  ```
  Then, install vpype and vsketch with the correct version:
  ```bash
  pipx install --python ~/.pyenv/versions/3.12.11/bin/python vpype
  pipx install --python ~/.pyenv/versions/3.12.11/bin/python vsketch
  ```

3. **Install this library in development mode**:
   ```bash
   cd /path/to/pjg_library
   pipx runpip vsketch install -e .
   ```

### Adding Dependencies

If you need additional Python packages:

```bash
# Add packages to the vsketch environment
pipx inject vsketch package_name

# For example, to add the noise library:
pipx inject vsketch noise
```

## Usage

After installation, you can import the library modules in your Python scripts:

```python
from pjg_library import SketchBorder
from pjg_library import utilityfunctions as uf
from pjg_library import bezierUtilities
# ... and other modules
```

## Library Structure

```
pjg_library/
├── setup.py              # Package configuration
├── README.md             # This file
├── pjg_library/          # Main package directory
│   ├── __init__.py       # Package initialization
│   ├── SketchBorder.py   # Border utilities for sketches
│   ├── utilityfunctions.py # General utility functions
│   ├── bezierUtilities.py  # Bezier curve utilities
│   ├── HeightMap.py      # Height map utilities
│   ├── IsoLayer.py       # Isometric layer utilities
│   ├── Path.py           # Path utilities
│   ├── SegmentDisplay.py # Segment display utilities
│   ├── SegmentLines.py   # Segment line utilities
│   ├── SegmentCodes.py   # Segment code utilities
│   ├── diffraction.py    # Diffraction utilities
│   ├── movingBezier.py   # Moving Bezier utilities
│   ├── spirograph.py     # Spirograph utilities
│   └── boilerplate.py    # Boilerplate code
```

## Development Workflow

### Making Changes

Since the library is installed in development mode (`-e` flag), any changes you make to the source files will be immediately available in your scripts without reinstalling.

### Testing Changes

```bash
# Test that the library can be imported
pipx run vsketch python -c "import pjg_library; print('Import successful!')"

# Run a vsketch project that uses the library
vsketch run path/to/your/sketch.py
```

### Adding New Modules

1. Create your new `.py` file in the `pjg_library/` directory
2. No reinstallation needed - it will be automatically available for import

### Troubleshooting

**"ModuleNotFoundError: No module named 'pjg_library'"**
- Make sure you installed the library with `pipx runpip vsketch install -e .`
- Verify you're in the correct directory when running the install command
- Check that your `setup.py` is properly configured

**"No module named 'specific_module'"**
- Ensure the module file exists in the `pjg_library/` directory
- Check that the module name matches the filename (case-sensitive)
- Verify there are no syntax errors in the module

**Python version conflicts**
- Ensure you're using Python 3.12 for all vpype/vsketch operations
- Check your pyenv configuration if using pyenv

## Contributing

When adding new utilities:

1. Place new modules in the `pjg_library/` directory
2. Follow existing naming conventions
3. Add appropriate imports to `__init__.py` if needed
4. Update this README if adding significant new functionality

## License

[Include your license information here]
