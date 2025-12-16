# Final Project

[Project Plan](#project-plan) 

[Functioning Project](#functioning-project) 

[Documentation of Design Process](#documentation-of-design-process) 

[Archive of All Code and Design Patterns](#archive-of-all-code-and-design-patterns) 

[Video Demo](#video-demo) 

[Reflections on Process](#reflections-on-process) 

[Group Work Distribution](#group-work-distribution) 

## Project Plan

This project will be done by Yannis Zhu & Amy Chen.

### Big Idea

CyberDuck is an AI-powered desk companion designed to support people during focused work and problem-solving through two complementary interaction modes: Timer Mode and TA Mode. While both modes aim to help users work more effectively, they address fundamentally different cognitive needs and are therefore not interchangeable.

Timer Mode is most effective when users already know what they want to work on but struggle with focus, motivation, or time awareness. In this mode, CyberDuck structures work into focused sessions, provides gentle audio cues, and offers light emotional encouragement. The goal is to support sustained attention without interrupting the user’s thinking. In these situations, giving advice or solutions would be distracting rather than helpful.

TA Mode, by contrast, is designed for moments of cognitive blockage, such as debugging code or reasoning through a difficult problem. Instead of behaving like a traditional chatbot that quickly provides answers, TA Mode is intentionally pedagogical. CyberDuck guides users through their own reasoning process by asking leading questions, breaking problems into smaller steps, and encouraging reflection. This design emphasizes learning and understanding over efficiency, making it especially suitable for educational or skill-building contexts.

These two modes serve different purposes and are most valuable at different moments in a user’s workflow. A timer alone cannot help a user reason through a logic bug, just as an intelligent tutor may interrupt deep focus when the user simply needs uninterrupted work time. By combining both modes into a single, embodied device, and allowing users to switch between them using simple physical gestures, CyberDuck adapts to changing cognitive needs throughout the day while keeping the interaction lightweight, playful, and intuitive.

![big idea](CyberDuck_Poster.png)

###  Timeline
11/10: Finish & submit project plan

11/11 – 11/14: Design iterations
- Storyboarding
- Dialogue design
- Wizard device to get user opinions (what’s a good voice + additional features)

11/15 – 11/20: Implement the design (device only)
- Raspberry Pi setup and configuration
- Implement STT → LLM → TTS pipeline
- Gesture sensor integration and mode switching logic
- Initial audio output and timing calibration

11/21 – 11/23: Module Testing
- Test each module separately
- Refine voice + timing

11/24 – 11/25: System Integration
- Combine gesture switching with conversation engine

11/26 – 11/31: Implement the design (physical build)
- Create the Cyberduck body
- Integrate Raspberry Pi, microphone, speaker, and sensors
- Finalize physical form and wiring

12/1: Functional check-off
- Present working prototype to teaching team
- Demonstrate Timer Mode and TA Mode switching

12/2 – 12/7: User testing & documentation
- Test with sample users
- Collect feedback on intuitiveness, latency, and clarity
- Record demo video and prepare presentation materials

12/8: Final project presentation
- Present CyberDuck to the class

12/9 – 12/15: Reflection & final write-up
- Summarize design process and user feedback
- Reflect on trade-offs, limitations, and future improvements
- Submit final documentationion

### Parts Needed

Raspberry Pi 4 – main computing unit

USB microphone – speech input for user interaction

Mini speaker – audio output for feedback and responses

APDS-9960 gesture sensor – physical gesture detection for mode switching

Fast LLM model and improved TTS – to reduce latency and improve conversational quality

### Fallback Plan

Given the complexity of real-time speech and gesture interaction, several fallback strategies are planned to ensure robustness:

- If LLM response latency becomes too high, CyberDuck will switch to pre-scripted prompts for common encouragements or guiding questions.

- If real-time generation is unreliable, speech-to-text results can be used to trigger predefined responses rather than full conversational output.

- If the gesture sensor proves unreliable, it can be replaced with a simple physical button for mode switching while preserving the core interaction logic.

These fallback options ensure that even if advanced components fail, the core user experience—mode switching and supportive interaction—remains functional and testable.

## Functioning Project

![final product]

## Documentation of Design Process

### Storyboards

#### Scenario 1: 

![storyboard 1]

#### Scenario 1: 

![storyboard 2]

### Wizard 


#### Notes

#### Reflection

### Building Functionality

### User Testing

### Additional Feature

## Archive of All Code and Design Patterns

#### Please view my source code

## Video Demo

## Reflections on Process

## Group Work Distribution


