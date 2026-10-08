from fastapi.testclient import TestClient


def test_a_product_shows_its_price_and_stock(client: TestClient) -> None:
    response = client.get("/products/BOOK-1")

    assert response.status_code == 200
    assert response.json() == {
        "sku": "BOOK-1",
        "name": "Clean Code",
        "price_cents": 2500,
        "stock": 10,
    }


def test_a_missing_product_gives_404(client: TestClient) -> None:
    assert client.get("/products/NOPE-1").status_code == 404


def test_all_products_are_listed_by_sku(client: TestClient) -> None:
    skus = [product["sku"] for product in client.get("/products").json()]

    assert skus == ["BOOK-1", "LAPTOP-1", "PEN-1"]
