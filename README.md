# mahlo_popup

This project needed to be able to do several things: show a popup on an existing HMI screen when operation was stopped, not obstruct the original HMI while in operation, and capture operator feedback about operating conditions - saving it to a database.

It uses a flask RESTful API for the RPC for signaling that operation has stopped/started (built for Ignition SCADA, but it would work with anything that can do HTTP requests), flask SQLalchemy to interact with the database, and a themed tkinter interface for the popup.

It uses a pair of deques for bidrectional communication between the flask server and the tkinter thread. The flask SQLalchemy model has been integrated into the tkinter popup.
