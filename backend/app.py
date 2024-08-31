from flask import Flask, request, jsonify
from models.yard import Yard
from models.yard_config import YardConfig
from models.container import Container
from models.database import get_db, engine, Base
from optimizer.optimizer import Optimizer
from utils.csv_parser import parse_csv
from utils.logger import app_logger
from utils.auth import require_auth
from utils.config import config
import os
import threading
import time

app = Flask(__name__)

# Initialize database
Base.metadata.create_all(bind=engine)

# Initialize yard and optimizer
yard_config = YardConfig(
    length=10, width=10, height=5,
    energy_consumption_rate=0.1,
    carbon_emission_factor=0.5,
    max_weight_per_stack=10000,
    crane_speed=2,
    crane_energy_consumption=5
)
yard = Yard(yard_config)
optimizer = Optimizer(yard)

def training_loop():
    while True:
        optimizer.train(batch_size=32)
        time.sleep(60)  # Train every minute

def optimization_loop():
    while True:
        optimizer.reoptimize()
        time.sleep(config.OPTIMIZATION_INTERVAL)

# Start training and optimization loops in separate threads
threading.Thread(target=training_loop, daemon=True).start()
threading.Thread(target=optimization_loop, daemon=True).start()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/upload_csv', methods=['POST'])
@require_auth
def upload_csv():
    if 'file' not in request.files:
        app_logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        app_logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.csv'):
        file_path = os.path.join('/tmp', file.filename)
        file.save(file_path)
        containers = parse_csv(file_path)
        db = next(get_db())
        for container in containers:
            position = optimizer.optimize_placement(container)
            yard.add_container(container, position)
            db.add(container)
        db.commit()
        os.remove(file_path)
        app_logger.info(f"CSV processed successfully: {file.filename}")
        return jsonify({"message": "CSV processed successfully"}), 200
    app_logger.error("Invalid file format")
    return jsonify({"error": "Invalid file format"}), 400

@app.route('/containers', methods=['GET'])
@require_auth
def get_containers():
    containers_data = [
        {
            "id": container.id,
            "weight": container.weight,
            "destination": container.destination,
            "position": yard.get_container_position(container.id)
        }
        for container in yard.containers.values()
    ]
    app_logger.info(f"Retrieved {len(containers_data)} containers")
    return jsonify(containers_data), 200

@app.route('/container/<container_id>', methods=['GET'])
@require_auth
def get_container(container_id):
    container = yard.containers.get(container_id)
    if container:
        container_data = {
            "id": container.id,
            "weight": container.weight,
            "destination": container.destination,
            "arrival_date": container.arrival_date,
            "departure_date": container.departure_date,
            "position": yard.get_container_position(container.id)
        }
        app_logger.info(f"Retrieved container {container_id}")
        return jsonify(container_data), 200
    app_logger.error(f"Container {container_id} not found")
    return jsonify({"error": f"Container {container_id} not found"}), 404

@app.route('/metrics', methods=['GET'])
@require_auth
def get_metrics():
    metrics = optimizer.calculate_metrics()
    app_logger.info("Metrics calculated and retrieved")
    return jsonify(metrics), 200

@app.route('/remove_container/<container_id>', methods=['POST'])
@require_auth
def remove_container(container_id):
    if yard.remove_container(container_id):
        optimizer.reoptimize()
        app_logger.info(f"Container {container_id} removed successfully")
        return jsonify({"message": f"Container {container_id} removed successfully"}), 200
    app_logger.error(f"Container {container_id} not found")
    return jsonify({"error": f"Container {container_id} not found"}), 404

@app.route('/manual_place_container/<container_id>', methods=['POST'])
@require_auth
def manual_place_container(container_id):
    position = request.json
    if not position or 'x' not in position or 'y' not in position or 'z' not in position:
        app_logger.error("Invalid position data")
        return jsonify({"error": "Invalid position data"}), 400
    
    container = yard.containers.get(container_id)
    if not container:
        app_logger.error(f"Container {container_id} not found")
        return jsonify({"error": f"Container {container_id} not found"}), 404
    
    if yard.move_container(container_id, (position['x'], position['y'], position['z'])):
        optimizer.reoptimize()
        app_logger.info(f"Container {container_id} manually placed successfully")
        return jsonify({"message": f"Container {container_id} manually placed successfully"}), 200
    app_logger.error(f"Unable to place container {container_id} at specified position")
    return jsonify({"error": "Unable to place container at specified position"}), 400

@app.route('/logs', methods=['GET'])
@require_auth
def get_logs():
    log_type = request.args.get('type', 'app')
    log_file = os.path.join('backend', 'logs', f'{log_type}.log')
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]  # Get last 100 lines
        return jsonify(logs), 200
    return jsonify({"error": "Log file not found"}), 404

@app.route('/training_progress', methods=['GET'])
@require_auth
def get_training_progress():
    progress = optimizer.get_training_progress()
    return jsonify(progress), 200

if __name__ == '__main__':
    app.run(debug=config.DEBUG)
