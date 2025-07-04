# NetTrends - Trending Keywords & Domains Dashboard

A pure Python Streamlit application that helps no-code makers and small startups discover trending keywords and domains online by aggregating data from Google Trends, Reddit, and Hacker News.

## Features

🔍 **Multi-Source Data Collection**
- Google Trends: Fetch current trending searches
- Reddit: Scrape trending posts from popular subreddits
- Hacker News: Extract trending stories from front page

📊 **Interactive Dashboard**
- Clean, mobile-friendly interface with tabs for each data source
- Real-time data visualization with word clouds and bar charts
- Keyword trend analysis with historical data
- Domain extraction from URLs

🎯 **Keyword Analysis**
- Search for specific keyword trends over time
- Related queries and regional interest data
- Multiple time range options (7 days to 5 years)

📱 **User-Friendly Features**
- Responsive design that works on mobile and desktop
- Data filtering and export options
- Automatic data caching for better performance
- No external API keys or authentication required

## Installation

1. **Clone or download the project:**
   ```bash
   cd NetTrends
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run main.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## Usage

### Main Dashboard
- **Overview Tab**: See aggregated trending keywords from all sources with word cloud visualization
- **Google Trends Tab**: Current trending searches with rankings
- **Reddit Tab**: Popular posts and extracted keywords
- **Hacker News Tab**: Front page stories and common domains
- **Keyword Search Tab**: Analyze specific keywords over time

### Data Sources
- **Google Trends**: Real-time trending searches in the US
- **Reddit**: Posts from r/popular, r/all, r/news, and r/technology
- **Hacker News**: Front page stories with domain extraction

### Filtering Options
- Select specific data sources
- Choose content types (keywords, post titles, domains)
- Filter by time ranges for trend analysis

## Technical Details

### Libraries Used
- **Streamlit**: Web app framework
- **pytrends**: Google Trends API
- **requests**: HTTP requests for web scraping
- **BeautifulSoup**: HTML parsing
- **pandas**: Data manipulation
- **WordCloud**: Text visualization
- **matplotlib**: Plotting and charts

### Data Processing
- Automatic keyword extraction from post titles
- Domain extraction from URLs
- Stop word filtering for better keyword quality
- Data aggregation and ranking
- 1-hour caching for improved performance

### Error Handling
- Graceful handling of network errors
- Fallback mechanisms for data sources
- User-friendly error messages
- Retry logic for failed requests

## Customization

### Adding New Data Sources
1. Create a new fetch function following the pattern:
   ```python
   @st.cache_data(ttl=3600)
   def fetch_new_source():
       # Implementation here
       return pd.DataFrame(data)
   ```

2. Add the source to the aggregation function
3. Create a new tab in the interface

### Modifying Scraping Logic
- Update the BeautifulSoup selectors in fetch functions
- Adjust the keyword extraction rules
- Modify the domain extraction logic

### UI Customization
- Edit the CSS styles in the `st.markdown()` section
- Modify the color schemes and layouts
- Add new visualization types

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.7+)

2. **Network Issues**
   - Some sites may block requests; the app includes proper headers and delays
   - Check internet connection and firewall settings

3. **Empty Data**
   - Reddit and Hacker News scraping may fail due to site changes
   - Google Trends may have rate limits; use the refresh button sparingly

4. **Performance Issues**
   - Data is cached for 1 hour to reduce API calls
   - Use the refresh button only when necessary

### Rate Limiting
- Google Trends has rate limits; avoid excessive requests
- Reddit and Hacker News scraping includes delays between requests
- Data is cached to minimize API calls

## Future Enhancements

- Add more data sources (Twitter, LinkedIn, etc.)
- Implement sentiment analysis
- Add trend prediction algorithms
- Create export formats (PDF, Excel)
- Add user authentication and saved searches
- Implement real-time notifications for trending keywords

## License

This project is for educational and personal use. Please respect the terms of service of the data sources being accessed.

## Contributing

Feel free to submit issues and enhancement requests. This is a learning project designed to help small startups and no-code makers stay ahead of online trends.
