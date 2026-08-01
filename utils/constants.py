"""
Configuration constants for VLR.GG API
"""

# Base URLs
VLR_BASE_URL = "https://www.vlr.gg"
VLR_EVENTS_URL = f"{VLR_BASE_URL}/events"
VLR_MATCHES_URL = f"{VLR_BASE_URL}/matches"
VLR_RANKINGS_URL = f"{VLR_BASE_URL}/rankings"
VLR_STATS_URL = f"{VLR_BASE_URL}/stats"
VLR_NEWS_URL = f"{VLR_BASE_URL}/news"

# API Settings
API_TITLE = "vlrggapi"
API_DESCRIPTION = (
    "An Unofficial REST API for [vlr.gg](https://www.vlr.gg/), "
    "a site for Valorant Esports match and news coverage. "
    "Made by [axsddlr](https://github.com/axsddlr)"
)
API_PORT = 3001

# Pagination limits
MAX_PAGE_LIMIT = 100
MIN_PAGE_LIMIT = 1

# Request settings
# A single scrape used to be able to take up to ~90s worst case (3 retries x
# 30s timeout + backoff) before returning anything — well past Vercel's own
# function execution ceiling, so the platform kills the invocation mid-flight
# and the client just sees a dropped connection with no error at all. Tightened
# so a slow/unresponsive vlr.gg fails fast (~17s worst case) instead of hanging.
DEFAULT_TIMEOUT = 8
DEFAULT_RETRIES = 2
DEFAULT_REQUEST_DELAY = 1.0
MIN_RESPONSE_SIZE = 100

# Pagination concurrency
PAGINATION_SEMAPHORE_LIMIT = 4

# Circuit breaker
# All vlr.gg requests share one circuit (keyed by host only), so a burst of
# concurrent scrapes (e.g. a map win-rate fan-out hitting /match/details ~15-30
# times at once) can rack up 5 failures within the same window even though each
# call already retried internally. Raised the threshold and shortened the
# reset window so a short concurrent blip doesn't blanket-503 every endpoint
# for a full 30s.
CIRCUIT_FAIL_MAX = 10
CIRCUIT_RESET_TIMEOUT = 15.0

# Request hardening limits for expensive paginated scrapes
MAX_MATCH_PAGE_WINDOW = 20
MAX_MATCH_QUERY_BOUND = 100
MAX_MATCH_RETRIES = 3
MAX_MATCH_TIMEOUT = 45
LIVE_DETAIL_FETCH_CONCURRENCY = 4
LIVE_DETAIL_FETCH_TIMEOUT = 10
MATCH_DETAIL_TAB_FETCH_CONCURRENCY = 4
MATCH_DETAIL_TAB_FETCH_TIMEOUT = 10

# Cache TTLs (seconds)
CACHE_TTL_LIVE = 30
CACHE_TTL_UPCOMING = 300
CACHE_TTL_RESULTS = 60
CACHE_TTL_NEWS = 600
CACHE_TTL_STATS = 1800
CACHE_TTL_RANKINGS = 3600
CACHE_TTL_EVENTS = 1800
CACHE_TTL_SEARCH = 300
CACHE_MAX_SIZE = 1000

# Cache TTLs — new scraper endpoints
CACHE_TTL_MATCH_DETAIL = 300
CACHE_TTL_MATCH_DETAIL_LIVE = 30
CACHE_TTL_PLAYER = 1800
CACHE_TTL_PLAYER_MATCHES = 600
CACHE_TTL_TEAM = 1800
CACHE_TTL_TEAM_MATCHES = 600
CACHE_TTL_TEAM_TRANSACTIONS = 3600
CACHE_TTL_TEAM_STATS = 600
CACHE_TTL_EVENT_MATCHES = 600
CACHE_TTL_HEALTH_UPSTREAM = 60

# /stats region vocabulary
# The /stats page uses a DIFFERENT region taxonomy from /rankings. vlr.gg's
# <select name="region"> offers exactly these canonical values; any other value
# silently falls back to "all". Kept separate from utils.utils.region (the
# /rankings contract) so /rankings?region=americas still returns 400.
STATS_REGIONS = frozenset({"all", "americas", "emea", "pacific", "china", "intl"})

# /stats map filter uses vlr.gg's internal numeric map_id, not the map name —
# scraped directly from <select name="map_id"> on the stats page itself (these
# are stable per-map ids, not derived from any pattern). API consumers pass a
# lowercase map name instead; this is the name -> id translation table.
STATS_MAP_IDS = {
    "ascent": "5",
    "breeze": "8",
    "haven": "2",
    "lotus": "11",
    "split": "3",
    "summit": "16",
    "sunset": "12",
    "abyss": "13",
    "bind": "1",
    "corrode": "14",
    "fracture": "9",
    "icebox": "6",
    "pearl": "10",
}
