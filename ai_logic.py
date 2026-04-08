import re
import ollama

# ====================== WHISPER / ASR CORRECTIONS ======================
def fix_whisper_errors(text: str) -> str:
    """Correct common speech recognition mistakes."""
    text = text.lower().strip()
    # v1's specific replacements
    text = text.replace("slice", "plus")
    text = text.replace("class", "plus")
    text = text.replace("glass", "plus")
    text = text.replace("mine is", "minus")
    text = text.replace("minus", "minus")   # already fine, but safe
    text = text.replace("times", "times")
    text = text.replace("into", "times")
    text = text.replace("divide by", "divided")
    return text

# ====================== WORD TO NUMBER CONVERSION ======================
def words_to_numbers(text: str) -> str:
    """Convert spoken number words to digits (supports up to 99)."""
    word_to_num = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
        "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    }
    
    tokens = text.split()
    i = 0
    while i < len(tokens):
        word = tokens[i].lower().rstrip('.,!?')
        if word in word_to_num:
            num = word_to_num[word]
            # Handle "twenty three", "thirty five", etc.
            if i + 1 < len(tokens):
                next_word = tokens[i + 1].lower().rstrip('.,!?')
                if next_word in word_to_num and word_to_num[next_word] < 10:
                    num = num + word_to_num[next_word]
                    tokens[i] = str(num)
                    del tokens[i + 1]
                    continue
            tokens[i] = str(num)
        i += 1
    return " ".join(tokens)

# ====================== NORMALIZATION ======================
def normalize_text(problem: str) -> str:
    """Convert various natural language expressions into a standard 'n1 op n2' form."""
    if not problem:
        return ""
    
    # 1. Fix whisper errors first
    text = fix_whisper_errors(problem)
    
    # 2. Convert math symbols to words (for easier detection)
    text = re.sub(r'\s*\+\s*', ' plus ', text)
    text = re.sub(r'\s*-\s*', ' minus ', text)
    text = re.sub(r'\s*\*\s*', ' times ', text)
    text = re.sub(r'\s*/\s*', ' divided by ', text)
    text = re.sub(r'\s*x\s*', ' times ', text)      # "12 x 3"
    
    # 3. Word-based replacements (longer phrases first)
    replacements = {
        "added to": " plus ",
        "add": " plus ",
        "take away": " minus ",
        "takeaway": " minus ",
        "subtract": " minus ",
        "subtracted from": " minus from ",
        "take from": " minus from ",
        "multiplied by": " times ",
        "multiply by": " times ",
        "multiply": " times ",
        "into": " times ",
        "divided by": " divided by ",
        "divide by": " divided by ",
        "divide": " divided by ",
    }
    for old, new in sorted(replacements.items(), key=lambda x: -len(x[0])):
        text = text.replace(old, new)
    
    # 4. Clean up spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 5. Convert number words to digits (e.g., "twenty three" -> "23")
    text = words_to_numbers(text)
    
    return text

# ====================== PARSER ======================
def parse_problem(problem: str):
    normalized = normalize_text(problem)
    print(f"[DEBUG] Normalized: '{normalized}'")
    
    # Detect operation
    op_patterns = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "divided by": "/",
        "divided": "/"
    }
    op = None
    normalized_lower = normalized.lower()
    for word, symbol in op_patterns.items():
        if word in normalized_lower:
            op = symbol
            break
    
    # Fallback for raw symbols (if words failed)
    if op is None:
        if '-' in normalized:
            op = "-"
        elif '+' in normalized:
            op = "+"
        elif '*' in normalized or 'x' in normalized_lower:
            op = "*"
        elif '/' in normalized:
            op = "/"
    
    if op is None:
        raise ValueError(f"Unsupported operation. Normalized: '{normalized}'")
    
    # Extract numbers
    nums = re.findall(r'\b\d+\b', normalized)
    if len(nums) != 2:
        raise ValueError(f"Exactly two numbers required. Found {len(nums)} in: '{normalized}'")
    
    n1 = int(nums[0])
    n2 = int(nums[1])
    
    # Handle "subtract 8 from 20" → 20 - 8
    if "minus from" in normalized_lower:
        n1, n2 = n2, n1
    
    if n1 < 0 or n2 < 0:
        raise ValueError("Negative numbers not supported in abacus tutor")
    
    return n1, n2, op

