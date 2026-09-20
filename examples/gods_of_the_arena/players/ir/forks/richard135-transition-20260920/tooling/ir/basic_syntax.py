"""Fail-closed parser for the structured scalar BASIC emitted by this binding.

This is a structural reader, not a second runtime. Precedence follows
src/polyworld/basic.nim; execution and integer semantics are tested in that VM.
"""

import re


TOKEN = re.compile(r"\s*(\d+|[a-zA-Z_]\w*|<>|<=|>=|[()+*/=<>,-])")
PRECEDENCE = {"or": 1, "xor": 1, "and": 2, "=": 3, "<>": 3, "<": 3,
              "<=": 3, ">": 3, ">=": 3, "+": 4, "-": 4, "*": 5, "/": 5, "mod": 5}


def tokens(source):
    result = []
    position = 0
    while position < len(source.rstrip()):
        match = TOKEN.match(source, position)
        if not match:
            raise ValueError(f"unsupported BASIC syntax at {source[position:]!r}")
        result.append(match[1].lower())
        position = match.end()
    return result


def expression(source):
    stream = tokens(source)
    position = 0

    def take():
        nonlocal position
        if position >= len(stream):
            raise ValueError("incomplete BASIC expression")
        value = stream[position]
        position += 1
        return value

    def peek():
        return stream[position] if position < len(stream) else ""

    def parse(minimum=1):
        token = take()
        if token in ("+", "-", "not"):
            left = ("unary", token, parse(6))
        elif token == "(":
            left = parse()
            if take() != ")":
                raise ValueError("expected closing parenthesis")
        elif token.isdecimal():
            if int(token) > 2147483647:
                raise ValueError("integer outside supported positive int32 range")
            left = ("int", int(token))
        elif re.fullmatch(r"[a-z_]\w*", token):
            if peek() == "(":
                take()
                args = []
                if peek() != ")":
                    args.append(parse())
                    while peek() == ",":
                        take()
                        args.append(parse())
                if take() != ")":
                    raise ValueError("expected closing call parenthesis")
                left = ("call", token, tuple(args))
            else:
                left = ("var", token)
        else:
            raise ValueError(f"unexpected expression token: {token}")
        while PRECEDENCE.get(peek(), 0) >= minimum:
            op = take()
            left = ("binary", op, left, parse(PRECEDENCE[op] + 1))
        return left

    result = parse()
    if position != len(stream):
        raise ValueError(f"unconsumed expression: {stream[position:]}")
    return result


def parse(source):
    lines = []
    for number, line in enumerate(source.splitlines(), 1):
        line = line.split("'", 1)[0].strip().lower()
        if line and not re.match(r"rem(?:\s|$)", line):
            lines.append((number, line))
    position = 0

    def block(stops=()):
        nonlocal position
        body = []
        while position < len(lines):
            number, line = lines[position]
            if line in stops:
                break
            position += 1
            if line.startswith("if ") and line.endswith(" then"):
                condition = expression(line[3:-5])
                yes = block(("else", "end if"))
                no = ()
                if position < len(lines) and lines[position][1] == "else":
                    position += 1
                    no = block(("end if",))
                require("end if")
                body.append(("if", condition, yes, no))
            elif line.startswith("while "):
                condition = expression(line[6:])
                loop = block(("wend",))
                require("wend")
                body.append(("while", condition, loop))
            elif match := re.fullmatch(r"([a-z_]\w*)\s*=\s*(.+)", line):
                body.append(("assign", match[1], expression(match[2])))
            else:
                value = expression(line)
                if value[0] != "call":
                    raise ValueError(f"unsupported statement on line {number}: {line}")
                body.append(("do", value))
        return tuple(body)

    def require(expected):
        nonlocal position
        if position >= len(lines) or lines[position][1] != expected:
            raise ValueError(f"expected {expected}")
        position += 1

    return block()


def match_template(pattern, actual, parameters):
    """Match all nodes, capturing only declared literal parameter positions."""
    if isinstance(pattern, tuple) and len(pattern) == 2 and pattern[0] == "var":
        if pattern[1].startswith("param_"):
            name = pattern[1][6:]
            if not isinstance(actual, tuple) or actual[0] != "int":
                return False
            if name in parameters and parameters[name] != actual[1]:
                return False
            parameters[name] = actual[1]
            return True
    if isinstance(pattern, tuple):
        return (isinstance(actual, tuple) and len(pattern) == len(actual)
                and all(match_template(p, a, parameters) for p, a in zip(pattern, actual)))
    return pattern == actual
