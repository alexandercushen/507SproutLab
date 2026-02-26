Welcome to my first home software project: 507SproutLab!

This project is to allow me to monitor my vegetable seedlings through a variety of sensors, analyse their growth and climate data, and hopefully one day be able to perform actions to support them!

---------

static/: 
contains data for rendering the website (images, etc)

templates/: 
contains files for controling the website functioknality

app.py:
run using "python3 app.py" to host the website locally.
Using screen allows it to run in the background; to enter the screen, use:
screen -S sproutlab
The screen can be left with control + A, then D
It can be returned to later to check in with screen -r sproutlab
The website can be made available to the web using "cloudflared tunnel --url http://localhost:5000"

data/:
contains all of the records of plant growth

scripts/:
how to update plant logs, and perform other actions

-----------

To-do:
- Make plant log visible on the website
- Make python scripts usable from the site
- Add live camera view
- Add camera history page
- Add temp/humidity sensor record
- Add image analysis tools for growth detection and pest warning
