import re

line = "            with it('should consist of one rule file'):"
print(f"Testing line: {line}")
print(f"Contains 'with it('? {('with it(' in line)}")

match = re.search(r"with it\(['\"]([^'\"]+)['\"]", line)
if match:
    print(f"MATCHED: {match.group(1)}")
else:
    print("NO MATCH")
    print("Regex expects: with it('text') ")
    print(f"Line has: {line.strip()}")

