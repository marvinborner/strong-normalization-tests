#!/bin/env python3

import subprocess

subprocess.run(["cc", "AIT/nf.c"])

TESTS = open("tests").readlines()
TIMEOUT = 5  # seconds


def toBLC(term):
    if term == "":
        return term

    if term[0] == "\\":
        res = "00"
    elif term[0] == "`":
        res = "01"
    else:
        idx = int(term[0]) + 1
        res = "1" * idx + "0"
    return res + toBLC(term[1:])


def reduce(term):
    proc = subprocess.Popen(
        ["./a.out", "-b"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    try:
        stdout, stderr = proc.communicate(term.encode("utf-8"), timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()  # SIGKILL required
        raise TimeoutError

    if proc.returncode != 0:
        raise Exception(proc.returncode)

    return toBLC(stdout.decode("utf-8").strip())


def test(a, b):
    nf = reduce(a)
    return (nf == b, nf)


passed = []
timeout = []
failed = []
for l in TESTS:
    bruijn, tests = l.split(": ")
    left, right = tests.split(" - ")
    # left, right = f"00{left}", f"00{right}"

    try:
        success, nf = test(left, right.strip())
        if success:
            passed.append(bruijn)
        else:
            print("failed! Got", nf, "expected", right.strip())
            failed.append(bruijn)
    except TimeoutError:
        print("timeout!")
        timeout.append(bruijn)
    except Exception as e:
        print("exception!", str(e))
        failed.append(bruijn)


print("passed:", len(passed))
print("timeout:", len(timeout))
print("failed:", len(failed))
