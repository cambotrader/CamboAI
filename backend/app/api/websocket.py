from __future__ import annotations
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import logging
from app.services.websocket_manager import manager, broadcaster

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    connection_id: Optional[str] = Query(None)
):
    """
    Main WebSocket endpoint for real-time CamboAI updates.
    
    Supported message types:
    - subscribe: {"type": "subscribe", "topic": "prices|alerts|sentiment|prices_AAPL"}
    - unsubscribe: {"type": "unsubscribe", "topic": "topic_name"}
    - ping: {"type": "ping"}
    """
    
    connection_id = await manager.connect(websocket, connection_id)
    
    try:
        # Start broadcasting if not already running
        await broadcaster.start_broadcasting()
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "message": "Connected to CamboAI real-time feed"
        }, connection_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "")
                
                if message_type == "subscribe":
                    topic = message.get("topic", "")
                    if topic:
                        success = await manager.subscribe(connection_id, topic)
                        await manager.send_personal_message({
                            "type": "subscription_response",
                            "topic": topic,
                            "subscribed": success
                        }, connection_id)
                        
                elif message_type == "unsubscribe":
                    topic = message.get("topic", "")
                    if topic:
                        await manager.unsubscribe(connection_id, topic)
                        await manager.send_personal_message({
                            "type": "unsubscription_response", 
                            "topic": topic,
                            "unsubscribed": True
                        }, connection_id)
                        
                elif message_type == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp", "")
                    }, connection_id)
                    
                elif message_type == "get_stats":
                    stats = manager.get_stats()
                    await manager.send_personal_message({
                        "type": "stats",
                        "data": stats
                    }, connection_id)
                    
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    }, connection_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON message"
                }, connection_id)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Message processing error: {str(e)}"
                }, connection_id)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
    finally:
        manager.disconnect(connection_id)

@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return manager.get_stats()

@router.post("/ws/broadcast")
async def broadcast_message(message: dict, topic: str):
    """
    Broadcast custom message to topic subscribers.
    Admin/testing endpoint.
    """
    count = await manager.broadcast_to_topic(message, topic)
    return {"message": "Broadcast sent", "recipients": count, "topic": topic}