# ====================== CALCULATION ======================
def calculate(n1: int, n2: int, op: str) -> int:
    if op == "+":
        return n1 + n2
    if op == "-":
        return n1 - n2
    if op == "*":
        return n1 * n2
    if op == "/":
        if n2 == 0:
            raise ValueError("Cannot divide by zero")
        return n1 // n2
    raise ValueError(f"Unknown operation: {op}")

# ====================== STEP GENERATORS ======================
def generate_addition_steps(n1: int, n2: int):
    t1, o1 = divmod(n1, 10)
    t2, o2 = divmod(n2, 10)
    steps = []
    ones = o1 + o2
    carry = ones // 10
    steps.append(f"Ones place: {o1} + {o2} = {ones}")
    if carry:
        steps.append(f"Carry {carry} to tens place")
    tens = t1 + t2 + carry
    steps.append(f"Tens place: {t1} + {t2} + {carry} = {tens}")
    return steps

def generate_subtraction_steps(n1: int, n2: int):
    t1, o1 = divmod(n1, 10)
    t2, o2 = divmod(n2, 10)
    steps = []
    if o1 < o2:
        steps.append(f"Ones: {o1} < {o2}, borrow 1 from tens")
        o1 += 10
        t1 -= 1
    steps.append(f"Ones: {o1} - {o2} = {o1 - o2}")
    steps.append(f"Tens: {t1} - {t2} = {t1 - t2}")
    return steps

def generate_multiplication_steps(n1: int, n2: int):
    steps = []
    total = 0
    for i in range(n2):
        prev = total
        total += n1
        steps.append(f"Add {n1} again: {prev} + {n1} = {total}")
    return steps

def generate_division_steps(n1: int, n2: int):
    quotient = n1 // n2
    remainder = n1 % n2
    steps = [
        f"Divide {n1} into groups of {n2}",
        f"Number of complete groups: {quotient}"
    ]
    if remainder:
        steps.append(f"Remainder: {remainder}")
    return steps

# ====================== PROMPT BUILDER ======================
def build_prompt(steps, result):
    steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    return f"""You are a strict abacus teacher.

STRICT RULES - DO NOT BREAK ANY:
- Explain ONLY the exact steps provided below.
- Use EXACTLY the numbers and words from the steps.
- NEVER reinterpret, recalculate, add extra steps, or change any value.
- For carry, say exactly "Carry X to tens place".
- Speak calmly, clearly, and educationally with short sentences.
- End with the final result exactly as given.

Official Steps:
{steps_text}

Final Result: {result}

Now explain these steps in natural spoken English. Do not add anything else."""

# ====================== MAIN FUNCTION ======================
def get_abacus_explanation(problem: str):
    try:
        n1, n2, op = parse_problem(problem)
        result = calculate(n1, n2, op)

        if op == "+":
            steps = generate_addition_steps(n1, n2)
        elif op == "-":
            steps = generate_subtraction_steps(n1, n2)
        elif op == "*":
            steps = generate_multiplication_steps(n1, n2)
        elif op == "/":
            steps = generate_division_steps(n1, n2)
        else:
            raise ValueError("Unsupported operation")

        prompt = build_prompt(steps, result)

        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': (
                    "You are an extremely strict, rule-following abacus tutor. "
                    "Explain ONLY the given steps using exactly the numbers and words provided. "
                    "Never reinterpret math, never add extra logic, never correct anything."
                )},
                {'role': 'user', 'content': prompt},
            ],
            options={"temperature": 0.0, "top_p": 0.1, "num_predict": 400}
        )
        explanation = response['message']['content'].strip()

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")

    return {
        "problem": problem.strip(),
        "operation": op,
        "result": result,
        "steps": steps,
        "explanation": explanation
    }