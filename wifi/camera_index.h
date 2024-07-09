#ifndef _CAMERA_INDEX_H_
#define _CAMERA_INDEX_H_

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-CAM</title>
</head>
<body>
    <h1>ESP32-CAM Web Server</h1>
    <img src="/stream" style="width: 100%;">
</body>
</html>
)rawliteral";

#endif // _CAMERA_INDEX_H_
