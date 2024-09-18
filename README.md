# How to run:
* Clone repo
* create "mylibrary" postgres database (createdb mylibrary)
* create venv (python3 -m venv venv && source venv/bin/activate)
* install everything from requirements.txt (pip install -r requirements.txt)
* initilise and upgrade database (
    flask db init
    flask db migrate
    flask db upgrade
    )
* run app (maybe hopefully probably)

# TODO
* Figure out what API to use - binned this for now. It was annoying me
* Get add / search working - add is working
* Improve currently reading
* Ensure changes work across users
* Add more fields to currently reading (data (editable), (pages (editable), etc))