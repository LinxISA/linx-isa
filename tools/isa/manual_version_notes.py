"""Present the fault and usage constraints of a released operation."""

from html import escape


def release_constraints(source, *, base=False, current_name=None):
    roles = source.get("roles", {})
    statements = roles.get("constraints", {}).get("statements", [])
    if current_name is not None:
        from manual_current_prose import golden_constraints

        statements = golden_constraints(current_name, statements)
    if not statements:
        return ""
    label = "基础形式的约束与异常" if base else "约束与异常"
    return (
        '<details class="fault-reference"><summary>'
        + label
        + "（PTO 中文参考）</summary><ul>"
        + "".join("<li>" + escape(v) + "</li>" for v in statements)
        + "</ul></details>"
    )
