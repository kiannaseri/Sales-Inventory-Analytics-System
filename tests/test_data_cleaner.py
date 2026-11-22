"""Unit tests for sales dataset cleaning and schema validation."""
import pandas as pd

from data.data_cleaner import clean_data, validate_excel_columns


def test_clean_data_removes_invalid_dates_negative_values_and_duplicates():
    frame = pd.DataFrame(
        [
            {"date": "2026-01-01", "product": "Tea", "sales_amount": 100, "quantity_sold": 2, "customer_id": "C1"},
            {"date": "not-a-date", "product": "Tea", "sales_amount": 100, "quantity_sold": 2, "customer_id": "C2"},
            {"date": "2026-01-02", "product": "Herbal", "sales_amount": -5, "quantity_sold": 1, "customer_id": "C3"},
            {"date": "2026-01-01", "product": "Tea", "sales_amount": 100, "quantity_sold": 2, "customer_id": "C1"},
        ]
    )

    cleaned, removed, reason = clean_data(frame)

    assert len(cleaned) == 1
    assert removed == 3
    assert cleaned.iloc[0]["product"] == "Tea"
    assert "تاریخ نامعتبر" in reason
    assert "تکراری" in reason


def test_clean_data_does_not_mutate_input_frame():
    frame = pd.DataFrame(
        [{"date": "2026-02-01", "product": "Tea", "sales_amount": "12", "quantity_sold": "1", "customer_id": "C1"}]
    )
    original = frame.copy(deep=True)

    clean_data(frame)

    pd.testing.assert_frame_equal(frame, original)


def test_validate_excel_columns_reports_missing_fields():
    frame = pd.DataFrame({"date": [], "product": [], "sales_amount": []})

    valid, message = validate_excel_columns(frame)

    assert valid is False
    assert "quantity_sold" in message
    assert "current_inventory" in message


def test_validate_excel_columns_accepts_required_schema():
    frame = pd.DataFrame(
        columns=["date", "product", "sales_amount", "quantity_sold", "customer_id", "current_inventory"]
    )

    valid, message = validate_excel_columns(frame)

    assert valid is True
    assert message == "ستون‌ها معتبر هستند"
