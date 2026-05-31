Develop a professional desktop .exe application called “Smart Security IoT” designed as a real intelligent security and access control system using:

- Artificial Intelligence
- Facial Recognition
- EZVIZ RTSP Camera
- Siemens LOGO! V8 PLC
- Cybersecurity best practices
- Real-time monitoring
- Automatic alerts
- Secure database
- Industrial automation

The project must look and behave like a real professional AI security platform used in smart homes, industrial environments, or advanced surveillance systems.

━━━━━━━━━━━━━━━━━━
🎯 MAIN OBJECTIVE
━━━━━━━━━━━━━━━━━━

The system must:

- Automatically recognize authorized persons
- Detect unknown persons
- Control an outdoor light using Siemens LOGO! V8
- Send instant alerts
- Store events securely
- Work in real-time with very high accuracy
- Follow ISO 27001 and cybersecurity best practices

━━━━━━━━━━━━━━━━━━
🔥 REQUIRED MODES
━━━━━━━━━━━━━━━━━━

The application must contain TWO MODES:

1. LOCAL TEST MODE
2. REAL PRODUCTION MODE

━━━━━━━━━━━━━━━━━━
🧪 MODE 1 — LOCAL TEST MODE
━━━━━━━━━━━━━━━━━━

Create a testing mode using the PC webcam.

Purpose:
- Test the AI system without real hardware
- Test facial recognition
- Test alerts
- Test system logic
- Debug easily

Features:
- Webcam detection
- Face recognition
- Add faces from webcam
- Real-time detection
- Virtual light simulation
- Local notifications

When an authorized person is detected:
- Display “AUTHORIZED”
- Turn ON a virtual light inside the UI

When an unknown face is detected:
- Display “UNKNOWN DETECTED”
- Save screenshot
- Send local notification
- Store detection in database

━━━━━━━━━━━━━━━━━━
🏠 MODE 2 — REAL MODE (EZVIZ + SIEMENS LOGO! V8)
━━━━━━━━━━━━━━━━━━

Use:
- EZVIZ RTSP Camera
- Siemens LOGO! V8 PLC
- Local network communication

Example RTSP:
rtsp://username:password@ip:554

━━━━━━━━━━━━━━━━━━
✅ AUTHORIZED PERSON SCENARIO
━━━━━━━━━━━━━━━━━━

If a detected face matches an authorized user:

Example:
BENAMAR Othmane

Then:

1. Recognize the face
2. Display the name in the UI
3. Save log entry
4. Send command to Siemens LOGO! V8
5. Activate PLC output
6. Turn ON outdoor light
7. Keep light ON for configurable duration
8. Turn OFF automatically after timer expires

━━━━━━━━━━━━━━━━━━
🚨 UNKNOWN PERSON SCENARIO
━━━━━━━━━━━━━━━━━━

If an unknown person is detected:

1. Capture image automatically
2. Store image in database
3. Create intrusion log
4. DO NOT turn ON light
5. Send immediate alert

Alert must contain:
- Photo
- Date
- Time
- Detection type
- Risk level

━━━━━━━━━━━━━━━━━━
🤖 AI & FACIAL RECOGNITION
━━━━━━━━━━━━━━━━━━

Use:
- Python
- OpenCV
- face_recognition
- DeepFace
- dlib

The system must:
- Detect faces
- Recognize authorized users
- Display confidence score
- Work in real-time
- Minimize false positives

━━━━━━━━━━━━━━━━━━
🎯 AI ACCURACY REQUIREMENTS
━━━━━━━━━━━━━━━━━━

Target near 0% error rate.

Security is more important than speed.

Prevent:
- False positives
- Unauthorized access

━━━━━━━━━━━━━━━━━━
✅ REQUIRED AI SECURITY MECHANISMS
━━━━━━━━━━━━━━━━━━

1. Double AI validation:
- face_recognition
- DeepFace

Both systems must validate before authorization.

2. Multi-frame verification:
- Require multiple consecutive positive frames
- Example: 5 valid frames before approval

3. High confidence threshold:
- Minimum 90%–95%

4. Anti-spoofing protection:
- Detect fake photos
- Detect phone screens
- Detect printed images

5. OpenCV preprocessing:
- Noise reduction
- Brightness enhancement
- Sharpening
- Histogram equalization

━━━━━━━━━━━━━━━━━━
⚡ SIEMENS LOGO! V8 PLC
━━━━━━━━━━━━━━━━━━

Communication:
- Ethernet
- Modbus TCP

