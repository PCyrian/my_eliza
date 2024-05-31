import requests
import feedparser


def get_current_location():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        return data['city'], data['region'], data['country']
    except Exception as e:
        print(f"Error getting location: {e}")


def get_weather_forecast(city):
    try:
        response = requests.get(f'https://wttr.in/{city}?format=%C+%t+%w+%h')
        current_weather = response.text.strip() + " humidity"
        response_next_day = requests.get(f'https://wttr.in/{city}?format=%C+%t+%w+%h&1')
        next_day_weather = response_next_day.text.strip() + " humidity"
        response_forecast = requests.get(f'https://wttr.in/{city}?format=%C+%t+%w+%h&2')
        forecast_weather = response_forecast.text.strip() + " humidity"
        return {
            'current_weather': current_weather,
            'next_day_weather': next_day_weather,
            'forecast_weather': forecast_weather
        }
    except Exception as e:
        print(f"Error getting weather: {e}")
        return None


def get_news(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        news_items = []
        for entry in feed.entries[:5]:
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'summary': entry.summary
            })
        return news_items
    except Exception as e:
        print(f"Error getting news: {e}")
        return []


def get_tech_news():
    return get_news('http://feeds.arstechnica.com/arstechnica/index')


def get_sports_news():
    return get_news('http://feeds.bbci.co.uk/sport/rss.xml?edition=int')


def get_politics_news():
    return get_news('http://feeds.bbci.co.uk/news/politics/rss.xml')


def get_location_and_weather():
    city, region, country = get_current_location()
    if city:
        weather_info = get_weather_forecast(city)
        return {
            'location': f"{city}, {region}, {country}",
            'current_weather': weather_info['current_weather'],
            'next_day_weather': weather_info['next_day_weather'],
            'forecast_weather': weather_info['forecast_weather']
        }
    else:
        return {
            'location': 'Unknown',
            'current_weather': 'Could not retrieve current weather information',
            'next_day_weather': 'Could not retrieve next day weather information',
            'forecast_weather': 'Could not retrieve forecast weather information'
        }


def generate_daily_report():
    weather_info = get_location_and_weather()
    tech_news = get_tech_news()
    sports_news = get_sports_news()
    politics_news = get_politics_news()

    report = "################### Weather Info:\n"
    report += f"Location: {weather_info['location']}\n"
    report += f"Current Weather: {weather_info['current_weather']}\n"
    report += f"Next Day Weather: {weather_info['next_day_weather']}\n"
    report += f"Forecast Weather: {weather_info['forecast_weather']}\n\n"

    report += "################### Tech News:\n"
    for news in tech_news:
        report += f"- {news['title']}\n  {news['link']}\n  {news['summary']}\n\n"

    report += "################### Sports News:\n"
    for news in sports_news:
        report += f"- {news['title']}\n  {news['link']}\n  {news['summary']}\n\n"

    report += "################### Politics News:\n"
    for news in politics_news:
        report += f"- {news['title']}\n  {news['link']}\n  {news['summary']}\n\n"

    return report


def save_report(report):
    with open("daily_report.txt", "w", encoding="utf-8") as file:
        file.write(report)


def get_daily_report():
    daily_report = generate_daily_report()
    save_report(daily_report)
    print("Daily report saved to daily_report.txt")
