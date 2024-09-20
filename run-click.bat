set FLASK_ENV=development
set FLASK_DEBUG=1
set FLASK_APP=app:app
set CONFIG_FILE=dev.conf

flask %*
