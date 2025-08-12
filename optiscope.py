#!/bin/env python3

import subprocess

funcId = 0


def symbolify(n):
    CHRS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    b = len(CHRS)

    res = ""
    while n:
        res += CHRS[int(n % b)]
        n //= b
    return res


def toC(blc):
    global funcId

    symbols = 1

    used = set()
    stack = []

    res = ""

    def parse(i):
        nonlocal res, symbols

        if blc[i] == "0" and blc[i + 1] == "0":
            symbol = symbolify(symbols)
            used.add(symbol)
            stack.append(symbol)
            res += f"lambda({symbol}, "
            symbols += 1
            j = parse(i + 2)
            res += ")"
            stack.pop()
            return j
        elif blc[i] == "0" and blc[i + 1] == "1":
            res += f"apply("
            a = parse(i + 2)
            res += ", "
            b = parse(a + 1)
            res += ")"
            return b
        else:
            cnt = 0
            while blc[i] == "1":
                i += 1
                cnt += 1
            var = stack[-cnt]
            res += f"var({var})"
            return i

    parse(0)

    decls = ""
    for u in used:
        decls += f"*{u},"
    decls = decls[:-1]

    func = f"""
static struct lambda_term *
func{funcId}(void) {{
  struct lambda_term {decls};
  return {res};
}}
    """
    funcId += 1
    return func


def toLambda(blc):
    res = ""

    def parse(i):
        nonlocal res

        if blc[i] == "0" and blc[i + 1] == "0":
            res += "(λ "
            j = parse(i + 2)
            res += ")"
            return j
        elif blc[i] == "0" and blc[i + 1] == "1":
            res += "("
            a = parse(i + 2)
            res += " "
            b = parse(a + 1)
            res += ")"
            return b
        else:
            cnt = 0
            while blc[i] == "1":
                i += 1
                cnt += 1
            res += f"{cnt - 1}"
            return i

    parse(0)
    return res


def genFile(funcs, tests):
    return f"""
#include <sys/wait.h>
#include <unistd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

#define TIMEOUT_TEST(test_code) do {{ \\
    pid_t pid = fork(); \\
    if (pid == 0) {{ \\
        test_code; \\
        exit(0); \\
    }} else if (pid > 0) {{ \\
        int status; \\
        pid_t result = waitpid(pid, &status, WNOHANG); \\
        \\
        for (int i = 0; i < 50 && result == 0; i++) {{ \\
            usleep(100000); /* Sleep 0.1 seconds */ \\
            result = waitpid(pid, &status, WNOHANG); \\
        }} \\
        \\
        if (result == 0) {{ \\
            printf("Timeout!\\n"); \\
            kill(pid, SIGKILL); \\
            waitpid(pid, &status, 0); \\
        }} else if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {{ \\
            printf("Passed!\\n"); \\
        }} else {{ \\
            printf("Failed!\\n"); \\
        }} \\
    }} else {{ \\
        perror("Failed!"); \\
    }} \\
}} while(0)

#define OPTISCOPE_TESTS_NO_MAIN

#include "optiscope/tests.c"

// TODO: this should be injected into tests.c in order not to crash on failures
//#undef assert
//#define assert(expr) \\
//    ((expr) ? (void)0 : \\
//     fprintf(stderr, "Assertion failed: %s, file %s, line %d\\n", \\
//             #expr, __FILE__, __LINE__))

{funcs}

int main(void) {{
  {tests}
}}
"""


funcs = ""
cases = ""
TESTS = open("tests").readlines()
for l in TESTS:
    bruijn, tests = l.split(": ")
    left, right = tests.split(" - ")

    cases += f'TIMEOUT_TEST(TEST_CASE(func{funcId}, "{toLambda(right)}"));\n'
    funcs += f"// {bruijn}\n"
    funcs += toC(left)

with open(f"optiscopeTests.c", "w") as f:
    f.write(genFile(funcs, cases))

subprocess.run(["cc", "optiscopeTests.c", "optiscope/optiscope.c"])
out = subprocess.check_output("./a.out", stderr=subprocess.STDOUT).decode(
    "utf-8"
)

print("passed:", out.count("Good:"))
print("timeout:", out.count("Timeout!"))
print("failed:", out.count("Failed!"))  # TODO: does not count NF mismatches
