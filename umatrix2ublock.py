#!/usr/bin/env python
import sys

# Input files
UMATRIX = sys.argv[1]  # "my-umatrix-rules.txt"
UBLOCK_OLD = sys.argv[2]  # "my-ublock-dynamic-rules_2020-02-26_14.07.25.txt"
# Output file
UBLOCK_NEW = "my-ublock-dynamic-rules.txt"


with open(UMATRIX) as fp:
    rules = fp.readlines()


# Dictionaries which translate the rule
# NOTE: Only translated when destination is "*" or src is the same as dest
translate_request = {
    "*": "{request}",
    "image": "{request}",
    "script": "{prefix}-{request}",
    "frame": "{prefix}-{request}",
    "xhr": "inline-script",
}

translate_action = {"allow": "noop", "inherit": "noop", "block": "block"}

# Requests which cannot be translated
skip_requests = ("cookie", "css", "plugin", "media", "other")

skip_rules = (
    "* * * block",
)

ub_rules = []

ub_rules.append(
"""
no-large-media: * true
no-scripting: * true
* * 1p-script block
* * 1p-script block
* * 3p-script block
* * inline-script block
"""
)

for rule in rules:
    rule = rule.rstrip("\n")

    if rule in skip_rules:
        print("Skipping rule:".rjust(15), rule)
        continue

    words = rule.split()
    if len(words) == 4:
        # Is a site specific rule
        src, dest, request, action = words

        if request in skip_requests:
            print("Skipping req:".rjust(15), rule)
            continue

        ub_action = translate_action[action]

        if dest == "*" or src == dest:
            # First party or third party
            prefix = "1p" if src == dest else "3p"
            dest = "*"

            ub_request = translate_request[request].format(
                prefix=prefix, request=request
            )

            if ub_request == "1p-script":
                ub_rules.append(f"{src} {dest} inline-script {ub_action}\n")
                ub_rules.append(f"{src} {dest} xmlhttprequest {ub_action}\n")
            if src != "*" and ub_action == "noop":
                ub_rules.append(f"no-scripting: {src} false\n")
        else:
            ub_request = "*"

        ub_rule = f"{src} {dest} {ub_request} {ub_action}"
        print("Adding:".rjust(15), ub_rule)
        ub_rules.append(ub_rule + "\n")
    else:
        # Is a global rule
        continue

with open(UBLOCK_OLD) as old:
    #  ub_rules_old = {rule + "\n" for rule in old.readlines()}
    ub_rules_old = set(old.readlines())

# Make a union of old and new uBlock rules
ub_rules_merged = sorted(ub_rules_old.union(ub_rules))


with open(UBLOCK_NEW, "w") as fp:
    fp.writelines(ub_rules_merged)
