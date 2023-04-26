def parse_string(s):
    """
    Try parsing a string as an int or float;
    otherwise leave it as a string.
    """
    try:
        f = float(s)
    except ValueError:
        return s

    if f == int(f):
        return int(f)
    return f


def parse(f):
    """Parse a file to Python objects.
    Example:
                        =>    [
      Version 8 2       =>      ("Version", 8, 2),
      {                 =>      [
        Foo Bar 1       =>        ("Foo", "Bar", 1),
        Baz             =>        ("Baz",),
        {               =>        [
          1.2 3.4       =>          (1.2, 3.4),
        }               =>        ],
      }                 =>      ],
                        =>    ]
    """
    cur = []
    stack = [cur]

    for line in f:
        line = line.strip()
        if not line:
            continue
        if line == "{":
            cur.append([])
            cur = cur[-1]
            stack.append(cur)
        elif line == "}":
            stack.pop()
            cur = stack[-1]
        else:
            cur.append(
                tuple(parse_string(s) for s in line.split(" "))
            )

    assert len(stack) == 1, "mismatched {} during parse"

    return stack[0]


def get_key(lines, key):
    """
    Get the value of a line that starts with a given key.
    """
    for line in lines:
        if line[0] == key:
            return line[1] if len(line) == 2 else line[1:]
    return None


def get_after_key(lines, key):
    """
    Get the line/block after a line that starts with a given key.
    """
    for i, line in enumerate(lines):
        if line[0] == key and i + 1 < len(lines):
            return lines[i + 1]
    return None
