# goit-pyweb-hw-14
run project

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

run terminal 1:
unicorn main:app --reload --port 8001

run terminal 2:
python -m unittest discover unit_tests
pytest --cov=. tests/
