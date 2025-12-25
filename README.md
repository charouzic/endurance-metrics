# Endurance Metrics

A Streamlit dashboard for analyzing Strava training data with intelligent caching and rate limit protection.

## Features

- **📊 Overview Dashboard**: KPIs, weekly trends, rolling averages, and personal bests
- **📅 Weekly Analysis**: Detailed weekly breakdowns with optional sport stacking
- **📈 Yearly Statistics**: Year-over-year comparisons and long-term trends
- **📋 Raw Data Export**: Explore and download your activity data as CSV

### Key Capabilities

- **Smart Caching**: Two-tier caching (memory + local parquet file) minimizes API calls
- **Rate Limit Protection**: Automatically falls back to cached data if Strava rate limits are hit
- **Interactive Charts**: Built with Plotly for zoom, pan, and hover interactions
- **Flexible Filtering**: Filter by date range and sport type across all pages
- **Data Persistence**: Local parquet cache survives app restarts

## Prerequisites

- Python 3.8 or higher
- Strava API credentials (Client ID, Client Secret, Refresh Token)

## Setup

### 1. Get Strava API Credentials

1. Go to https://www.strava.com/settings/api
2. Create an application (if you haven't already)
3. Note your **Client ID** and **Client Secret**
4. Generate a **Refresh Token**:
   - You can use the OAuth playground or follow Strava's documentation
   - See: https://developers.strava.com/docs/getting-started/#oauth

### 2. Install Dependencies

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials

Copy the example secrets file and fill in your credentials:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
STRAVA_CLIENT_ID = "your_client_id_here"
STRAVA_CLIENT_SECRET = "your_client_secret_here"
STRAVA_REFRESH_TOKEN = "your_refresh_token_here"
```

**Important**: Never commit `.streamlit/secrets.toml` to version control (it's already in `.gitignore`)

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage

### First Run

On first run, the app will:
1. Validate your Strava credentials
2. Fetch all your historical activities from Strava
3. Cache the data locally in `data/strava_activities.parquet`

This initial fetch may take a moment depending on how many activities you have.

### Subsequent Runs

On subsequent runs, the app will:
- Load data from the local cache (instant)
- Display a message: "📦 Loaded X activities from cache"

### Refreshing Data

To fetch the latest activities from Strava:
1. Click **"🔄 Refresh from Strava"** in the sidebar
2. The app will clear the cache and fetch fresh data
3. New data will be cached for future sessions

### Filtering

Use the sidebar filters to narrow down your data:
- **Date Range**: Select start and end dates (defaults to last 12 months)
- **Sport Types**: Select one or more sports (leave empty for all)

Filters apply across all pages in the app.

## Pages

### 📊 Overview
- Key metrics: total distance, elevation, duration, and activity count
- Weekly distance chart with 4-week rolling average
- Weekly elevation gain chart
- Personal bests: best week and best month

### 📅 Weekly View
- Detailed weekly distance chart
- Toggle to stack by sport type
- Weekly statistics table
- Summary averages (distance, elevation, activities per week)

### 📈 Yearly Stats
- Yearly summary table with year-over-year percentage changes
- Bar charts for distance and elevation by year
- Sport breakdown by year (stacked)
- YoY insights for latest year

### 📋 Raw Data
- Interactive data table with column selector
- Download full data as CSV
- Download filtered view as CSV
- Data summary statistics
- Sport type distribution

## Rate Limits

Strava enforces the following rate limits:
- **100 read requests per 15 minutes**
- **1,000 read requests per day**

The app respects these limits by:
- Using `per_page=200` for efficient pagination
- Caching data locally to minimize API calls
- Adding 0.5s delays between paginated requests
- Detecting HTTP 429 responses and falling back to cache
- Showing clear error messages when rate limited

If you see a rate limit error:
1. The app will automatically try to load cached data
2. Wait 15 minutes before refreshing from Strava
3. Use the cached data in the meantime

## Project Structure

```
endurance-metrics/
├── app.py                          # Main entry point
├── endurance_metrics/              # Core application modules
│   ├── __init__.py
│   ├── config.py                   # Configuration and secrets
│   ├── strava_client.py            # API client with rate limiting
│   ├── data_loader.py              # ETL and caching logic
│   ├── weekly_stats.py             # Weekly aggregations
│   ├── yearly_stats.py             # Yearly aggregations
│   └── ui_components.py            # Reusable UI components
├── pages/                          # Streamlit multipage app
│   ├── 1_📊_overview.py
│   ├── 2_📅_weekly_view.py
│   ├── 3_📈_yearly_stats.py
│   └── 4_📋_raw_data.py
├── .streamlit/
│   ├── secrets.toml                # Your credentials (gitignored)
│   └── secrets.toml.example        # Template
├── data/                           # Cache directory (gitignored)
│   └── strava_activities.parquet   # Cached activities
├── requirements.txt
└── README.md
```

## Troubleshooting

### "Missing required Strava API credentials"

- Check that `.streamlit/secrets.toml` exists and contains all three credentials
- Ensure the file is in TOML format with quotes around values
- Restart the Streamlit app after editing secrets.toml

### "Invalid Strava credentials"

- Verify your Client ID and Client Secret are correct
- Ensure your Refresh Token is valid and hasn't expired
- Generate a new Refresh Token if needed

### "Rate limit exceeded"

- Wait 15 minutes before trying to refresh from Strava
- The app should automatically fall back to cached data
- Check `data/strava_activities.parquet` exists

### "No cached data available"

- This happens if rate limited on first run (rare)
- Wait 15 minutes and try again
- Ensure the `data/` directory is writable

### Charts not displaying

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check for JavaScript errors in browser console
- Try clearing browser cache

## Data Privacy

- All data is stored locally on your machine
- The app does not send data to any third-party services
- Credentials are stored in `.streamlit/secrets.toml` (gitignored)
- Access tokens are kept in memory only and never persisted

## Development

### Adding New Features

The codebase is modular and easy to extend:

- **New metrics**: Add functions to `weekly_stats.py` or `yearly_stats.py`
- **New pages**: Create a new file in `pages/` (e.g., `5_new_page.py`)
- **New charts**: Use Plotly in any page module
- **New filters**: Update `display_sidebar()` in `ui_components.py`

### Testing

Manual testing checklist:
- [ ] App starts without errors
- [ ] Credentials validation works
- [ ] Data fetches from API successfully
- [ ] Data caches to parquet file
- [ ] Refresh button clears cache and refetches
- [ ] All pages render correctly
- [ ] Filters work (date range, sport type)
- [ ] Charts are interactive
- [ ] CSV export works
- [ ] Rate limit error handling works

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Data from [Strava API](https://developers.strava.com/)
- Charts powered by [Plotly](https://plotly.com/)

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Strava API documentation: https://developers.strava.com/
3. Check Streamlit documentation: https://docs.streamlit.io/

Happy training! 🏃‍♂️🚴‍♀️⛰️