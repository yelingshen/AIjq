from fastapi import FastAPI, HTTPException
import asyncio
from pydantic import BaseModel
from typing import Any, Dict

from ai.model_loader import ModelLoader

app = FastAPI()


class GenerateRequest(BaseModel):
    model: str
    prompt: str


@app.post('/api/generate')
async def generate(req: GenerateRequest) -> Dict[str, Any]:
    try:
        ml = ModelLoader()
        load_res = ml.load_model(model_path=req.model, backend='ollama')
        if load_res.get('error'):
            raise HTTPException(status_code=500, detail=load_res.get('error'))
        adapter_cls = ml.adapters.get('ollama')
        adapter = adapter_cls()

        # Prefer async interface if available
        if hasattr(adapter, 'ainfer') and callable(getattr(adapter, 'ainfer')):
            out = await adapter.ainfer(load_res['model'], req.prompt)
        else:
            # run sync infer in threadpool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            out = await loop.run_in_executor(None, lambda: adapter.infer(load_res['model'], req.prompt))

        if isinstance(out, dict) and 'text' in out:
            return {'text': out.get('text'), 'meta': out.get('meta', {})}
        return {'text': str(out), 'meta': {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
