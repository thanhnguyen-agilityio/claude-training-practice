# Issue [#6](https://github.com/thanhnguyen-agilityio/claude-training-practice/issues/6)
## Title: Conversation freezes after clicking Yes/No approval buttons
## Description:

**Issue**
- When the chatbot asks for approval (for example, "create a support ticket" or "search Google Shopping"), it shows Yes and No buttons.
- After clicking either Yes or No, nothing happens - the conversation just stops.
- Users don't see any response or confirmation that their action was received.
- Users don't know if they need to wait, refresh the page, or try again.
- The conversation appears frozen and users feel stuck.

**Expected**
- After clicking Yes, the chatbot should immediately continue and complete the action.
- After clicking No, the chatbot should acknowledge and continue helping with an alternative solution.
- Users should see visual feedback that their click was registered (e.g., loading indicator, confirmation message).
- The conversation should flow naturally without freezing.

**Example Scenario**
1. User: "I want to create a support ticket"
2. Bot: "We are about to create a support ticket. Please review details... [Yes] [No]"
3. User clicks "Yes"
4. **Current**: Nothing happens, conversation freezes
5. **Expected**: Bot says "Great! I've created your support ticket. Your ticket number is #123. Is there anything else I can help you with?"

**Technical Note from Dev**
- The approve/reject API calls are working on the backend but the response is not handled in the UI.
- No visual feedback or conversation continuation is implemented after button clicks.
