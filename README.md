# Bulk-Transaction-Tester
Bulk Transaction Tester for Stress Testing


In order to use the 'runUpdateTaid', you will need to have the O Series Client Utilities installed and have the oseries-client.properties file configured for your O Series /vertex-remote-services endpoint. This .py file relies on this service to run a data extract for Tax Areas which it then uses to populate its dictionary.

The goal is to use this 'runTaidUpdate' whenever the Transaction Tester selects the option to generate a random TAID for populating in each soap_payload. This keeps the TAID's up to date based on your O Series environment.

The other file which combines both of these features into a single UI does not full work yet.
