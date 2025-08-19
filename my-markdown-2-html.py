import markdown

# Read the Markdown file
with open("action_items.md", "r") as md_file:
    markdown_content = md_file.read()

# Convert Markdown to HTML
html_content = markdown.markdown(markdown_content)

# Save the HTML to a new file
with open("test_action_items.html", "w") as html_file:
    html_file.write(html_content)

print("Markdown successfully converted to HTML.")