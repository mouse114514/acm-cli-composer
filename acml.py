def parse_acml(filepath):
    """Parse .acml file, return (name, bpm, loop, tracks_list)."""
    with open(filepath, encoding="utf-8-sig") as f:
        content = f.read()
    content = _unroll_repeats(content)
    return _parse_acml_lines(content)


def _unroll_repeats(content):
    """Unroll [repeat N]...[/repeat] blocks (supports nesting)."""
    lines = content.split("\n")
    result = []
    stack = []  # [(count, [lines])]
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[repeat ") and stripped.endswith("]"):
            count = int(stripped[8:-1].strip())
            stack.append((count, []))
        elif stripped == "[/repeat]":
            if not stack:
                continue
            count, block = stack.pop()
            repeated = block * count
            if stack:
                stack[-1][1].extend(repeated)
            else:
                result.extend(repeated)
        elif stack:
            stack[-1][1].append(line)
        else:
            result.append(line)
    return "\n".join(result)


def _parse_acml_lines(content):
    name = "untitled"
    bpm = 120
    loop = 1
    tracks = []
    current = None

    lines = _join_continuation_lines(content.split("\n"))

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("[") and line.endswith("]"):
            if current is not None:
                tracks.append(current)
            label = line[1:-1].strip()
            if label.startswith("track "):
                label = label[6:]
            current = {"name": label}
            continue

        key, val = _split_key_value(line)
        if key is None:
            continue

        if current is not None:
            current[key] = val
        elif key == "name":
            name = val
        elif key == "bpm":
            bpm = int(val)
        elif key == "loop":
            loop = int(val)

    if current is not None:
        tracks.append(current)

    return name, bpm, loop, tracks


def _join_continuation_lines(lines):
    """Join lines ending with + to the next line (strips leading whitespace on continuation).
    Inserts ,, at bar boundaries (where + was) so expand_compact_notes can group bars."""
    result = []
    pending = None
    for line in lines:
        if pending is not None:
            # Strip trailing comma from pending, then add bar separator ,,
            pending = pending.rstrip()
            if pending.endswith(","):
                pending = pending[:-1]
            pending += ",," + line.lstrip()
            if line.rstrip().endswith("+"):
                pending = pending.rstrip()[:-1]
            else:
                result.append(pending)
                pending = None
        elif line.rstrip().endswith("+"):
            pending = line.rstrip()[:-1]
        else:
            result.append(line)
    if pending is not None:
        result.append(pending)
    return result


def _split_key_value(line):
    for sep in ("=", ":"):
        if sep in line:
            idx = line.index(sep)
            key = line[:idx].strip().lower()
            raw = line[idx + 1:].strip()
            if raw[:1] in ('"', "'"):
                # Quoted value: keep everything up to the closing quote (no comment stripping)
                quote = raw[0]
                end = raw.find(quote, 1)
                val = raw[1:end] if end != -1 else raw[1:]
            else:
                # Unquoted: '#' starts a comment only when preceded by whitespace,
                # so sharp note names like F#1 / C#4 stay intact.
                comment = None
                for i, ch in enumerate(raw):
                    if ch == "#" and (i == 0 or raw[i - 1].isspace()):
                        comment = i
                        break
                val = raw[:comment] if comment is not None else raw
                val = val.strip()
            return key, val
    return None, None
