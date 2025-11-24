
    #rm -rf /tmp/mathics-* /tmp/.venv
    #python -m venv /tmp/.venv

    cd /tmp
    source .venv/bin/activate

    #git clone https://github.com/bdlucas1/mathics-core
    #cd mathics-core
    #git checkout plot3d-default-options
    #make develop
    #exit


    git clone https://github.com/bdlucas1/mathics-demo
    cd mathics-demo
    pip install -r requirements.txt
    python fe_browser.py demos/demo_*.m
