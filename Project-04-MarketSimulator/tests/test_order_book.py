from market_sim.core.types import Contract, OrderRequest, Side
from market_sim.market.book import LimitOrderBook


def make_book() -> LimitOrderBook:
    return LimitOrderBook(Contract("x", "Will X occur?", expires_at=100))


def test_crossing_order_executes_at_resting_price() -> None:
    book = make_book()
    sell, _ = book.submit(OrderRequest("seller", Side.SELL, 3, price=6_000), 0)
    buy, trades = book.submit(OrderRequest("buyer", Side.BUY, 2, price=6_200), 1)
    assert buy.remaining == 0
    assert trades[0].price == 6_000
    assert trades[0].quantity == 2
    assert book.snapshot(1).ask_depth == 1
    assert sell.order_id == trades[0].maker_order_id


def test_price_time_priority() -> None:
    book = make_book()
    first, _ = book.submit(OrderRequest("first", Side.SELL, 1, price=6_000), 0)
    second, _ = book.submit(OrderRequest("second", Side.SELL, 1, price=6_000), 1)
    _, trades = book.submit(OrderRequest("buyer", Side.BUY, 1, price=6_000), 2)
    assert trades[0].maker_order_id == first.order_id
    assert book.snapshot(2).best_ask == 6_000
    assert second.order_id != first.order_id


def test_only_owner_can_cancel() -> None:
    book = make_book()
    order, _ = book.submit(OrderRequest("owner", Side.BUY, 1, price=4_000), 0)
    assert not book.cancel(order.order_id, "other")
    assert book.cancel(order.order_id, "owner")
    assert book.snapshot(0).best_bid is None

