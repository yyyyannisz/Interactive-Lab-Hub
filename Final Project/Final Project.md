# Final Project

[Project Plan](#project-plan) 

[Functioning Project](#functioning-project) 

[Documentation of Design Process](#documentation-of-design-process) 

[Archive of All Code and Design Patterns](#archive-of-all-code-and-design-patterns) 

[Video Demo](#video-demo) 

[Reflections on Process](#reflections-on-process) 

[Group Work Distribution](#group-work-distribution) 

## Project Plan

This project is done by Yannis Zhu & Amy Chen.

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

Plush duck enclosure – physical embodiment of CyberDuck and housing for the system

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

#### TA Mode: 

![storyboard 1](Storyboard2.jpg)

#### Timer Mode: 

![storyboard 2](Storyboard1.jpg)

### Wizard 

1. Wizarding with Wendy
   
![Wizarded with Wendy](Wizard_Wendy.jpg)

During the session with Wendy, one of the most prominent observations was that most people work silently during focused tasks. This made it difficult to determine when CyberDuck should interject, since there were few explicit cues indicating whether the user wanted interaction or uninterrupted focus.

Wendy suggested that CyberDuck could adopt a Pomodoro-like structure, where the duck announces when a focus session ends, asks what the user has accomplished, and offers brief positive reinforcement. This approach would allow CyberDuck to support users without requiring continuous conversational engagement. Wendy also commented on the voice, suggesting that it could be more “duck-like”, reinforcing the playful, companion-based nature of the device.

Insight: Structured, time-based interventions may feel more appropriate than spontaneous conversational interruptions during focus-heavy workflows.

2. Wizarding with Jade Change(Interactive Device Classmate)

Jade found the interaction meaningful and potentially useful, noting that the cuteness of the duck made the experience more engaging and approachable. However, she felt that the chosen voice (Zephyr; one of the Gemini AI voices) was too high-pitched and hyper, which could become distracting during extended use.

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

#### Physical Construction

For the physical embodiment of CyberDuck, we were fortunate to find a plush duck toy whose size, proportions, and visual character closely matched our envisioned product. The softness and familiarity of the plush material helped reinforce CyberDuck’s role as a friendly desk companion rather than a piece of technical equipment.

Initially, we considered opening the plush duck and embedding a mini speaker inside the body. However, after further consideration, we realized that the battery life and maintenance of an internally embedded speaker could become problematic, especially during longer work sessions. To avoid frequent disassembly or charging difficulties, we instead designed a small external pouch that CyberDuck “wears” like a backpack. The mini speaker is placed inside this pouch, allowing easy access for charging or replacement while preserving the integrity of the duck body. This solution balanced practicality with the playful character of the object, and it visually reinforced CyberDuck as an active, mobile companion.

#### Early Software Prototypes

On the software side, development began with two largely independent prototypes corresponding to the two interaction modes.

The initial TA Mode, built by Amy, relied on a slower, native large language model with relatively poor text-to-speech quality. While the core idea of conversational assistance was present, the latency and robotic audio output made interactions feel sluggish and unnatural, especially during problem-solving scenarios.

In parallel, I built the first version of Timer Mode, which relied entirely on pre-recorded audio. These audio clips used a Gemini-generated voice, and based on feedback from Wizard-of-Oz testing, I selected the “Sulafat” voice, which is warm and mid-pitched. To further enhance the playful tone, I added a soft quack sound as an auditory signature to make interactions feel lighter and more engaging.

However, the flow of this early Timer Mode was intentionally simple. It consisted of:

- A greeting announcing the start of the session

- A silent focus period

- A announcement when five minutes remained, paired with encouragement

- A announcement marking the end of the session and encouraging future focus

While this version established the basic rhythm of Timer Mode, it lacked interactivity and personalization.

#### Feedback from Functional Check-off

After presenting this version during the functionality check, we received several important pieces of feedback from the teaching team:

- TA Mode should move to a faster language model with improved text-to-speech, potentially using an API-based approach to reduce latency and improve conversational quality.

- Timer Mode could benefit from richer interaction, such as incorporating contextual sensing (e.g., phone detection or mug detection) to make the experience more responsive and playful. For example, detecting phone usage could trigger a gentle reminder to refocus, while detecting a coffee mug could prompt a lighthearted comment encouraging productivity.

This feedback motivated a significant refinement of both modes.

#### Refined TA Mode

In the later version, the TA Mode was redesigned to prioritize responsiveness and guided reasoning. It now uses the Gemini API to answer user questions, with the key design constraint that the assistant should walk the user through a problem rather than simply provide solutions. To support this, the system sends the full conversational context with each request, allowing the model to remember what the user has previously said and maintain continuity across turns. Conceptually, this makes TA Mode feel closer to a thoughtful tutor than a search engine.

#### Expanded Timer Mode

The new Timer Mode evolved substantially from the initial prototype. In addition to pre-recorded audio cues, we introduced user voice input, allowing the system to ask what the user is focusing on and how long they would like to work. The interaction now includes a calming breathing ritual at the start of each session, mid-session encouragement, optional check-ins, and a structured countdown at the end.

Technically, Timer Mode integrates speech recognition to capture short user responses and treats these inputs as lightweight signals rather than open-ended conversation. This design choice was informed by Wizard-of-Oz findings indicating that excessive or poorly timed interaction can disrupt focus. All audio feedback remains intentionally brief, supportive, and predictable.

Together, these refinements transformed Timer Mode from a static timer into a guided focus experience that balances structure, encouragement, and user agency.

#### Gesture-Based Mode Switching

A key milestone in the development of CyberDuck was getting gesture-based mode switching fully functional. Using a gesture sensor, we enabled users to switch between Timer Mode and TA Mode through simple hand gestures, without needing to speak commands or touch the device. This decision reinforced CyberDuck’s role as an embodied, ambient companion, allowing mode changes to feel lightweight and intentional rather than conversational or menu-driven.

Technically, gesture detection runs continuously in the background and updates the system’s current mode state in real time. An upward gesture activates Timer Mode, while a downward gesture switches to TA Mode. Once a gesture is detected, CyberDuck provides brief audio confirmation to make the transition clear to the user.

From an interaction design perspective, this feature addressed a recurring concern identified during Wizard-of-Oz testing: users did not always want to verbally engage with the system, especially during focused work. Gesture-based switching allowed users to control CyberDuck without breaking cognitive flow, and it provided a clear boundary between focused and problem-solving states. This functionality ultimately became a core part of CyberDuck’s interaction model, tying together the physical form of the duck with its software behavior.

#### User Testing

We used the Final Project Presentation as an opportunity to conduct informal user testing with our prototype. During the presentation session, at least eight users interacted with CyberDuck and explored its core features. However, because multiple groups were presenting in the same room simultaneously, the environment was noisy and highly dynamic, which made both user voice input and hearing CyberDuck’s audio output challenging. As a result, users were only able to test gesture-based mode switching and Timer Mode, while extended verbal interaction in TA Mode was limited.

Despite these constraints, users responded positively to several aspects of the system. Many participants found the breathing exercise at the start of Timer Mode to be engaging and calming, noting that it helped signal a clear transition into focused work. Users also expressed strong interest in the overall concept and physical appearance of CyberDuck, describing it as approachable, playful, and well-suited for a desk companion. Even without fully testing voice-based interaction, participants were able to understand the intended behaviors of the system and how the two modes support different working needs.

Overall, this testing session helped validate key design choices around embodiment, gesture-based interaction, and structured focus rituals, while also highlighting the importance of quieter environments for future evaluations of speech-based interaction.

Below is a photo of a participant talking to CyberDuck, demonstrating voice-based interaction:
![User Testing](Uer_testing.jpg)

Below is a photo of a participant testing CyberDuck’s gesture-based mode switching feature.:
![Testing Switching Mode](Switching_mode.jpg)

#### Additional Feature

## Archive of All Code and Design Patterns

#### Please view my source code [here]()

## Video Demo

## Reflections on Process

## Group Work Distribution
This project was divided by interaction mode, with each team member taking primary responsibility for one mode while maintaining close collaboration throughout the design and implementation process.

I took primary ownership of Timer Mode, including designing the interaction flow, implementing the timing logic, voice prompts, and overall behavior during focus sessions. I also created the storyboards and produced the draft version of the final report, as well as leading much of the documentation and Wizard-of-Oz evaluations that informed key design decisions.

Amy took primary ownership of TA Mode, focusing on the learning- and reasoning-oriented interaction design. She implemented the mode-switching mechanism, ensuring smooth transitions between Timer Mode and TA Mode, and shaped how the system responds during problem-solving interactions.

Despite this division of responsibility, all core design decisions were made collaboratively. We regularly shared ideas, discussed trade-offs, and supported each other’s work to ensure a cohesive overall design. While I prepared the initial draft of the final report, we ultimately each wrote and submitted our own final report, reflecting both individual contributions and the shared design process.

## Notes on AI Assistant
For this lab, I used ChatGPT to help me summarize my design decisions and rewrite some sections into clearer paragraphs. All reflection points and design choices are my own. Also, some of my script was coded using the assistance of ChatGPT.
