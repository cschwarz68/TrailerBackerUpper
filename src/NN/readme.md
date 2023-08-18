# NN
Legacy neural network source code. 

Files in models/ are models trained for forward driving. Training data is generated using the same process as [`this article`](https://towardsdatascience.com/deeppicar-part-1-102e03c83f2c)

These models are not good.  I'm only really keeping them here because they were here before I got here.

The modules ending in _legacy are here because there was a file in here that used RPi.GPIO to drive the car with the neural network.
I've updated that module (model.py) to use pigpiod and moved it into the main project src directory.
-Chris
