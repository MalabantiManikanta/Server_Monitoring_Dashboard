import pandas as pd
from django.utils.timezone import make_aware
from monitoring.models import WebsiteUptime, HourlyWebsiteUptime, DailyWebsiteUptime
import os

# Define base directory
BASE_DIR = r"D:\projects\server_monitor_env\server_monitor\monitoring"

def import_csv(file_name, model):
    file_path = os.path.join(BASE_DIR, file_name)

    try:
        # Load CSV data
        df = pd.read_csv(file_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Fill missing values with 100.0
        df.fillna(100.0, inplace=True)

        # Import to DB
        for _, row in df.iterrows():
            data = {
                "timestamp": make_aware(row["timestamp"]),
                "twitter": row.get("twitter.com", 100.0),
                "amazon": row.get("www.amazon.com", 100.0),
                "apple": row.get("www.apple.com", 100.0),
                "facebook": row.get("www.facebook.com", 100.0),
                "friendster": row.get("www.friendster.com", 100.0),
                "geocities": row.get("www.geocities.com", 100.0),
                "google": row.get("www.google.com", 100.0),
                "microsoft": row.get("www.microsoft.com", 100.0),
                "myspace": row.get("www.myspace.com", 100.0),
                "netflix": row.get("www.netflix.com", 100.0),
                "reddit": row.get("www.reddit.com", 100.0),
                "wikipedia": row.get("www.wikipedia.org", 100.0),
                "youtube": row.get("www.youtube.com", 100.0),
            }
            model.objects.update_or_create(timestamp=data["timestamp"], defaults=data)

        print(f"✅ {file_name} imported successfully!")

    except FileNotFoundError:
        print(f"❌ Error: {file_name} not found in {BASE_DIR}")
    except Exception as e:
        print(f"❌ Error importing {file_name}: {e}")


# Import all files
import_csv("reshaped_website_uptime.csv", WebsiteUptime)
import_csv("hourly_website_uptime.csv", HourlyWebsiteUptime)
import_csv("daily_website_uptime.csv", DailyWebsiteUptime)
