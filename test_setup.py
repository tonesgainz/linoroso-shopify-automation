#!/usr/bin/env python3
"""
Quick setup test for Linoroso Shopify Automation
Run this to verify your installation and API keys
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("🔍 Testing Environment Setup...\n")
    
    # Load .env file
    load_dotenv()
    
    # Check Python version
    print(f"✓ Python version: {sys.version.split()[0]}")
    
    # Check required environment variables
    required_vars = {
        'ANTHROPIC_API_KEY': 'Anthropic API Key',
        'SHOPIFY_STORE_URL': 'Shopify Store URL',
        'SHOPIFY_ACCESS_TOKEN': 'Shopify Access Token'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"✗ {description}: NOT SET")
            missing_vars.append(var)
        else:
            # Mask the value for security
            masked = value[:8] + '...' if len(value) > 8 else '***'
            print(f"✓ {description}: {masked}")
    
    print()
    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease edit your .env file and add these values.")
        return False
    
    return True

def test_imports():
    """Test required package imports"""
    print("📦 Testing Package Imports...\n")
    
    packages = [
        ('anthropic', 'Anthropic (Claude AI)'),
        ('requests', 'Requests'),
        ('pandas', 'Pandas'),
        ('beautifulsoup4', 'BeautifulSoup'),
        ('dotenv', 'Python-dotenv'),
    ]
    
    failed = []
    for package, name in packages:
        try:
            if package == 'beautifulsoup4':
                import bs4
            elif package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name}: NOT INSTALLED")
            failed.append(package)
    
    print()
    
    if failed:
        print("⚠️  Some packages are missing. Run:")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def test_anthropic_connection():
    """Test Anthropic API connection"""
    print("🤖 Testing Anthropic API Connection...\n")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key.startswith('your_'):
        print("✗ Anthropic API key not configured")
        return False
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # Simple test message
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'API connection successful' in 3 words"}
            ]
        )
        
        response = message.content[0].text
        print(f"✓ Anthropic API connected successfully")
        print(f"  Response: {response}\n")
        return True
        
    except Exception as e:
        print(f"✗ Anthropic API connection failed: {str(e)}\n")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 LINOROSO SHOPIFY AUTOMATION - SETUP TEST")
    print("=" * 60)
    print()
    
    results = []
    
    # Test environment
    results.append(("Environment", test_environment()))
    
    # Test imports
    results.append(("Package Imports", test_imports()))
    
    # Test API connection (only if env is set up)
    if results[0][1]:  # If environment test passed
        results.append(("Anthropic API", test_anthropic_connection()))
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print()
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python3 content_engine.py")
        print("2. Run: python3 optimizer.py")
        print("3. Run: python3 seo_engine.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Edit .env file with your API keys")
        print("2. Activate virtual environment: source venv/bin/activate")
        print("3. Install dependencies: pip install -r requirements.txt")
    
    print()
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
