from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.timezone import now
from datetime import timedelta
import numpy as np
from .models import SensorData
from .serializers import SensorDataSerializer
from django.http import JsonResponse
import csv
from io import TextIOWrapper
from collections import defaultdict
from datetime import datetime


def handle_time_window(time_window_str):
    """
    Helper function to handle time window parsing and validation
    """
    try:
        if "m" in time_window_str:  # Time in minutes
            minutes = int(time_window_str.replace("m", ""))
            if 1 <= minutes <= 60:
                return now() - timedelta(minutes=minutes)
            else:
                return None
        elif "h" in time_window_str:  # Time in hours
            hours = int(time_window_str.replace("h", ""))
            if 1 <= hours <= 24:
                return now() - timedelta(hours=hours)
            else:
                return None
        return None
    except ValueError:
        return None


def z_score(data):
    """
    Helper function to calculate Z-scores.
    Filters None values and avoids division by zero.
    """
    filtered_data = [x for x in data if x is not None]
    if not filtered_data:
        return []
    mean = np.mean(filtered_data)
    std = np.std(filtered_data)
    return [(x - mean) / std if std != 0 else 0 for x in filtered_data]


def process_anomalies(timestamps, temp_z_scores, humidity_z_scores, air_quality_z_scores, temperature, humidity, air_quality):
    """
    Helper function to process anomalies in data
    """
    anomalies = defaultdict(list)
    highlighted_anomalies = {"temperature": [], "humidity": [], "air_quality": []}

    for i, (t_score, h_score, a_score) in enumerate(zip(temp_z_scores, humidity_z_scores, air_quality_z_scores)):
        if abs(t_score) > 3:
            anomalies["temperature"].append(timestamps[i])
            highlighted_anomalies["temperature"].append(temperature[i])
        else:
            highlighted_anomalies["temperature"].append(None)

        if abs(h_score) > 3:
            anomalies["humidity"].append(timestamps[i])
            highlighted_anomalies["humidity"].append(humidity[i])
        else:
            highlighted_anomalies["humidity"].append(None)

        if abs(a_score) > 3:
            anomalies["air_quality"].append(timestamps[i])
            highlighted_anomalies["air_quality"].append(air_quality[i])
        else:
            highlighted_anomalies["air_quality"].append(None)

    return highlighted_anomalies


@api_view(["POST"])
def upload_csv(request):
    """
    Receive CSV file and store data in the database.
    """
    if "file" not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    file = request.FILES["file"]
    decoded_file = TextIOWrapper(file, encoding="utf-8")
    csv_reader = csv.reader(decoded_file)

    # Skip header
    next(csv_reader, None)

    data_list = []
    for row in csv_reader:
        try:
            timestamp = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ")
            temperature = float(row[1]) if row[1] else None
            humidity = float(row[2]) if row[2] else None
            air_quality = float(row[3]) if row[3] else None

            data_list.append(SensorData(
                timestamp=timestamp,
                temperature=temperature,
                humidity=humidity,
                air_quality=air_quality
            ))
        except (IndexError, ValueError) as e:
            continue  # Skip rows with invalid data

    SensorData.objects.bulk_create(data_list)  # Bulk insert data
    return JsonResponse({"message": "CSV uploaded successfully", "rows_inserted": len(data_list)})


@api_view(["POST"])
def ingest_sensor_data(request):
    """
    Receive sensor data (temperature, humidity, air_quality).
    """
    serializer = SensorDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Data ingested successfully"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
def get_processed_data(request):
    """
    Return cleaned data and detected anomalies.
    """
    data = SensorData.objects.all().order_by("timestamp")

    if not data.exists():
        return Response({"message": "No data available"}, status=404)

    # Remove duplicate timestamps (keep the first occurrence)
    unique_data = {d.timestamp: d for d in data}
    cleaned_data = list(unique_data.values())

    # Prepare data
    timestamps = [d.timestamp.strftime("%Y-%m-%d %H:%M:%S") for d in cleaned_data]
    temperature = [d.temperature if d.temperature is not None else 0 for d in cleaned_data]
    humidity = [d.humidity if d.humidity is not None else 0 for d in cleaned_data]
    air_quality = [d.air_quality if d.air_quality is not None else 0 for d in cleaned_data]

    # Calculate Z-scores
    temp_z_scores = z_score(temperature)
    humidity_z_scores = z_score(humidity)
    air_quality_z_scores = z_score(air_quality)

    anomalies = process_anomalies(timestamps, temp_z_scores, humidity_z_scores, air_quality_z_scores, temperature, humidity, air_quality)

    return Response({
        "timestamps": timestamps,
        "data": {
            "temperature": temperature,
            "humidity": humidity,
            "air_quality": air_quality
        },
        "anomalies": anomalies,
    })


