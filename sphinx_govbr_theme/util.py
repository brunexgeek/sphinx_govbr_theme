def normalize_path(path: str) -> str:
    """
    Normalize a Sphinx-style abstract POSIX path (docname or URI-like),
    resolving '.' and '..' without filesystem access.

    Rules aligned with Sphinx docname semantics:
    - '.' is ignored
    - '..' pops previous segment if possible
    - absolute paths cannot go above root
    - relative paths preserve leading '..' if necessary
    """

    if path is None:
        return ""

    absolute = path.startswith("/")
    parts = path.split("/")

    stack = []

    for part in parts:
        if part == "" or part == ".":
            continue

        if part == "..":
            if stack and stack[-1] != "..":
                # normal backtracking
                stack.pop()
            else:
                # cannot resolve further
                # only allowed to accumulate for relative paths
                if not absolute:
                    stack.append("..")
        else:
            stack.append(part)

    normalized = "/".join(stack)

    if absolute:
        return "/" + normalized if normalized else "/"

    return normalized or "."