import requests

URL = "https://www.ic3.gov/PSA/2025/PSA250226"
HEADERS = {"User-Agent":"Mozilla/5.0 (research script by Linda; contact:linda@lindagicheru.com)"}

response = requests.get(URL, headers=HEADERS, timeout=30)

print("Status code:", response.status_code)
print("Page length:", len(response.text), "characters")
#print(response.text[:500])

import re
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")

ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")

addresses = []
for item in soup.find_all("li"):
    text = item.get_text(strip=True)
    if ADDRESS_PATTERN.match(text):
        addresses.append(text)

print("Total <li> tags on the page:", len(soup.find_all("li")))
print("Ethereum addresses found:", len(addresses))
print("First:", addresses[0] if addresses else "none")
print("Last:", addresses[-1] if addresses else "none")

from datetime import datetime, timezone

if len(addresses) != 51:
    print("WARNING: expected 51 addresses. The page may have changed. Not saving.")
else:
    with open("fbi_addresses.txt", "w") as f:
        f.write(f"# Source: {URL}\n")
        f.write(f"# Scraped: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC\n")
        f.write(f"# Count: {len(addresses)}\n")
        for address in addresses:
            f.write(address + "\n")
    print("Saved to fbi_addresses.txt")