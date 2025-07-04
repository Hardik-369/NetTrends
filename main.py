import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import time
from collections import Counter
from urllib.parse import urlparse

# Initialize the Streamlit app
st.set_page_config(
    page_title="NetTrends - Trending Keywords & Domains",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "NetTrends helps no-code makers and small startups discover trending keywords and domains online."
    }
)

# Custom CSS for better mobile experience
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTab > div {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">🌐 NetTrends Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Discover trending keywords and domains from Google Trends, Reddit, and Hacker News**")

# Data fetching functions with error handling and caching

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_google_trends():
    """Fetch trending searches from Google Trends using actual API"""
    try:
        # Create pytrends object with minimal configuration to avoid errors
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Method 1: Try trending searches for different countries
        country_codes = ['united_states', 'p1', 'p4', 'p6']  # US, World, UK, Canada
        
        for country in country_codes:
            try:
                if country == 'united_states':
                    trending_searches = pytrends.trending_searches(pn=country)
                else:
                    trending_searches = pytrends.trending_searches(pn=country)
                
                if trending_searches is not None and not trending_searches.empty:
                    # Extract the first column which contains the trending terms
                    if len(trending_searches.columns) > 0:
                        keywords = trending_searches.iloc[:, 0].dropna().tolist()
                        if keywords:
                            df = pd.DataFrame(keywords, columns=['keyword'])
                            df['source'] = f'Google Trends ({country.replace("_", " ").title()})'
                            df['rank'] = range(1, len(df) + 1)
                            return df
            except Exception as country_error:
                continue
        
        # Method 2: Try without country parameter
        try:
            trending_searches = pytrends.trending_searches()
            if trending_searches is not None and not trending_searches.empty:
                keywords = trending_searches.iloc[:, 0].dropna().tolist()
                if keywords:
                    df = pd.DataFrame(keywords, columns=['keyword'])
                    df['source'] = 'Google Trends (Global)'
                    df['rank'] = range(1, len(df) + 1)
                    return df
        except Exception as global_error:
            pass
        
        # Method 3: Get trending keywords using interest over time for popular terms
        try:
            # Use a set of popular keywords to get current trending data
            popular_keywords = [
                'AI', 'Bitcoin', 'Tesla', 'iPhone', 'Netflix', 'Amazon', 'Google',
                'Facebook', 'Twitter', 'TikTok', 'YouTube', 'Instagram', 'WhatsApp',
                'COVID', 'Ukraine', 'Climate', 'NFT', 'Crypto', 'Stock', 'Weather'
            ]
            
            # Get interest data for these keywords
            trending_data = []
            for keyword in popular_keywords[:10]:  # Limit to avoid rate limiting
                try:
                    pytrends.build_payload([keyword], cat=0, timeframe='now 1-d')
                    interest = pytrends.interest_over_time()
                    if not interest.empty and keyword in interest.columns:
                        avg_interest = interest[keyword].mean()
                        if avg_interest > 0:
                            trending_data.append({'keyword': keyword, 'interest': avg_interest})
                    time.sleep(0.1)  # Small delay to avoid rate limiting
                except:
                    continue
            
            if trending_data:
                # Sort by interest level
                trending_df = pd.DataFrame(trending_data)
                trending_df = trending_df.sort_values('interest', ascending=False)
                df = pd.DataFrame(trending_df['keyword'].tolist(), columns=['keyword'])
                df['source'] = 'Google Trends (Current Interest)'
                df['rank'] = range(1, len(df) + 1)
                return df
        except Exception as interest_error:
            pass
        
        # If all methods fail, return empty DataFrame
        st.error("Unable to fetch Google Trends data. This may be due to API rate limiting or connectivity issues.")
        return pd.DataFrame(columns=['keyword', 'source', 'rank'])
        
    except Exception as e:
        st.error(f"Error connecting to Google Trends: {str(e)}")
        return pd.DataFrame(columns=['keyword', 'source', 'rank'])

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_reddit_trends():
    """Fetch trending posts from Reddit's front page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Try multiple subreddits for better data
        subreddits = ['popular', 'all', 'news', 'technology']
        all_titles = []
        
        for subreddit in subreddits:
            try:
                url = f'https://www.reddit.com/r/{subreddit}/'
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try different selectors for post titles
                titles = soup.find_all('h3', class_='_eYtD2XCVieq6emjKBH3m')
                if not titles:
                    titles = soup.find_all('h3')
                
                for title in titles[:10]:  # Limit to 10 per subreddit
                    text = title.get_text(strip=True)
                    if text and len(text) > 10:  # Filter out short/empty titles
                        all_titles.append(text)
                        
                time.sleep(0.5)  # Be respectful with requests
            except Exception as e:
                continue
        
        df = pd.DataFrame(all_titles[:30], columns=['keyword'])  # Top 30 posts
        df['source'] = 'Reddit'
        df['rank'] = range(1, len(df) + 1)
        return df
    except Exception as e:
        st.error(f"Error fetching Reddit data: {str(e)}")
        return pd.DataFrame(columns=['keyword', 'source', 'rank'])

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_hackernews_trends():
    """Fetch trending stories from Hacker News front page"""
    try:
        url = 'https://news.ycombinator.com/'
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find story titles and URLs
        titles = []
        urls = []
        
        # Look for story links
        story_links = soup.find_all('span', class_='titleline')
        for link in story_links:
            a_tag = link.find('a')
            if a_tag:
                title = a_tag.get_text(strip=True)
                url = a_tag.get('href', '')
                if title and len(title) > 10:
                    titles.append(title)
                    urls.append(url)
        
        df = pd.DataFrame({
            'keyword': titles[:30],  # Top 30 stories
            'url': urls[:30]
        })
        df['source'] = 'Hacker News'
        df['rank'] = range(1, len(df) + 1)
        return df
    except Exception as e:
        st.error(f"Error fetching Hacker News data: {str(e)}")
        return pd.DataFrame(columns=['keyword', 'source', 'rank', 'url'])

def extract_keywords_from_text(text):
    """Extract meaningful keywords from text"""
    # Remove common words and extract meaningful terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    # Extract words (2+ characters, alphanumeric)
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords

def extract_domains_from_urls(urls):
    """Extract domains from URLs"""
    domains = []
    for url in urls:
        try:
            if url.startswith('http'):
                domain = urlparse(url).netloc
                if domain:
                    domains.append(domain)
        except:
            continue
    return domains

def clean_and_aggregate_data(gt_data, reddit_data, hn_data):
    """Clean and aggregate data from all sources"""
    all_data = []
    
    # Process Google Trends data
    for _, row in gt_data.iterrows():
        all_data.append({
            'keyword': row['keyword'],
            'source': 'Google Trends',
            'rank': row['rank'],
            'type': 'keyword'
        })
    
    # Process Reddit data
    reddit_keywords = []
    for _, row in reddit_data.iterrows():
        keywords = extract_keywords_from_text(row['keyword'])
        reddit_keywords.extend(keywords)
        all_data.append({
            'keyword': row['keyword'][:100],  # Truncate long titles
            'source': 'Reddit',
            'rank': row['rank'],
            'type': 'post_title'
        })
    
    # Process Hacker News data
    hn_keywords = []
    hn_domains = []
    for _, row in hn_data.iterrows():
        keywords = extract_keywords_from_text(row['keyword'])
        hn_keywords.extend(keywords)
        all_data.append({
            'keyword': row['keyword'][:100],  # Truncate long titles
            'source': 'Hacker News',
            'rank': row['rank'],
            'type': 'post_title'
        })
        
        # Extract domains if URL available
        if 'url' in row and pd.notna(row['url']):
            domains = extract_domains_from_urls([row['url']])
            hn_domains.extend(domains)
    
    # Add extracted keywords
    keyword_counts = Counter(reddit_keywords + hn_keywords)
    for keyword, count in keyword_counts.most_common(20):
        all_data.append({
            'keyword': keyword,
            'source': 'Extracted',
            'rank': count,
            'type': 'extracted_keyword'
        })
    
    # Add domains
    domain_counts = Counter(hn_domains)
    for domain, count in domain_counts.most_common(10):
        all_data.append({
            'keyword': domain,
            'source': 'Domains',
            'rank': count,
            'type': 'domain'
        })
    
    return pd.DataFrame(all_data)

# Sidebar controls
st.sidebar.header("🔧 Controls")
refresh_data = st.sidebar.button("🔄 Refresh Data", help="Fetch latest trending data")
if refresh_data:
    st.cache_data.clear()
    st.rerun()

# Main content area
with st.spinner("Fetching trending data..."):
    # Fetch data from all sources
    gt_data = fetch_google_trends()
    reddit_data = fetch_reddit_trends()
    hn_data = fetch_hackernews_trends()
    
    # Aggregate and clean data
    aggregated_data = clean_and_aggregate_data(gt_data, reddit_data, hn_data)

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Google Trends", len(gt_data))
with col2:
    st.metric("Reddit Posts", len(reddit_data))
with col3:
    st.metric("Hacker News", len(hn_data))
with col4:
    st.metric("Total Keywords", len(aggregated_data))

# Tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🔍 Google Trends", "📱 Reddit", "💻 Hacker News", "🎯 Keyword Search"])

with tab1:
    st.header("📊 Trending Keywords Overview")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        selected_sources = st.multiselect(
            "Select data sources:",
            options=aggregated_data['source'].unique(),
            default=aggregated_data['source'].unique()
        )
    with col2:
        selected_types = st.multiselect(
            "Select content types:",
            options=aggregated_data['type'].unique(),
            default=aggregated_data['type'].unique()
        )
    
    # Filter data
    filtered_data = aggregated_data[
        (aggregated_data['source'].isin(selected_sources)) &
        (aggregated_data['type'].isin(selected_types))
    ]
    
    if not filtered_data.empty:
        # Word cloud
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("☁️ Trending Keywords Word Cloud")
            try:
                text = ' '.join(filtered_data['keyword'].astype(str))
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='viridis',
                    max_words=100
                ).generate(text)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error generating word cloud: {str(e)}")
        
        with col2:
            st.subheader("📈 Top Keywords by Source")
            source_counts = filtered_data['source'].value_counts()
            st.bar_chart(source_counts)
        
        # Top keywords table
        st.subheader("🔥 Top Trending Keywords")
        top_keywords = filtered_data.head(20)
        st.dataframe(
            top_keywords,
            use_container_width=True,
            hide_index=True
        )
        
        # Download option
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="nettrends_data.csv",
            mime="text/csv"
        )

with tab2:
    st.header("🔍 Google Trends")
    if not gt_data.empty:
        st.subheader("Current Trending Searches")
        st.dataframe(gt_data, use_container_width=True, hide_index=True)
        
        # Bar chart of top trends
        if len(gt_data) > 0:
            st.subheader("📊 Top 10 Trends")
            top_10 = gt_data.head(10)
            st.bar_chart(top_10.set_index('keyword')['rank'])
    else:
        st.warning("No Google Trends data available")

with tab3:
    st.header("📱 Reddit Trending")
    if not reddit_data.empty:
        st.subheader("Popular Posts")
        st.dataframe(reddit_data, use_container_width=True, hide_index=True)
        
        # Extract and show common keywords
        all_reddit_text = ' '.join(reddit_data['keyword'].astype(str))
        reddit_keywords = extract_keywords_from_text(all_reddit_text)
        keyword_counts = Counter(reddit_keywords)
        
        st.subheader("🏷️ Most Common Keywords")
        common_keywords = pd.DataFrame(
            keyword_counts.most_common(15),
            columns=['keyword', 'frequency']
        )
        st.bar_chart(common_keywords.set_index('keyword')['frequency'])
    else:
        st.warning("No Reddit data available")

with tab4:
    st.header("💻 Hacker News")
    if not hn_data.empty:
        st.subheader("Front Page Stories")
        st.dataframe(hn_data, use_container_width=True, hide_index=True)
        
        # Extract and show domains
        if 'url' in hn_data.columns:
            domains = extract_domains_from_urls(hn_data['url'].fillna(''))
            domain_counts = Counter(domains)
            
            if domain_counts:
                st.subheader("🌐 Most Common Domains")
                domain_df = pd.DataFrame(
                    domain_counts.most_common(10),
                    columns=['domain', 'frequency']
                )
                st.bar_chart(domain_df.set_index('domain')['frequency'])
    else:
        st.warning("No Hacker News data available")

with tab5:
    st.header("🎯 Keyword Trend Analysis")
    
    # Keyword search input
    col1, col2 = st.columns([3, 1])
    with col1:
        user_keyword = st.text_input(
            "Enter a keyword to analyze its trend:",
            placeholder="e.g., artificial intelligence, cryptocurrency, climate change"
        )
    with col2:
        time_range = st.selectbox(
            "Time range:",
            options=["now 7-d", "now 1-M", "now 3-M", "now 12-M", "now 5-y"],
            index=2
        )
    
    if user_keyword:
        with st.spinner(f"Analyzing trend for '{user_keyword}'..."):
            try:
                # Create pytrends object with better error handling
                pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=2, backoff_factor=0.1)
                kw_list = [user_keyword]
                
                # Try to build payload with error handling
                try:
                    pytrends.build_payload(kw_list, cat=0, timeframe=time_range, geo='US', gprop='')
                    
                    # Get interest over time
                    interest_data = pytrends.interest_over_time()
                    
                    if not interest_data.empty and user_keyword in interest_data.columns:
                        st.subheader(f"📈 Trend Analysis for '{user_keyword}'")
                        
                        # Display the trend chart
                        chart_data = interest_data[user_keyword].dropna()
                        if not chart_data.empty:
                            st.line_chart(chart_data)
                            
                            # Show some statistics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Average Interest", f"{chart_data.mean():.1f}")
                            with col2:
                                st.metric("Peak Interest", f"{chart_data.max():.1f}")
                            with col3:
                                st.metric("Current Trend", "📈" if chart_data.iloc[-1] > chart_data.mean() else "📉")
                        else:
                            st.warning("No trend data points available for visualization.")
                        
                        # Related queries with better error handling
                        try:
                            related_queries = pytrends.related_queries()
                            if (user_keyword in related_queries and 
                                related_queries[user_keyword]['top'] is not None and 
                                not related_queries[user_keyword]['top'].empty):
                                st.subheader("🔗 Related Queries")
                                st.dataframe(related_queries[user_keyword]['top'])
                        except Exception as rq_error:
                            st.info("Related queries not available for this keyword.")
                        
                        # Regional interest with better error handling
                        try:
                            regional_interest = pytrends.interest_by_region(resolution='COUNTRY')
                            if not regional_interest.empty and user_keyword in regional_interest.columns:
                                # Filter out zero values and get top regions
                                regional_data = regional_interest[user_keyword]
                                regional_data = regional_data[regional_data > 0]
                                
                                if not regional_data.empty:
                                    st.subheader("🌍 Regional Interest")
                                    top_regions = regional_data.sort_values(ascending=False).head(10)
                                    st.bar_chart(top_regions)
                                else:
                                    st.info("No regional data available for this keyword.")
                        except Exception as ri_error:
                            st.info("Regional interest data not available for this keyword.")
                    else:
                        st.warning(f"No trend data available for '{user_keyword}'. This could be due to:")
                        st.write("• The keyword is too specific or uncommon")
                        st.write("• Google Trends API limitations")
                        st.write("• Try a more general or popular keyword")
                        
                except Exception as payload_error:
                    st.error(f"Error building search query: {str(payload_error)}")
                    st.write("Try using:")
                    st.write("• More common keywords")
                    st.write("• Single words instead of long phrases")
                    st.write("• Different time ranges")
                    
            except Exception as e:
                st.error(f"Error analyzing keyword: {str(e)}")
                st.write("**Troubleshooting tips:**")
                st.write("• Check your internet connection")
                st.write("• Try a different keyword")
                st.write("• Wait a moment and try again (rate limiting)")

# Footer
st.markdown("---")
st.markdown(
    "**NetTrends** | Built with Streamlit 🚀 | "
    "Data sources: Google Trends, Reddit, Hacker News | "
    "Refresh data every hour for latest trends"
)