@api_view(["GET"])
def get_aggregated_data(request):
    """
    ดึงข้อมูลสรุป (Mean, Median, Min/Max) ของเซนเซอร์
    """
    time_window = request.GET.get("time_window", "1h")  # ถ้าไม่ได้ระบุ time_window ให้ค่าเริ่มต้นเป็น 1h

    if time_window:
        # ตรวจสอบว่า time_window เป็นช่วงเวลาในรูปแบบที่ยอมรับได้
        try:
            if "m" in time_window:  # กรณีที่ time_window เป็นนาที เช่น 10m
                minutes = int(time_window.replace("m", ""))  # ดึงค่าจำนวนชั่วโมง
                if 1 <= minutes <= 60:  # ตรวจสอบช่วงเวลา 1-60 นาที
                    start_time = now() - timedelta(minutes=minutes)
                else:
                    return Response({"error": "Invalid time_window, minutes should be between 1 and 60"}, status=400)
            elif "h" in time_window:  # กรณีที่ time_window เป็นชั่วโมง เช่น 1h
                hours = int(time_window.replace("h", ""))  # ดึงค่าจำนวนชั่วโมง
                if 1 <= hours <= 24:  # ตรวจสอบช่วงเวลา 1-24 ชั่วโมง
                    start_time = now() - timedelta(hours=hours)
                else:
                    return Response({"error": "Invalid time_window, hours should be between 1 and 24"}, status=400)
            else:
                return Response({"error": "Invalid time_window format, use '1-60m' or '1-24h'"}, status=400)
        except ValueError:
            return Response({"error": "Invalid time_window format"}, status=400)
    else:
        # เมื่อไม่ได้ระบุ time_window ให้ใช้ค่าเริ่มต้นเป็น 1h
        start_time = now() - timedelta(hours=1)

    # ตรวจสอบว่ามีข้อมูลในช่วงเวลาที่ระบุหรือไม่
    if start_time:
        data = SensorData.objects.filter(timestamp__gte=start_time)
    else:
        data = SensorData.objects.all()  # ดึงข้อมูลทั้งหมด

    if not data.exists():
        return Response({"message": "No data available"}, status=404)

    # Remove duplicate timestamps by iterating over data and keeping the first occurrence of each timestamp
    seen_timestamps = set()
    unique_data = []
    for entry in data:
        if entry.timestamp not in seen_timestamps:
            seen_timestamps.add(entry.timestamp)
            unique_data.append(entry)

    # ดึงข้อมูลเซ็นเซอร์
    temperature = [d.temperature for d in unique_data]
    humidity = [d.humidity for d in unique_data]
    air_quality = [d.air_quality for d in unique_data]

    if not temperature or not humidity or not air_quality:
        return Response({"error": "Sensor data is incomplete for aggregation"}, status=400)

    # สร้างสรุปข้อมูลเซ็นเซอร์
    summary = {
        "time_window": time_window if time_window else "1h",  # ถ้าไม่ได้ระบุเวลาให้แสดงเป็น "1h"
        "temperature": {
            "min": min(temperature),
            "max": max(temperature),
            "mean": np.mean(temperature),
            "median": np.median(temperature),
        },
        "humidity": {
            "min": min(humidity),
            "max": max(humidity),
            "mean": np.mean(humidity),
            "median": np.median(humidity),
        },
        "air_quality": {
            "min": min(air_quality),
            "max": max(air_quality),
            "mean": np.mean(air_quality),
            "median": np.median(air_quality),
        },
    }

    # Return the summary as a response
    return Response(summary, status=200)