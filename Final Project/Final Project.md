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

These fallback options ensure that even if advanced components fail, the core user experience of mode switching and supportive interaction remains functional and testable.

## Functioning Project

![final product1](Cyberduck1.jpg)
![final product2](Cyberduck2.jpg)

## Documentation of Design Process

### Storyboards

#### Scenario 1: 

![storyboard 1](Storyboard1.jpg)

#### Scenario 1: 

![storyboard 2](Storyboard2.jpg)

### Wizard 

1. Wizarding with Wendy
   
![Wizarded with Wendy](Wizard_Wendy.jpg)

During the session with Wendy, one of the most prominent observations was that most people work silently during focused tasks. This made it difficult to determine when CyberDuck should interject, since there were few explicit cues indicating whether the user wanted interaction or uninterrupted focus.

Wendy suggested that CyberDuck could adopt a Pomodoro-like structure, where the duck announces when a focus session ends, asks what the user has accomplished, and offers brief positive reinforcement. This approach would allow CyberDuck to support users without requiring continuous conversational engagement. Wendy also commented on the voice, suggesting that it could be more “duck-like”, reinforcing the playful, companion-based nature of the device.

Insight: Structured, time-based interventions may feel more appropriate than spontaneous conversational interruptions during focus-heavy workflows.

2. Wizarding with Jade Change(Interactive Device Classmate)

Jade found the interaction meaningful and potentially useful, noting that the cuteness of the duck made the experience more engaging and approachable. However, she felt that the chosen voice (Zephyr) was too high-pitched and hyper, which could become distracting during extended use.

Jade also suggested the need for a clear wake-up line to signal when CyberDuck is actively listening, rather than always passively monitoring the environment. In the context of TA Mode, she wondered whether CyberDuck could have more contextual awareness, such as knowing what is on the user’s screen, to better support debugging or problem-solving.

Insight: Even when the overall concept is appealing, voice characteristics and clear listening boundaries strongly affect comfort and trust.

3. Wizarding with Jiayi Wu (UX Designer)

Jiayi raised several deeper concerns around conversational AI and cognitive flow. She emphasized the importance of customization, noting that not all users would want to interact with a duck persona or a playful voice. In fact, she felt that a duck voice could feel awkward or unnatural in serious work contexts.

Jiayi also stressed the need for explicit instructions about when CyberDuck is listening. She expressed discomfort with the idea of the duck listening at all times and strongly supported the idea of a wake-up line or deliberate activation mechanism. More broadly, she pointed out that conversation with AI can feel unnatural, especially because human conversation naturally involves interruptions, pauses, and overlapping speech.

Importantly, Jiayi noted that talking through ideas aloud is often part of her personal thinking process, and an AI responding at the wrong moment could actually pull her out of that flow. In some cases, she may want to verbalize thoughts without receiving any response at all—similar to the original idea of “rubber duck debugging.”

Insight: The hardest design challenge is not generating responses, but deciding when not to speak. Timing and restraint are critical for preserving users’ cognitive flow.

#### Key Takeaways & Design Implications

Across all three Wizard-of-Oz sessions, a consistent theme emerged: timing matters more than intelligence. While users appreciated the idea of an embodied AI companion, unsolicited or poorly timed interruptions risk breaking focus and feeling unnatural.

These findings directly informed several design decisions:

- Adopting Timer Mode as a structured, predictable interaction pattern

- Introducing a wake-up line to clearly signal when CyberDuck is listening

- Avoiding constant conversational engagement in favor of intentional, mode-based interaction

- Treating silence and non-response as valid and sometimes preferable system behaviors

- Considering voice customization and personality flexibility for different users

Overall, the Wizard-of-Oz study helped shift CyberDuck from a conversational AI that always responds toward a companion that is selectively present, supporting users without demanding attention.

### Building Functionality

#### User Testing

#### Additional Feature

## Archive of All Code and Design Patterns

#### Please view my source code

## Video Demo

## Reflections on Process

## Group Work Distribution
This project was divided by interaction mode, with each team member taking primary responsibility for one mode while maintaining close collaboration throughout the design and implementation process.

I took primary ownership of Timer Mode, including designing the interaction flow, implementing the timing logic, voice prompts, and overall behavior during focus sessions. I also created the storyboards and produced the draft version of the final report, as well as leading much of the documentation and Wizard-of-Oz evaluations that informed key design decisions.

Amy took primary ownership of TA Mode, focusing on the learning- and reasoning-oriented interaction design. She implemented the mode-switching mechanism, ensuring smooth transitions between Timer Mode and TA Mode, and shaped how the system responds during problem-solving interactions.

Despite this division of responsibility, all core design decisions were made collaboratively. We regularly shared ideas, discussed trade-offs, and supported each other’s work to ensure a cohesive overall design. While I prepared the initial draft of the final report, we ultimately each wrote and submitted our own final report, reflecting both individual contributions and the shared design process.
