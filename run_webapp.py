from backend.web_app import app

if __name__ == '__main__':
    print("=" * 60)
    print("Cryptography Toolkit - Web Application")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 60)
    print()
    app.run(debug=True, port=5000, host='0.0.0.0')
