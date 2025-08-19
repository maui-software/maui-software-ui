# MAUI Audio Data Loader

A professional Plotly Dash application for loading and analyzing acoustic ecology data using the MAUI software library.

## Features

- **Multi-page Application**: Built with Dash Pages for seamless navigation
- **Professional UI**: Styled with dash-mantine-components for a modern look
- **Audio Data Loading**: Integrate with maui-software for acoustic ecology analysis
- **Configurable Parameters**: Support for YAML configuration files and custom settings
- **Data Visualization**: Display loaded data in interactive tables with summary statistics

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8050`

## Usage

### Welcome Page
- Introduction to the MAUI Audio Data Loader
- Overview of key features
- Quick navigation to data loading functionality

### Load Audio Data Page
Configure and load your acoustic ecology data with the following parameters:

#### Required Parameters:
- **Audio Directory Path**: Path to the directory containing your audio files
- **YAML Configuration File Path**: Path to your YAML configuration file for filename formatting
- **Configuration Pattern Name**: Name of the pattern to use from your YAML file

#### Optional Parameters:
- **Timestamp Function**: Custom Python function for extracting timestamps from filenames
- **Store Duration**: Enable/disable audio duration calculation
- **Sample Percentage**: Specify what percentage of the data to load (1-100%)

#### Example YAML Configuration:
```yaml
patterns:
  default_pattern:
    format: "{site}_{date}_{time}.wav"
    date_format: "%Y%m%d"
    time_format: "%H%M%S"

  custom_pattern:
    format: "{location}_{timestamp}.wav"
    date_format: "%Y-%m-%d_%H-%M-%S"
```

## MAUI Software Integration

This application integrates with the `maui-software` library for acoustic ecology data processing. The main function used is:

```python
import maui.io

df = maui.io.get_audio_info(
    audio_directory_path,
    format_file_path="config.yaml",
    pattern_name="default_pattern",
    date_time_func=custom_timestamp_function,  # optional
    store_duration=True,
    perc_sample=1.0  # 100%
)
```

## Project Structure

```
maui-audio-loader/
├── app.py                 # Main application file
├── pages/
│   ├── __init__.py
│   └── load_data.py      # Load audio data page
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Dependencies

- **dash**: Web application framework
- **dash-mantine-components**: Modern UI components
- **maui-software**: Acoustic ecology data processing
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations

## Running the Application

1. **Development Mode**:
   ```bash
   python app.py
   ```
   The app will run on `http://localhost:8050` with hot reloading enabled.

2. **Production Mode**:
   For production deployment, consider using a WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn app:server
   ```

## Customization

### Styling
The application uses a custom color theme based on the MAUI software branding:
- **Primary Color**: Teal (#319795)
- **Secondary Color**: Blue (#3182ce)
- **Background**: Light gray (#f8fafc)

### Adding New Pages
To add new pages to the application:

1. Create a new Python file in the `pages/` directory
2. Use `dash.register_page()` to register the page
3. Import the page in `app.py`

Example:
```python
import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path="/new-page", name="New Page")

def layout():
    return dmc.Container([
        dmc.Title("New Page"),
        # Your page content here
    ])
```

## Troubleshooting

### Common Issues

1. **Import Error for dash-mantine-components**:
   - Ensure you have the correct version installed: `pip install dash-mantine-components>=0.12.1`
   - Check that React version is set correctly in the code

2. **MAUI Software Not Found**:
   - Install maui-software: `pip install maui-software`
   - Verify the installation: `python -c "import maui.io"`

3. **YAML Configuration Errors**:
   - Ensure your YAML file is properly formatted
   - Check that the pattern name exists in your configuration file

### Getting Help

- MAUI Software Documentation: https://maui-software.github.io/maui-software/
- Dash Documentation: https://dash.plotly.com/
- Dash Mantine Components: https://www.dash-mantine-components.com/

## License

This project is open source and available under the MIT License.
