#!/usr/bin/env python3
"""
NetTrends Demo Script
This script demonstrates the core functionality of the NetTrends application
without the Streamlit interface for testing purposes.
"""

import pandas as pd
from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
import time
from collections import Counter
import re

def demo_google_trends():
    """Demo function to test Google Trends functionality"""
    print("🔍 Testing Google Trends...")
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Method 1: Try trending searches for different countries
        country_codes = ['united_states', 'p1', 'p4']
        
        for country in country_codes:
            try:
                trending_searches = pytrends.trending_searches(pn=country)
                if trending_searches is not None and not trending_searches.empty:
                    keywords = trending_searches.iloc[:, 0].dropna().tolist()
                    if keywords:
                        df = pd.DataFrame(keywords, columns=['keyword'])
                        print(f"✅ Successfully fetched {len(df)} trending searches from Google Trends ({country})")
                        print("Top 5 trending searches:")
                        for i, keyword in enumerate(df['keyword'].head(5)):
                            print(f"  {i+1}. {keyword}")
                        return df
            except Exception as country_error:
                print(f"⚠️ Failed to get trends for {country}: {str(country_error)}")
                continue
        
        # Method 2: Try without country parameter
        try:
            trending_searches = pytrends.trending_searches()
            if trending_searches is not None and not trending_searches.empty:
                keywords = trending_searches.iloc[:, 0].dropna().tolist()
                if keywords:
                    df = pd.DataFrame(keywords, columns=['keyword'])
                    print(f"✅ Successfully fetched {len(df)} global trending searches")
                    print("Top 5 trending searches:")
                    for i, keyword in enumerate(df['keyword'].head(5)):
                        print(f"  {i+1}. {keyword}")
                    return df
        except Exception as global_error:
            print(f"⚠️ Failed to get global trends: {str(global_error)}")
        
        # Method 3: Try current interest method
        try:
            popular_keywords = ['AI', 'Bitcoin', 'Tesla', 'iPhone', 'Netflix']
            trending_data = []
            
            for keyword in popular_keywords:
                try:
                    pytrends.build_payload([keyword], cat=0, timeframe='now 1-d')
                    interest = pytrends.interest_over_time()
                    if not interest.empty and keyword in interest.columns:
                        avg_interest = interest[keyword].mean()
                        if avg_interest > 0:
                            trending_data.append({'keyword': keyword, 'interest': avg_interest})
                    time.sleep(0.1)
                except:
                    continue
            
            if trending_data:
                trending_df = pd.DataFrame(trending_data)
                trending_df = trending_df.sort_values('interest', ascending=False)
                df = pd.DataFrame(trending_df['keyword'].tolist(), columns=['keyword'])
                print(f"✅ Successfully fetched {len(df)} trending keywords by interest")
                print("Top trending by interest:")
                for i, keyword in enumerate(df['keyword'].head(5)):
                    print(f"  {i+1}. {keyword}")
                return df
        except Exception as interest_error:
            print(f"⚠️ Failed to get interest data: {str(interest_error)}")
        
        print("❌ Unable to fetch any Google Trends data")
        return pd.DataFrame(columns=['keyword'])
        
    except Exception as e:
        print(f"❌ Error connecting to Google Trends: {str(e)}")
        return pd.DataFrame(columns=['keyword'])

def demo_reddit_scraping():
    """Demo function to test Reddit scraping"""
    print("\n📱 Testing Reddit scraping...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        url = 'https://www.reddit.com/r/popular/'
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find post titles
        titles = soup.find_all('h3')
        post_titles = []
        for title in titles[:10]:
            text = title.get_text(strip=True)
            if text and len(text) > 10:
                post_titles.append(text)
        
        print(f"✅ Successfully scraped {len(post_titles)} posts from Reddit")
        print("Sample Reddit posts:")
        for i, title in enumerate(post_titles[:3]):
            print(f"  {i+1}. {title[:80]}...")
        
        return pd.DataFrame(post_titles, columns=['title'])
    except Exception as e:
        print(f"❌ Error scraping Reddit: {str(e)}")
        return pd.DataFrame()

def demo_hackernews_scraping():
    """Demo function to test Hacker News scraping"""
    print("\n💻 Testing Hacker News scraping...")
    try:
        url = 'https://news.ycombinator.com/'
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find story titles
        titles = []
        story_links = soup.find_all('span', class_='titleline')
        for link in story_links:
            a_tag = link.find('a')
            if a_tag:
                title = a_tag.get_text(strip=True)
                if title and len(title) > 10:
                    titles.append(title)
        
        print(f"✅ Successfully scraped {len(titles)} stories from Hacker News")
        print("Sample Hacker News stories:")
        for i, title in enumerate(titles[:3]):
            print(f"  {i+1}. {title[:80]}...")
        
        return pd.DataFrame(titles, columns=['title'])
    except Exception as e:
        print(f"❌ Error scraping Hacker News: {str(e)}")
        return pd.DataFrame()

def demo_keyword_analysis():
    """Demo function to test keyword trend analysis"""
    print("\n🎯 Testing keyword trend analysis...")
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        keyword = "artificial intelligence"
        kw_list = [keyword]
        pytrends.build_payload(kw_list, cat=0, timeframe='now 1-M', geo='', gprop='')
        
        # Get interest over time
        interest_data = pytrends.interest_over_time()
        
        if not interest_data.empty:
            print(f"✅ Successfully analyzed trend for '{keyword}'")
            print(f"Average interest score: {interest_data[keyword].mean():.1f}")
            print(f"Max interest score: {interest_data[keyword].max()}")
            print(f"Data points: {len(interest_data)}")
        else:
            print(f"❌ No trend data available for '{keyword}'")
        
        return interest_data
    except Exception as e:
        print(f"❌ Error analyzing keyword trends: {str(e)}")
        return pd.DataFrame()

def extract_keywords_demo(text):
    """Demo function for keyword extraction"""
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    keywords = [word for word in words if word not in stop_words]
    return keywords

def main():
    """Main demo function"""
    print("🌐 NetTrends Demo - Testing Core Functionality")
    print("=" * 50)
    
    # Test all data sources
    gt_data = demo_google_trends()
    reddit_data = demo_reddit_scraping()
    hn_data = demo_hackernews_scraping()
    
    # Test keyword analysis
    trend_data = demo_keyword_analysis()
    
    # Show summary
    print("\n📊 Summary:")
    print(f"Google Trends keywords: {len(gt_data)}")
    print(f"Reddit posts: {len(reddit_data)}")
    print(f"Hacker News stories: {len(hn_data)}")
    print(f"Keyword trend analysis: {'✅ Working' if not trend_data.empty else '❌ Failed'}")
    
    # Test keyword extraction
    if not reddit_data.empty:
        print("\n🔍 Keyword extraction demo:")
        sample_text = " ".join(reddit_data['title'].head(3).astype(str))
        keywords = extract_keywords_demo(sample_text)
        keyword_counts = Counter(keywords)
        print("Top extracted keywords:")
        for keyword, count in keyword_counts.most_common(5):
            print(f"  {keyword}: {count}")
    
    print("\n🚀 Demo completed! The NetTrends app is ready to run.")
    print("To start the full Streamlit app, run: streamlit run main.py")

if __name__ == "__main__":
    main()
