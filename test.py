import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.skripthub_service import SkriptHubService

print("🦆 Testing SkriptHub Integration...")
print("="*50)

# Initialize service
skripthub = SkriptHubService()

# Test cases
test_queries = [
    "on death",
    "kill player",
    "teleport",
    "send message",
    "has permission"
]

print("\n📚 Testing documentation search...")
for query in test_queries:
    print(f"\n🔍 Searching for: {query}")
    
    # Test direct keyword lookup
    result = skripthub.find_syntax_by_keyword(query)
    if result:
        print(f"✅ Found: {result.get('title', 'Unknown')}")
        if result.get('syntax'):
            print(f"   Syntax: {result['syntax'][0][:60]}...")
        if result.get('examples'):
            print(f"   Example: {result['examples'][0][:60]}...")
    else:
        print("❌ Not found in local mapping")
        
        # Try search
        search_results = skripthub.search_documentation(query)
        if search_results:
            print(f"🔎 Found {len(search_results)} search results")
            for i, res in enumerate(search_results[:3]):
                print(f"   {i+1}. {res.get('title', 'Unknown')}")

print("\n\n📊 Testing user request analysis...")
user_requests = [
    "create a kill counter",
    "make a teleport home system",
    "I need a combat log plugin"
]

for request in user_requests:
    print(f"\n💬 User: {request}")
    findings = skripthub.analyze_user_request(request)
    
    total_findings = sum(len(items) for items in findings.values())
    print(f"📋 Found {total_findings} relevant syntax items")
    
    for category, items in findings.items():
        if items:
            print(f"   {category}: {len(items)} items")

print("\n\n✅ SkriptHub integration test complete!")
print("\nNOTE: If you see many 'Not found' messages, it means:")
print("1. SkriptHub might have changed their HTML structure")
print("2. You might need to update the selectors in skripthub_service.py")
print("3. The cache is working (check data/skripthub_cache/)")

input("\nPress Enter to exit...")