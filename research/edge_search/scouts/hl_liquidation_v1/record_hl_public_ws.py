#!/usr/bin/env python3
"""Prospective raw-only Hyperliquid market recorder for the frozen liquidation study.

This does NOT obtain market-wide liquidation labels. Those come from a colocated
Hyperliquid non-validating node running:

  hl-visor run-non-validator --write-fills --batch-by-block --disable-output-file-buffering

This process records only public BTC/ETH context: trades, BBO, L2 and
activeAssetCtx (mark/mid context). No account, orders, credentials or capital.
"""
from __future__ import annotations

import argparse, asyncio, json, os, signal, time
from pathlib import Path

WS = "wss://api.hyperliquid.xyz/ws"
COINS = ("BTC", "ETH")
SUB_TYPES = ("trades", "bbo", "l2Book", "activeAssetCtx")


def write_jsonl(f, obj: dict) -> None:
    f.write(json.dumps(obj, separators=(",", ":"), sort_keys=True) + "\n")
    # Flush Python buffering immediately; do not fsync every high-rate L2 frame.
    # Completeness is checked by feed/session markers and BBO staleness in replay.
    f.flush()


async def run(out: Path) -> None:
    try:
        import websockets
    except ImportError as e:
        raise SystemExit("install the 'websockets' package on the recorder host") from e
    out.mkdir(parents=True, exist_ok=True)
    raw_path = out / "market_ws_raw.jsonl"
    sess_path = out / "session_events.jsonl"
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass

    attempt = 0
    with raw_path.open("a", encoding="utf-8", buffering=1) as raw, sess_path.open("a", encoding="utf-8", buffering=1) as sess:
        while not stop.is_set():
            attempt += 1
            try:
                async with websockets.connect(WS, ping_interval=None, close_timeout=5, max_queue=100_000) as ws:
                    write_jsonl(sess, {"kind":"connect","recv_ns":time.time_ns(),"attempt":attempt})
                    for coin in COINS:
                        for typ in SUB_TYPES:
                            await ws.send(json.dumps({"method":"subscribe","subscription":{"type":typ,"coin":coin}}))

                    async def pinger():
                        while True:
                            await asyncio.sleep(30)
                            await ws.send(json.dumps({"method":"ping"}))

                    pt = asyncio.create_task(pinger())
                    try:
                        while not stop.is_set():
                            msg = await asyncio.wait_for(ws.recv(), timeout=65)
                            recv_ns = time.time_ns()  # availability timestamp is taken before JSON parsing
                            obj = json.loads(msg)
                            if isinstance(obj, dict):
                                obj["_recv_ns"] = recv_ns
                            write_jsonl(raw, obj)
                    finally:
                        pt.cancel()
            except Exception as e:
                write_jsonl(sess, {"kind":"disconnect","recv_ns":time.time_ns(),"attempt":attempt,"error":type(e).__name__})
                try:
                    os.fsync(raw.fileno()); os.fsync(sess.fileno())
                except OSError:
                    pass
                if not stop.is_set():
                    await asyncio.sleep(min(30, 2 ** min(attempt, 5)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    args = ap.parse_args()
    asyncio.run(run(Path(args.out_dir)))


if __name__ == "__main__":
    main()