Features:
- ON/OFF commands
- Configurable timer
- Auto reconnect
- PLC monitoring

━━━━━━━━━━━━━━━━━━
🎥 EZVIZ RTSP CAMERA
━━━━━━━━━━━━━━━━━━

Features:
- Automatic connection
- Auto reconnect
- FPS optimization
- Real-time processing
- Multi-threading

━━━━━━━━━━━━━━━━━━
🗄️ DATABASE
━━━━━━━━━━━━━━━━━━

Use SQLite.

Tables:

Users:
- id
- first_name
- last_name
- face_image
- face_encoding

Detections:
- type
- user
- confidence_score
- timestamp
- captured_image

Security Logs:
- alerts
- errors
- PLC actions
- connections

━━━━━━━━━━━━━━━━━━
🔐 CYBERSECURITY & ISO 27001
━━━━━━━━━━━━━━━━━━

Apply:
- ISO/IEC 27001 principles
- ISO 27002
- OWASP best practices
- Secure coding
- Application hardening

━━━━━━━━━━━━━━━━━━
🛡️ REQUIRED SECURITY FEATURES
━━━━━━━━━━━━━━━━━━

Authentication:
- bcrypt password hashing
- Admin/User roles
- Session timeout
- Brute-force protection

Sensitive Data Protection:
- Never hardcode passwords
- Never expose RTSP credentials
- Never expose API tokens

Use:
.env

Input Security:
- Prepared SQL statements
- Input validation
- Exception handling
- SQL injection protection

Logging:
- Security logs
- Detection logs
- Error logs
- Connection logs

Application Hardening:
- Watchdog system
- Crash recovery
- Log rotation
- Alert cooldown
- File size limitation

━━━━━━━━━━━━━━━━━━
🖥️ UI/UX DESIGN
━━━━━━━━━━━━━━━━━━

Create a futuristic AI Security Control Center interface.

Style:
- Dark mode
- Cybersecurity dashboard
- Glassmorphism
- Neon blue glow
- SCADA-inspired design

Colors:
- Deep black
- Neon blue
- Cyan
- Dark gray

Effects:
- Smooth animations
- Glow effects
- Modern cards
- Live indicators
- Real-time dashboard

━━━━━━━━━━━━━━━━━━
📊 APPLICATION PAGES
━━━━━━━━━━━━━━━━━━

1. Dashboard
- AI status
- Camera status
- PLC status
- Alerts
- Statistics

2. Live Camera
- Real-time stream
- Face detection boxes
- Confidence score

3. Face Recognition
- Registered users
- Add/remove faces
- Recognition history

4. Access Control
- Light control
- Manual override
- PLC logs

5. Alerts Center
- Intrusion alerts
- Notifications
- Unknown face captures

6. Settings
- RTSP settings
- PLC IP
- Telegram API
- Confidence threshold
- Light duration

━━━━━━━━━━━━━━━━━━
📱 FREE ALERT SYSTEM
━━━━━━━━━━━━━━━━━━

Use:
- Telegram Bot API
- Discord Webhook
- Gmail SMTP
- Windows notifications

━━━━━━━━━━━━━━━━━━
🧠 TECH STACK
━━━━━━━━━━━━━━━━━━

Backend & AI:
- Python
- OpenCV
- face_recognition
- DeepFace
- SQLite

Desktop UI:
- PyQt5 or PySide6

PLC:
- Siemens LOGO! V8

Networking:
- Modbus TCP

Notifications:
- Telegram Bot API

━━━━━━━━━━━━━━━━━━
📂 PROJECT STRUCTURE
━━━━━━━━━━━━━━━━━━

/app
/ui
/core
/ai
/database
/services
/logs
/config
/assets
/models
/tests

━━━━━━━━━━━━━━━━━━
📦 FINAL EXPORT
━━━━━━━━━━━━━━━━━━

Export as:
.exe

Use:
- PyInstaller
- Modular architecture
- Secure configuration
- Easy maintenance

━━━━━━━━━━━━━━━━━━
🎯 FINAL GOAL
━━━━━━━━━━━━━━━━━━

Build a complete professional AI security application capable of:

- Recognizing authorized people
- Working with PC webcam OR EZVIZ RTSP camera
- Controlling outdoor lights using Siemens LOGO! V8
- Detecting unknown persons
- Sending instant alerts
- Following ISO 27001 cybersecurity practices
- Minimizing false positives
- Operating in real-time
- Providing a futuristic professional interface
- Being stable, secure, scalable, and realistic like a real industrial AI security platform.