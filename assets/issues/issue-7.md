# Issue [#7](https://github.com/thanhnguyen-agilityio/claude-training-practice/issues/7)
## Title: No clear feedback on what the chatbot is doing
## Description:

**Issue**
- After asking a question, users only see a generic "Thinking..." message.
- Users cannot tell what the chatbot is actually doing or if it's working properly.
- For complex requests, users don't know if the system is:
  - Searching the product database
  - Looking up policies
  - Creating a support ticket
  - Comparing products
  - Stuck or frozen
- This creates anxiety and uncertainty, especially when responses take a few seconds.
- Users sometimes think the app is broken and refresh the page or give up.

**Expected**
- Show progressive status updates that tell users what's happening in real-time.
- Examples of helpful status messages:
  - "Searching product database..."
  - "Found 3 matching products, comparing details..."
  - "Looking up our return policy..."
  - "Creating your support ticket..."
  - "Searching for similar items..."
- This builds trust and keeps users engaged while waiting.
- Users understand the chatbot is actively working on their request.

**Benefits**
- Reduces user anxiety during wait times.
- Makes the system feel more transparent and trustworthy.
- Helps users understand what capabilities the chatbot has.
- Prevents users from abandoning the conversation during processing.

**Example Flow**
1. User: "Compare product A and product B"
2. Bot shows: "🔍 Searching product database..."
3. Bot shows: "✓ Found both products"
4. Bot shows: "📊 Comparing features and prices..."
5. Bot shows the comparison result
