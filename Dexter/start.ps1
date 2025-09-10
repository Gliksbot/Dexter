Start-Process -NoNewWindow -FilePath "python" -ArgumentList "dexter_agent.py"

# Wait a few seconds for API to start
Start-Sleep -Seconds 5

# Start ngrok tunnel
Start-Process -NoNewWindow -FilePath "ngrok.exe" -ArgumentList "http 5001"

# Start Dexter UI (blocking)
python dexter_ui.py