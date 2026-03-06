
import re

def clean_and_repair(content):
    # exact copy of my function
    if not content: return ""
    clean_content = content.replace("```json", "").replace("```", "").strip()
    if "{" in clean_content:
        match = re.search(r'(\{.*\})', clean_content, re.DOTALL)
        if match:
            clean_content = match.group(1)
            
    # Repair
    print("Before repair:", repr(clean_content))
    clean_content = re.sub(r',\s*}', '}', clean_content)
    clean_content = re.sub(r',\s*\]', ']', clean_content)
    print("After repair: ", repr(clean_content))
    return clean_content

bad_snippet = '{\n"practical_skill_activity_2": "Students bring boxes... commerce.",\n    },\n    {\n      "practical_skill_activity_3": "..."'

print("--- Test 1: Snippet ---")
# Wrap in list to make it sort of valid-ish structure for regex test
test_str = '[\n  ' + bad_snippet + '\n]'
cleaned = clean_and_repair(test_str)

# Verify if the comma after "commerce." is gone.
if 'commerce."\n    }' in cleaned:
    print("✅ Comma removed!")
else:
    print("❌ Comma persisting!", repr(cleaned))
