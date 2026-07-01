from pathlib import Path
import json
import ast


def load_debugging_prompt() -> dict:
    prompt_path = Path(__file__).resolve().parent / "prompts" / "debugging_prompt.json"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Debugging prompt JSON not found at: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_debugging_prompt(user_input: str) -> str:
    prompt_json = load_debugging_prompt()
    system_instruction = prompt_json["system_instruction"]
    template = prompt_json["user_prompt_template"]

    full_prompt = (
        system_instruction + "\n\n" +
        template.replace("{{USER_INPUT}}", user_input.strip())
    )
    return full_prompt


def analyze_code_complexity(code: str) -> dict:
    """Analyze Python code complexity without AI."""
    lines = [l for l in code.strip().splitlines() if l.strip()]
    line_count = len(lines)

    if line_count <= 20:
        complexity = "🟢 Simple"
    elif line_count <= 50:
        complexity = "🟡 Moderate"
    else:
        complexity = "🔴 Complex"

    # Count functions and classes
    functions = 0
    classes = 0
    loops = 0
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, (ast.For, ast.While)):
                loops += 1
    except Exception:
        pass  # If code has syntax errors, skip AST analysis

    # Quick syntax check
    syntax_ok = True
    syntax_error = None
    try:
        ast.parse(code)
    except SyntaxError as e:
        syntax_ok = False
        syntax_error = str(e)

    return {
        "line_count": line_count,
        "complexity": complexity,
        "functions": functions,
        "classes": classes,
        "loops": loops,
        "syntax_ok": syntax_ok,
        "syntax_error": syntax_error
    }


def extract_severity(response: str) -> str:
    """Extract severity level from AI response."""
    upper = response.upper()
    if "SEVERITY** HIGH" in upper or "SEVERITY: HIGH" in upper or "**HIGH**" in upper:
        return "HIGH"
    elif "SEVERITY** MEDIUM" in upper or "SEVERITY: MEDIUM" in upper or "**MEDIUM**" in upper:
        return "MEDIUM"
    elif "SEVERITY** LOW" in upper or "SEVERITY: LOW" in upper or "**LOW**" in upper:
        return "LOW"
    return "MEDIUM"


def extract_fixed_code(response: str) -> str:
    """Extract fixed code block from AI response."""
    if "```python" in response:
        start = response.find("```python") + 9
        end = response.find("```", start)
        if end > start:
            return response[start:end].strip()
    return ""
