##################################################
An Attempt at Creating Mods for Sims4
#################################################

DEMO: https://youtu.be/isrfFLIS3Fs

A demo of our Phase 3 Flatiron school project is linked above. Phase 3 focused on fundamentals in Python, and as Sims 4 (EA) is built on Python, Yinson and I, Jolie, tried our hand at a Sims 4 game mod (and had to get familiar with markup language XML in the process). In the process of doing so, we found that not only would it have been nearly impossible on our own with our beginner programming skills, but also that the process of creating mods for the Sims4 was made easier through applications that were developed by other individuals. EA unfortunately does not provide much documentation. This respository includes the data that was decompiled using LuquanLi's Sims4 Decompiler/Mod Creator. A Full guide can be found on their github at https://github.com/LuquanLi/TheSims4ScriptModBuilder. We also used cmarNYC's s4pe to decompile the mods that we made to analyze the code and XML(https://github.com/s4ptacle/Sims4Tools/releases/). 

The mod allows Sims to attend a simulation of the Flatiron school and follow vocational tracks in Software Engineering or Cyber Security, with different tasks and promotional requirements for each. As Sims 4 already has functionality to build a programming skill, Sims can practice programming, hack, create viruses, mod games, make web pages, apps, video games, and more! Completing these tasks and boosting programming and charisma skills (after all, we are here to learn the technical skills we need to get into the work force!) will progress Sims through 5 phases of each branch until they have mastered these skills.



**************************************************
.
├── Game
│    ├── *decompiled files/folders
├── src
│    ├── *command cheats
├── test
│    ├── *created modpack
│        ├── *modpack files
├── utils
│    ├──*requirements for  compiler/decompiler to work
├── compile.py
├── config.ini
├── decompile.py
└── README.md
