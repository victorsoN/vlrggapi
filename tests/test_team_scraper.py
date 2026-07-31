import pytest
from fastapi import HTTPException

from api.scrapers.teams import (
    vlr_team,
    vlr_team_matches,
    vlr_team_transactions,
)
from api.scrapers.teams.parsers import _extract_prize_from_text, _parse_single_roster_item
from utils.html_parsers import parse_html


class FakeResponse:
    def __init__(self, status_code: int, text: str = "<html></html>"):
        self.status_code = status_code
        self.text = text
        self.content = text.encode("utf-8")
        self.headers: dict = {}


class FakeAsyncClient:
    def __init__(self, response: FakeResponse):
        self.response = response
        self.calls: list[tuple[str, int | None]] = []

    async def get(self, url: str, timeout=None, headers=None):
        self.calls.append((url, timeout))
        return self.response


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1st $50,0002024", "$50,000"),
        ("2nd $2,024", "$2,024"),
        ("special prize $2024", "$2024"),
        ("winner $100K 2024", "$100K"),
        ("no prize here", ""),
        ("", ""),
    ],
)
def test_extract_prize_from_text_handles_concatenated_years(text, expected):
    assert _extract_prize_from_text(text) == expected


def test_parse_single_roster_item_alias_substring_of_real_name():
    """Regression test: when a player's alias is also a substring of their
    real name (e.g. alias "Thuy" inside real name "Ngoc-Thuy Duong"), the
    leftover-text role extraction must not strip every occurrence of the
    alias — that corrupts the real name into a bogus role like "Ngoc- Duong",
    which then gets misread elsewhere as a coaching title and excludes an
    active player from the roster."""
    html = parse_html(
        '<div class="team-roster-item">'
        '<a href="/player/41197/thuy">'
        '<div class="team-roster-item-img"><img src="/img/avatar.png"></div>'
        '<div class="team-roster-item-name">'
        '<div class="team-roster-item-name-alias">Thuy</div>'
        '<div class="team-roster-item-name-real">Ngoc-Thuy Duong</div>'
        "</div>"
        "</a>"
        "</div>"
    )
    item = html.css_first(".team-roster-item")
    player = _parse_single_roster_item(item, is_staff=False)

    assert player["alias"] == "Thuy"
    assert player["real_name"] == "Ngoc-Thuy Duong"
    assert player["role"] == ""


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("scraper", "args", "expected_status", "expected_detail"),
    [
        (vlr_team, ("77",), 404, "VLR.GG returned status 404 for team 77"),
        (
            vlr_team_matches,
            ("77", 3),
            503,
            "VLR.GG returned status 503 for team matches 77 page 3",
        ),
        (
            vlr_team_transactions,
            ("77",),
            429,
            "VLR.GG returned status 429 for team transactions 77",
        ),
    ],
)
async def test_team_scrapers_raise_http_errors_for_upstream_failures(
    monkeypatch, scraper, args, expected_status, expected_detail
):
    client = FakeAsyncClient(FakeResponse(expected_status))

    monkeypatch.setattr("api.scrapers.teams.crawlers.get_http_client", lambda: client)

    with pytest.raises(HTTPException) as exc_info:
        await scraper(*args)

    assert exc_info.value.status_code == expected_status
    assert exc_info.value.detail == expected_detail
