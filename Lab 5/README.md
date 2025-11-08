# Observant Systems

**NAMES OF COLLABORATORS HERE**


For lab this week, we focus on creating interactive systems that can detect and respond to events or stimuli in the environment of the Pi, like the Boat Detector we mentioned in lecture. 
Your **observant device** could, for example, count items, find objects, recognize an event or continuously monitor a room.

This lab will help you think through the design of observant systems, particularly corner cases that the algorithms need to be aware of.

## Prep

1.  Install VNC on your laptop if you have not yet done so. This lab will actually require you to run script on your Pi through VNC so that you can see the video stream. Please refer to the [prep for Lab 2](https://github.com/FAR-Lab/Interactive-Lab-Hub/blob/-/Lab%202/prep.md#using-vnc-to-see-your-pi-desktop).
2.  Install the dependencies as described in the [prep document](prep.md). 
3.  Read about [OpenCV](https://opencv.org/about/),[Pytorch](https://pytorch.org/), [MediaPipe](https://mediapipe.dev/), and [TeachableMachines](https://teachablemachine.withgoogle.com/).
4.  Read Belloti, et al.'s [Making Sense of Sensing Systems: Five Questions for Designers and Researchers](https://www.cc.gatech.edu/~keith/pubs/chi2002-sensing.pdf).

### For the lab, you will need:
1. Pull the new Github Repo
1. Raspberry Pi
1. Webcam 

### Deliverables for this lab are:
1. Show pictures, videos of the "sense-making" algorithms you tried.
1. Show a video of how you embed one of these algorithms into your observant system.
1. Test, characterize your interactive device. Show faults in the detection and how the system handled it.

## Overview
Building upon the paper-airplane metaphor (we're understanding the material of machine learning for design), here are the four sections of the lab activity:

A) [Play](#part-a)

B) [Fold](#part-b)

C) [Flight test](#part-c)

D) [Reflect](#part-d)

---

### Part A
### Play with different sense-making algorithms.

#### Pytorch for object recognition

For this first demo, you will be using PyTorch and running a MobileNet v2 classification model in real time (30 fps+) on the CPU. We will be following steps adapted from [this tutorial](https://pytorch.org/tutorials/intermediate/realtime_rpi.html).

![torch](Readme_files/pyt.gif)


To get started, install dependencies into a virtual environment for this exercise as described in [prep.md](prep.md).

Make sure your webcam is connected.

You can check the installation by running:

```
python -c "import torch; print(torch.__version__)"
```

If everything is ok, you should be able to start doing object recognition. For this default example, we use [MobileNet_v2](https://arxiv.org/abs/1801.04381). This model is able to perform object recognition for 1000 object classes (check [classes.json](classes.json) to see which ones.

Start detection by running  

```
python infer.py
```

The first 2 inferences will be slower. Now, you can try placing several objects in front of the camera.

Read the `infer.py` script and become familiar with the code. You can change the video resolution and frames per second (FPS). You may also use the weights of the larger pre-trained mobilenet_v3_large model, as described [here](https://pytorch.org/tutorials/intermediate/realtime_rpi.html#model-choices).

#### More classes

[PyTorch supports transfer learning](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html), so you can fine‑tune and transfer learn models to recognize your own objects. It requires extra steps, so we won't cover it here.

For more details on transfer learning and deployment to embedded devices, see Deep Learning on Embedded Systems: A Hands‑On Approach Using Jetson Nano and Raspberry Pi (Tariq M. Arif). [Chapter 10](https://onlinelibrary.wiley.com/doi/10.1002/9781394269297.ch10) covers transfer learning for object detection on desktop, and [Chapter 15](https://onlinelibrary.wiley.com/doi/10.1002/9781394269297.ch15) describes moving models to the Pi using ONNX.

### Machine Vision With Other Tools
The following sections describe tools ([MediaPipe](#mediapipe) and [Teachable Machines](#teachable-machines)).

#### MediaPipe

A established open source and efficient method of extracting information from video streams comes out of Google's [MediaPipe](https://mediapipe.dev/), which offers state of the art face, face mesh, hand pose, and body pose detection.

![Media pipe](Readme_files/mp.gif)

To get started, install dependencies into a virtual environment for this exercise as described in [prep.md](prep.md):

Each of the installs will take a while, please be patient. After successfully installing mediapipe, connect your webcam to your Pi and use **VNC to access to your Pi**, open the terminal, and go to Lab 5 folder and run the hand pose detection script we provide:
(***it will not work if you use ssh from your laptop***)


```
(venv-ml) pi@ixe00:~ $ cd Interactive-Lab-Hub/Lab\ 5
(venv-ml) pi@ixe00:~ Interactive-Lab-Hub/Lab 5 $ python hand_pose.py
```

Try the two main features of this script: 1) pinching for percentage control, and 2) "[Quiet Coyote](https://www.youtube.com/watch?v=qsKlNVpY7zg)" for instant percentage setting. Notice how this example uses hardcoded positions and relates those positions with a desired set of events, in `hand_pose.py`. 

Consider how you might use this position based approach to create an interaction, and write how you might use it on either face, hand or body pose tracking.

(You might also consider how this notion of percentage control with hand tracking might be used in some of the physical UI you may have experimented with in the last lab, for instance in controlling a servo or rotary encoder.)



#### Moondream Vision-Language Model

[Moondream](https://www.ollama.com/library/moondream) is a lightweight vision-language model that can understand and answer questions about images. Unlike the classification models above, Moondream can describe images in natural language and answer specific questions about what it sees.

To use Moondream, first make sure Ollama is running and pull the model:
```bash
ollama pull moondream
```

Then run the simple demo script:
```bash
python moondream_simple.py
```

This will capture an image from your webcam and let you ask questions about it in natural language. Note that vision-language models are slower than classification models (responses may take up to minutes on a Raspberry Pi). There are newer models like [LFM2-VL](https://huggingface.co/LiquidAI/LFM2-VL-450M-GGUF), but many are very recent and not yet optimized for embedded devices.

**Design consideration**: Think about how slower response times change your interaction design. What kinds of observant systems benefit from thoughtful, delayed responses rather than real-time classification? Consider systems that monitor over longer time periods or provide periodic summaries rather than instant feedback.

#### Teachable Machines
Google's [TeachableMachines](https://teachablemachine.withgoogle.com/train) is very useful for prototyping with the capabilities of machine learning. We are using [a python package](https://github.com/MeqdadDev/teachable-machine-lite) with tensorflow lite to simplify the deployment process.

![Tachable Machines Pi](Readme_files/tml_pi.gif)

To get started, install dependencies into a virtual environment for this exercise as described in [prep.md](prep.md):

After installation, connect your webcam to your Pi and use **VNC to access to your Pi**, open the terminal, and go to Lab 5 folder and run the example script:
(***it will not work if you use ssh from your laptop***)


```
(venv-tml) pi@ixe00:~ Interactive-Lab-Hub/Lab 5 $ python tml_example.py
```


Next train your own model. Visit [TeachableMachines](https://teachablemachine.withgoogle.com/train), select Image Project and Standard model. The raspberry pi 4 is capable to run not just the low resource models. Second, use the webcam on your computer to train a model. *Note: It might be advisable to use the pi webcam in a similar setting you want to deploy it to improve performance.*  For each class try to have over 150 samples, and consider adding a background or default class where you have nothing in view so the model is trained to know that this is the background. Then create classes based on what you want the model to classify. Lastly, preview and iterate. Finally export your model as a 'Tensorflow lite' model. You will find an '.tflite' file and a 'labels.txt' file. Upload these to your pi (through one of the many ways such as [scp](https://www.raspberrypi.com/documentation/computers/remote-access.html#using-secure-copy), sftp, [vnc](https://help.realvnc.com/hc/en-us/articles/360002249917-VNC-Connect-and-Raspberry-Pi#transferring-files-to-and-from-your-raspberry-pi-0-6), or a connected visual studio code remote explorer).
![Teachable Machines Browser](Readme_files/tml_browser.gif)
![Tensorflow Lite Download](Readme_files/tml_download-model.png)

Include screenshots of your use of Teachable Machines, and write how you might use this to create your own classifier. Include what different affordances this method brings, compared to the OpenCV or MediaPipe options.

I used Teachable Machines to create my own pose classifier that recognizes two actions: looking at a cellphone and drinking water. To train the model, I collected around 200 image samples for each class using my webcam and exported the trained model as a TensorFlow Lite file for use on the Raspberry Pi. This process was simple and intuitive because Teachable Machines provides a visual interface — I didn’t need to write any code or manually label data.
Compared to OpenCV or MediaPipe, Teachable Machines offers a much easier way to customize what the model learns. While OpenCV and MediaPipe use predefined detection methods, Teachable Machines lets me define my own classes based on any kind of image data. This gives it greater flexibility for personalized recognition tasks, such as detecting specific objects, gestures, or activities. However, Teachable Machines models are more general and may be less efficient or less precise than optimized pipelines like MediaPipe for specific tasks such as pose or hand tracking.

![Training model 1](Training-model-0.png)
![Training model 2](Training-model.png)

#### (Optional) Legacy audio and computer vision observation approaches
In an earlier version of this class students experimented with observing through audio cues. Find the material here:
[Audio_optional/audio.md](Audio_optional/audio.md). 
Teachable machines provides an audio classifier too. If you want to use audio classification this is our suggested method. 

In an earlier version of this class students experimented with foundational computer vision techniques such as face and flow detection. Techniques like these can be sufficient, more performant, and allow non discrete classification. Find the material here:
[CV_optional/cv.md](CV_optional/cv.md).

### Part B
### Construct a simple interaction.

* Pick one of the models you have tried, and experiment with prototyping an interaction.
* This can be as simple as the boat detector shown in lecture.
* Try out different interaction outputs and inputs.

**\*\*\*Describe and detail the interaction, as well as your experimentation here.\*\*\***

**Human Detection Greeter System**

***Motivation: Encouragement for Solo Study***

As someone who lives alone, I often struggle with staying focused and motivated, especially when it comes to sitting down at my desk to begin work. Without external accountability or subtle social cues, it can be easy to avoid starting tasks or get stuck in a state of inertia. I became curious whether a lightweight, ambient form of interaction — something as simple as a warm "Welcome!" — could serve as a positive nudge to shift me into a productive mindset. This curiosity led to the development of a small but meaningful system: a Raspberry Pi-powered greeter that detects when I approach my desk and welcomes me with visual and auditory feedback.

***Model Design: Custom Human Classifier***

To power the detection, I trained a custom image classification model using Google’s Teachable Machine platform. The model was built with two primary classes: "Human" and "Not Human." For the "Human" class, I uploaded around 400 images of myself sitting at my desk, taken under varied lighting conditions, camera angles, and wearing different outfits. Some of the images included partial occlusion—such as my hand raised or my body leaning to one side—to help the model generalize across real-world variations.

The "Not Human" class consisted of approximately 200 images showing the same environment without me present. These included common desk objects such as pencil cases, iPads, and books, as well as furniture like chairs and monitors that might visually resemble a person when seen from certain angles. This diversity helped the model distinguish between actual human presence and background clutter.

![Model Human](Model-Human.png)

![Model NotHuman](Model-NotHuman.png)
![Model NotHuman2](Model-NotHuman2.png)
![Model NotHuman3](Model-NotHuman3.png)

One interesting edge case emerged during testing: I placed a Chappell Roan album poster in front of the camera, and the model briefly identified it as a human. While technically a false positive, I considered this acceptable given the limitations of image classification at a glance, and it didn’t affect the practical goal of encouraging me to sit at my desk to study.
![Model Human2](Model-Human2.png)


***Model Export and Deployment***

Once I was satisfied with the model’s performance, I exported it from Teachable Machine as a TensorFlow Lite model, which is optimized for use on Raspberry Pi. The export generated two files: a .tflite model file containing the compressed classifier, and a labels.txt file mapping numeric class IDs to class names. These files were transferred to my Pi using the scp command-line tool.

On the Raspberry Pi, I wrote a Python script that uses the teachable_machine_lite module and OpenCV to capture live camera frames. Each frame is passed through the classifier, and the prediction is checked for its top label and confidence. The system is programmed to treat any detection of "Human" with over 80% confidence as a true positive and respond accordingly.

![Pi Human](Pi-Human.jpg)
![Pi NotHuman](Pi-NotHuman.jpg)

***System Setup and Functionality***

The hardware configuration for this interaction includes a Raspberry Pi paired with a webcam for real-time image capture and a 1.14-inch Adafruit ST7789 TFT screen for visual output. At startup, the screen displays a neutral standby message: “Waiting… Scanning for human.” This early screen setup was intentionally designed to prevent a bug encountered in earlier iterations, where the display would default to an unintended “Welcome!” message even before any inference was complete. To address this, the system now only transitions to the greeting screen after receiving a valid detection result.

Once the model detects a human with a confidence score above 80%, the system dynamically updates the display to show a green-background message: “Welcome! Human Detected.” This visual feedback provides a friendly and ambient interaction, reinforcing presence awareness in the space. After five seconds, the display automatically reverts to its scanning mode, preparing for the next interaction.

If no human is detected or if confidence is too low, the system maintains the default “Waiting...” message without redundantly repeating outputs. This state machine prevents flickering and creates a smoother user experience. The backlight remains on once the initial detection completes, allowing the screen to remain visibly responsive throughout the session.

[![Watch the demo with screen output](thumbnail.png)](https://youtu.be/z0HW9PHHPuM)

***Exploration of Inputs and Outputs***

To explore input variation, I tested the model under several real-world conditions. I tried approaching the desk from different angles and distances, observed the effect of varied lighting (daylight, overhead lamp, and dim light), and experimented with partial occlusion — for instance, wearing a hoodie, leaning sideways, or partially hiding behind the monitor. The model consistently handled these variations well, maintaining high accuracy in detecting a human presence.

For output variation, I initially started with just visual feedback using the TFT screen. Later, I added audio output via the espeak library to create a spoken “Welcome!” message when a person is detected. This not only made the system feel more interactive and friendly but also allowed it to function as a useful ambient cue, especially when I’m not directly looking at the screen.

Exploring these input and output combinations helped me understand how multi-sensory interaction can improve the effectiveness of a simple system. The auditory feedback is especially helpful during low-light settings or when I’m approaching the desk from the side. Meanwhile, the visual feedback reinforces the feeling of being “seen” or acknowledged, which contributes to the motivational aspect of the system.

[![Watch the demo with both screen and audio output](thumbnail.png)](https://youtu.be/7MZTJp3idu4)

### Part C
### Test the interaction prototype

Now flight test your interactive prototype and **note down your observations**:
For example:
1. When does it what it is supposed to do?
1. When does it fail?
1. When it fails, why does it fail?
1. Based on the behavior you have seen, what other scenarios could cause problems?

During testing, the system performed reliably in most scenarios. It correctly identified me as a human even when I was standing far away from the camera, and it maintained high accuracy across different poses, such as turning sideways or wearing a mask. I was also impressed that it did not misclassify non-human objects, even when I moved items like a pillows, iPad, or book directly in front of the camera. These results suggest the model is robust against everyday desk clutter and movement.

However, there were a few notable failure cases. When I held up a hoodie—without myself being visible—the system sometimes misclassified it as a human. Similarly, a poster of Chappell Roan showing her full frontal face occasionally triggered a false positive. While this type of misclassification is understandable given the visual similarity, it is less concerning in this context since the system is designed to offer a friendly prompt rather than make high-stakes decisions. The model also struggled in extremely low-light conditions, failing to detect me reliably when the lighting was too dim for the camera to capture clear features.

Based on these observations, other potential failure scenarios may include highly realistic human-shaped mannequins, face-like drawings near the camera, or someone walking past the camera wearing bulky clothes that distort shape. While these edge cases may lead to occasional false positives, they do not critically impact the goal of creating a motivational, human-responsive study environment.

**\*\*\*Think about someone using the system. Describe how you think this will work.\*\*\***
1. Are they aware of the uncertainties in the system?
1. How bad would they be impacted by a miss classification?
1. How could change your interactive system to address this?
1. Are there optimizations you can try to do on your sense-making algorithm.

If someone else were to use this system, I imagine it would feel like a subtle, ambient interaction — a low-effort way to mark the start of a work session. They would walk up to their desk and be greeted by a simple welcome message, offering a gentle psychological cue to begin focusing. However, they may not immediately be aware of the uncertainties built into the system. Because the interface is minimal and doesn’t display detection confidence or reasoning, users might assume it's more accurate than it actually is.

Fortunately, the consequences of a misclassification in this context are fairly minor. A false negative (not detecting a human) might mean the welcome screen doesn’t appear right away, which is not disruptive. A false positive (detecting a human when there is none) might result in an occasional premature “Welcome!” message, which could feel odd but not harmful. In both cases, the stakes are low because the system serves more as an ambient motivator than a security or productivity enforcement tool.

To improve the interaction, I could add subtle visual or audio indicators of detection confidence — for instance, dimming the display slightly when the model is less confident, or using a short animation delay before the welcome message to confirm sustained presence. These design choices would make users more attuned to the system’s behavior and help them understand when it’s uncertain.

In terms of improving the sense-making algorithm, I could refine the dataset further by adding more diverse “Not Human” examples, especially those involving ambiguous objects like hoodies, posters, or mannequins. Additionally, collecting more nighttime or low-light examples could help improve performance in dim conditions. Another potential optimization could involve combining image classification with a secondary input — such as motion detection or infrared proximity sensing — to cross-validate the presence of a human more accurately.

### Part D
### Characterize your own Observant system

Now that you have experimented with one or more of these sense-making systems **characterize their behavior**.
During the lecture, we mentioned questions to help characterize a material:
* What can you use X for?
* What is a good environment for X?
* What is a bad environment for X?
* When will X break?
* When it breaks how will X break?
* What are other properties/behaviors of X?
* How does X feel?

**\*\*\*Include a short video demonstrating the answers to these questions.\*\*\***

***What can you use this system for?***
This system is designed to create an ambient cue for study motivation. When a person approaches the desk, the system detects their presence and displays a welcoming message. It can be used as a soft nudge to help users begin a focused session, or even as a lightweight check-in mechanism to track time spent at the desk.

***What is a good environment for this system?***
The system works best in a well-lit, indoor space where the lighting is consistent and the background is relatively static. It thrives when used by a single primary user, particularly in solo work setups where desk layout and background conditions are predictable.

***What is a bad environment for this system?***
The system struggles in low-light or heavily cluttered environments. It may also misclassify things in shared or dynamic spaces — such as public libraries or co-working spaces — where multiple people, posters, or objects move in and out of frame frequently.

***When will it break?***
It will likely break in very dim conditions where the camera cannot capture clear input, or when unfamiliar objects (e.g. posters of human faces, or clothes with human-like form) are presented. The model might also break if the user makes significant appearance changes not represented in training (e.g., wearing a full costume or hat).

***When it breaks, how will it break?***
It typically breaks by producing a false positive, such as misclassifying a static object as a human, or a false negative, where a real human is not detected due to low confidence. In both cases, the user might see a wrong message (“Welcome!” when no one is there, or no message when they are present).

***Other properties or behaviors?***
The system responds quickly and does not require active input, making it feel seamless. It does not require an internet connection once deployed and can be customized with other outputs, such as audio or smart light integration, making it extensible.

***How does it feel?***
The interaction feels ambient and gentle — not intrusive, but quietly encouraging. It blends into the background of your daily routine, almost like a digital pet that acknowledges your presence and helps anchor your focus.

[![Good Environment & Pass Cases](thumbnail.png)](https://youtube.com/shorts/adgnVRHFiWs?feature=share)
[![Failed Case](thumbnail.png)](https://youtube.com/shorts/m6jAsJ6bOdk?feature=share)
[![Failed Case 2](thumbnail.png)](https://youtu.be/4O2F7VAke7Y)

### Part 2.

Following exploration and reflection from Part 1, finish building your interactive system, and demonstrate it in use with a video.

**\*\*\*Include a short video demonstrating the finished result.\*\*\***

***Model Improvements***
Based on observations from Part 1, I improved the model by retraining it with more “Not Human” examples that previously caused false positives, such as a hoodie held in front of the camera. I also balanced the dataset more evenly and added some samples in dim lighting conditions to improve performance. After retraining, the model showed fewer false positives and more robust detection in edge cases. These targeted improvements demonstrate how small changes in training data can significantly impact system reliability.

![Retrain Model](Retrain-Model.png)
![Retrain Model2](Retrain-Model2.png)

***Interaction Improvements***

To enhance user interaction and make the experience feel more personal, we updated the system to provide time-specific motivational messages. Instead of repeating the same greeting throughout the day, the device now delivers context-aware responses—such as a gentle "Good morning! You've got this." or an encouraging "Good evening. Let’s get a bit done."—based on the current hour.

In addition, I enhanced the text-to-speech audio quality. The default voice previously sounded too robotic and detached. I replaced it with a more natural-sounding voice using a built-in speech synthesis tool that better conveys tone and warmth. This makes the motivational prompts feel more encouraging and pleasant to hear during interaction.

[![Demo](thumbnail.png)](https://youtu.be/7mVEo3a3GHE) 
[![Edge Case Testing - Dim light](thumbnail.png)](https://youtube.com/shorts/XjR7BTSQimY?feature=share) 
[![Edge Case Testing - Dim light](thumbnail.png)](https://youtu.be/B8TMCJNlymg) 
