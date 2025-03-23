import pika, json

import pika.spec

def upload(file, gridfs_instane, rabbitmq_channel, access):
    try:
        file_id = gridfs_instane.put(file)
    except Exception as error:
        return "Internal server error", 500

    message = {
        "video_file_id": str(file_id),
        "mp3_file_id": None,
        "username": access["username"]
    }

    try:
        rabbitmq_channel.basic_publish(
            exchange = "",
            routing_key = "video",
            body = json.dumps(message),
            properties = pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except:
        gridfs_instane.delete(file_id)
        return "Internal server error", 500
    
    