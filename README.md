# MediaHost

A comprehensive video hosting platform built with Python, Streamlit, and various other technologies.

## 🚀 Quick Start

1. Clone the repository:
   ```
   git clone https://github.com/dodwmd/mediahost.git
   cd mediahost
   ```

2. Set up the Conda environment:
   ```
   conda env create -f environment.yml
   conda activate video-hosting-saas
   ```

3. Install dependencies using Poetry:
   ```
   poetry install
   ```

4. Set up environment variables:
   Copy `.env.example` to `.env` and fill in the required values.

5. Initialize the database:
   ```
   python generate_test_data.py
   ```

6. Run the application:
   ```
   poetry run streamlit run app/main.py
   ```

## 🛠️ Development Setup

### Prerequisites

- Conda
- Poetry
- MySQL 8.0+
- MinIO
- NATS Server
- Docker and Docker Compose (for containerized setup)

### Running with Docker

1. Build and start the containers:
   ```
   docker-compose up --build
   ```

2. Access the application at `http://localhost:8501`

### Running Tests

```
poetry run python -m unittest
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📁 Project Structure

mediahost/
├── app/
│   ├── ...
├── config/
│   ├── kubernetes/
│   │   └── k8s-dev.yaml
│   └── monitoring/
│       ├── loki-config.yaml
│       ├── prometheus.yml
│       └── promtail-config.yaml
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
└── Tiltfile

## 📧 Contact

dodwmd - michael@dodwell.us

Project Link: [https://github.com/dodwmd/mediahost](https://github.com/dodwmd/mediahost)
