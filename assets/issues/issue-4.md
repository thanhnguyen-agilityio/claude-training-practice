# Issue [#4](https://github.com/thanhnguyen-agilityio/claude-training-practice/issues/4)
## Title: Quick start examples are too long and not interactive
## Description:

**Issue**
- The Quick Start section shows a long list of example questions that users have to read and manually type.
- Users need to copy the text or type it themselves, which creates unnecessary friction.
- The expander shows too much text at once, which can be overwhelming for first-time users.
- Users might not realize these are example queries they can try.

**Expected**
- Quick start examples should be clickable buttons or chips that users can tap to try them immediately.
- Instead of showing all examples in one long list, organize them by category with clickable options.
- When a user clicks an example, it should automatically send that query to the chatbot.
- This would be especially helpful when the conversation first starts - show a few suggested queries right above the input box.

**Example of Better UX**
- Show 3-4 clickable suggestions like:
  - 🏷️ "Show me categories"
  - 📦 "Do you offer free shipping?"
  - 👗 "Find me a dress"
- When clicked, the query is automatically sent instead of requiring the user to type.
