import csv
import uuid
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader
from pathlib import Path


def random_ref(prefix):
    return prefix + "-" + uuid.uuid4().hex[:10]


def run_cli_script(folder):
    """a bit of python import hackery to load the script and run its main()"""
    path = Path(__file__).parent / "../../src/bin/allocate-from-csv"
    spec = spec_from_loader("script", SourceFileLoader("script", str(path)))
    script = module_from_spec(spec)
    spec.loader.exec_module(script)
    script.main(folder)


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

    run_cli_script(orders_csv.parent)

    expected_output_csv = orders_csv.parent / "allocations.csv"
    with open(expected_output_csv) as f:
        rows = list(csv.reader(f))
    assert rows == [
        ["orderid", "sku", "qty", "batchref"],
        [order_ref, sku1, "3", batch1],
        [order_ref, sku2, "12", batch2],
    ]


def test_cli_app_also_reads_existing_allocations_and_can_append_to_them(make_csv):
    sku = random_ref("s")
    batch1, batch2 = random_ref("b1"), random_ref("b2")
    old_order, new_order = random_ref("o1"), random_ref("o2")
    make_csv("batches.csv", [
        ["ref", "sku", "qty", "eta"],
        [batch1, sku, 10, "2011-01-01"],
        [batch2, sku, 10, "2011-01-02"],
    ])
    make_csv("allocations.csv", [
        ["orderid", "sku", "qty", "batchref"],
        [old_order, sku, 10, batch1],
    ])
    orders_csv = make_csv("orders.csv", [
        ["orderid", "sku", "qty"],
        [new_order, sku, 7],
    ])

    run_cli_script(orders_csv.parent)

    expected_output_csv = orders_csv.parent / "allocations.csv"
    with open(expected_output_csv) as f:
        rows = list(csv.reader(f))
    assert rows == [
        ["orderid", "sku", "qty", "batchref"],
        [old_order, sku, "10", batch1],
        [new_order, sku, "7", batch2],
    ]
