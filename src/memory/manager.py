from collections import deque
from datetime import datetime, UTC
import tiktoken


class TokenLimitedMemoryBuffer:
    def __init__(self, max_tokens=3000, encoding_name="cl100k_base"):
        self.buffer = deque()
        self.max_tokens = max_tokens
        self.total_tokens = 0
        self.encoding = tiktoken.get_encoding(encoding_name)

    def _count_tokens(self, text):
        return len(self.encoding.encode(text))

    def add_message(self, role, content):
        tokens = self._count_tokens(content)
        timestamp = datetime.now(UTC)
        message = {
            "role": role,
            "content": content,
            "tokens": tokens,
            "timestamp": timestamp
        }

        self.buffer.append(message)
        self.total_tokens += tokens
        self._trim_buffer()

    def _trim_buffer(self):
        while self.total_tokens > self.max_tokens and self.buffer:
            removed = self.buffer.popleft()
            self.total_tokens -= removed["tokens"]

    def get_context(self):
        return list(self.buffer)
    
    def get_context_markdown(self):
        """
        Return the buffer as a single Markdown-formatted string.
        Example:
        ### User:
        Hello, how are you?

        ### Assistant:
        I'm good, thank you!
        """
        lines = []
        for msg in self.buffer:
            role_header = f"### {msg['role'].capitalize()}:"
            lines.append(f"{role_header}\n{msg['content']}\n")
        return "\n".join(lines)


    def get_token_count(self):
        return self.total_tokens

    def __repr__(self):
        return "\n".join([
            f"[{msg['timestamp']}] {msg['role'].capitalize()}: {msg['content']}"
            for msg in self.buffer
        ])



if __name__ == "__main__":
    memory = TokenLimitedMemoryBuffer(max_tokens=30)  # Small limit to see trimming

    # Sample messages
    messages = [
        ("user", "Hello, how are you?"),
        ("assistant", "I'm good! How can I help you today?"),
        ("user", "Tell me about the weather in Vancouver."),
        ("assistant", "Sure! Vancouver is currently cloudy with some light rain."),
        ("user", "What's the forecast for the weekend?"),
        ("assistant", "It's expected to be sunny and warm this weekend.")
    ]

    for role, content in messages:
        memory.add_message(role, content)
        print(f"\n📥 Added: {role} → '{content}'")
        print(f"🧠 Current Token Count: {memory.get_token_count()}")
        print("📝 Buffer State:")
        print(memory.get_context_markdown())
        print("-" * 50)