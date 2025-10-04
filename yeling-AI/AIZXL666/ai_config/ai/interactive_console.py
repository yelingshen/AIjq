"""Simple interactive console using cached context and model if available."""
import asyncio, readline, os
from utils.memory_cache import MemoryCache
from ai.context_manager import ContextManager
from ai.model_loader import ModelLoader
from ai.responder import Responder
async def main():
    cache = MemoryCache()
    ctxm = ContextManager(cache=cache)
    ml = ModelLoader()
    ml_info = ml.load_model()
    print('Interactive console. Type exit to quit.')
    while True:
        q = input('> ')
        if q.strip().lower() in ('exit','quit'): break
        ctx = cache.get('latest_context') or {'summary':{}}
        # if model available, call simple backend or fallback to responder
        if ml_info and ml_info.get('backend') in ('pygpt4all','llama-cpp'):
            try:
                model = ml_info.get('model')
                # for pygpt4all, call model.generate; for llama-cpp, call model.create
                if ml_info['backend']=='pygpt4all':
                    ans = model.generate(q)
                else:
                    ans = model.create(q)['choices'][0]['text']
                print(ans)
                continue
            except Exception:
                pass
        print(Responder().respond(ctx, q))
if __name__ == "__main__":
    print("InteractiveConsole 仅作为模块使用，不建议直接运行。")
