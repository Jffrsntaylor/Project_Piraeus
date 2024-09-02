from flask import Flask, request, jsonify
from flask_cors import CORS
from .models.container import Container
from .models.yard import Yard
from .models.yard_config import YardConfig
from .models.database import get_db, engine, Base
from .optimizer.optimizer import Optimizer
from .utils.csv_parser import parse_csv
from .utils.logger import app_logger
from .utils.auth import require_auth
from .utils.config import config
import os
import threading
import time
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
CORS(app)
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

@app.errorhandler(Exception)
def handle_exception(e):
    app_logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500

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
        try:
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
        except Exception as e:
            db.rollback()
            app_logger.error(f"Error processing CSV: {str(e)}")
            return jsonify({"error": "Error processing CSV"}), 500
    app_logger.error("Invalid file format")
    return jsonify({"error": "Invalid file format"}), 400

@app.route('/containers', methods=['GET'])
@require_auth
def get_containers():
    try:
        containers_data = [container.to_dict() for container in yard.containers.values()]
        app_logger.info(f"Retrieved {len(containers_data)} containers")
        return jsonify(containers_data), 200
    except Exception as e:
        app_logger.error(f"Error retrieving containers: {str(e)}")
        return jsonify({"error": "Error retrieving containers"}), 500

@app.route('/container', methods=['POST'])
@require_auth
def add_container():
    try:
        data = request.json
        container = Container(
            id=data['id'],
            weight=data['weight'],
            destination=data['destination'],
            arrival_date=data['arrival_date'],
            departure_date=data['departure_date']
        )
        position = optimizer.optimize_placement(container)
        if yard.add_container(container, position):
            db = next(get_db())
            db.add(container)
            db.commit()
            app_logger.info(f"Container {container.id} added successfully")
            return jsonify({"message": "Container added successfully"}), 201
        else:
            app_logger.error(f"Unable to place container {container.id}")
            return jsonify({"error": "Unable to place container"}), 400
    except KeyError as e:
        app_logger.error(f"Missing required field: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except SQLAlchemyError as e:
        app_logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        app_logger.error(f"Error adding container: {str(e)}")
        return jsonify({"error": "Error adding container"}), 500

@app.route('/container/<container_id>', methods=['GET', 'PUT', 'DELETE'])
@require_auth
def container_operations(container_id):
    if request.method == 'GET':
        container = yard.containers.get(container_id)
        if container:
            app_logger.info(f"Retrieved container {container_id}")
            return jsonify(container.to_dict()), 200
        app_logger.error(f"Container {container_id} not found")
        return jsonify({"error": f"Container {container_id} not found"}), 404

    elif request.method == 'PUT':
        try:
            container = yard.containers.get(container_id)
            if not container:
                app_logger.error(f"Container {container_id} not found")
                return jsonify({"error": f"Container {container_id} not found"}), 404
            
            data = request.json
            container.weight = data.get('weight', container.weight)
            container.destination = data.get('destination', container.destination)
            container.arrival_date = container._parse_date(data.get('arrival_date', container.arrival_date))
            container.departure_date = container._parse_date(data.get('departure_date', container.departure_date))
            
            db = next(get_db())
            db.commit()
            optimizer.reoptimize()
            app_logger.info(f"Container {container_id} updated successfully")
            return jsonify({"message": f"Container {container_id} updated successfully"}), 200
        except SQLAlchemyError as e:
            db.rollback()
            app_logger.error(f"Database error: {str(e)}")
            return jsonify({"error": "Database error"}), 500
        except Exception as e:
            app_logger.error(f"Error updating container {container_id}: {str(e)}")
            return jsonify({"error": f"Error updating container {container_id}"}), 500

    elif request.method == 'DELETE':
        if yard.remove_container(container_id):
            try:
                db = next(get_db())
                container = db.query(Container).get(container_id)
                if container:
                    db.delete(container)
                    db.commit()
                optimizer.reoptimize()
                app_logger.info(f"Container {container_id} removed successfully")
                return jsonify({"message": f"Container {container_id} removed successfully"}), 200
            except SQLAlchemyError as e:
                db.rollback()
                app_logger.error(f"Database error: {str(e)}")
                return jsonify({"error": "Database error"}), 500
        app_logger.error(f"Container {container_id} not found")
        return jsonify({"error": f"Container {container_id} not found"}), 404

@app.route('/metrics', methods=['GET'])
@require_auth
def get_metrics():
    try:
        metrics = optimizer.calculate_metrics()
        app_logger.info("Metrics calculated and retrieved")
        return jsonify(metrics), 200
    except Exception as e:
        app_logger.error(f"Error calculating metrics: {str(e)}")
        return jsonify({"error": "Error calculating metrics"}), 500

@app.route('/manual_place_container/<container_id>', methods=['POST'])
@require_auth
def manual_place_container(container_id):
    try:
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
    except Exception as e:
        app_logger.error(f"Error manually placing container: {str(e)}")
        return jsonify({"error": "Error manually placing container"}), 500

@app.route('/reoptimize', methods=['POST'])
@require_auth
def trigger_reoptimization():
    try:
        optimizer.reoptimize()
        app_logger.info("Manual reoptimization triggered successfully")
        return jsonify({"message": "Reoptimization triggered successfully"}), 200
    except Exception as e:
        app_logger.error(f"Error triggering reoptimization: {str(e)}")
        return jsonify({"error": "Error triggering reoptimization"}), 500

@app.route('/logs', methods=['GET'])
@require_auth
def get_logs():
    try:
        log_type = request.args.get('type', 'app')
        log_file = os.path.join('backend', 'logs', f'{log_type}.log')
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.readlines()[-100:]  # Get last 100 lines
            return jsonify(logs), 200
        return jsonify({"error": "Log file not found"}), 404
    except Exception as e:
        app_logger.error(f"Error retrieving logs: {str(e)}")
        return jsonify({"error": "Error retrieving logs"}), 500

@app.route('/training_progress', methods=['GET'])
@require_auth
def get_training_progress():
    try:
        progress = optimizer.get_training_progress()
        return jsonify(progress), 200
    except Exception as e:
        app_logger.error(f"Error retrieving training progress: {str(e)}")
        return jsonify({"error": "Error retrieving training progress"}), 500

if __name__ == '__main__':
    app.run(debug=config.DEBUG)
