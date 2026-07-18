#!/usr/bin/env python3

import argparse
import os
import random
import re
import string

SITE_MENTION = "contohnya.web.id"
MENTION_EVERY_N_ITEMS = 5

HEADER = (
    '{"metadata":{"generator":"Dummy JSON Generator","website":"'
    + SITE_MENTION
    + '"},"data":['
)

PADDING_PREFIX = '],"padding":"'
FOOTER = '"}'

DEFAULT_SIZES = {
    "1kb": 1_000,
    "10kb": 10_000,
    "50kb": 50_000,
    "100kb": 100_000,
    "500kb": 500_000,
    "1mb": 1_000_000,
    "5mb": 5_000_000,
    "10mb": 10_000_000,
    "50mb": 50_000_000,
    "100mb": 100_000_000,
}

DEFAULT_SIZES_BINARY = {
    "1kb": 1024,
    "10kb": 10 * 1024,
    "50kb": 50 * 1024,
    "100kb": 100 * 1024,
    "500kb": 500 * 1024,
    "1mb": 1024 * 1024,
    "5mb": 5 * 1024 * 1024,
    "10mb": 10 * 1024 * 1024,
    "50mb": 50 * 1024 * 1024,
    "100mb": 100 * 1024 * 1024,
}


def parse_size(s, binary=False):
    s = s.strip().lower()

    m = re.match(r"^([\d.]+)\s*(kb|mb|gb|b)?$", s)
    if not m:
        raise ValueError(s)

    num, unit = m.groups()

    base = 1024 if binary else 1000

    mult = {
        "b": 1,
        "kb": base,
        "mb": base ** 2,
        "gb": base ** 3,
        None: 1,
    }[unit]

    return int(float(num) * mult)


def format_label(label):
    m = re.match(r"^([\d.]+)(kb|mb|gb|b)$", label.lower())
    if not m:
        return label

    n, u = m.groups()
    return f"{n}{u.upper()}"


def random_text(length=50):
    return "".join(
        random.choices(
            string.ascii_letters + "     ",
            k=length,
        )
    ).strip()


def make_object(idx):

    source = (
        SITE_MENTION
        if idx % MENTION_EVERY_N_ITEMS == 0
        else ""
    )

    return (
        "{"
        f'"id":{idx},'
        f'"title":"Dummy Record {idx}",'
        f'"description":"Dummy data testing {random_text()}",'
        f'"category":"Testing",'
        f'"source":"{source}"'
        "}"
    )


def build_json(target):

    base_size = (
        len(HEADER.encode())
        + len(PADDING_PREFIX.encode())
        + len(FOOTER.encode())
    )

    size = base_size

    objects = []

    idx = 0

    while True:

        idx += 1

        obj = make_object(idx)

        if objects:
            obj = "," + obj

        obj_size = len(obj.encode())

        if size + obj_size > target:
            idx -= 1
            break

        objects.append(obj)
        size += obj_size

    remain = target - size

    body = (
        HEADER
        + "".join(objects)
        + PADDING_PREFIX
        + ("x" * remain)
        + FOOTER
    )

    diff = target - len(body.encode())

    if diff > 0:
        body = (
            HEADER
            + "".join(objects)
            + PADDING_PREFIX
            + ("x" * (remain + diff))
            + FOOTER
        )

    elif diff < 0:
        body = (
            HEADER
            + "".join(objects)
            + PADDING_PREFIX
            + ("x" * (remain + diff))
            + FOOTER
        )

    actual = len(body.encode())

    if actual != target:
        raise RuntimeError(
            f"Target={target} Actual={actual}"
        )

    return body, actual, idx


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--sizes")
    parser.add_argument("--outdir", default=".")
    parser.add_argument("--prefix", default="Contohnya-JSON")
    parser.add_argument("--binary", action="store_true")

    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    table = (
        DEFAULT_SIZES_BINARY
        if args.binary
        else DEFAULT_SIZES
    )

    if args.sizes:

        targets = {}

        for s in args.sizes.split(","):

            s = s.strip()

            if s.lower() in table:
                targets[s.lower()] = table[s.lower()]
            else:
                targets[s.lower()] = parse_size(
                    s,
                    args.binary,
                )

    else:

        targets = table

    for label, target in sorted(
        targets.items(),
        key=lambda x: x[1],
    ):

        body, actual, count = build_json(target)

        path = os.path.join(
            args.outdir,
            f"{args.prefix}-{format_label(label)}.json",
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(body)

        real = os.path.getsize(path)

        print(
            f"{label:>8} -> {path} "
            f"[{real} bytes, {count} object] "
            f'{"OK" if real == target else "MELESET"}'
        )


if __name__ == "__main__":
    main()
