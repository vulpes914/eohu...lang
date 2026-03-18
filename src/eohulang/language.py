from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DECLARATION_KEYS = {
    "ㅇㅎ": "+",
    "대꼴": "-",
    "후방주의": ">",
    "19": "<",
    "꼴.": ".",
    "꼴,": ",",
}

RESERVED_TOKENS = {
    "어흐ㅋㅋ": "[",
    "ㅗㅜㅑ": "]",
}

DEFAULT_DECLARATIONS = {
    "ㅇㅎ": "어흐.",
    "대꼴": "어흐,",
    "후방주의": "어흐..",
    "19": "어흐,,",
    "꼴.": "어흐...",
    "꼴,": "어흐,,,",
}

DEFAULT_BODY_MAP = {
    "어흐.": "+",
    "어흐,": "-",
    "어흐..": ">",
    "어흐,,": "<",
    "어흐...": ".",
    "어흐,,,": ",",
    **RESERVED_TOKENS,
}

DEFAULT_DECLARATION_ORDER = ["ㅇㅎ", "대꼴", "후방주의", "19", "꼴.", "꼴,"]


class EohulangError(ValueError):
    """Raised when an 어흐랭 program is invalid."""


@dataclass(slots=True)
class ParsedProgram:
    declarations: dict[str, str]
    body_tokens: list[str]
    brainfuck: str


def strip_comment(line: str) -> str:
    return line.split("#", 1)[0].strip()


def parse_declaration(line: str) -> tuple[str, str]:
    if "=" not in line:
        raise EohulangError(f"잘못된 선언문입니다: {line}")
    key, token = (part.strip() for part in line.split("=", 1))
    if key not in DECLARATION_KEYS:
        raise EohulangError(f"알 수 없는 선언 키워드입니다: {key}")
    if token not in DEFAULT_BODY_MAP or token in RESERVED_TOKENS:
        raise EohulangError(f"선언에 사용할 수 없는 토큰입니다: {token}")
    return key, token


def parse_program(source: str) -> ParsedProgram:
    declarations: dict[str, str] = {}
    body_fragments: list[str] = []

    for raw_line in source.splitlines():
        line = strip_comment(raw_line)
        if not line:
            continue
        if "=" in line:
            key, token = parse_declaration(line)
            declarations[key] = token
        else:
            body_fragments.append(line)

    missing = [key for key in DEFAULT_DECLARATION_ORDER if key not in declarations]
    if missing:
        missing_list = ", ".join(missing)
        raise EohulangError(f"필수 선언이 없습니다: {missing_list}")

    used_tokens = list(declarations.values())
    if len(set(used_tokens)) != len(used_tokens):
        raise EohulangError("선언 토큰은 서로 달라야 합니다.")

    token_to_bf = {token: DECLARATION_KEYS[key] for key, token in declarations.items()}
    token_to_bf.update(RESERVED_TOKENS)

    body = "".join(body_fragments)
    body_tokens = tokenize_body(body, token_to_bf)
    brainfuck = "".join(token_to_bf[token] for token in body_tokens)
    validate_brackets(brainfuck)

    return ParsedProgram(
        declarations=declarations,
        body_tokens=body_tokens,
        brainfuck=brainfuck,
    )


def tokenize_body(body: str, token_to_bf: dict[str, str]) -> list[str]:
    tokens = sorted(token_to_bf, key=len, reverse=True)
    index = 0
    parsed: list[str] = []

    while index < len(body):
        if body[index].isspace():
            index += 1
            continue

        match = next((token for token in tokens if body.startswith(token, index)), None)
        if match is None:
            snippet = body[index : index + 12]
            raise EohulangError(f"본문을 해석할 수 없습니다: {snippet!r}")
        parsed.append(match)
        index += len(match)

    return parsed


def validate_brackets(brainfuck: str) -> None:
    depth = 0
    for instruction in brainfuck:
        if instruction == "[":
            depth += 1
        elif instruction == "]":
            depth -= 1
            if depth < 0:
                raise EohulangError("ㅗㅜㅑ가 어흐ㅋㅋ보다 먼저 나왔습니다.")
    if depth != 0:
        raise EohulangError("어흐ㅋㅋ와 ㅗㅜㅑ의 개수가 맞지 않습니다.")


def run_brainfuck(program: str, input_text: str = "") -> str:
    jumps = build_jump_table(program)
    tape = [0]
    pointer = 0
    pc = 0
    input_index = 0
    output: list[str] = []

    while pc < len(program):
        instruction = program[pc]
        if instruction == ">":
            pointer += 1
            if pointer == len(tape):
                tape.append(0)
        elif instruction == "<":
            if pointer == 0:
                raise EohulangError("테이프 시작점보다 왼쪽으로 이동할 수 없습니다.")
            pointer -= 1
        elif instruction == "+":
            tape[pointer] = (tape[pointer] + 1) % 256
        elif instruction == "-":
            tape[pointer] = (tape[pointer] - 1) % 256
        elif instruction == ".":
            output.append(chr(tape[pointer]))
        elif instruction == ",":
            if input_index < len(input_text):
                tape[pointer] = ord(input_text[input_index]) % 256
                input_index += 1
            else:
                tape[pointer] = 0
        elif instruction == "[" and tape[pointer] == 0:
            pc = jumps[pc]
        elif instruction == "]" and tape[pointer] != 0:
            pc = jumps[pc]
        pc += 1

    return "".join(output)


def build_jump_table(program: str) -> dict[int, int]:
    stack: list[int] = []
    jumps: dict[int, int] = {}

    for index, instruction in enumerate(program):
        if instruction == "[":
            stack.append(index)
        elif instruction == "]":
            if not stack:
                raise EohulangError("닫는 괄호가 먼저 나왔습니다.")
            start = stack.pop()
            jumps[start] = index
            jumps[index] = start

    if stack:
        raise EohulangError("열린 괄호가 닫히지 않았습니다.")

    return jumps


def run_program(source: str, input_text: str = "") -> str:
    parsed = parse_program(source)
    return run_brainfuck(parsed.brainfuck, input_text=input_text)


def compile_bf_to_eohulang(program: str) -> str:
    translated = [DEFAULT_DECLARATIONS_BLOCK(), ""]
    body_lines = [translate_instruction(ch) for ch in program if ch in "><+-.,[]"]
    translated.append(" ".join(body_lines))
    return "\n".join(translated).strip() + "\n"


def translate_instruction(instruction: str) -> str:
    table = {
        "+": DEFAULT_DECLARATIONS["ㅇㅎ"],
        "-": DEFAULT_DECLARATIONS["대꼴"],
        ">": DEFAULT_DECLARATIONS["후방주의"],
        "<": DEFAULT_DECLARATIONS["19"],
        ".": DEFAULT_DECLARATIONS["꼴."],
        ",": DEFAULT_DECLARATIONS["꼴,"],
        "[": "어흐ㅋㅋ",
        "]": "ㅗㅜㅑ",
    }
    return table[instruction]


def DEFAULT_DECLARATIONS_BLOCK() -> str:
    return "\n".join(
        f"{key} = {DEFAULT_DECLARATIONS[key]}" for key in DEFAULT_DECLARATION_ORDER
    )


def read_source(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")
