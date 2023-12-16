import json

###############################################################################
##                          Classify SFO Gates                               ##
###############################################################################
## Requester:                              United Airlines Ground Ops
## Documentation: https://www.flightaware.com/aeroapi/portal/documentation#overview
## Created by:    Tanay Gupta
## Created by:
## Created by:
##
''' Purpose:
Help United optimize aircraft gating at SFO Airport. 
This application will first classify all of the United-accessible gates
based on allowable aircraft types and then develop optimization algorithm
that reflects bank and lull periods.

'''
##-----------------------------------------------------------------------------
##                            Source tables                                  ##
##-----------------------------------------------------------------------------
##      Using aero API's GET /flights/{ident}
##
##
##----------------------------------------------------------------------------- 
##                         calcs/business rules                              ##
##-----------------------------------------------------------------------------
##
##
##
##-----------------------------------------------------------------------------
##                             CHANGE LOG                                    ##
##-----------------------------------------------------------------------------
## DATE | FIRST NAME | LAST NAME      |CHANGE MADE
## 12/15                Gupta           init
##
###############################################################################


###############################################################################
##                          Step 1: Get Flights at SFO                       ##
###############################################################################

'''
Establish data structure: Dictionary <gate, (aircraft_type1,aircraft_type2...) >
'''
file_path = 'sfo_aircraft_response.json'
all_sfo_flights = ""
with open(file_path, 'r') as json_file:
    all_sfo_flights = json.load(json_file)

aircraft_by_gate_dict = {}

for arriving_flight in all_sfo_flights["arrivals"]:
    # print(arriving_flight)
    if arriving_flight["destination"]["code"] == "KSFO":
        curr_gate = arriving_flight["gate_destination"]
        curr_aircraft = arriving_flight["aircraft_type"]
        aircraft_by_gate_dict[str(curr_gate)].add(str(curr_aircraft))
        print(f"{curr_gate},{curr_aircraft}")