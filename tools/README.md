# Tools Directory Structure

This directory contains all the tools available in the framework. Each tool is a self-contained module with its own directory, configuration, and documentation.

## Directory Structure

```
tools/
├── __init__.py                 # Exports all tools and provides unified interface
├── common/                     # Shared utilities and helpers
│   ├── __init__.py
│   ├── python/                # Python-specific shared utilities
│   ├── typescript/            # TypeScript-specific shared utilities
│   └── validation/            # Shared validation utilities
├── config/                    # Tool configuration files
│   ├── tool_types.ts         # TypeScript type definitions
│   ├── tool_schema.json      # JSON schema for tool configuration
│   └── defaults.json         # Default configuration values
└── modules/                  # Individual tool modules
    ├── sales_data_processor/ # Example Python tool
    │   ├── __init__.py
    │   ├── main.py          # Main tool implementation
    │   ├── config.json      # Tool-specific configuration
    │   ├── test_main.py     # Tests
    │   └── README.md        # Tool-specific documentation
    ├── weather_api/         # Example TypeScript tool
    │   ├── index.ts         # Main tool implementation
    │   ├── config.json      # Tool-specific configuration
    │   ├── types.ts         # Type definitions
    │   ├── test.ts          # Tests
    │   └── README.md        # Tool-specific documentation
    └── react_component/     # Example mixed Python/TypeScript tool
        ├── main.py          # Python interface
        ├── generator.ts     # TypeScript implementation
        ├── config.json      # Tool-specific configuration
        ├── test_main.py     # Python tests
        ├── test.ts          # TypeScript tests
        └── README.md        # Tool-specific documentation
```

## Tool Module Structure

Each tool module should follow these conventions:

### Python Tools
```
tool_name/
├── __init__.py              # Exports the tool interface
├── main.py                  # Main implementation
├── config.json             # Tool configuration
├── test_main.py           # Tests
└── README.md              # Documentation
```

### TypeScript Tools
```
tool_name/
├── index.ts               # Main implementation
├── types.ts              # Type definitions
├── config.json           # Tool configuration
├── test.ts              # Tests
└── README.md            # Documentation
```

## Tool Configuration

Each tool's `config.json` should include:

```json
{
    "name": "tool_name",
    "version": "1.0.0",
    "language": "python|typescript|mixed",
    "description": "Tool description",
    "author": "Author name",
    "dependencies": {
        "python": {
            "packages": ["package==version"]
        },
        "node": {
            "packages": ["package@version"]
        }
    },
    "inputs": [
        {
            "name": "input_name",
            "type": "string|number|etc",
            "description": "Input description",
            "required": true|false
        }
    ],
    "outputs": [
        {
            "name": "output_name",
            "type": "type",
            "description": "Output description"
        }
    ],
    "metrics": {
        "average_execution_time": "0.0s",
        "error_rate": "0.0%",
        "usage_count": 0
    }
}
```

## Integration

The main `__init__.py` provides a unified interface to all tools:

```python
from tools.modules.sales_data_processor import process_sales_data
from tools.modules.weather_api import get_weather
from tools.modules.react_component import generate_component

# Export all tools
__all__ = [
    'process_sales_data',
    'get_weather',
    'generate_component'
]
```

## Adding New Tools

1. Create a new directory under `modules/` with your tool name
2. Add the required files based on your tool's language
3. Implement the tool following the structure above
4. Add tool configuration in `config.json`
5. Write tests
6. Create tool-specific README.md
7. Update the main `__init__.py` to export your tool
8. The framework will automatically update `README_AGENT_TOOLS.md`

## Development Guidelines

1. Each tool should be self-contained
2. Use shared utilities from `common/` when possible
3. Always include tests and documentation
4. Keep tool-specific configuration in the tool's directory
5. Use type hints in Python and strict types in TypeScript
6. Follow the language-specific style guides
7. Update the tool's metrics in its config.json

## Testing

Run tests for all tools:
```bash
# Python tests
pytest tools/modules/*/test_*.py

# TypeScript tests
npm test
```

## Documentation

Each tool's README.md should include:
1. Tool description
2. Installation
3. Usage examples
4. API reference
5. Configuration options
6. Dependencies
7. Testing instructions
8. Troubleshooting 