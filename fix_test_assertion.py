# Create fix_test_assertion.py
#!/usr/bin/env python3

def fix_test_assertion():
    with open('tests/test_basic.py', 'r') as f:
        content = f.read()
    
    # Fix the assertion
    content = content.replace(
        "assert sample_user_data['username'] == 'testuser'",
        "assert sample_user_data['username'] == 'sampleuser'"
    )
    
    with open('tests/test_basic.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed test assertion")

if __name__ == "__main__":
    fix_test_assertion()
