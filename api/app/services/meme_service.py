import subprocess

def process_meme(task_id: str, redis_client):
    task_info = redis_client.hgetall(task_id)
    input_image_path = task_info.get(b"input").decode("utf-8")
    output_image_path = task_info.get(b"output").decode("utf-8")
    top_text = task_info.get(b"top_text").decode("utf-8")
    bottom_text = task_info.get(b"bottom_text").decode("utf-8")

    command = ["/app/app/c_processing/meme_generator", input_image_path, top_text, bottom_text, output_image_path]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        redis_client.hset(task_id, "status", "completed")
    else:
        redis_client.hset(task_id, "status", "failed")
        print(f"Error in processing image: {result.stderr}")
