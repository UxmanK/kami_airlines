# KAMI Airlines API

## Overview

A RESTful API for managing airplane fuel consumption and flight capacity.

## Requirements

- Python 3.x
- Django
- Django Rest Framework

## Setup

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd kami_airlines
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Apply migrations:

   ```bash
   python manage.py migrate
   ```

4. Run the server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- `GET /api/airplanes/`: List all airplanes.
- `POST /api/airplanes/`: Add a new airplane.

## Example Request

```json
{
  "id": 1,
  "passengers": 150
}
```

## Example Response

```json
{
  "id": 1,
  "passengers": 150,
  "total_fuel_consumption": 0.8,
  "max_flight_minutes": 250
}
```

## Running Tests

Run tests with:

```bash
python manage.py test
```

Measure test coverage:

```bash
coverage run manage.py test
coverage report
```
