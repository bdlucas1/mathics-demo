    cd /tmp
    #rm -rf .venv
    #python -m venv .venv
    source .venv/bin/activate
    #git clone https://github.com/bdlucas1/mathics-core
    #cd mathics-core
    #git checkout plot3d-default-options
    #make develop
    #cd ..
    #git clone https://github.com/bdlucas1/mathics-demo
    cd mathics-demo
    pip install -r requirements.txt
    DEMO_BROWSER=webbrowser python fe_browser.py demos/demo_*.m
