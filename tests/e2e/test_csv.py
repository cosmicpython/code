import csv
import subprocess
import uuid


def random_ref(prefix):
    return prefix + "-" + uuid.uuid4().hex[:10]


def test_cli_app_reads_csvs_with_batches_and_orders_and_outputs_allocations(make_csv):
    sku1, sku2 = random_ref("s1"), random_ref("s2")
    batch1, batch2, batch3 = random_ref("b1"), random_ref("b2"), random_ref("b3")
    order_ref = random_ref("o")
    make_csv("batches.csv", [
        ["ref", "sku", "qty", "eta"],
        [batch1, sku1, 100, ""],
        [batch2, sku2, 100, "2011-01-01"],
        [batch3, sku2, 100, "2011-01-02"],
    ])
    orders_csv = make_csv("orders.csv", [
        ["orderid", "sku", "qty"],
        [order_ref, sku1, 3],
        [order_ref, sku2, 12],
    ])

    subprocess.run(["allocate-from-csv", orders_csv.parent])

    expected_output_csv = orders_csv.parent / "allocations.csv"
    with open(expected_output_csv) as f:
        rows = list(csv.reader(f))
    assert rows == [
        ["orderid", "sku", "qty", "batchref"],
        [order_ref, sku1, "3", batch1],
        [order_ref, sku2, "12", batch2],
    ]
