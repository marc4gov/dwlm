curl -X POST http://marc4gov.pythonanywhere.com/predict \
-H "Content-Type: application/json" \
-d '{
  "profiles": [0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.2, -0.1],
  "prices": [50, 45, 40, 35, 30, 25, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 75, 70, 65, 60, 55]
}'