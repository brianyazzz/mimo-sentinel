from mimo_sentinel.parser import parse_line


def test_parse_structured_text_line():
    event = parse_line("2026-05-22T14:04:22Z ERROR checkout-api - database pool timeout", 1)

    assert event.id == "E0001"
    assert event.level == "error"
    assert event.service == "checkout-api"
    assert "pool timeout" in event.message


def test_parse_json_line():
    event = parse_line('{"ts":"now","level":"WARN","service":"api","msg":"slow"}', 2)

    assert event.timestamp == "now"
    assert event.level == "warn"
    assert event.service == "api"
