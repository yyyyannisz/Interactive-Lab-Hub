# Interactive Prototyping: The Clock of Pi

# Lab 2 Part 1

Yannis Zhu yz3477 

![Set up](device-set-up.jpg)

![Displaying an image](display-image.jpg)

![Set up the Display Clock Demo](provided-demo-click.jpg)

![button using video](button-use-video.mov)


## Sketch and brainstorm further interactions and features you would like for your clock for Part 2.

***Introduction***:
I want to reimagine time as a cyclical, body-based rhythm rather than a strictly linear measure. For many women and people who menstruate, time is already experienced this way — not only in weeks or months, but in recurring physical and emotional patterns shaped by the menstrual cycle. With this in mind, my goal for this project is to build a ***“Period Clock”***, a physical interface that helps users understand and track the phases of their cycle in a gentle, intuitive, and empowering way. This design aims to support self-awareness, encourage planning around one’s natural fluctuations in energy and mood, and make visible the cyclical nature of menstruation as it is lived and felt.

![Interface Desgin & Storyboard](storyboard.jpg) 

***Interface Design***:
Our Period Clock uses a circular display to represent the menstrual cycle, divided into ***four phases: Menstrual, Follicular, Ovulatory, and Luteal***. A pointer shows the user’s current position in the cycle, making it easy to see where they are and what phase comes next. Alongside the diagram, the interface presents today’s date, the day of the cycle, a short phrase describing energy or mood, symptom reminders, and a suggested action such as “Start new projects” or “Rest more.” This design turns abstract cycle data into an intuitive, everyday reference.

***Storyboard***:
The storyboard shows one example of how the Period Clock helps users connect daily experiences to their cycle. At first, the user feels terrible during their period. Later, the clock explains they are in the Luteal phase, helping them understand low energy and cravings. The interface suggests rest, and the user realizes they should care for themselves more during this time. A month later, the user feels prepared and reflects, “Better planning this month,” showing how the clock builds awareness and self-compassion.

# Lab 2 Part 2

### Modify the barebones clock to make it your own

***Peer Feedback***: 

Because I missed some class time due to being sick, I was not able to get feedback from classmates in this course, but I reached out to other Cornell Tech students and peers for their input.

1. Ruowen Lou HT'27 (II2226)
-  Your project reminds them of the Clue period tracking app. While Clue also uses a "period clock" visual, your design stands out by clearly identifying the four distinct phases (menstrual, follicular, ovulatory, luteal), which they find more informative and helpful.

- I really like the educational content about menstrual health, but I think more details would be better (e.g., phase explanations, hormone changes). I like that it includes symptom tracking, such as recording bleeding volume or other physical/emotional states.

- Suggestion: Consider integrating with fitness and self-care routines, such as: yoga, meditation, or exercise planning. These could be tailored to the user’s current cycle phase to support holistic well-being. 

2. Xinyi Huang CM'27 (xh453)
-  I think your design concept is very useful. It turns the menstrual cycle, which can feel abstract, into a familiar format like a clock. This makes it easier to understand and remember which stage someone is in.
  
- I wonder how the app can be used by different people. For example, how does it know my cycle? Is there a way for me to enter my own data? 

- Showing energy, symptoms, and activities all at once could feel overwhelming. The layout could be reorganized to make the interface cleaner and easier to use.

- I really like your design overall. I think adding a mood or lifestyle recommendation module would be a good idea. For example, it could say “Today is good for watching a relaxing movie” or “Chat with friends.” Another idea is to connect with an external calendar so exercise or activity suggestions fit the user’s actual schedule.

3. Jiayi Wu Industry UX designer
- I noticed that the four phases are not evenly divided on the cycle, since the menstrual cycle has different lengths for each phase. You could think about how to represent that more clearly in your design. One idea is to use color to show the relative share of each phase.

- Also, consider how to place or style the titles of each phase on the clock so that they are easier to read and look more visually balanced.


Based on feedback from peers, they all felt the clock-based visualization of the menstrual cycle was intuitive and helpful in making abstract cycle concepts more concrete. A key takeaway was the need to think carefully about how to divide the four phases, since they are not equal in length. I did a little bit of research on this: the ***Menstrual phase*** (about 3–7 days) is when bleeding occurs and hormone levels are at their lowest. The ****Follicular*** phase (about 7–10 days) is when the body prepares an egg and energy levels usually begin to rise. The ***Ovulatory*** phase (about 1–2 days) is when ovulation happens and fertility is at its peak. The ***Luteal*** phase (about 12–14 days) is when the body prepares for a possible pregnancy and many people experience PMS symptoms. I plan to refine the design so that each phase reflects its typical duration, using color to visually represent the proportion of time each phase takes within the cycle.

Another recurring point was the potential information overload on a single screen. To address this, I plan to improve the layout by organizing content into different screens. The ***main screen*** will display the ****period clock with phase visualization***. A ***second screen*** will focus on daily details such as ****energy level, symptoms, and activity suggestions****, presented in a cleaner and less crowded way. I also plan to add a ***third screen*** where users can enter the ***date of their last period***. This will allow the clock to calculate their current cycle day more accurately and make the display more relevant.

Upadted Interface Design: 


\*\*\***A copy of your code should be in your Lab 2 Github repo.**\*\*\*



## Make a short video of your modified barebones PiClock

\*\*\***Take a video of your PiClock.**\*\*\*

After you edit and work on the scripts for Lab 2, the files should be upload back to your own GitHub repo! You can push to your personal github repo by adding the files here, commiting and pushing.

```
(venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 2 $ git add .
(venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 2 $ git commit -m 'your commit message here'
(venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 2 $ git push
```

After that, Git will ask you to login to your GitHub account to push the updates online, you will be asked to provide your GitHub user name and password. Remember to use the "Personal Access Tokens" you set up in Part A as the password instead of your account one! Go on your GitHub repo with your laptop, you should be able to see the updated files from your Pi!


[Update your Lab Hub](pull_updates/README.md) to get the latest content and requirements for Part 2.

Modify the code from last week's lab to make a new visual interface for your new clock. You may [extend the Pi](Extending%20the%20Pi.md) by adding sensors or buttons, but this is not required.

As always, make sure you document contributions and ideas from others explicitly in your writeup.

You are permitted (but not required) to work in groups and share a turn in; you are expected to make equal contribution on any group work you do, and N people's group project should look like N times the work of a single person's lab. What each person did should be explicitly documented. Make sure the page for the group turn in is linked to your Interactive Lab Hub page. 


