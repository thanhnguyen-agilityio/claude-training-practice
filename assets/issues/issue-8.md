# Issue [#8](https://github.com/thanhnguyen-agilityio/claude-training-practice/issues/8)
## Title: Chat messages disappear without warning or explanation
## Description:

**Issue**
- During long conversations, older messages suddenly disappear from the chat history.
- Users don't receive any warning or explanation about why this is happening.
- Users worry that:
  - The chatbot has forgotten their earlier questions and context
  - Something is broken or malfunctioning
  - Important information from the conversation is lost
- This creates confusion and erodes trust in the system.
- Users don't know if they should repeat earlier information or if the bot still remembers.

**Expected**
- When the chatbot needs to summarize the conversation, notify the user clearly.
- Show a friendly message like:
  - "💡 This conversation is getting long. I've summarized our earlier discussion to keep things focused. Don't worry - I still remember everything we talked about!"
  - Or: "📝 To keep things running smoothly, I've created a summary of our conversation so far. Your earlier messages are saved in the summary."
- Optionally, allow users to view the summary or expand to see older messages.
- Build trust by being transparent about what's happening.

**Current Behavior** (from dev team)
- After approximately 5-6 messages back and forth, the system automatically summarizes older messages to manage conversation length.
- The summarization happens silently without any user notification.
- Messages are trimmed when the conversation reaches about 1000 tokens.
- While the chatbot retains context through summarization, users can't see this happening.

**Benefits of Fixing This**
- Increases user trust and confidence in the system.
- Reduces confusion about "missing" messages.
- Users understand the chatbot still remembers their context.
- Makes the system feel more professional and polished.
- Related to Issue #2 - this explains why messages appear to be "cut off."
