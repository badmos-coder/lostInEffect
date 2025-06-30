#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <esp_timer.h>
#include <img_converters.h>

// WiFi credentials - Set up direct connection
const char* ssid = "ESP32_CAM_DIRECT";
const char* password = "12345678";

// Camera model - WROVER-KIT Pin definition
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Built-in LED for status indication
#define LED_BUILTIN 4

WebServer server(80);

// Recording state
bool recording = false;
String currentSession = "";
unsigned long recordingStartTime = 0;
const unsigned long RECORDING_DURATION = 10000; // 10 seconds in milliseconds

// Frame buffer for streaming
camera_fb_t * fb = NULL;

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  
  // Initialize LED
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  
  // Initialize camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Frame size and quality settings for video recording
  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 12;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA; // 320x240
    config.jpeg_quality = 15;
    config.fb_count = 1;
  }
  
  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  
  // Set up WiFi Access Point
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("ESP32-CAM AP IP address: ");
  Serial.println(IP);
  
  // Set up web server routes
  server.on("/", handleRoot);
  server.on("/start_recording", handleStartRecording);
  server.on("/stop_recording", handleStopRecording);
  server.on("/status", handleStatus);
  server.on("/stream", handleStream);
  server.on("/capture", handleCapture);
  
  server.begin();
  Serial.println("HTTP server started");
  Serial.println("Camera ready for video recording");
  
  // Flash LED to indicate ready
  for(int i = 0; i < 3; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
  }
}

void loop() {
  server.handleClient();
  
  // Handle recording timeout
  if (recording && (millis() - recordingStartTime) >= RECORDING_DURATION) {
    stopRecording();
  }
  
  // Blink LED during recording
  if (recording) {
    digitalWrite(LED_BUILTIN, (millis() / 500) % 2);
  }
  
  delay(10);
}

void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Video Recorder</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { padding: 20px; border-radius: 5px; margin: 20px 0; }
        .ready { background-color: #d4edda; color: #155724; }
        .recording { background-color: #f8d7da; color: #721c24; }
        button { padding: 10px 20px; margin: 10px; font-size: 16px; cursor: pointer; }
        #stream { width: 100%; max-width: 640px; height: auto; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32-CAM Video Recorder</h1>
        <div id="status" class="status ready">Ready for recording</div>
        
        <div>
            <img id="stream" src="/stream" alt="Camera Stream">
        </div>
        
        <div>
            <button onclick="startRecording()">Start Recording (10s)</button>
            <button onclick="stopRecording()">Stop Recording</button>
        </div>
        
        <div id="info">
            <p>Session ID: <span id="sessionId">None</span></p>
            <p>Recording Status: <span id="recordingStatus">Stopped</span></p>
        </div>
    </div>

    <script>
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('sessionId').textContent = data.session || 'None';
                    document.getElementById('recordingStatus').textContent = data.recording ? 'Recording...' : 'Stopped';
                    
                    const statusDiv = document.getElementById('status');
                    if (data.recording) {
                        statusDiv.className = 'status recording';
                        statusDiv.textContent = 'Recording in progress... (' + data.session + ')';
                    } else {
                        statusDiv.className = 'status ready';
                        statusDiv.textContent = 'Ready for recording';
                    }
                });
        }
        
        function startRecording() {
            fetch('/start_recording', {method: 'POST'})
                .then(response => response.text())
                .then(data => {
                    console.log(data);
                    updateStatus();
                });
        }
        
        function stopRecording() {
            fetch('/stop_recording', {method: 'POST'})
                .then(response => response.text())
                .then(data => {
                    console.log(data);
                    updateStatus();
                });
        }
        
        // Update status every second
        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>
  )rawliteral";

  server.send(200, "text/html", html);
}

void handleStartRecording() {
  if (!recording) {
    currentSession = "REC_" + String(millis());
    recording = true;
    recordingStartTime = millis();
    digitalWrite(LED_BUILTIN, HIGH);
    
    Serial.println("RECORDING_START:" + currentSession);
    server.send(200, "text/plain", "Recording started: " + currentSession);
  } else {
    server.send(200, "text/plain", "Already recording: " + currentSession);
  }
}

void handleStopRecording() {
  if (recording) {
    stopRecording();
    server.send(200, "text/plain", "Recording stopped: " + currentSession);
  } else {
    server.send(200, "text/plain", "Not recording");
  }
}

void stopRecording() {
  if (recording) {
    recording = false;
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("RECORDING_END:" + currentSession);
    currentSession = "";
  }
}

void handleStatus() {
  String json = "{";
  json += "\"recording\":" + String(recording ? "true" : "false") + ",";
  json += "\"session\":\"" + currentSession + "\",";
  json += "\"duration\":" + String(recording ? (millis() - recordingStartTime) : 0);
  json += "}";
  
  server.send(200, "application/json", json);
}

void handleStream() {
  WiFiClient client = server.client();
  
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
  server.sendContent_P(response.c_str());
  
  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      break;
    }
    
    String header = "--frame\r\n";
    header += "Content-Type: image/jpeg\r\n";
    header += "Content-Length: " + String(fb->len) + "\r\n\r\n";
    
    server.sendContent_P(header.c_str());
    
    uint8_t *fbBuf = fb->buf;
    size_t fbLen = fb->len;
    
    // Send image data in chunks
    size_t chunkSize = 1024;
    for (size_t i = 0; i < fbLen; i += chunkSize) {
      size_t currentChunkSize = min(chunkSize, fbLen - i);
      client.write(fbBuf + i, currentChunkSize);
    }
    
    server.sendContent_P("\r\n");
    esp_camera_fb_return(fb);
    
    delay(30); // ~30 FPS
  }
}

void handleCapture() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }
  
  server.sendHeader("Content-Disposition", "attachment; filename=capture.jpg");
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
}