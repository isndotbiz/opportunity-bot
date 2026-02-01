#!/usr/bin/env python3
"""
Test Reddit API connection and configuration.
Verifies that credentials are valid and the API is accessible.
"""

import os
import sys
from pathlib import Path

# Add project to path
PROJECT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))

def print_header(text):
    print(f"\n{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}\n")

def print_success(text):
    print(f"✓ {text}")

def print_error(text):
    print(f"✗ {text}")

def print_warning(text):
    print(f"⚠ {text}")

def print_info(text):
    print(f"ℹ {text}")

def check_env_file():
    """Check if .env file exists and is readable."""
    print_header("Step 1: Checking .env File")

    env_file = PROJECT_DIR / ".env"

    if not env_file.exists():
        print_error(f".env file not found at {env_file}")
        print_info("Create one with: bash configure_reddit.sh")
        return False

    print_success(f".env file found at {env_file}")

    # Check permissions
    stat_info = env_file.stat()
    mode = oct(stat_info.st_mode)[-3:]

    if mode == "600":
        print_success(f"File permissions are secure: {mode}")
    else:
        print_warning(f"File permissions are {mode} (should be 600)")
        print_info("Run: chmod 600 .env")

    return True

def check_env_variables():
    """Check if required environment variables are set."""
    print_header("Step 2: Checking Environment Variables")

    from dotenv import load_dotenv

    env_file = PROJECT_DIR / ".env"
    load_dotenv(env_file)

    required_vars = {
        "REDDIT_CLIENT_ID": "OAuth2 client ID",
        "REDDIT_CLIENT_SECRET": "OAuth2 client secret",
        "REDDIT_USER_AGENT": "User agent string",
    }

    missing = []
    all_present = True

    for var_name, description in required_vars.items():
        value = os.getenv(var_name)

        if not value:
            print_error(f"{var_name}: NOT SET")
            print_info(f"  Description: {description}")
            missing.append(var_name)
            all_present = False
        else:
            # Show masked value for security
            if var_name == "REDDIT_CLIENT_SECRET":
                masked = f"{value[:4]}...{value[-4:]}"
            elif var_name == "REDDIT_CLIENT_ID":
                masked = f"{value[:4]}...{value[-4:]}"
            else:
                masked = value

            print_success(f"{var_name}: SET ({masked})")

    if missing:
        print_error(f"Missing variables: {', '.join(missing)}")
        return False

    return all_present

def check_dependencies():
    """Check if required Python packages are installed."""
    print_header("Step 3: Checking Dependencies")

    dependencies = {
        "praw": "Python Reddit API Wrapper",
        "dotenv": "Environment variable loader",
    }

    missing = []

    for package, description in dependencies.items():
        try:
            __import__(package)
            print_success(f"{package}: Installed")
        except ImportError:
            print_error(f"{package}: NOT INSTALLED")
            print_info(f"  Description: {description}")
            missing.append(package)

    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print_info("Install with: pip install -r requirements.txt")
        return False

    return True

def test_reddit_connection():
    """Test actual Reddit API connection."""
    print_header("Step 4: Testing Reddit API Connection")

    try:
        import praw
        from dotenv import load_dotenv

        env_file = PROJECT_DIR / ".env"
        load_dotenv(env_file)

        print_info("Initializing Reddit client...")

        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            check_for_async=False
        )

        print_success("Reddit client initialized")

        # Test read-only access (no authentication required)
        print_info("Testing read-only access to r/python...")

        test_sub = reddit.subreddit("python")
        test_posts = list(test_sub.hot(limit=3))

        if test_posts:
            print_success(f"Successfully retrieved {len(test_posts)} posts")

            for i, post in enumerate(test_posts, 1):
                title = post.title[:50] + "..." if len(post.title) > 50 else post.title
                print_info(f"  {i}. {title}")
                print_info(f"     Score: {post.score}, Comments: {post.num_comments}")
        else:
            print_warning("No posts retrieved (subreddit may be empty)")

        return True

    except ImportError as e:
        if "praw" in str(e):
            print_error("PRAW library not installed")
            print_info("Run: pip install praw python-dotenv")
        else:
            print_error(f"Import error: {e}")
        return False

    except Exception as e:
        error_msg = str(e)

        # Categorize the error
        if "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
            print_error(f"Invalid credentials: {error_msg}")
            print_info("Check your REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
            print_info("Get credentials from: https://www.reddit.com/prefs/apps")

        elif "403" in error_msg or "forbidden" in error_msg.lower():
            print_error(f"Access forbidden: {error_msg}")
            print_info("Your app may have been revoked")
            print_info("Create a new app at: https://www.reddit.com/prefs/apps")

        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            print_warning(f"Network error: {error_msg}")
            print_info("Check your internet connection")
            print_info("Credentials may still be valid")

        else:
            print_error(f"Unexpected error: {error_msg}")

        return False

def test_reddit_scraper():
    """Test the actual Reddit scraper."""
    print_header("Step 5: Testing Reddit Scraper")

    try:
        from scrapers.reddit_scraper import RedditScraper

        print_info("Initializing Reddit scraper...")
        scraper = RedditScraper()

        print_success("Scraper initialized successfully")

        print_info("Testing scraper with r/SideProject (limit: 5 posts)...")
        opportunities = scraper.scrape_subreddit(
            "SideProject",
            time_filter="week",
            limit=5
        )

        if opportunities:
            print_success(f"Found {len(opportunities)} opportunities")

            # Show first opportunity
            if opportunities:
                opp = opportunities[0]
                print_info(f"\nSample opportunity:")
                print_info(f"  Title: {opp['title'][:60]}...")
                print_info(f"  Revenue: {opp['revenue_claim']}")
                print_info(f"  Score: {opp['score']}")
                print_info(f"  URL: {opp['url']}")
        else:
            print_warning("No opportunities found (might be normal for this subreddit)")

        return True

    except Exception as e:
        print_error(f"Scraper test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + "Reddit API Configuration Test".center(58) + "║")
    print("║" + "Opportunity Bot".center(58) + "║")
    print("╚" + "="*58 + "╝")

    tests = [
        ("Environment File", check_env_file),
        ("Environment Variables", check_env_variables),
        ("Python Dependencies", check_dependencies),
        ("Reddit API Connection", test_reddit_connection),
        ("Reddit Scraper", test_reddit_scraper),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            results[test_name] = False

    # Summary
    print_header("Test Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print_success("All tests passed! Reddit API is properly configured.")
        print_info("You can now run the opportunity bot:")
        print_info("  python3 production_opportunity_pipeline.py")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        print_info("See above for details and how to fix each issue")
        return 1

if __name__ == "__main__":
    sys.exit(main())
