ME 135 Final Project "FOOSBOT":

Project Statement: Automate one side of play in a game of foosball with real-time response rates and scaleable difficulty settings. 

Implementation:
Camera-based ball detection and tracking
Motorized actuation of foosball player handles
Labview GUI for manual control and difficulty settings

Motor control and pass through of the camera video feed were handled on the ESP32, one of the constraints of the project was to use the esp32, a compact low-energy microcontroller capable of executing real time programs. Below is a diagram of the Foosball table along with some photos of the finished project. 

![70500968664__3A12B3AA-1744-433F-80E5-C5084A4FB672](https://github.com/user-attachments/assets/a8cbb718-8a61-479a-8739-a511e3cb9eac)
![IMG_7352](https://github.com/user-attachments/assets/5b46d428-2c94-4739-aa80-3410a34d3b82=250x250)
![IMG_8752](https://github.com/user-attachments/assets/f0aa22fa-c8c9-46f9-9401-2f7f77e308e0)

Image processing was done with the built in tools packaged with OpenCV, but the image detection model was custom built in Tensor flow from several videos of test footage we recorded playing the foosball table normally. The footage was then manually labeled with bounding boxes for the foosball and a GOTURN model was trained on the labeled footage. I chose to use a GOTURN model both for its library of ball tracking data and for its ability to operate offline and frame by frame, making processing and storage requirements relatively small.

![70481645185__3D14F179-4B2F-4908-B162-068B88FD658C](https://github.com/user-attachments/assets/020ce42c-e0f3-45a0-8e59-f73327ebb6f0)

The original goal was to port the frozen graph to the ESP32 with Camera module in order to do every part of the project on the esp32, however unfortunately due to time constraints and an issue with the version of OpenCV/Tensorflow/Keras that we were using, the functions which produced a frozen graph for the model we had trained had become deprecated and unusable and the unfrozen graph was too expensive to run on the hardware. We then switched to the final model we implemented, performing motor control and passing the camera feed through the ESP32 to a nearby laptop to process the frames with the unfrozen graph. In this way we were still able to maintain sub 100ms latency and respond to camera feedback in real time.
