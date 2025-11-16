import pytest
import requests
from urllib.parse import urlparse

# Configuration
NON_WWW_DOMAIN = "kouidri.fr"
WWW_DOMAIN = f"www.{NON_WWW_DOMAIN}"

# URLs for the tests
HTTP_WWW_URL = f"http://{WWW_DOMAIN}" 
HTTPS_NON_WWW_URL = f"https://{NON_WWW_DOMAIN}"
HTTPS_WWW_URL = f"https://{WWW_DOMAIN}"

@pytest.fixture
def http_session():
    """Fixture for a reusable HTTP session, with SSL verification enabled."""
    session = requests.Session()
    session.verify = True
    return session

def test_liveness(http_session):
    """
    Tests that the server is up and responds with 200
    """
    # Test 1: HTTPS
    https_response = http_session.get(HTTPS_WWW_URL, allow_redirects=True)
    assert https_response.status_code == 200, \
        f"Unexpected response code: {https_response.status_code} (expected 200)"

def test_http_to_https_redirect(http_session):
    """
    Tests the HTTP -> HTTPS redirect, preserving the 'www' domain intact.
    - Sends an HTTP request without following redirects.
    - Verifies a mandatory 301 code and that Location points to HTTPS with the same domain.
    """
    # Send the request without redirecting to inspect the response
    response = http_session.get(HTTP_WWW_URL, allow_redirects=False)
    
    # Assertion 1: Permanent redirect code only (301)
    assert response.status_code == 301, \
        f"Unexpected code: {response.status_code} (strictly expected 301 for a permanent redirect)"
    
    # Assertion 2: Location header exists and points to HTTPS
    location = response.headers.get("Location")
    assert location is not None, "Location header missing"
    
    # Parse the URL to verify the scheme and domain
    parsed_location = urlparse(location)
    assert parsed_location.scheme == "https", \
        f"Redirect to {parsed_location.scheme}, not HTTPS"
    
    # Key assertion: The domain (including 'www') remains exactly the same
    assert parsed_location.netloc == WWW_DOMAIN, \
        f"Domain changed: {parsed_location.netloc} (expected {WWW_DOMAIN} to preserve 'www')"
    
    # Bonus: Verify that the path is preserved (if applicable)
    assert parsed_location.path == "/", \
        f"Path changed: {parsed_location.path} (expected '/' for root)"
    
    # Log for debug (optional, pytest displays it if test fails)
    print(f"HTTP->HTTPS redirect successful: {HTTP_WWW_URL} -> {location}")

def test_non_www_to_www_redirect(http_session):
    """
    Tests the HTTPS without 'www' -> HTTPS with 'www' redirect.
    - Sends an HTTPS request without www, without following redirects.
    - Verifies a mandatory 301 code and that Location points to HTTPS with 'www' added.
    """
    # Send the request without redirecting to inspect the response
    response = http_session.get(HTTPS_NON_WWW_URL, allow_redirects=False)
    
    # Assertion 1: Permanent redirect code only (301)
    assert response.status_code == 301, \
        f"Unexpected code: {response.status_code} (strictly expected 301 for a permanent redirect)"
    
    # Assertion 2: Location header exists and points to HTTPS
    location = response.headers.get("Location")
    assert location is not None, "Location header missing"
    
    # Parse the URL to verify the scheme and domain
    parsed_location = urlparse(location)
    assert parsed_location.scheme == "https", \
        f"Redirect to {parsed_location.scheme}, not HTTPS"
    
    # Key assertion: The domain properly goes from without 'www' to with 'www'
    assert parsed_location.netloc == WWW_DOMAIN, \
        f"Domain unchanged or incorrect: {parsed_location.netloc} (expected {WWW_DOMAIN} with 'www' added)"
    
    # Bonus: Verify that the path is preserved (if applicable)
    assert parsed_location.path == "/", \
        f"Path changed: {parsed_location.path} (expected '/' for root)"
    
    # Log for debug (optional, pytest displays it if test fails)
    print(f"Without www -> with www redirect successful: {HTTPS_NON_WWW_URL} -> {location}")

def test_hsts_header(http_session):
    """
    Tests the presence of the HSTS header on HTTPS and its absence on HTTP.
    - For HTTP: Verifies the header's absence (before redirect).
    - For HTTPS: Verifies presence and basic validity (max-age present).
    """
    # Test 1: Absence of the HSTS header on HTTP (redirect response)
    http_response = http_session.get(HTTP_WWW_URL, allow_redirects=False)
    hsts_http = http_response.headers.get("Strict-Transport-Security")
    assert hsts_http is None, \
        f"HSTS present on HTTP: {hsts_http} (should be absent to avoid leaks)"
    
    # Test 2: Presence and validity of the HSTS header on HTTPS (final response)
    https_response = http_session.get(HTTPS_WWW_URL, allow_redirects=True)  # Follows redirects if needed
    assert https_response.status_code == 200, \
        f"Unexpected HTTPS status: {https_response.status_code} (expected 200)"
    
    hsts_https = https_response.headers.get("Strict-Transport-Security")
    assert hsts_https is not None, "HSTS header missing on HTTPS"
    assert "max-age" in hsts_https.lower(), \
        f"Invalid HSTS value on HTTPS: {hsts_https} (should include 'max-age')"
    
    # Log for debug
    print(f"HSTS verified: Absent on HTTP, present on HTTPS with '{hsts_https}'")