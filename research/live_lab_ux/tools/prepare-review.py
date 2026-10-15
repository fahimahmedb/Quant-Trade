"""Package review captures and same-world fallback assets; no semantic image editing."""
from pathlib import Path
from shutil import copy2
from PIL import Image
import json
root=Path(__file__).resolve().parents[1]
review=root/'review';review.mkdir(exist_ok=True)
for name in ['laboratory-idle','laboratory-idle-mobile']:
    path=root/'assets'/f'{name}.png'
    if path.exists():
        Image.open(path).save(path.with_suffix('.webp'),quality=92)
        path.unlink()
for name in ['A_IDLE','B_ACTIVE','C_SELECTED','D_ECONOMIC','E_IPHONE','F_FALLBACK']:
    path=root/'artifacts'/f'{name}.png'
    if path.exists():copy2(path,review/path.name)
for name in ['capture-manifest.json','browser-qa.json']:
    path=root/'artifacts'/name
    if path.exists():copy2(path,review/path.name)
labels={'A_IDLE':'A · Connected / no work','B_ACTIVE':'B · Explicit native activity','C_SELECTED':'C · Camera focus / optional context','D_ECONOMIC':'D · Explicit reducer Economic Look','E_IPHONE':'E · iPhone portrait (emulated)','F_FALLBACK':'F · Forced illustrated fallback'}
cards=''.join(f'<figure><a href="{name}.png"><img src="{name}.png" loading="lazy" alt="{label}"></a><figcaption>{label}</figcaption></figure>' for name,label in labels.items() if (review/f'{name}.png').exists())
(review/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quant · Integrated visual review</title><style>body{margin:0;padding:28px;background:#0e2030;color:#d3dde3;font:14px system-ui}h1{font-weight:450;font-size:22px}p{max-width:800px;line-height:1.6;color:#a1b1bc}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,450px),1fr));gap:22px}figure{margin:0;background:#152c3e}img{display:block;width:100%;max-height:650px;object-fit:contain}figcaption{padding:14px;color:#ceb38b}a{color:#d5bc98}</style><h1>Quant · Integrated owner visual review</h1><p>All activity is synthetic and explicitly marked. A/B/C/E exercise the real live entry, native mapper and reducer using a browser-only EventSource mock. D is an explicit Economic Look reducer fixture. No production event, research result or deployment is claimed.</p><p>PRODUCTION_REPLACEMENT_AUTHORIZED = FALSE · VISUAL_REVIEW_REQUIRED = TRUE</p><main>'''+cards+'</main><p><a href="capture-manifest.json">Capture provenance</a> · <a href="browser-qa.json">Browser checks</a> · <a href="../index.html">Interactive isolated review</a></p></html>')
print('Review package prepared')
