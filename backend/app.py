from flask import Flask, request, jsonify
from models.yard import Yard
from models.yard_config import YardConfig
from optimizer.optimizer import Optimizer
from utils.csv_parser import parse_csv
import os

app = Flask(__name__)

# Initialize yard and optimizer
yard_config = YardConfig(length=10, width=10, height=5, energy_consumption_rate=0.1, carbon_emission_factor=0.5)
yard = Yard(yard_config)
optimizer = Optimizer(yard)

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.csv'):
        file_path = os.path.join('/tmp', file.filename)
        file.save(file_path)
        containers = parse_csv(file_path)
        for container in containers:
            position = optimizer.optimize_placement(container)
            yard.add_container(container, position)
        os.remove(file_path)
        return jsonify({"message": "CSV processed successfully"}), 200
    return jsonify({"error": "Invalid file format"}), 400

@app.route('/containers', methods=['GET'])
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
    return jsonify(containers_data), 200

@app.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = optimizer.calculate_metrics()
    return jsonify(metrics), 200

@app.route('/remove_container/<container_id>', methods=['POST'])
def remove_container(container_id):
    if yard.remove_container(container_id):
        optimizer.reoptimize()
        return jsonify({"message": f"Container {container_id} removed successfully"}), 200
    return jsonify({"error": f"Container {container_id} not found"}), 404

@app.route('/manual_place_container/<container_id>', methods=['POST'])
def manual_place_container(container_id):
    position = request.json
    if not position or 'x' not in position or 'y' not in position or 'z' not in position:
        return jsonify({"error": "Invalid position data"}), 400
    
    container = yard.containers.get(container_id)
    if not container:
        return jsonify({"error": f"Container {container_id} not found"}), 404
    
    if yard.move_container(container_id, (position['x'], position['y'], position['z'])):
        optimizer.reoptimize()
        return jsonify({"message": f"Container {container_id} manually placed successfully"}), 200
    return jsonify({"error": "Unable to place container at specified position"}), 400

if __name__ == '__main__':
    app.run(debug=True)
