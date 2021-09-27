# virtual-factory
Virtual Factory web app, used to receive and display graphical machine data from Learning Factory in real-time.

## Installation Instructions
First, ensure that you have the latest build tools installed on your machine:
```
python3 -m pip install --upgrade build
python3 -m build
```

Then, you can install the `virtual-factory` package as follows:
```
python3 -m pip install -e .
```

## Testing Instructions
You can run the integration test with the following command:
```
python tests/test_integration.py
```
