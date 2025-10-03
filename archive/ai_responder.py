"""Responder: simple function that uses context to craft answer. Designed to be replaced by real LLM calls."""
class Responder:
    def respond(self, context, prompt):
        # Basic heuristics: if ask about a file, try to list file summary if in context
        import re
        m = re.search(r'(explain|show|open|what).*(\.py|\.js|\.html|file)', prompt, re.I)
        if m:
            # try to find first matching file
            files = context.get('files',{})
            if files:
                f = list(files.keys())[0]
                return f"(placeholder) I see {len(files)} files. Example: {f}. You asked: {prompt}"
        # default reply includes scanner summaries
        keys = ', '.join(context.get('summary',{}).keys())
        return f"(placeholder) Context has scanners: {keys}. You asked: {prompt}"

if __name__ == "__main__":
    print("Responder 仅作为模块使用，不建议直接运行。")
