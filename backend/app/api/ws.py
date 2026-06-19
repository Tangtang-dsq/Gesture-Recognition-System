from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.core.dynamic_classifier import DynamicClassifier, SessionContext
from app.core.features import validate_feature
from app.core.postprocess import Stabilizer, StaticStabilizer
from app.core.static_classifier import StaticClassifier

router = APIRouter()
static_classifier = StaticClassifier.load()
dynamic_classifier = DynamicClassifier.load()


@router.websocket("/ws/recognize")
async def recognize(ws: WebSocket) -> None:
    await ws.accept()
    ctx = SessionContext(seq_len=settings.seq_len)
    static_stabilizer = StaticStabilizer(
        threshold=settings.conf_threshold,
        vote_n=3,
        vote_min=2,
    )
    dynamic_stabilizer = Stabilizer(
        threshold=settings.conf_threshold,
        vote_n=settings.vote_n,
        vote_min=settings.vote_min,
        cooldown_seconds=settings.cooldown_seconds,
    )

    try:
        while True:
            msg = await ws.receive_json()
            if msg.get("type") == "reset":
                ctx.reset()
                await ws.send_json({"type": "ready"})
                continue
            if msg.get("type") != "frame":
                continue

            try:
                feature = validate_feature(msg.get("feature", []))
            except ValueError as exc:
                await ws.send_json({"type": "error", "message": str(exc), "ts": msg.get("ts")})
                continue

            if msg.get("mode") == "dynamic":
                predicted = dynamic_classifier.update(ctx, feature)
                label, confidence = predicted if predicted else (None, 0.0)
                stable = dynamic_stabilizer.stabilize(label, confidence)
            else:
                label, confidence = static_classifier.predict(feature)
                stable = static_stabilizer.stabilize(label, confidence)

            await ws.send_json(
                {
                    "type": "result",
                    "label": stable,
                    "rawLabel": label,
                    "confidence": confidence,
                    "mode": msg.get("mode", "static"),
                    "ts": msg.get("ts"),
                }
            )
    except WebSocketDisconnect:
        return
